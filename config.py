"""
Configurações da aplicação de automação de Histórias de Usuário.
Todas as configurações sensíveis são carregadas de variáveis de ambiente.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Config:
    """Configurações da aplicação."""
    
    # Configurações do Flask
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST: str = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT: int = int(os.getenv('FLASK_PORT', '5000'))
    
    # Configurações das LLMs
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    ZELLO_API_KEY: Optional[str] = os.getenv('ZELLO_API_KEY')
    ZELLO_BASE_URL: str = os.getenv('ZELLO_BASE_URL', 'https://api.zello.com')
    
    # Configurações de e-mail
    SMTP_SERVER: str = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('EMAIL_SMTP_PORT', '587'))
    SMTP_USERNAME: Optional[str] = os.getenv('EMAIL_USERNAME')
    SMTP_PASSWORD: Optional[str] = os.getenv('EMAIL_PASSWORD')
    EMAIL_FROM: Optional[str] = os.getenv('EMAIL_FROM', os.getenv('EMAIL_USERNAME'))
    
    # Configurações de upload
    MAX_CONTENT_LENGTH: int = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    UPLOAD_FOLDER: str = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS: set = {'txt', 'pdf', 'doc', 'docx', 'md'}
    
    @classmethod
    def validate_config(cls) -> list[str]:
        """
        Valida se todas as configurações necessárias estão definidas.
        
        Returns:
            Lista de mensagens de erro se houver configurações faltando.
        """
        errors = []
        
        if not cls.OPENAI_API_KEY and not cls.ZELLO_API_KEY:
            errors.append("Pelo menos uma chave de API (OPENAI_API_KEY ou ZELLO_API_KEY) deve ser definida")
        
        if not cls.SMTP_USERNAME or not cls.SMTP_PASSWORD:
            errors.append("Configurações de SMTP (SMTP_USERNAME e SMTP_PASSWORD) são obrigatórias")
        
        if not cls.EMAIL_FROM:
            errors.append("EMAIL_FROM deve ser definido")
        
        return errors


# Instância global de configuração
config = Config()
