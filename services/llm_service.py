"""
Serviço para integração com Zello MIND LLM.
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List
from config import config


class LLMService:
    """Serviço para comunicação com Zello MIND LLM."""
    
    def __init__(self, zello_api_key: str = None):
        """
        Inicializa o serviço de LLM.
        
        Args:
            zello_api_key: Chave de API da Zello (opcional, usa config se não fornecida)
        """
        self.zello_api_key = zello_api_key or config.ZELLO_API_KEY
    
    def get_completion(self, provider: str, messages: List[Dict[str, str]]) -> str:
        """
        Obtém uma resposta de completão da Zello MIND LLM.
        
        Args:
            provider: Provedor da LLM (apenas 'zello' é suportado)
            messages: Lista de mensagens no formato [{"role": "user", "content": "texto"}]
            
        Returns:
            Conteúdo da resposta da IA
            
        Raises:
            Exception: Se houver erro na comunicação com a API
        """
        # Apenas Zello MIND é suportado - forçar provider para 'zello' se não for
        if provider != 'zello':
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
        
        else:
            raise Exception(f"Provedor não suportado: {provider}. Apenas 'zello' é suportado.")
    
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
    
    def process_text(self, text: str, llm_type: str = "zello", model: str = None) -> Dict[str, Any]:
        """
        Processa texto usando a Zello MIND LLM.
        
        Args:
            text: Texto para processar
            llm_type: Tipo de LLM (apenas "zello" é suportado)
            model: Modelo específico a ser usado
            
        Returns:
            Dicionário com o resultado do processamento
        """
        if llm_type.lower() == "zello":
            model = model or "zello-mind"
            return self.process_with_zello(text, model)
        else:
            return {
                "success": False,
                "error": f"Tipo de LLM não suportado: {llm_type}. Apenas 'zello' é suportado.",
                "model": model
            }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """
        Retorna os modelos disponíveis para Zello MIND.
        
        Returns:
            Dicionário com listas de modelos disponíveis
        """
        return {
            "zello": ["zello-mind", "zello-mind-pro"]
        }
