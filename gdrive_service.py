"""
Serviço para interação com Google Drive API usando Domain-Wide Delegation.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
from io import BytesIO

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload


class GDriveService:
    """
    Serviço para interação com Google Drive API usando Service Account com Domain-Wide Delegation.
    
    Permite criar pastas e fazer upload de arquivos na conta de qualquer usuário do domínio autorizado.
    """
    
    # Scopes necessários para Google Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_path: str, delegated_user: str):
        """
        Inicializa o serviço Google Drive.
        
        Args:
            credentials_path: Caminho para o arquivo JSON de credenciais da Service Account
            delegated_user: Email do usuário a ser delegado (ex: user@empresa.com)
        """
        self.credentials_path = credentials_path
        self.delegated_user = delegated_user
        self._service = None
        self._folders_cache = {}
    
    def _get_service(self):
        """
        Obtém o serviço Google Drive autenticado.
        
        Returns:
            Serviço Google Drive autenticado
        """
        if self._service is None:
            # Carregar credenciais da Service Account
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            
            # Aplicar delegação de domínio
            delegated_credentials = credentials.with_subject(self.delegated_user)
            
            # Construir serviço Google Drive
            self._service = build('drive', 'v3', credentials=delegated_credentials)
        
        return self._service
    
    def find_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Busca ou cria uma pasta no Google Drive.
        
        Args:
            folder_name: Nome da pasta
            parent_id: ID da pasta pai (opcional, se None usa root)
            
        Returns:
            ID da pasta encontrada/criada ou None se houver erro
            
        Raises:
            Exception: Se houver erro na API do Google Drive
        """
        try:
            service = self._get_service()
            
            # Criar chave de cache
            cache_key = f"{parent_id or 'root'}:{folder_name}"
            if cache_key in self._folders_cache:
                return self._folders_cache[cache_key]
            
            # Construir query de busca
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            else:
                query += " and 'root' in parents"
            
            # Buscar pasta existente
            results = service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                # Pasta encontrada
                folder_id = files[0]['id']
                self._folders_cache[cache_key] = folder_id
                return folder_id
            
            # Criar nova pasta
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            
            folder = service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            self._folders_cache[cache_key] = folder_id
            
            print(f"  📂 Criando pasta '{folder_name}'...")
            return folder_id
            
        except HttpError as error:
            raise Exception(f"Erro ao criar/buscar pasta '{folder_name}': {error}")
    
    def upload_text_file(self, folder_id: str, filename: str, content: str) -> Optional[str]:
        """
        Faz upload de um arquivo de texto para o Google Drive.
        
        Args:
            folder_id: ID da pasta de destino
            filename: Nome do arquivo
            content: Conteúdo do arquivo em texto
            
        Returns:
            ID do arquivo criado ou None se houver erro
            
        Raises:
            Exception: Se houver erro na API do Google Drive
        """
        try:
            service = self._get_service()
            
            # Converter conteúdo para bytes
            content_bytes = content.encode('utf-8')
            media = MediaIoBaseUpload(
                BytesIO(content_bytes),
                mimetype='text/plain',
                resumable=True
            )
            
            # Metadata do arquivo
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Fazer upload
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except HttpError as error:
            raise Exception(f"Erro ao fazer upload do arquivo '{filename}': {error}")
    
    def list_files_in_folder(self, folder_id: str) -> list[Dict[str, Any]]:
        """
        Lista arquivos em uma pasta.
        
        Args:
            folder_id: ID da pasta
            
        Returns:
            Lista de arquivos na pasta
            
        Raises:
            Exception: Se houver erro na API do Google Drive
        """
        try:
            service = self._get_service()
            
            results = service.files().list(
                q=f"'{folder_id}' in parents",
                fields="files(id, name, mimeType, size, createdTime)"
            ).execute()
            
            return results.get('files', [])
            
        except HttpError as error:
            raise Exception(f"Erro ao listar arquivos da pasta {folder_id}: {error}")
    
    def delete_file(self, file_id: str) -> bool:
        """
        Deleta um arquivo do Google Drive.
        
        Args:
            file_id: ID do arquivo
            
        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            service = self._get_service()
            service.files().delete(fileId=file_id).execute()
            return True
            
        except HttpError as error:
            print(f"  ⚠️ Erro ao deletar arquivo {file_id}: {error}")
            return False
    
    def get_file_content(self, file_id: str) -> Optional[str]:
        """
        Obtém o conteúdo de um arquivo de texto.
        
        Args:
            file_id: ID do arquivo
            
        Returns:
            Conteúdo do arquivo ou None se houver erro
        """
        try:
            service = self._get_service()
            
            # Obter conteúdo do arquivo
            result = service.files().get_media(fileId=file_id).execute()
            return result.decode('utf-8')
            
        except HttpError as error:
            print(f"  ⚠️ Erro ao obter conteúdo do arquivo {file_id}: {error}")
            return None
    
    def list_folders_in_folder(self, parent_folder_id: str) -> list[Dict[str, Any]]:
        """
        Lista todas as subpastas dentro de uma pasta.
        
        Args:
            parent_folder_id: ID da pasta pai
            
        Returns:
            Lista de dicts com: {'id': str, 'name': str}
            
        Raises:
            Exception: Se houver erro na API do Google Drive
        """
        try:
            service = self._get_service()
            
            query = f"mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents and trashed=false"
            
            response = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                orderBy='name'
            ).execute()
            
            return response.get('files', [])
            
        except HttpError as error:
            raise Exception(f"Erro ao listar subpastas da pasta {parent_folder_id}: {error}")
    
    def download_file_content(self, file_id: str) -> str:
        """
        Baixa o conteúdo de um arquivo de texto.
        
        Args:
            file_id: ID do arquivo no Drive
            
        Returns:
            Conteúdo do arquivo como string
            
        Raises:
            Exception: Se houver erro ao baixar o arquivo
        """
        from googleapiclient.http import MediaIoBaseDownload
        
        try:
            service = self._get_service()
            
            request = service.files().get_media(fileId=file_id)
            
            file_buffer = BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            return file_buffer.read().decode('utf-8')
            
        except HttpError as error:
            raise Exception(f"Erro ao baixar conteúdo do arquivo {file_id}: {error}")
