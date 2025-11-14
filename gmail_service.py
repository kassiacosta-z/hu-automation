"""
Serviço para coleta de emails usando Gmail API com Domain-Wide Delegation.
"""

from __future__ import annotations

import base64
import email
from typing import Dict, List, Optional, Any
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailService:
    """
    Serviço para interação com Gmail API usando Service Account com Domain-Wide Delegation.
    
    Permite acessar emails de qualquer usuário do domínio autorizado.
    """
    
    # Scopes necessários para Gmail API
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_path: str, delegated_user: str):
        """
        Inicializa o serviço Gmail.
        
        Args:
            credentials_path: Caminho para o arquivo JSON de credenciais da Service Account
            delegated_user: Email do usuário a ser delegado (ex: user@empresa.com)
        """
        self.credentials_path = credentials_path
        self.delegated_user = delegated_user
        self._service = None
        self._labels_cache = {}
    
    def _get_service(self):
        """
        Obtém o serviço Gmail autenticado.
        
        Returns:
            Serviço Gmail autenticado
        """
        if self._service is None:
            # Carregar credenciais da Service Account
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            
            # Aplicar delegação de domínio
            delegated_credentials = credentials.with_subject(self.delegated_user)
            
            # Construir serviço Gmail
            self._service = build('gmail', 'v1', credentials=delegated_credentials)
        
        return self._service
    
    def search_emails(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Busca emails usando query do Gmail.
        
        Args:
            query: Query de busca do Gmail (ex: "from:gemini@google.com")
            max_results: Número máximo de resultados
            
        Returns:
            Lista de dicionários com informações básicas dos emails
            
        Raises:
            Exception: Se houver erro na API do Gmail
        """
        try:
            service = self._get_service()
            
            # Buscar mensagens
            result = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = result.get('messages', [])
            
            print(f"  🔍 Buscando emails com filtro: {query}")
            print(f"  📬 {len(messages)} emails encontrados")
            
            return messages
            
        except HttpError as error:
            raise Exception(f"Erro ao buscar emails: {error}")
    
    def get_email_details(self, message_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de um email.
        
        Args:
            message_id: ID da mensagem no Gmail
            
        Returns:
            Dicionário com detalhes do email
            
        Raises:
            Exception: Se houver erro na API do Gmail
        """
        try:
            service = self._get_service()
            
            # Obter mensagem completa
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extrair headers
            headers = message['payload'].get('headers', [])
            header_dict = {h['name']: h['value'] for h in headers}
            
            # Extrair corpo do email
            body = self._extract_body(message['payload'])
            
            # Formatar data
            date_str = header_dict.get('Date', '')
            try:
                parsed_date = email.utils.parsedate_to_datetime(date_str)
                formatted_date = parsed_date.strftime('%a, %d %b %Y %H:%M:%S %z')
            except:
                formatted_date = date_str
            
            return {
                'id': message_id,
                'subject': header_dict.get('Subject', 'Sem assunto'),
                'from': header_dict.get('From', 'Remetente desconhecido'),
                'date': formatted_date,
                'body': body,
                'owner': self.delegated_user
            }
            
        except HttpError as error:
            raise Exception(f"Erro ao obter detalhes do email {message_id}: {error}")
    
    def mark_as_read(self, message_id: str) -> bool:
        """
        Marca um email como lido.
        
        Args:
            message_id: ID da mensagem no Gmail
            
        Returns:
            True se marcado com sucesso, False caso contrário
        """
        try:
            service = self._get_service()
            
            # Marcar como lido (remover label UNREAD)
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return True
            
        except HttpError as error:
            print(f"  ⚠️ Erro ao marcar email {message_id} como lido: {error}")
            return False
    
    def add_label(self, message_id: str, label_name: str) -> bool:
        """
        Adiciona uma label a um email.
        
        Args:
            message_id: ID da mensagem no Gmail
            label_name: Nome da label a ser adicionada
            
        Returns:
            True se label adicionada com sucesso, False caso contrário
        """
        try:
            service = self._get_service()
            
            # Obter ou criar label
            label_id = self._get_or_create_label(label_name)
            if not label_id:
                return False
            
            # Adicionar label ao email
            service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return True
            
        except HttpError as error:
            print(f"  ⚠️ Erro ao adicionar label '{label_name}' ao email {message_id}: {error}")
            return False
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extrai o corpo de texto de um email (suporta multipart).
        
        Args:
            payload: Payload da mensagem do Gmail
            
        Returns:
            Corpo do email em texto plano
        """
        body = ""
        
        if 'parts' in payload:
            # Email multipart
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    # Fallback para HTML se não houver texto plano
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
        else:
            # Email simples
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(
                        payload['body']['data']
                    ).decode('utf-8', errors='ignore')
            elif payload['mimeType'] == 'text/html':
                if 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(
                        payload['body']['data']
                    ).decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def _get_or_create_label(self, label_name: str) -> Optional[str]:
        """
        Obtém ou cria uma label no Gmail.
        
        Args:
            label_name: Nome da label
            
        Returns:
            ID da label ou None se houver erro
        """
        try:
            service = self._get_service()
            
            # Verificar cache
            if label_name in self._labels_cache:
                return self._labels_cache[label_name]
            
            # Listar labels existentes
            labels_result = service.users().labels().list(userId='me').execute()
            labels = labels_result.get('labels', [])
            
            # Procurar label existente
            for label in labels:
                if label['name'] == label_name:
                    self._labels_cache[label_name] = label['id']
                    return label['id']
            
            # Criar nova label
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            
            created_label = service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            self._labels_cache[label_name] = created_label['id']
            return created_label['id']
            
        except HttpError as error:
            print(f"  ⚠️ Erro ao criar/obter label '{label_name}': {error}")
            return None
