"""
Serviço para processamento de arquivos.
"""

import os
import time
import mimetypes
from typing import Dict, Any, Optional, List
from werkzeug.utils import secure_filename
from config import config


class FileService:
    """Serviço para processamento de arquivos."""
    
    def __init__(self):
        """Inicializa o serviço de arquivos."""
        self.upload_folder = config.UPLOAD_FOLDER
        self.allowed_extensions = config.ALLOWED_EXTENSIONS
        self.max_content_length = config.MAX_CONTENT_LENGTH
        
        # Criar diretório de upload se não existir
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def is_allowed_file(self, filename: str) -> bool:
        """
        Verifica se o arquivo tem extensão permitida.
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            True se o arquivo é permitido
        """
        if not filename:
            return False
        
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def get_file_extension(self, filename: str) -> str:
        """
        Obtém a extensão do arquivo.
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Extensão do arquivo (sem o ponto)
        """
        if not filename or '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[1].lower()
    
    def get_file_mime_type(self, filename: str) -> str:
        """
        Obtém o tipo MIME do arquivo.
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            Tipo MIME do arquivo
        """
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    def save_file(self, file, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Salva um arquivo no diretório de upload.
        
        Args:
            file: Objeto de arquivo do Flask
            filename: Nome personalizado (opcional)
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            if not file or not file.filename:
                return {
                    "success": False,
                    "error": "Nenhum arquivo fornecido"
                }
            
            if not self.is_allowed_file(file.filename):
                return {
                    "success": False,
                    "error": f"Tipo de arquivo não permitido. Extensões aceitas: {', '.join(self.allowed_extensions)}"
                }
            
            # Usar nome personalizado ou nome seguro do arquivo original
            if filename:
                safe_filename = secure_filename(filename)
            else:
                safe_filename = secure_filename(file.filename)
            
            # Garantir que o nome seja único
            file_path = os.path.join(self.upload_folder, safe_filename)
            counter = 1
            while os.path.exists(file_path):
                name, ext = os.path.splitext(safe_filename)
                file_path = os.path.join(self.upload_folder, f"{name}_{counter}{ext}")
                counter += 1
            
            # Salvar arquivo
            file.save(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "filename": os.path.basename(file_path),
                "size": os.path.getsize(file_path),
                "mime_type": self.get_file_mime_type(file_path)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao salvar arquivo: {str(e)}"
            }
    
    def read_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        Lê o conteúdo de um arquivo.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Dicionário com o conteúdo do arquivo
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "Arquivo não encontrado"
                }
            
            # Detectar tipo de arquivo e ler adequadamente
            mime_type = self.get_file_mime_type(file_path)
            
            if mime_type.startswith('text/'):
                # Arquivo de texto
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # Arquivo binário - ler como bytes
                with open(file_path, 'rb') as f:
                    content = f.read()
            
            return {
                "success": True,
                "content": content,
                "mime_type": mime_type,
                "size": os.path.getsize(file_path)
            }
            
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "Erro de codificação: arquivo não é texto válido"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao ler arquivo: {str(e)}"
            }
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """
        Remove um arquivo.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return {
                    "success": True,
                    "message": "Arquivo removido com sucesso"
                }
            else:
                return {
                    "success": False,
                    "error": "Arquivo não encontrado"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao remover arquivo: {str(e)}"
            }
    
    def get_uploaded_files(self) -> List[Dict[str, Any]]:
        """
        Lista todos os arquivos no diretório de upload.
        
        Returns:
            Lista de informações sobre os arquivos
        """
        try:
            files = []
            for filename in os.listdir(self.upload_folder):
                file_path = os.path.join(self.upload_folder, filename)
                if os.path.isfile(file_path):
                    files.append({
                        "filename": filename,
                        "file_path": file_path,
                        "size": os.path.getsize(file_path),
                        "mime_type": self.get_file_mime_type(file_path),
                        "extension": self.get_file_extension(filename)
                    })
            return files
        except Exception as e:
            return []
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extrai texto de um arquivo de forma inteligente.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Dicionário com o texto extraído
        """
        try:
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "Arquivo não encontrado"
                }
            
            file_extension = self.get_file_extension(file_path)
            mime_type = self.get_file_mime_type(file_path)
            
            # Arquivos de texto simples
            if file_extension in ['txt', 'md'] or mime_type.startswith('text/'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    "success": True,
                    "text": content,
                    "method": "text_file"
                }
            
            # PDF - requer biblioteca adicional
            elif file_extension == 'pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                    return {
                        "success": True,
                        "text": text.strip(),
                        "method": "pdf_extraction"
                    }
                except ImportError:
                    return {
                        "success": False,
                        "error": "Biblioteca PyPDF2 não instalada para processar PDFs"
                    }
            
            # DOCX - requer biblioteca adicional
            elif file_extension == 'docx':
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return {
                        "success": True,
                        "text": text.strip(),
                        "method": "docx_extraction"
                    }
                except ImportError:
                    return {
                        "success": False,
                        "error": "Biblioteca python-docx não instalada para processar DOCX"
                    }
            
            # DOC - requer biblioteca adicional
            elif file_extension == 'doc':
                try:
                    import subprocess
                    import tempfile
                    
                    # Tentar converter DOC para TXT usando antiword (Linux/Mac) ou catdoc
                    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
                        tmp_path = tmp_file.name
                    
                    try:
                        subprocess.run(['antiword', file_path], stdout=open(tmp_path, 'w'), check=True)
                        with open(tmp_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        os.unlink(tmp_path)
                        return {
                            "success": True,
                            "text": content.strip(),
                            "method": "doc_extraction_antiword"
                        }
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        try:
                            subprocess.run(['catdoc', file_path], stdout=open(tmp_path, 'w'), check=True)
                            with open(tmp_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            os.unlink(tmp_path)
                            return {
                                "success": True,
                                "text": content.strip(),
                                "method": "doc_extraction_catdoc"
                            }
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            return {
                                "success": False,
                                "error": "Ferramentas antiword ou catdoc não encontradas para processar DOC"
                            }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Erro ao processar DOC: {str(e)}"
                    }
            
            # Fallback: tentar ler como texto
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    return {
                        "success": True,
                        "text": content,
                        "method": "fallback_text"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Tipo de arquivo não suportado: {file_extension}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao extrair texto: {str(e)}"
            }
    
    def create_document(self, content: str, format_type: str, filename: str = None) -> Dict[str, Any]:
        """
        Cria um documento no formato especificado.
        
        Args:
            content: Conteúdo do documento
            format_type: Tipo do documento ('pdf' ou 'docx')
            filename: Nome do arquivo (opcional)
            
        Returns:
            Dicionário com resultado da criação
        """
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"user_stories_{timestamp}"
            
            file_path = os.path.join(self.upload_folder, f"{filename}.{format_type}")
            
            if format_type.lower() == 'pdf':
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet
                    from reportlab.lib.units import inch
                    
                    doc = SimpleDocTemplate(file_path, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = []
                    
                    # Título
                    title = Paragraph("Histórias de Usuário", styles['Title'])
                    story.append(title)
                    story.append(Spacer(1, 12))
                    
                    # Conteúdo
                    content_paragraphs = content.split('\n')
                    for para in content_paragraphs:
                        if para.strip():
                            p = Paragraph(para.strip(), styles['Normal'])
                            story.append(p)
                            story.append(Spacer(1, 6))
                    
                    doc.build(story)
                    
                    return {
                        "success": True,
                        "file_path": file_path,
                        "filename": f"{filename}.pdf",
                        "size": os.path.getsize(file_path)
                    }
                    
                except ImportError:
                    return {
                        "success": False,
                        "error": "Biblioteca reportlab não instalada para criar PDFs"
                    }
            
            elif format_type.lower() == 'docx':
                try:
                    from docx import Document
                    from docx.shared import Inches
                    
                    doc = Document()
                    
                    # Título
                    title = doc.add_heading('Histórias de Usuário', 0)
                    
                    # Conteúdo
                    content_paragraphs = content.split('\n')
                    for para in content_paragraphs:
                        if para.strip():
                            doc.add_paragraph(para.strip())
                    
                    doc.save(file_path)
                    
                    return {
                        "success": True,
                        "file_path": file_path,
                        "filename": f"{filename}.docx",
                        "size": os.path.getsize(file_path)
                    }
                    
                except ImportError:
                    return {
                        "success": False,
                        "error": "Biblioteca python-docx não instalada para criar DOCX"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Formato não suportado: {format_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao criar documento: {str(e)}"
            }
