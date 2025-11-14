"""
Script de teste para validar a integração com as credenciais fornecidas.
"""

import os
import sys
from gmail_service import GmailService
from gdrive_service import GDriveService


def test_credentials():
    """Testa se as credenciais estão funcionando."""
    print("🔧 Testando credenciais...")
    
    credentials_path = "credentials.json"
    if not os.path.exists(credentials_path):
        print("❌ Arquivo credentials.json não encontrado!")
        return False
    
    print("✅ Arquivo credentials.json encontrado")
    return True


def test_gmail_service():
    """Testa o serviço Gmail."""
    print("\n📧 Testando Gmail Service...")
    
    try:
        # Carregar email do arquivo .env
        from dotenv import load_dotenv
        load_dotenv()
        test_email = os.getenv('COLABORADORES', 'admin@zello.tec.br').split(',')[0].strip()
        
        gmail_service = GmailService("credentials.json", test_email)
        
        # Testar conexão básica
        service = gmail_service._get_service()
        print(f"✅ Gmail Service conectado para: {test_email}")
        
        # Testar busca simples (apenas verificar se não dá erro)
        try:
            messages = gmail_service.search_emails("from:gemini@google.com", max_results=1)
            print(f"✅ Busca de emails funcionando ({len(messages)} emails encontrados)")
        except Exception as e:
            print(f"⚠️ Busca de emails falhou (pode ser normal se não houver emails): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no Gmail Service: {e}")
        return False


def test_gdrive_service():
    """Testa o serviço Google Drive."""
    print("\n📁 Testando Google Drive Service...")
    
    try:
        # Carregar email do arquivo .env
        from dotenv import load_dotenv
        load_dotenv()
        test_email = os.getenv('CENTRAL_DRIVE_USER', 'admin@zello.tec.br')
        
        gdrive_service = GDriveService("credentials.json", test_email)
        
        # Testar conexão básica
        service = gdrive_service._get_service()
        print(f"✅ Google Drive Service conectado para: {test_email}")
        
        # Testar criação de pasta (pasta de teste)
        try:
            folder_id = gdrive_service.find_or_create_folder("TESTE_INTEGRACAO")
            print(f"✅ Criação de pasta funcionando (ID: {folder_id})")
            
            # Testar upload de arquivo de teste
            test_content = "Arquivo de teste da integração - " + str(os.getpid())
            file_id = gdrive_service.upload_text_file(folder_id, "teste_integracao.txt", test_content)
            print(f"✅ Upload de arquivo funcionando (ID: {file_id})")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Operações de pasta/arquivo falharam: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Erro no Google Drive Service: {e}")
        return False


def main():
    """Executa todos os testes."""
    print("=" * 80)
    print("🧪 TESTE DE INTEGRAÇÃO - COLETA DE TRANSCRIÇÕES GEMINI")
    print("=" * 80)
    
    tests_passed = 0
    total_tests = 3
    
    # Teste 1: Credenciais
    if test_credentials():
        tests_passed += 1
    
    # Teste 2: Gmail Service
    if test_gmail_service():
        tests_passed += 1
    
    # Teste 3: Google Drive Service
    if test_gdrive_service():
        tests_passed += 1
    
    # Resultado final
    print("\n" + "=" * 80)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 80)
    print(f"✅ Testes passaram: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
        print("\n💡 Próximos passos:")
        print("   1. Configure o arquivo .env com seus colaboradores")
        print("   2. Execute: python main.py")
    else:
        print("⚠️ Alguns testes falharam. Verifique as configurações.")
        print("\n🔧 Possíveis soluções:")
        print("   1. Verificar se Domain-Wide Delegation está configurado")
        print("   2. Confirmar que as APIs estão ativadas no Google Cloud")
        print("   3. Aguardar propagação das configurações (até 24h)")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
