"""
Serviço para envio de e-mails.
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from config import config


class EmailService:
    """Serviço para envio de e-mails."""
    
    def __init__(self):
        """Inicializa o serviço de e-mail."""
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.username = config.SMTP_USERNAME
        self.password = config.SMTP_PASSWORD
        self.from_email = config.EMAIL_FROM
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        is_html: bool = False,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Envia um e-mail.
        
        Args:
            to_emails: Lista de e-mails destinatários
            subject: Assunto do e-mail
            body: Corpo do e-mail
            is_html: Se o corpo é HTML
            attachments: Lista de anexos (opcional)
            
        Returns:
            Dicionário com resultado do envio
            
        Raises:
            Exception: Se houver erro no envio
        """
        if not all([self.username, self.password, self.from_email]):
            return {
                "success": False,
                "error": "Configurações de e-mail não definidas"
            }
        
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            # Adicionar corpo
            if is_html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Adicionar anexos se houver
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Conectar e enviar
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return {
                "success": True,
                "message": f"E-mail enviado com sucesso para {len(to_emails)} destinatário(s)"
            }
            
        except smtplib.SMTPAuthenticationError as e:
            return {
                "success": False,
                "error": f"Erro de autenticação SMTP: {str(e)}"
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "error": f"Erro SMTP: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro inesperado: {str(e)}"
            }
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]) -> None:
        """
        Adiciona um anexo à mensagem.
        
        Args:
            msg: Mensagem MIME
            attachment: Dicionário com dados do anexo
        """
        filename = attachment.get('filename', 'attachment')
        content = attachment.get('content', b'')
        content_type = attachment.get('content_type', 'application/octet-stream')
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(content)
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        msg.attach(part)
    
    def send_user_stories_email(
        self,
        to_emails: List[str],
        user_stories: str,
        format_type: str = "html"
    ) -> Dict[str, Any]:
        """
        Envia e-mail com Histórias de Usuário formatadas.
        
        Args:
            to_emails: Lista de e-mails destinatários
            user_stories: Texto das Histórias de Usuário
            format_type: Tipo de formatação ("html" ou "text")
            
        Returns:
            Dicionário com resultado do envio
        """
        subject = "Histórias de Usuário - Processamento Automatizado"
        
        if format_type.lower() == "html":
            body = self._format_user_stories_html(user_stories)
            is_html = True
        else:
            body = self._format_user_stories_text(user_stories)
            is_html = False
        
        return self.send_email(to_emails, subject, body, is_html)
    
    def _format_user_stories_html(self, user_stories: str) -> str:
        """
        Formata Histórias de Usuário em HTML.
        
        Args:
            user_stories: Texto das Histórias de Usuário
            
        Returns:
            HTML formatado
        """
        # Converter markdown para HTML
        html_content = self._markdown_to_html(user_stories)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Histórias de Usuário</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background-color: #f8f9fa;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    color: white; 
                    padding: 30px; 
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 16px;
                }}
                .content {{ 
                    padding: 30px; 
                    line-height: 1.7;
                }}
                .user-story {{ 
                    background-color: #f8f9ff; 
                    border-left: 4px solid #4facfe; 
                    padding: 20px; 
                    margin: 20px 0; 
                    border-radius: 0 8px 8px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }}
                .user-story h3 {{
                    color: #2c3e50;
                    margin-top: 0;
                    font-size: 20px;
                }}
                .user-story p {{
                    margin: 10px 0;
                }}
                .user-story ul {{
                    margin: 10px 0;
                    padding-left: 20px;
                }}
                .user-story li {{
                    margin: 5px 0;
                }}
                .criteria {{
                    background-color: #e8f5e8;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .criteria h4 {{
                    margin-top: 0;
                    color: #27ae60;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #ffc107;
                    margin: 15px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Histórias de Usuário</h1>
                    <p>Documento gerado automaticamente pelo sistema de automação</p>
                </div>
                <div class="content">
                    {html_content}
                </div>
                <div class="footer">
                    <p>Enviado automaticamente pelo Sistema de Automação de Histórias de Usuário</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_user_stories_text(self, user_stories: str) -> str:
        """
        Formata Histórias de Usuário em texto simples.
        
        Args:
            user_stories: Texto das Histórias de Usuário
            
        Returns:
            Texto formatado
        """
        # Converter markdown para texto limpo
        clean_text = self._markdown_to_text(user_stories)
        
        return f"""
HISTÓRIAS DE USUÁRIO
====================

Documento gerado automaticamente pelo sistema de automação

{clean_text}

---
Enviado automaticamente pelo Sistema de Automação de Histórias de Usuário
        """.strip()
    
    def _markdown_to_html(self, text: str) -> str:
        """
        Converte markdown básico para HTML.
        
        Args:
            text: Texto em markdown
            
        Returns:
            HTML convertido
        """
        import re
        
        # Converter títulos
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        
        # Converter negrito
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        
        # Converter itálico
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        
        # Converter listas
        lines = text.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            if re.match(r'^\s*[-*+]\s+', line):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                content = re.sub(r'^\s*[-*+]\s+', '', line)
                html_lines.append(f'<li>{content}</li>')
            elif re.match(r'^\s*\d+\.\s+', line):
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True
                content = re.sub(r'^\s*\d+\.\s+', '', line)
                html_lines.append(f'<li>{content}</li>')
            else:
                if in_list:
                    html_lines.append('</ul>' if 'ol>' not in ''.join(html_lines[-3:]) else '</ol>')
                    in_list = False
                if line.strip():
                    html_lines.append(f'<p>{line}</p>')
                else:
                    html_lines.append('<br>')
        
        if in_list:
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
    
    def _markdown_to_text(self, text: str) -> str:
        """
        Converte markdown para texto limpo.
        
        Args:
            text: Texto em markdown
            
        Returns:
            Texto limpo
        """
        import re
        
        # Remover títulos (###, ##, #)
        text = re.sub(r'^#{1,3}\s+', '', text, flags=re.MULTILINE)
        
        # Remover negrito e itálico
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        
        # Converter listas para texto simples
        lines = text.split('\n')
        clean_lines = []
        
        for line in lines:
            if re.match(r'^\s*[-*+]\s+', line):
                # Lista com marcadores
                content = re.sub(r'^\s*[-*+]\s+', '• ', line)
                clean_lines.append(content)
            elif re.match(r'^\s*\d+\.\s+', line):
                # Lista numerada
                content = re.sub(r'^\s*\d+\.\s+', '', line)
                clean_lines.append(f"  {content}")
            else:
                clean_lines.append(line)
        
        return '\n'.join(clean_lines)
    
    def send_user_stories_with_attachment(
        self,
        to_emails: List[str],
        user_stories: str,
        attachment_path: str,
        attachment_filename: str = None,
        summary: str = None,
        subject: str = None,
        body_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Envia e-mail com Histórias de Usuário e anexo.
        
        Args:
            to_emails: Lista de e-mails destinatários
            user_stories: Texto das Histórias de Usuário
            attachment_path: Caminho para o arquivo anexo
            attachment_filename: Nome do arquivo anexo (opcional)
            summary: Resumo da reunião (opcional)
            subject: Assunto do e-mail (opcional, será gerado se não fornecido)
            body_format: Formato do corpo ('html' ou 'text')
            
        Returns:
            Dicionário com resultado do envio
        """
        try:
            if not os.path.exists(attachment_path):
                return {
                    "success": False,
                    "error": "Arquivo anexo não encontrado"
                }
            
            # Ler conteúdo do anexo
            with open(attachment_path, 'rb') as f:
                attachment_content = f.read()
            
            # Determinar tipo MIME do anexo
            import mimetypes
            mime_type, _ = mimetypes.guess_type(attachment_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Preparar anexo
            attachment = {
                'filename': attachment_filename or os.path.basename(attachment_path),
                'content': attachment_content,
                'content_type': mime_type
            }
            
            # Preparar assunto do e-mail
            if not subject:
                subject = "Histórias de Usuário - Documento Anexo"
            
            # Preparar corpo do e-mail com explicações
            if body_format.lower() == "html":
                body = self._format_email_with_attachment_html(user_stories, summary, attachment_filename)
                is_html = True
            else:
                body = self._format_email_with_attachment_text(user_stories, summary, attachment_filename)
                is_html = False
            
            # Enviar e-mail com anexo
            return self.send_email(
                to_emails=to_emails,
                subject=subject,
                body=body,
                is_html=is_html,
                attachments=[attachment]
            )
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao enviar e-mail com anexo: {str(e)}"
            }
    
    def _format_email_with_attachment_html(self, user_stories: str, summary: str = None, filename: str = None) -> str:
        """
        Formata corpo do e-mail em HTML com explicações quando há anexo.
        
        Args:
            user_stories: Histórias de usuário
            summary: Resumo da reunião (opcional)
            filename: Nome do arquivo anexo (opcional)
            
        Returns:
            HTML formatado
        """
        # Converter markdown para HTML
        hus_html = self._markdown_to_html(user_stories) if user_stories else ""
        summary_html = self._markdown_to_html(summary) if summary else ""
        
        file_info = f"<p><strong>Arquivo anexo:</strong> {filename or 'documento'}</p>" if filename else ""
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Histórias de Usuário</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background-color: #f8f9fa;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #FF6F00 0%, #cc5900 100%);
                    color: white; 
                    padding: 30px; 
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 16px;
                }}
                .content {{ 
                    padding: 30px; 
                    line-height: 1.7;
                }}
                .info-box {{
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196F3;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 0 8px 8px 0;
                }}
                .info-box h3 {{
                    margin-top: 0;
                    color: #1976D2;
                }}
                .content-section {{
                    margin: 30px 0;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Histórias de Usuário</h1>
                    <p>Documento gerado automaticamente pelo sistema de automação</p>
                </div>
                <div class="content">
                    <div class="info-box">
                        <h3>📎 Documento Anexo</h3>
                        <p>Este e-mail contém um documento anexo com as Histórias de Usuário e/ou Resumo da Reunião gerados automaticamente.</p>
                        {file_info}
                        <p><strong>Formato:</strong> O documento está disponível no formato solicitado e pode ser aberto em qualquer visualizador compatível.</p>
                    </div>
                    
                    <div class="content-section">
                        <h2>📝 Resumo do Conteúdo</h2>
                        <p>O documento anexo contém as seguintes informações:</p>
                        <ul>
                            <li><strong>Histórias de Usuário:</strong> Documentação completa das funcionalidades identificadas</li>
                            {f'<li><strong>Resumo da Reunião:</strong> Síntese dos principais pontos discutidos</li>' if summary else ''}
                        </ul>
                    </div>
                    
                    {f'<div class="content-section"><h2>📝 Histórias de Usuário</h2>{hus_html}</div>' if hus_html else ''}
                    {f'<div class="content-section"><h2>📄 Resumo da Reunião</h2>{summary_html}</div>' if summary_html else ''}
                </div>
                <div class="footer">
                    <p>Enviado automaticamente pelo Sistema de Automação de Histórias de Usuário</p>
                    <p>Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_email_with_attachment_text(self, user_stories: str, summary: str = None, filename: str = None) -> str:
        """
        Formata corpo do e-mail em texto simples com explicações quando há anexo.
        
        Args:
            user_stories: Histórias de usuário
            summary: Resumo da reunião (opcional)
            filename: Nome do arquivo anexo (opcional)
            
        Returns:
            Texto formatado
        """
        hus_text = self._markdown_to_text(user_stories) if user_stories else ""
        summary_text = self._markdown_to_text(summary) if summary else ""
        
        file_info = f"\nArquivo anexo: {filename or 'documento'}\n" if filename else ""
        
        return f"""
HISTÓRIAS DE USUÁRIO - DOCUMENTO ANEXO
========================================

Este e-mail contém um documento anexo com as Histórias de Usuário e/ou Resumo da Reunião gerados automaticamente.
{file_info}
Formato: O documento está disponível no formato solicitado e pode ser aberto em qualquer visualizador compatível.

RESUMO DO CONTEÚDO
------------------
O documento anexo contém as seguintes informações:
- Histórias de Usuário: Documentação completa das funcionalidades identificadas
{f'- Resumo da Reunião: Síntese dos principais pontos discutidos' if summary else ''}

{f'HISTÓRIAS DE USUÁRIO\n{"=" * 40}\n{hus_text}\n' if hus_text else ''}
{f'RESUMO DA REUNIÃO\n{"=" * 40}\n{summary_text}\n' if summary_text else ''}
---
Enviado automaticamente pelo Sistema de Automação de Histórias de Usuário
Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento.
        """.strip()
