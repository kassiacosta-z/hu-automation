"""
Aplicação Flask para automação de Histórias de Usuário.
"""

import os
import json
from typing import Dict, Any, List
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.exceptions import RequestEntityTooLarge

from config import config
from services import LLMService, EmailService, FileService, GenerationService
from prompts import UserStoryPrompts


def create_app() -> Flask:
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    
    # Inicializar serviços
    llm_service = LLMService()
    email_service = EmailService()
    file_service = FileService()
    generation_service = GenerationService(llm_service)
    
    @app.route('/')
    def index():
        """Página principal da aplicação."""
        return render_template('index.html')
    
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
            provider = request.form.get('provider', request.form.get('llm_type', 'openai'))
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
                    return jsonify(generation_result), 500
                
                user_stories = generation_result['content']
                
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
                    'email_configured': bool(config.SMTP_USERNAME and config.SMTP_PASSWORD)
                }
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
        print("⚠️  AVISOS DE CONFIGURAÇÃO:")
        for error in config_errors:
            print(f"   - {error}")
        print("\n💡 Dica: Crie um arquivo .env baseado no env.example")
    
    print(f"🚀 Iniciando servidor em http://{config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
