"""
Integração com Gmail API para coleta de e-mails do Gemini.
Suporta Domain-Wide Delegation (DWD) via service account ou OAuth local.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import base64
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]


class GmailService:
    def __init__(self, credentials_json_path: str, delegated_user: Optional[str] = None):
        self.credentials_json_path = credentials_json_path
        self.delegated_user = delegated_user
        self._service = None

    def _get_service(self):
        if self._service:
            return self._service
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_json_path, scopes=GMAIL_SCOPES
        )
        if self.delegated_user:
            creds = creds.with_subject(self.delegated_user)
        self._service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        return self._service

    def list_gemini_messages(self, user_email: str, max_results: int = 50) -> List[Dict[str, Any]]:
        service = self._get_service()
        query = 'from:gemini-noreply@google.com'
        try:
            resp = service.users().messages().list(
                userId=user_email, q=query, maxResults=max_results
            ).execute()
            return resp.get("messages", [])
        except HttpError as e:
            raise Exception(f"Erro Gmail list: {e}")

    def get_message(self, user_email: str, message_id: str) -> Dict[str, Any]:
        service = self._get_service()
        try:
            return service.users().messages().get(userId=user_email, id=message_id, format="full").execute()
        except HttpError as e:
            raise Exception(f"Erro Gmail get: {e}")

    def extract_plain_text(self, message: Dict[str, Any]) -> str:
        # Procura partes text/plain preferencialmente
        payload = message.get("payload", {})
        parts = payload.get("parts", [])
        if parts:
            for part in parts:
                if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                    data = part["body"]["data"]
                    return base64.urlsafe_b64decode(data.encode()).decode("utf-8", errors="replace")
        # Fallback: corpo simples
        body = payload.get("body", {}).get("data")
        if body:
            return base64.urlsafe_b64decode(body.encode()).decode("utf-8", errors="replace")
        return ""


