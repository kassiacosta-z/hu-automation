"""
Aplicação Flask para automação de Histórias de Usuário.
"""

import os
import json
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
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
            # Usar apenas Zello MIND (sem fallback para OpenAI)
            provider = 'zello'
            email = request.form.get('email', request.form.get('email_recipients', ''))
            output_format = request.form.get('output_format', request.form.get('email_format', 'preview'))
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
                
                # Gerar Histórias de Usuário com auto-correção
                generation_result = generation_service.generate_with_auto_correction(
                    text=extracted_text,
                    provider=provider,
                    max_attempts=max_attempts
                )
                
                if not generation_result['success']:
                    error_msg = generation_result.get('error', 'Erro desconhecido')
                    print(f"Erro na geração: {error_msg}")
                    return jsonify(generation_result), 500
                
                user_stories = generation_result['content']
                print(f"Geração bem-sucedida! Provider: {generation_result.get('provider', 'unknown')}")
                
                # Processar baseado no formato de saída
                if api_output_format in ['pdf', 'docx']:
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
                
                elif api_output_format == 'email_body_txt' or (api_output_format == 'preview' and email and email_body_format in ['html','text']):
                    # Enviar conteúdo diretamente no corpo do e-mail
                    if email:
                        email_list = [email.strip() for email in email.split(',') if email.strip()]
                        if email_list:
                            email_result = email_service.send_user_stories_email(
                                to_emails=email_list,
                                user_stories=user_stories,
                                format_type='html' if email_body_format == 'html' else 'text'
                            )
                            
                            return jsonify({
                                'success': True,
                                'message': 'E-mail enviado com sucesso',
                                'email_result': email_result,
                                'generation_info': generation_result
                            })
                    
                    return jsonify({
                        'success': False,
                        'error': 'E-mail não especificado para formato email_body_txt'
                    }), 400
                
                elif api_output_format == 'preview':
                    # Retornar JSON completo para preview
                    return jsonify({
                        'success': True,
                        'user_stories': user_stories,
                        'generation_info': generation_result,
                        'extraction_info': text_result
                    })
                
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
        Testa conectividade com Zello e OpenAI.
        """
        results = {}
        # teste Zello
        try:
            llm_service.get_completion('zello', [{"role": "user", "content": "ping"}])
            results['zello'] = {'ok': True}
        except Exception as e:
            results['zello'] = {'ok': False, 'error': str(e)}
        # teste OpenAI
        try:
            llm_service.get_completion('openai', [{"role": "user", "content": "ping"}])
            results['openai'] = {'ok': True}
        except Exception as e:
            results['openai'] = {'ok': False, 'error': str(e)}
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
                    'openai_configured': bool(config.OPENAI_API_KEY),
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
