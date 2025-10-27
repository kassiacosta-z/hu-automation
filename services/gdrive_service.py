"""
Integração com Google Drive API para salvar transcrições.
"""

from __future__ import annotations

from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaInMemoryUpload


DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


class GDriveService:
    def __init__(self, credentials_json_path: str):
        self.credentials_json_path = credentials_json_path
        self._service = None

    def _get_service(self):
        if self._service:
            return self._service
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_json_path, scopes=DRIVE_SCOPES
        )
        self._service = build("drive", "v3", credentials=creds, cache_discovery=False)
        return self._service

    def ensure_folder(self, parent_id: Optional[str], name: str) -> str:
        service = self._get_service()
        query = f"mimeType='application/vnd.google-apps.folder' and name='{name}'"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        resp = service.files().list(q=query, fields="files(id,name)").execute()
        files = resp.get("files", [])
        if files:
            return files[0]["id"]
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            file_metadata["parents"] = [parent_id]
        folder = service.files().create(body=file_metadata, fields="id").execute()
        return folder["id"]

    def upload_text(self, parent_id: str, filename: str, content: str) -> str:
        service = self._get_service()
        media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain")
        file_metadata = {"name": filename, "parents": [parent_id]}
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return file["id"]


