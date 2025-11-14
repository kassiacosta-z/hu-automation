"""
Script de execução rápida com configurações pré-definidas para teste.
"""

import os
import sys
from datetime import datetime

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_service import GmailService
from gdrive_service import GDriveService


def quick_test():
    """
    Executa um teste rápido com as credenciais fornecidas.
    """
    print("=" * 80)
    print("🚀 TESTE RÁPIDO - COLETA DE TRANSCRIÇÕES GEMINI")
    print("=" * 80)
    
    # Configurações de teste
    credentials_path = "credentials.json"
    central_user = "admin@zello.tec.br"  # Ajuste conforme necessário
    test_collaborators = ["admin@zello.tec.br"]  # Teste com um usuário primeiro
    email_query = "from:gemini@google.com"
    folder_name = f"Teste Gemini - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"📋 Configurações de teste:")
    print(f"  • Drive central: {central_user}")
    print(f"  • Colaborador de teste: {test_collaborators[0]}")
    print(f"  • Filtro: {email_query}")
    print(f"  • Pasta: {folder_name}")
    
    try:
        # Conectar ao Google Drive
        print(f"\n✅ Conectando ao Google Drive...")
        gdrive_service = GDriveService(credentials_path, central_user)
        
        # Criar pasta de teste
        main_folder_id = gdrive_service.find_or_create_folder(folder_name)
        if not main_folder_id:
            print("❌ Erro ao criar pasta principal")
            return False
        
        print(f"✅ Pasta criada: {folder_name}")
        
        # Testar com um colaborador
        collaborator = test_collaborators[0]
        print(f"\n👤 Testando com: {collaborator}")
        
        # Conectar ao Gmail do colaborador
        gmail_service = GmailService(credentials_path, collaborator)
        
        # Buscar emails
        messages = gmail_service.search_emails(email_query, max_results=5)
        
        if not messages:
            print("ℹ️ Nenhum email encontrado para teste")
            return True
        
        # Criar subpasta para o colaborador
        collaborator_name = collaborator.split('@')[0]
        collaborator_folder_id = gdrive_service.find_or_create_folder(
            collaborator_name,
            main_folder_id
        )
        
        # Processar alguns emails
        processed = 0
        for i, message in enumerate(messages[:3], 1):  # Apenas 3 para teste
            try:
                # Obter detalhes do email
                email_details = gmail_service.get_email_details(message['id'])
                
                # Formatar conteúdo
                content = f"""Transcrição do Google Gemini - TESTE
================================================================================

Proprietário: {email_details['owner']}
Assunto: {email_details['subject']}
De: {email_details['from']}
Data: {email_details['date']}

================================================================================

{email_details['body'][:500]}...

[Conteúdo truncado para teste]
"""
                
                # Gerar nome do arquivo
                filename = f"teste_transcricao_{i}.txt"
                
                # Fazer upload
                file_id = gdrive_service.upload_text_file(
                    collaborator_folder_id,
                    filename,
                    content
                )
                
                if file_id:
                    print(f"  ✅ [{i}/{min(3, len(messages))}] Salvo: {filename}")
                    processed += 1
                else:
                    print(f"  ❌ [{i}/{min(3, len(messages))}] Erro ao salvar: {filename}")
                
            except Exception as e:
                print(f"  ❌ [{i}/{min(3, len(messages))}] Erro: {str(e)}")
        
        print(f"\n🎉 Teste concluído!")
        print(f"  • Emails processados: {processed}")
        print(f"  • Pasta no Drive: {folder_name}")
        print(f"  • Acesse o Google Drive de {central_user}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False


def main():
    """Executa o teste rápido."""
    if not os.path.exists("credentials.json"):
        print("❌ Arquivo credentials.json não encontrado!")
        print("💡 Certifique-se de que o arquivo está na raiz do projeto")
        sys.exit(1)
    
    success = quick_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
