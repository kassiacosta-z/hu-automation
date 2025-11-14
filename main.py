"""
Script principal para coleta centralizada de transcrições do Google Gemini.

Este script coleta emails de transcrições do Gemini de múltiplas contas de colaboradores
e salva tudo centralizado em um único Google Drive usando Domain-Wide Delegation.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from gmail_service import GmailService
from gdrive_service import GDriveService


def load_configuration() -> Dict[str, Any]:
    """
    Carrega e valida as configurações do arquivo .env.
    
    Returns:
        Dicionário com as configurações carregadas
        
    Raises:
        SystemExit: Se houver configurações obrigatórias faltando
    """
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Configurações obrigatórias
    required_vars = [
        'GOOGLE_CREDENTIALS_JSON',
        'CENTRAL_DRIVE_USER',
        'COLABORADORES',
        'EMAIL_QUERY',
        'BACKUP_FOLDER_NAME'
    ]
    
    config = {}
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            config[var] = value
    
    if missing_vars:
        print("❌ ERRO: As seguintes variáveis de ambiente são obrigatórias:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\n💡 Dica: Copie o arquivo .env.example para .env e preencha as configurações.")
        sys.exit(1)
    
    # Configurações opcionais
    config['MARK_AS_PROCESSED'] = os.getenv('MARK_AS_PROCESSED', 'True').lower() == 'true'
    
    # Validar se arquivo de credenciais existe
    if not os.path.exists(config['GOOGLE_CREDENTIALS_JSON']):
        print(f"❌ ERRO: Arquivo de credenciais não encontrado: {config['GOOGLE_CREDENTIALS_JSON']}")
        sys.exit(1)
    
    # Processar lista de colaboradores
    colaboradores_str = config['COLABORADORES']
    config['COLABORADORES_LIST'] = [email.strip() for email in colaboradores_str.split(',') if email.strip()]
    
    if not config['COLABORADORES_LIST']:
        print("❌ ERRO: Nenhum colaborador válido encontrado na configuração COLABORADORES")
        sys.exit(1)
    
    return config


def format_transcription_content(email_details: Dict[str, Any]) -> str:
    """
    Formata o conteúdo de uma transcrição para salvar no arquivo.
    
    Args:
        email_details: Detalhes do email obtidos do Gmail
        
    Returns:
        Conteúdo formatado para o arquivo
    """
    content = f"""Transcrição do Google Gemini
================================================================================

Proprietário: {email_details['owner']}
Assunto: {email_details['subject']}
De: {email_details['from']}
Data: {email_details['date']}

================================================================================

{email_details['body']}
"""
    return content


def generate_filename(email_details: Dict[str, Any], index: int) -> str:
    """
    Gera um nome de arquivo único para a transcrição.
    
    Args:
        email_details: Detalhes do email
        index: Índice do email (para evitar duplicatas)
        
    Returns:
        Nome do arquivo único
    """
    # Extrair data do email
    try:
        # Tentar extrair data do header Date
        date_str = email_details['date']
        if date_str:
            # Formato esperado: "Thu, 10 Oct 2025 14:30:22 -0300"
            date_obj = datetime.strptime(date_str.split(' (')[0], '%a, %d %b %Y %H:%M:%S')
            date_part = date_obj.strftime('%Y%m%d_%H%M%S')
        else:
            date_part = datetime.now().strftime('%Y%m%d_%H%M%S')
    except:
        date_part = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Limpar assunto para usar no nome do arquivo
    subject_clean = "".join(c for c in email_details['subject'] if c.isalnum() or c in (' ', '-', '_')).strip()
    subject_clean = subject_clean.replace(' ', '_')[:50]  # Limitar tamanho
    
    filename = f"transcricao_{date_part}_{index}_{subject_clean}.txt"
    return filename


def process_collaborator(
    collaborator_email: str,
    config: Dict[str, Any],
    gmail_service: GmailService,
    gdrive_service: GDriveService,
    main_folder_id: str
) -> int:
    """
    Processa emails de um colaborador específico.
    
    Args:
        collaborator_email: Email do colaborador
        config: Configurações do sistema
        gmail_service: Serviço Gmail
        gdrive_service: Serviço Google Drive
        main_folder_id: ID da pasta principal no Drive
        
    Returns:
        Número de emails processados com sucesso
    """
    try:
        print(f"\n{'='*80}")
        print(f"👤 Processando: {collaborator_email}")
        print(f"{'='*80}")
        
        # Conectar ao Gmail do colaborador
        gmail_service.delegated_user = collaborator_email
        gmail_service._service = None  # Forçar reconexão
        
        print(f"✅ Gmail conectado para: {collaborator_email}")
        
        # Buscar emails
        messages = gmail_service.search_emails(config['EMAIL_QUERY'])
        
        if not messages:
            print(f"  ℹ️ Nenhum email encontrado para {collaborator_email}")
            return 0
        
        # Criar subpasta para o colaborador
        collaborator_name = collaborator_email.split('@')[0]
        collaborator_folder_id = gdrive_service.find_or_create_folder(
            collaborator_name,
            main_folder_id
        )
        
        if not collaborator_folder_id:
            print(f"  ❌ Erro ao criar pasta para {collaborator_email}")
            return 0
        
        # Processar cada email
        processed_count = 0
        for i, message in enumerate(messages, 1):
            try:
                # Obter detalhes do email
                email_details = gmail_service.get_email_details(message['id'])
                
                # Formatar conteúdo
                content = format_transcription_content(email_details)
                
                # Gerar nome do arquivo
                filename = generate_filename(email_details, i)
                
                # Fazer upload para o Drive
                file_id = gdrive_service.upload_text_file(
                    collaborator_folder_id,
                    filename,
                    content
                )
                
                if file_id:
                    print(f"  ✅ [{i}/{len(messages)}] Salvo: {filename}")
                    processed_count += 1
                    
                    # Marcar como processado se configurado
                    if config['MARK_AS_PROCESSED']:
                        gmail_service.mark_as_read(message['id'])
                        gmail_service.add_label(message['id'], 'BACKUP_REALIZADO')
                else:
                    print(f"  ❌ [{i}/{len(messages)}] Erro ao salvar: {filename}")
                
            except Exception as e:
                print(f"  ❌ [{i}/{len(messages)}] Erro ao processar email: {str(e)}")
                continue
        
        print(f"  ✅ {processed_count} emails processados de {collaborator_email}")
        return processed_count
        
    except Exception as e:
        print(f"  ❌ Erro ao processar colaborador {collaborator_email}: {str(e)}")
        return 0


def main():
    """
    Função principal que orquestra todo o processo de coleta.
    """
    print("=" * 80)
    print("COLETA CENTRALIZADA DE TRANSCRICOES DO GEMINI")
    print("=" * 80)
    
    try:
        # Carregar configurações
        print("\nCarregando configuracoes...")
        config = load_configuration()
        
        print(f"\n📋 Configurações:")
        print(f"  • Drive central: {config['CENTRAL_DRIVE_USER']}")
        print(f"  • Colaboradores: {len(config['COLABORADORES_LIST'])}")
        print(f"  • Filtro: {config['EMAIL_QUERY']}")
        print(f"  • Pasta: {config['BACKUP_FOLDER_NAME']}")
        print(f"  • Marcar como processado: {config['MARK_AS_PROCESSED']}")
        
        # Conectar ao Google Drive da conta central
        print(f"\n✅ Google Drive conectado para: {config['CENTRAL_DRIVE_USER']}")
        gdrive_service = GDriveService(
            config['GOOGLE_CREDENTIALS_JSON'],
            config['CENTRAL_DRIVE_USER']
        )
        
        # Criar pasta principal
        main_folder_id = gdrive_service.find_or_create_folder(config['BACKUP_FOLDER_NAME'])
        if not main_folder_id:
            print("❌ Erro ao criar pasta principal no Drive")
            sys.exit(1)
        
        # Inicializar serviço Gmail (será reconfigurado para cada colaborador)
        gmail_service = GmailService(
            config['GOOGLE_CREDENTIALS_JSON'],
            config['CENTRAL_DRIVE_USER']  # Será alterado para cada colaborador
        )
        
        # Processar cada colaborador
        total_emails = 0
        successful_collaborators = 0
        
        for collaborator in config['COLABORADORES_LIST']:
            try:
                emails_count = process_collaborator(
                    collaborator,
                    config,
                    gmail_service,
                    gdrive_service,
                    main_folder_id
                )
                
                if emails_count > 0:
                    total_emails += emails_count
                    successful_collaborators += 1
                    
            except Exception as e:
                print(f"❌ Erro crítico ao processar {collaborator}: {str(e)}")
                continue
        
        # Resumo final
        print(f"\n{'='*80}")
        print("🎉 PROCESSO CONCLUÍDO!")
        print(f"{'='*80}")
        print(f"  • Total de emails salvos: {total_emails}")
        print(f"  • Colaboradores processados: {successful_collaborators}/{len(config['COLABORADORES_LIST'])}")
        print(f"  • Pasta no Drive: {config['BACKUP_FOLDER_NAME']}")
        print(f"\n✅ Acesse o Google Drive de {config['CENTRAL_DRIVE_USER']} para ver os arquivos")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Processo interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
