"""
Aplicação Flask para automação de Histórias de Usuário.
"""

import os
import json
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.exceptions import RequestEntityTooLarge

from config import config
from services import LLMService, EmailService, FileService, GenerationService, RepositoryMonitor
from prompts import UserStoryPrompts
from database import init_db, SessionLocal
from models import TranscriptionJob, ProcessingArtifact, JobStatus


def create_app() -> Flask:
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    
    # Inicializar banco (apenas estrutura; pode ser substituído por Alembic)
    if os.getenv('AUTO_CREATE_DB', 'true').lower() == 'true':
        try:
            init_db()
        except Exception as _:
            # Mantém a aplicação viva mesmo se preferirmos rodar migrações Alembic
            pass

    # Inicializar serviços
    llm_service = LLMService()
    email_service = EmailService()
    file_service = FileService()
    generation_service = GenerationService(llm_service)
    
    # Inicializar monitor de repositório (se configurado)
    repository_monitor = None
    if config.TRANSCRIPTION_REPO_PATH:
        try:
            # Certificar que o diretório do repositório existe
            try:
                os.makedirs(config.TRANSCRIPTION_REPO_PATH, exist_ok=True)
                print(f"Repositório de transcrições: {config.TRANSCRIPTION_REPO_PATH}")
            except Exception as dir_err:
                print(f"Aviso: não foi possível criar o diretório do repositório: {dir_err}")

            repository_monitor = RepositoryMonitor()
        except Exception as e:
            print(f"Aviso: Não foi possível inicializar o monitor de repositório: {str(e)}")
    
    @app.route('/')
    def index():
        """Página principal da aplicação."""
        return render_template('index.html')
    
    @app.route('/admin/monitor')
    def admin_monitor():
        """Página de administração do monitor de repositório."""
        return render_template('admin_monitor.html')
    
    @app.route('/api/process', methods=['POST'])
    def process_file():
        """
        Processa um arquivo enviado e gera Histórias de Usuário com auto-correção.
        
        Returns:
            JSON com resultado do processamento
        """
        try:
            # Verificar se arquivo foi enviado
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'Nenhum arquivo enviado'
                }), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'Nenhum arquivo selecionado'
                }), 400
            
            # Obter parâmetros da requisição
            # Usar apenas Zello MIND como LLM
            provider = 'zello'
            email = request.form.get('email', request.form.get('email_recipients', ''))
            output_format = request.form.get('output_format', request.form.get('email_format', 'preview'))
            observations = request.form.get('observations', '').strip()
            output_type = request.form.get('output_type', 'hus').strip().lower()  # 'hus', 'summary', 'both'
            # Validar output_type
            if output_type not in ['hus', 'summary', 'both']:
                print(f"[DEBUG] ⚠️ output_type inválido recebido: '{output_type}', usando padrão 'hus'")
                output_type = 'hus'
            # Normalizar valores possíveis do dropdown antigo para os novos
            if output_format in ['html', 'text']:
                # Se apenas o formato de corpo foi enviado, consideramos preview na API
                # e usamos o formato somente para o envio opcional de e-mail
                api_output_format = 'preview'
                email_body_format = output_format
            else:
                api_output_format = output_format
                email_body_format = request.form.get('email_format', 'html')
            max_attempts = int(request.form.get('max_attempts', '3'))
            
            # Detectar tipo de arquivo
            file_extension = file_service.get_file_extension(file.filename)
            is_audio = file_extension in ['mp3', 'wav']
            
            # Salvar arquivo temporariamente
            save_result = file_service.save_file(file)
            if not save_result['success']:
                return jsonify(save_result), 400
            
            try:
                # Extrair texto do arquivo
                text_result = file_service.extract_text_from_file(save_result['file_path'])
                if not text_result['success']:
                    return jsonify(text_result), 400
                
                extracted_text = text_result['text']
                
                # Se for áudio, retornar transcrição para revisão
                if is_audio:
                    return jsonify({
                        'success': True,
                        'requires_review': True,
                        'transcription': extracted_text,
                        'file_path': save_result['file_path'],
                        'extraction_info': text_result,
                        'message': 'Transcrição concluída. Revise e confirme para gerar HUs/Resumo.'
                    })
                
                # Para documentos, processar diretamente
                # Processar baseado no tipo de saída solicitado
                print(f"[DEBUG] ========== PROCESSANDO DOCUMENTO ==========")
                print(f"[DEBUG] output_type recebido: '{output_type}'")
                print(f"[DEBUG] output_type é 'summary'? {output_type == 'summary'}")
                print(f"[DEBUG] output_type é 'hus'? {output_type == 'hus'}")
                print(f"[DEBUG] output_type é 'both'? {output_type == 'both'}")
                
                results = {}
                
                # Gerar HUs se solicitado
                if output_type in ['hus', 'both']:
                    print(f"[DEBUG] Gerando HUs (output_type: {output_type})")
                    generation_result = generation_service.generate_with_auto_correction(
                        text=extracted_text,
                        provider=provider,
                        max_attempts=max_attempts,
                        observations=observations if observations else None
                    )
                    
                    if not generation_result['success']:
                        error_msg = generation_result.get('error', 'Erro desconhecido')
                        print(f"[DEBUG] Erro na geração de HUs: {error_msg}")
                        # Se apenas HUs foram solicitadas, retornar erro
                        if output_type == 'hus':
                            return jsonify(generation_result), 500
                        # Se ambos foram solicitados, continuar sem HUs
                        print(f"[DEBUG] Continuando sem HUs (output_type: {output_type})")
                    else:
                        results['user_stories'] = generation_result['content']
                        results['generation_info'] = generation_result
                        print(f"[DEBUG] HUs geradas com sucesso: {len(generation_result['content'])} caracteres")
                else:
                    print(f"[DEBUG] HUs NÃO serão geradas (output_type: {output_type})")
                
                # Gerar resumo se solicitado
                if output_type in ['summary', 'both']:
                    print(f"[DEBUG] Gerando resumo (output_type: {output_type})")
                    summary_result = generation_service.generate_summary(
                        text=extracted_text,
                        provider=provider,
                        observations=observations if observations else None
                    )
                    
                    if not summary_result['success']:
                        error_msg = summary_result.get('error', 'Erro desconhecido')
                        print(f"[DEBUG] Erro na geração de resumo: {error_msg}")
                        # Se apenas resumo foi solicitado, retornar erro
                        if output_type == 'summary':
                            return jsonify(summary_result), 500
                        # Se ambos foram solicitados, continuar sem resumo
                        print(f"[DEBUG] Continuando sem resumo (output_type: {output_type})")
                    else:
                        results['summary'] = summary_result['content']
                        results['summary_info'] = summary_result
                        print(f"[DEBUG] Resumo gerado com sucesso: {len(summary_result['content'])} caracteres")
                else:
                    print(f"[DEBUG] Resumo NÃO será gerado (output_type: {output_type})")
                
                # Se nenhum resultado foi gerado, retornar erro
                if not results:
                    return jsonify({
                        'success': False,
                        'error': 'Nenhum tipo de saída foi gerado. Verifique o parâmetro output_type.'
                    }), 400
                
                user_stories = results.get('user_stories', '')
                summary = results.get('summary', '')
                generation_result = results.get('generation_info', {})
                
                print(f"Geração bem-sucedida! Provider: {generation_result.get('provider', 'unknown')}")
                
                # Processar baseado no formato de saída (apenas para HUs, resumo sempre retorna preview)
                if api_output_format in ['pdf', 'docx'] and user_stories:
                    # Criar documento
                    doc_result = file_service.create_document(
                        content=user_stories,
                        format_type=output_format
                    )
                    
                    if not doc_result['success']:
                        return jsonify(doc_result), 500
                    
                    # Enviar por e-mail com anexo
                    if email:
                        email_list = [email.strip() for email in email.split(',') if email.strip()]
                        if email_list:
                            email_result = email_service.send_user_stories_with_attachment(
                                to_emails=email_list,
                                user_stories=user_stories,
                                attachment_path=doc_result['file_path'],
                                attachment_filename=doc_result['filename'],
                                body_format=email_body_format
                            )
                            
                            # Limpar arquivo temporário
                            file_service.delete_file(save_result['file_path'])
                            
                            return jsonify({
                                'success': True,
                                'message': 'Documento criado e enviado por e-mail',
                                'document_created': doc_result,
                                'email_result': email_result,
                                'generation_info': generation_result
                            })
                    
                    # Retornar informações do documento criado
                    return jsonify({
                        'success': True,
                        'message': 'Documento criado com sucesso',
                        'document_created': doc_result,
                        'generation_info': generation_result
                    })
                
                # Sempre retornar preview primeiro (email será enviado após confirmação do usuário)
                # Removida lógica de envio automático - agora sempre mostra preview
                if api_output_format in ['preview', 'email_body_txt']:
                    # Retornar JSON completo para preview
                    # IMPORTANTE: Incluir texto original para permitir regeneração
                    print(f"[DEBUG] Retornando preview. Texto original: {len(extracted_text)} caracteres")
                    print(f"[DEBUG] HUs geradas: {len(user_stories) if user_stories else 0} caracteres")
                    print(f"[DEBUG] Resumo gerado: {len(summary) if summary else 0} caracteres")
                    
                    response_data = {
                        'success': True,
                        'extraction_info': text_result,
                        'original_text': extracted_text  # Texto original para regeneração
                    }
                    
                    if user_stories:
                        response_data['user_stories'] = user_stories
                        response_data['generation_info'] = generation_result
                    
                    if summary:
                        response_data['summary'] = summary
                        response_data['summary_info'] = results.get('summary_info', {})
                    
                    return jsonify(response_data)
                
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Formato de saída não suportado: {output_format}'
                    }), 400
                
            finally:
                # Limpar arquivo temporário
                file_service.delete_file(save_result['file_path'])
            
        except RequestEntityTooLarge:
            return jsonify({
                'success': False,
                'error': 'Arquivo muito grande. Tamanho máximo: 16MB'
            }), 413
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }), 500

    @app.route('/api/process-transcription', methods=['POST'])
    def process_transcription():
        """
        Processa uma transcrição revisada e gera HUs e/ou resumo.
        
        Returns:
            JSON com resultado do processamento
        """
        try:
            transcription_text = request.form.get('transcription_text', '').strip()
            observations = request.form.get('observations', '').strip()
            output_type = request.form.get('output_type', 'hus').strip().lower()  # 'hus', 'summary', 'both'
            # Validar output_type
            if output_type not in ['hus', 'summary', 'both']:
                print(f"[DEBUG] ⚠️ output_type inválido recebido: '{output_type}', usando padrão 'hus'")
                output_type = 'hus'
            provider = 'zello'
            max_attempts = int(request.form.get('max_attempts', '3'))
            
            if not transcription_text:
                return jsonify({
                    'success': False,
                    'error': 'Texto da transcrição não fornecido'
                }), 400
            
            print(f"[DEBUG] ========== PROCESSANDO TRANSCRIÇÃO ==========")
            print(f"[DEBUG] output_type recebido: '{output_type}'")
            print(f"[DEBUG] output_type é 'summary'? {output_type == 'summary'}")
            print(f"[DEBUG] output_type é 'hus'? {output_type == 'hus'}")
            print(f"[DEBUG] output_type é 'both'? {output_type == 'both'}")
            
            results = {}
            
            # Gerar HUs se solicitado
            if output_type in ['hus', 'both']:
                print(f"[DEBUG] Gerando HUs (output_type: {output_type})")
                generation_result = generation_service.generate_with_auto_correction(
                    text=transcription_text,
                    provider=provider,
                    max_attempts=max_attempts,
                    observations=observations if observations else None
                )
                
                if not generation_result['success']:
                    error_msg = generation_result.get('error', 'Erro desconhecido')
                    print(f"[DEBUG] Erro na geração de HUs: {error_msg}")
                    # Se apenas HUs foram solicitadas, retornar erro
                    if output_type == 'hus':
                        return jsonify(generation_result), 500
                    # Se ambos foram solicitados, continuar sem HUs
                    print(f"[DEBUG] Continuando sem HUs (output_type: {output_type})")
                else:
                    results['user_stories'] = generation_result['content']
                    results['generation_info'] = generation_result
                    print(f"[DEBUG] HUs geradas com sucesso: {len(generation_result['content'])} caracteres")
            else:
                print(f"[DEBUG] HUs NÃO serão geradas (output_type: {output_type})")
            
            # Gerar resumo se solicitado
            if output_type in ['summary', 'both']:
                print(f"[DEBUG] Gerando resumo (output_type: {output_type})")
                summary_result = generation_service.generate_summary(
                    text=transcription_text,
                    provider=provider,
                    observations=observations if observations else None
                )
                
                if not summary_result['success']:
                    error_msg = summary_result.get('error', 'Erro desconhecido')
                    print(f"[DEBUG] Erro na geração de resumo: {error_msg}")
                    # Se apenas resumo foi solicitado, retornar erro
                    if output_type == 'summary':
                        return jsonify(summary_result), 500
                    # Se ambos foram solicitados, continuar sem resumo
                    print(f"[DEBUG] Continuando sem resumo (output_type: {output_type})")
                else:
                    results['summary'] = summary_result['content']
                    results['summary_info'] = summary_result
                    print(f"[DEBUG] Resumo gerado com sucesso: {len(summary_result['content'])} caracteres")
            else:
                print(f"[DEBUG] Resumo NÃO será gerado (output_type: {output_type})")
            
            if not results:
                return jsonify({
                    'success': False,
                    'error': 'Nenhum tipo de saída foi gerado. Verifique o parâmetro output_type.'
                }), 400
            
            # Retornar preview com texto original para regeneração
            print(f"[DEBUG] Retornando preview de transcrição. Texto: {len(transcription_text)} caracteres")
            response_data = {
                'success': True,
                'message': 'Processamento concluído com sucesso',
                'original_text': transcription_text  # IMPORTANTE: Incluir texto original para regeneração
            }
            
            if 'user_stories' in results:
                response_data['user_stories'] = results['user_stories']
                response_data['generation_info'] = results['generation_info']
            
            if 'summary' in results:
                response_data['summary'] = results['summary']
                response_data['summary_info'] = results['summary_info']
            
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }), 500

    @app.route('/api/regenerate-hus', methods=['POST'])
    def regenerate_hus():
        """
        Regenera Histórias de Usuário com observações adicionais.
        
        Returns:
            JSON com HUs regeneradas
        """
        try:
            original_text = request.form.get('original_text', '').strip()
            observations = request.form.get('observations', '').strip()
            current_hus = request.form.get('current_hus', '')
            provider = 'zello'
            max_attempts = int(request.form.get('max_attempts', '3'))
            
            print(f"[DEBUG] ========== REGENERANDO HUs ==========")
            print(f"[DEBUG] Tamanho do texto original: {len(original_text)} caracteres")
            print(f"[DEBUG] Observações: {observations[:200] if observations else 'nenhuma'}...")
            print(f"[DEBUG] HUs atuais: {len(current_hus) if current_hus else 0} caracteres")
            
            if not original_text:
                print("[DEBUG] ❌ Erro: Texto original não fornecido")
                return jsonify({
                    'success': False,
                    'error': 'Texto original não fornecido'
                }), 400
            
            # Contextualizar observações para regeneração de HUs
            if observations and observations.strip():
                contextualized_observations = f"""CONTEXTO DE REGENERAÇÃO:
Você está regenerando as Histórias de Usuário com base no mesmo texto original, mas incorporando as seguintes observações específicas do usuário para melhorar ou refinar o resultado:

{observations.strip()}

IMPORTANTE: Estas observações são instruções específicas para adaptar ou melhorar as Histórias de Usuário que serão geradas. Aplique-as de forma contextualizada, considerando que o usuário quer um resultado diferente ou melhorado em relação à geração anterior."""
            else:
                contextualized_observations = None
            
            print(f"[DEBUG] Observações contextualizadas: {len(contextualized_observations) if contextualized_observations else 0} caracteres")
            
            generation_result = generation_service.generate_with_auto_correction(
                text=original_text,
                provider=provider,
                max_attempts=max_attempts,
                observations=contextualized_observations
            )
            
            if not generation_result['success']:
                return jsonify(generation_result), 500
            
            return jsonify({
                'success': True,
                'user_stories': generation_result['content'],
                'generation_info': generation_result,
                'message': 'HUs regeneradas com sucesso'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }), 500

    @app.route('/api/send-email', methods=['POST'])
    def send_email():
        """
        Envia HUs e/ou resumo por e-mail após confirmação do usuário.
        """
        try:
            email = request.form.get('email', '').strip()
            email_format = request.form.get('email_format', 'html')
            user_stories = request.form.get('user_stories', '').strip()
            summary = request.form.get('summary', '').strip()
            
            if not email:
                return jsonify({
                    'success': False,
                    'error': 'E-mail não especificado'
                }), 400
            
            if not user_stories and not summary:
                return jsonify({
                    'success': False,
                    'error': 'Nenhum conteúdo disponível para enviar'
                }), 400
            
            email_list = [e.strip() for e in email.split(',') if e.strip()]
            if not email_list:
                return jsonify({
                    'success': False,
                    'error': 'Lista de e-mails inválida'
                }), 400
            
            # Preparar conteúdo do e-mail
            email_content = ""
            if user_stories and summary:
                email_content = f"# Histórias de Usuário\n\n{user_stories}\n\n---\n\n# Resumo da Reunião\n\n{summary}"
            elif user_stories:
                email_content = user_stories
            elif summary:
                email_content = summary
            
            # Enviar e-mail
            email_result = email_service.send_user_stories_email(
                to_emails=email_list,
                user_stories=email_content,
                format_type=email_format
            )
            
            if email_result.get('success'):
                return jsonify({
                    'success': True,
                    'message': f'E-mail enviado com sucesso para {len(email_list)} destinatário(s)',
                    'email_result': email_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': email_result.get('error', 'Erro ao enviar e-mail')
                }), 500
                
        except Exception as e:
            print(f"Erro ao enviar e-mail: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Erro ao enviar e-mail: {str(e)}'
            }), 500
    
    @app.route('/api/download-document', methods=['POST'])
    def download_document():
        """
        Gera e retorna documento (PDF ou DOC) para download.
        """
        try:
            file_format = request.form.get('file_format', 'pdf').lower()
            user_stories = request.form.get('user_stories', '').strip()
            summary = request.form.get('summary', '').strip()
            
            if not user_stories and not summary:
                return jsonify({
                    'success': False,
                    'error': 'Nenhum conteúdo disponível para gerar documento'
                }), 400
            
            if file_format not in ['pdf', 'doc']:
                return jsonify({
                    'success': False,
                    'error': f'Formato não suportado: {file_format}. Use "pdf" ou "doc"'
                }), 400
            
            # Gerar documento
            doc_result = file_service.create_document(
                content='',
                format_type=file_format,
                user_stories=user_stories if user_stories else None,
                summary=summary if summary else None
            )
            
            if not doc_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': doc_result.get('error', 'Erro ao gerar documento')
                }), 500
            
            file_path = doc_result['file_path']
            filename = doc_result['filename']
            
            # Retornar arquivo para download
            # Nota: Arquivo será limpo após download pelo cliente
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf' if file_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            
        except Exception as e:
            print(f"Erro ao gerar documento: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Erro ao gerar documento: {str(e)}'
            }), 500

    @app.route('/api/send-email-with-attachment', methods=['POST'])
    def send_email_with_attachment():
        """
        Gera documento e envia por e-mail como anexo.
        """
        try:
            email = request.form.get('email', '').strip()
            file_format = request.form.get('file_format', 'pdf').lower()
            user_stories = request.form.get('user_stories', '').strip()
            summary = request.form.get('summary', '').strip()
            
            if not email:
                return jsonify({
                    'success': False,
                    'error': 'E-mail não especificado'
                }), 400
            
            if not user_stories and not summary:
                return jsonify({
                    'success': False,
                    'error': 'Nenhum conteúdo disponível para enviar'
                }), 400
            
            if file_format not in ['pdf', 'doc']:
                return jsonify({
                    'success': False,
                    'error': f'Formato não suportado: {file_format}. Use "pdf" ou "doc"'
                }), 400
            
            email_list = [e.strip() for e in email.split(',') if e.strip()]
            if not email_list:
                return jsonify({
                    'success': False,
                    'error': 'Lista de e-mails inválida'
                }), 400
            
            # Gerar documento
            doc_result = file_service.create_document(
                content='',
                format_type=file_format,
                user_stories=user_stories if user_stories else None,
                summary=summary if summary else None
            )
            
            if not doc_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': doc_result.get('error', 'Erro ao gerar documento')
                }), 500
            
            file_path = doc_result['file_path']
            filename = doc_result['filename']
            
            # Preparar assunto do email baseado no conteúdo
            if user_stories and summary:
                # Tentar extrair título da primeira HU
                title_from_hus = file_service._extract_title_from_hus(user_stories)
                if title_from_hus:
                    subject = f"{title_from_hus} - Histórias de Usuário e Resumo"
                else:
                    subject = "Histórias de Usuário e Resumo da Reunião - Documento Anexo"
            elif user_stories:
                # Tentar extrair título da primeira HU
                title_from_hus = file_service._extract_title_from_hus(user_stories)
                if title_from_hus:
                    subject = f"{title_from_hus} - Documento Anexo"
                else:
                    subject = "Histórias de Usuário - Documento Anexo"
            elif summary:
                subject = "Resumo da Reunião - Documento Anexo"
            else:
                subject = "Documento Anexo"
            
            # Enviar email com anexo
            email_result = email_service.send_user_stories_with_attachment(
                to_emails=email_list,
                user_stories=user_stories if user_stories else '',
                summary=summary if summary else '',
                attachment_path=file_path,
                attachment_filename=filename,
                subject=subject,
                body_format='html'
            )
            
            # Limpar arquivo temporário
            import os
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
            
            if email_result.get('success'):
                return jsonify({
                    'success': True,
                    'message': f'E-mail enviado com sucesso para {len(email_list)} destinatário(s)',
                    'email_result': email_result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': email_result.get('error', 'Erro ao enviar e-mail')
                }), 500
                
        except Exception as e:
            print(f"Erro ao enviar e-mail com anexo: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Erro ao enviar e-mail: {str(e)}'
            }), 500

    @app.route('/api/download-and-send', methods=['POST'])
    def download_and_send():
        """
        Gera documento, retorna para download e envia por e-mail como anexo.
        """
        try:
            email = request.form.get('email', '').strip()
            file_format = request.form.get('file_format', 'pdf').lower()
            user_stories = request.form.get('user_stories', '').strip()
            summary = request.form.get('summary', '').strip()
            
            if not email:
                return jsonify({
                    'success': False,
                    'error': 'E-mail não especificado'
                }), 400
            
            if not user_stories and not summary:
                return jsonify({
                    'success': False,
                    'error': 'Nenhum conteúdo disponível'
                }), 400
            
            if file_format not in ['pdf', 'doc']:
                return jsonify({
                    'success': False,
                    'error': f'Formato não suportado: {file_format}. Use "pdf" ou "doc"'
                }), 400
            
            email_list = [e.strip() for e in email.split(',') if e.strip()]
            if not email_list:
                return jsonify({
                    'success': False,
                    'error': 'Lista de e-mails inválida'
                }), 400
            
            # Gerar documento
            doc_result = file_service.create_document(
                content='',
                format_type=file_format,
                user_stories=user_stories if user_stories else None,
                summary=summary if summary else None
            )
            
            if not doc_result.get('success'):
                return jsonify({
                    'success': False,
                    'error': doc_result.get('error', 'Erro ao gerar documento')
                }), 500
            
            file_path = doc_result['file_path']
            filename = doc_result['filename']
            
            # Preparar assunto do email baseado no conteúdo
            if user_stories and summary:
                # Tentar extrair título da primeira HU
                title_from_hus = file_service._extract_title_from_hus(user_stories)
                if title_from_hus:
                    subject = f"{title_from_hus} - Histórias de Usuário e Resumo"
                else:
                    subject = "Histórias de Usuário e Resumo da Reunião - Documento Anexo"
            elif user_stories:
                # Tentar extrair título da primeira HU
                title_from_hus = file_service._extract_title_from_hus(user_stories)
                if title_from_hus:
                    subject = f"{title_from_hus} - Documento Anexo"
                else:
                    subject = "Histórias de Usuário - Documento Anexo"
            elif summary:
                subject = "Resumo da Reunião - Documento Anexo"
            else:
                subject = "Documento Anexo"
            
            # Enviar email com anexo (em background, não esperar)
            import threading
            def send_email_async():
                try:
                    email_service.send_user_stories_with_attachment(
                        to_emails=email_list,
                        user_stories=user_stories if user_stories else '',
                        summary=summary if summary else '',
                        attachment_path=file_path,
                        attachment_filename=filename,
                        subject=subject,
                        body_format='html'
                    )
                    # Limpar arquivo após envio
                    import os
                    import time
                    time.sleep(5)  # Aguardar um pouco antes de limpar
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Erro ao enviar email em background: {str(e)}")
            
            thread = threading.Thread(target=send_email_async)
            thread.daemon = True
            thread.start()
            
            # Retornar arquivo para download
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf' if file_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            
        except Exception as e:
            print(f"Erro ao gerar documento e enviar: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Erro: {str(e)}'
            }), 500

    @app.route('/api/regenerate-summary', methods=['POST'])
    def regenerate_summary():
        """
        Regenera resumo de reunião com observações adicionais.
        
        Returns:
            JSON com resumo regenerado
        """
        try:
            original_text = request.form.get('original_text', '').strip()
            observations = request.form.get('observations', '').strip()
            current_summary = request.form.get('current_summary', '')
            provider = 'zello'
            
            print(f"[DEBUG] ========== REGENERANDO RESUMO ==========")
            print(f"[DEBUG] Tamanho do texto original: {len(original_text)} caracteres")
            print(f"[DEBUG] Observações: {observations[:200] if observations else 'nenhuma'}...")
            print(f"[DEBUG] Resumo atual: {len(current_summary) if current_summary else 0} caracteres")
            
            if not original_text:
                return jsonify({
                    'success': False,
                    'error': 'Texto original não fornecido'
                }), 400
            
            # Contextualizar observações para regeneração de resumo
            if observations and observations.strip():
                contextualized_observations = f"""CONTEXTO DE REGENERAÇÃO:
Você está regenerando o resumo da reunião com base no mesmo texto original, mas incorporando as seguintes observações específicas do usuário para melhorar ou refinar o resultado:

{observations.strip()}

IMPORTANTE: Estas observações são instruções específicas para adaptar ou melhorar o resumo que será gerado. Aplique-as de forma contextualizada, considerando que o usuário quer um resultado diferente ou melhorado em relação ao resumo anterior (por exemplo: mudança de tom, foco em aspectos específicos, nível de detalhe, formato, etc.)."""
            else:
                contextualized_observations = None
            
            print(f"[DEBUG] Observações contextualizadas: {len(contextualized_observations) if contextualized_observations else 0} caracteres")
            
            summary_result = generation_service.generate_summary(
                text=original_text,
                provider=provider,
                observations=contextualized_observations
            )
            
            if not summary_result['success']:
                return jsonify(summary_result), 500
            
            return jsonify({
                'success': True,
                'summary': summary_result['content'],
                'summary_info': summary_result,
                'message': 'Resumo regenerado com sucesso'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erro interno: {str(e)}'
            }), 500

    @app.route('/api/process-file/<int:job_id>', methods=['POST'])
    def process_single_job(job_id: int):
        """
        Processa um arquivo específico identificado por job_id.
        Atualiza status do job e cria artefato JSON com o resultado.
        """
        session = SessionLocal()
        try:
            job: TranscriptionJob | None = session.get(TranscriptionJob, job_id)
            if not job:
                return jsonify({'success': False, 'error': 'Job não encontrado'}), 404

            # Atualizar status para processing
            job.status = JobStatus.PROCESSING
            job.attempts = (job.attempts or 0) + 1
            job.updated_at = __import__('datetime').datetime.utcnow()
            session.commit()

            # Extrair texto do arquivo
            text_result = file_service.extract_text_from_file(job.source_uri)
            if not text_result.get('success'):
                job.status = JobStatus.FAILED
                job.updated_at = __import__('datetime').datetime.utcnow()
                session.commit()
                return jsonify({'success': False, 'error': text_result.get('error', 'Falha ao extrair texto') }), 400

            extracted_text = text_result['text']

            # Gerar HU com auto-correção (usa apenas Zello MIND)
            provider = request.args.get('provider', 'zello')
            max_attempts = int(request.args.get('max_attempts', '3'))
            generation_result = generation_service.generate_with_auto_correction(
                text=extracted_text,
                provider=provider,
                max_attempts=max_attempts
            )

            if not generation_result.get('success'):
                job.status = JobStatus.FAILED
                job.updated_at = __import__('datetime').datetime.utcnow()
                session.commit()
                return jsonify({'success': False, 'error': generation_result.get('error', 'Falha na geração')}), 500

            user_stories = generation_result['content']

            # Salvar artefato JSON em disco
            artifacts_dir = os.path.join('artifacts')
            try:
                os.makedirs(artifacts_dir, exist_ok=True)
            except Exception:
                pass
            artifact_filename = f"job_{job.id}.json"
            artifact_path = os.path.join(artifacts_dir, artifact_filename)
            try:
                with open(artifact_path, 'w', encoding='utf-8') as f:
                    import json as _json
                    _json.dump({
                        'job_id': job.id,
                        'source_uri': job.source_uri,
                        'user_stories': user_stories,
                        'generation_info': generation_result
                    }, f, ensure_ascii=False, indent=2)
            except Exception as e:
                job.status = JobStatus.FAILED
                job.updated_at = __import__('datetime').datetime.utcnow()
                session.commit()
                return jsonify({'success': False, 'error': f'Falha ao salvar artefato: {str(e)}'}), 500

            # Registrar artefato no banco
            try:
                artifact = ProcessingArtifact(
                    job_id=job.id,
                    type='json',
                    path=artifact_path,
                    size=os.path.getsize(artifact_path),
                    created_at=__import__('datetime').datetime.utcnow()
                )
                session.add(artifact)
            except Exception:
                pass

            # Atualizar status para processed
            job.status = JobStatus.PROCESSED
            job.updated_at = __import__('datetime').datetime.utcnow()
            session.commit()

            # Envio de email opcional (se query param email for fornecido)
            email_recipients = request.args.get('email', '')
            email_result = None
            if email_recipients:
                emails = [e.strip() for e in email_recipients.split(',') if e.strip()]
                if emails:
                    try:
                        email_result = email_service.send_user_stories_email(
                            to_emails=emails,
                            user_stories=user_stories,
                            format_type='html'
                        )
                    except Exception as _:
                        email_result = {'success': False, 'error': 'Falha ao enviar e-mail'}

            return jsonify({
                'success': True,
                'message': 'Processamento concluído',
                'job': {
                    'id': job.id,
                    'status': job.status,
                },
                'artifact': {
                    'type': 'json',
                    'path': artifact_path,
                    'filename': artifact_filename
                },
                'email_result': email_result,
                'generation_info': generation_result
            })
        except Exception as e:
            try:
                # Tenta marcar como failed em caso de erro geral
                if 'job' in locals() and job:
                    job.status = JobStatus.FAILED
                    job.updated_at = __import__('datetime').datetime.utcnow()
                    session.commit()
            except Exception:
                pass
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/models', methods=['GET'])
    def get_available_models():
        """
        Retorna os modelos disponíveis para cada LLM.
        
        Returns:
            JSON com modelos disponíveis
        """
        try:
            models = llm_service.get_available_models()
            return jsonify({
                'success': True,
                'models': models
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/prompt-types', methods=['GET'])
    def get_prompt_types():
        """
        Retorna os tipos de prompt disponíveis.
        
        Returns:
            JSON com tipos de prompt
        """
        try:
            prompt_types = UserStoryPrompts.get_prompt_templates()
            return jsonify({
                'success': True,
                'prompt_types': prompt_types
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/test-llm-connection', methods=['GET'])
    def test_llm_connection():
        """
        Testa conectividade com Zello MIND.
        """
        results = {}
        # teste Zello
        try:
            llm_service.get_completion('zello', [{"role": "user", "content": "ping"}])
            results['zello'] = {'ok': True}
        except Exception as e:
            results['zello'] = {'ok': False, 'error': str(e)}
        return jsonify({'success': True, 'results': results})
    
    @app.route('/api/validate-config', methods=['GET'])
    def validate_config():
        """
        Valida as configurações da aplicação.
        
        Returns:
            JSON com status da validação
        """
        try:
            errors = config.validate_config()
            return jsonify({
                'success': len(errors) == 0,
                'errors': errors,
                'config_status': {
                    'zello_configured': bool(config.ZELLO_API_KEY),
                    'email_configured': bool(config.SMTP_USERNAME and config.SMTP_PASSWORD),
                    'repository_configured': bool(config.TRANSCRIPTION_REPO_PATH)
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/scan-repository', methods=['POST'])
    def scan_repository():
        """
        Escaneia o repositório de transcrições.
        
        Returns:
            JSON com resultado do scan
        """
        try:
            if not repository_monitor:
                return jsonify({
                    'success': False,
                    'error': 'Monitor de repositório não configurado'
                }), 400
            
            result = repository_monitor.scan_repository()
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/collect-emails', methods=['POST'])
    def collect_emails():
        """
        Coleta e-mails do Gemini via Gmail e registra jobs. Salva texto bruto no Drive (opcional).
        Body opcional: { "users": ["colab@empresa.com"], "max": 20 }
        """
        if not gmail_service:
            return jsonify({'success': False, 'error': 'Gmail não configurado'}), 400
        from database import SessionLocal
        from models import TranscriptionJob, JobStatus
        import datetime as _dt
        payload = request.get_json(silent=True) or {}
        users = payload.get('users') or ([config.GMAIL_DELEGATED_USER] if config.GMAIL_DELEGATED_USER else [])
        max_results = int(payload.get('max', 20))
        if not users:
            return jsonify({'success': False, 'error': 'Nenhum usuário fornecido'}), 400
        session = SessionLocal()
        created = 0
        errors = []
        try:
            for user in users:
                try:
                    msgs = gmail_service.list_gemini_messages(user, max_results=max_results)
                    for m in msgs:
                        mid = m['id']
                        full = gmail_service.get_message(user, mid)
                        text = gmail_service.extract_plain_text(full)
                        # hash simples baseado em id da mensagem
                        file_hash = mid
                        exists = session.query(TranscriptionJob).filter_by(source_hash=file_hash).first()
                        if exists:
                            continue
                        # opcionalmente salva no Drive
                        gdrive_path = None
                        if gdrive_service and config.GDRIVE_ROOT_FOLDER_ID:
                            folder_user = gdrive_service.ensure_folder(config.GDRIVE_ROOT_FOLDER_ID, user)
                            fid = gdrive_service.upload_text(folder_user, f"gemini_{mid}.txt", text)
                            gdrive_path = f"drive://{fid}"
                        job = TranscriptionJob(
                            source_uri=f"gmail://{user}/{mid}",
                            source_hash=file_hash,
                            status=JobStatus.DISCOVERED,
                            attempts=0,
                            created_at=_dt.datetime.utcnow(),
                            updated_at=_dt.datetime.utcnow(),
                            collaborator_email=user,
                        )
                        session.add(job)
                        session.commit()
                        created += 1
                except Exception as ue:
                    errors.append({'user': user, 'error': str(ue)})
            return jsonify({'success': True, 'created': created, 'errors': errors})
        except Exception as e:
            session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            session.close()
    
    @app.route('/api/repository-stats', methods=['GET'])
    def get_repository_stats():
        """
        Obtém estatísticas do repositório e banco de dados.
        
        Returns:
            JSON com estatísticas
        """
        try:
            if not repository_monitor:
                return jsonify({
                    'success': False,
                    'error': 'Monitor de repositório não configurado'
                }), 400
            
            result = repository_monitor.get_repository_stats()
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    
    @app.route('/api/recent-jobs', methods=['GET'])
    def get_recent_jobs():
        """
        Obtém jobs recentes do banco de dados.
        
        Returns:
            JSON com lista de jobs recentes
        """
        try:
            if not repository_monitor:
                return jsonify({
                    'success': False,
                    'error': 'Monitor de repositório não configurado'
                }), 400
            
            limit = request.args.get('limit', 50, type=int)
            jobs = repository_monitor.get_recent_jobs(limit)
            return jsonify({
                'success': True,
                'jobs': jobs
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.errorhandler(413)
    def too_large(e):
        """Handler para arquivos muito grandes."""
        return jsonify({
            'success': False,
            'error': 'Arquivo muito grande. Tamanho máximo: 16MB'
        }), 413
    
    @app.errorhandler(404)
    def not_found(e):
        """Handler para páginas não encontradas."""
        return jsonify({
            'success': False,
            'error': 'Página não encontrada'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(e):
        """Handler para erros internos."""
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor'
        }), 500
    
    return app


def _generate_prompt(prompt_type: str, content: str) -> str:
    """
    Gera prompt baseado no tipo especificado.
    
    Args:
        prompt_type: Tipo do prompt
        content: Conteúdo para processar
        
    Returns:
        Prompt formatado
    """
    if prompt_type == 'generate_from_requirements':
        return UserStoryPrompts.generate_user_stories_from_requirements(content)
    elif prompt_type == 'analyze_existing':
        return UserStoryPrompts.analyze_existing_user_stories(content)
    elif prompt_type == 'refine_story':
        return UserStoryPrompts.refine_user_story(content)
    elif prompt_type == 'generate_acceptance_criteria':
        return UserStoryPrompts.generate_acceptance_criteria(content)
    elif prompt_type == 'estimate_effort':
        return UserStoryPrompts.estimate_user_story_effort(content)
    else:
        return UserStoryPrompts.generate_user_stories_from_requirements(content)


if __name__ == '__main__':
    app = create_app()
    
    # Validar configurações antes de iniciar
    config_errors = config.validate_config()
    if config_errors:
        print("AVISOS DE CONFIGURACAO:")
        for error in config_errors:
            print(f"   - {error}")
        print("\nDica: Crie um arquivo .env baseado no env.example")
    
    print(f"Iniciando servidor em http://{config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
