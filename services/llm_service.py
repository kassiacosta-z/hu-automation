"""
Serviço para integração com LLMs (OpenAI e Zello MIND).
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List
from openai import OpenAI
from config import config


class LLMService:
    """Serviço para comunicação com diferentes LLMs."""
    
    def __init__(self, openai_api_key: str = None, zello_api_key: str = None):
        """
        Inicializa o serviço de LLM.
        
        Args:
            openai_api_key: Chave de API da OpenAI (opcional, usa config se não fornecida)
            zello_api_key: Chave de API da Zello (opcional, usa config se não fornecida)
        """
        self.openai_api_key = openai_api_key or config.OPENAI_API_KEY
        self.zello_api_key = zello_api_key or config.ZELLO_API_KEY
        
        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
    
    def get_completion(self, provider: str, messages: List[Dict[str, str]]) -> str:
        """
        Obtém uma resposta de completão de uma LLM.
        
        Args:
            provider: Provedor da LLM ('zello' ou 'openai')
            messages: Lista de mensagens no formato [{"role": "user", "content": "texto"}]
            
        Returns:
            Conteúdo da resposta da IA
            
        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        # Removido fallback automático - apenas Zello MIND
        if provider == 'auto':
            # Se tentar usar 'auto', forçar Zello
            provider = 'zello'

        if provider == 'zello':
            if not self.zello_api_key:
                raise Exception("Zello API key não configurada")
            
            try:
                headers = {
                    "zello_mind_key": self.zello_api_key,
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "messages": messages,
                    "model": "gpt-4o-mini",
                    "max_tokens": 2000,
                    "temperature": 0.7
                }

                base_url = (config.ZELLO_BASE_URL or "").rstrip("/")
                if not base_url:
                    raise Exception("ZELLO_BASE_URL não configurado")

                # retries com backoff exponencial e timeout maior
                last_err = None
                for attempt in range(3):
                    try:
                        print(f"Tentando conectar com Zello MIND (tentativa {attempt + 1}/3)...")
                        response = requests.post(
                            f"{base_url}/api/v1/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=(30, 60)  # (connect timeout, read timeout) em segundos
                        )
                        response.raise_for_status()
                        data = response.json()
                        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    except requests.exceptions.Timeout as e:
                        last_err = e
                        print(f"Timeout na tentativa {attempt + 1}: {str(e)}")
                        if attempt < 2:  # Não dormir na última tentativa
                            time.sleep(2 * (2 ** attempt))
                    except requests.exceptions.RequestException as e:
                        last_err = e
                        print(f"Erro na tentativa {attempt + 1}: {str(e)}")
                        if attempt < 2:
                            time.sleep(2 * (2 ** attempt))
                raise Exception(f"Erro na requisição Zello após 3 retries: {str(last_err)}. Verifique a conectividade para {config.ZELLO_BASE_URL}.")
                
            except requests.exceptions.RequestException as e:
                raise Exception(f"Erro na requisição Zello: {str(e)}. Verifique a conectividade e DNS para {config.ZELLO_BASE_URL}.")
            except Exception as e:
                raise Exception(f"Erro ao processar resposta Zello: {str(e)}")
        
        elif provider == 'openai':
            if not self.openai_client:
                raise Exception("OpenAI API key não configurada")
            
            # retries com backoff exponencial
            last_err = None
            for attempt in range(3):
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        max_tokens=2000,
                        temperature=0.7
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    last_err = e
                    time.sleep(1 * (2 ** attempt))
            raise Exception(f"Erro ao processar com OpenAI após retries: {str(last_err)}")
        
        else:
            raise Exception(f"Provedor não suportado: {provider}")
    
    def process_with_openai(self, prompt: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """
        Processa um prompt usando a API da OpenAI.
        
        Args:
            prompt: Texto do prompt para processar
            model: Modelo da OpenAI a ser usado
            
        Returns:
            Dicionário com a resposta da API
            
        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        if not self.openai_client:
            raise Exception("OpenAI API key não configurada")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de requisitos e criação de Histórias de Usuário."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model
            }
    
    def process_with_zello(self, prompt: str, model: str = "zello-mind") -> Dict[str, Any]:
        """
        Processa um prompt usando a API da Zello MIND.
        
        Args:
            prompt: Texto do prompt para processar
            model: Modelo da Zello a ser usado
            
        Returns:
            Dicionário com a resposta da API
            
        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        if not config.ZELLO_API_KEY:
            raise Exception("Zello API key não configurada")
        
        try:
            headers = {
                "Authorization": f"Bearer {config.ZELLO_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{config.ZELLO_BASE_URL}/v1/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "content": data.get("choices", [{}])[0].get("text", ""),
                "model": model,
                "usage": data.get("usage", {})
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Erro na requisição: {str(e)}",
                "model": model
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model
            }
    
    def process_text(self, text: str, llm_type: str = "openai", model: str = None) -> Dict[str, Any]:
        """
        Processa texto usando a LLM especificada.
        
        Args:
            text: Texto para processar
            llm_type: Tipo de LLM ("openai" ou "zello")
            model: Modelo específico a ser usado
            
        Returns:
            Dicionário com o resultado do processamento
        """
        if llm_type.lower() == "openai":
            model = model or "gpt-3.5-turbo"
            return self.process_with_openai(text, model)
        elif llm_type.lower() == "zello":
            model = model or "zello-mind"
            return self.process_with_zello(text, model)
        else:
            return {
                "success": False,
                "error": f"Tipo de LLM não suportado: {llm_type}",
                "model": model
            }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Retorna os modelos disponíveis para cada LLM.
        
        Returns:
            Dicionário com listas de modelos disponíveis
        """
        return {
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "zello": ["zello-mind", "zello-mind-pro"]
        }
