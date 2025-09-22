"""
Teste simples para verificar se a aplicação está funcionando.
"""

import os
import sys
from unittest.mock import patch, MagicMock

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os módulos podem ser importados."""
    try:
        from config import config
        print("✓ config.py importado com sucesso")
        
        from services import LLMService, EmailService, FileService
        print("✓ services importados com sucesso")
        
        from prompts import UserStoryPrompts
        print("✓ prompts importados com sucesso")
        
        from app import create_app
        print("✓ app.py importado com sucesso")
        
        return True
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False

def test_config():
    """Testa se as configurações estão funcionando."""
    try:
        from config import config
        
        print(f"✓ SECRET_KEY: {'Definida' if config.SECRET_KEY else 'Não definida'}")
        print(f"✓ DEBUG: {config.DEBUG}")
        print(f"✓ HOST: {config.HOST}")
        print(f"✓ PORT: {config.PORT}")
        
        # Testar validação
        errors = config.validate_config()
        if errors:
            print(f"⚠️  Avisos de configuração: {errors}")
        else:
            print("✓ Configurações válidas")
        
        return True
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

def test_services():
    """Testa se os serviços podem ser instanciados."""
    try:
        from services import LLMService, EmailService, FileService
        
        # Testar LLMService
        llm_service = LLMService()
        print("✓ LLMService instanciado com sucesso")
        
        # Testar EmailService
        email_service = EmailService()
        print("✓ EmailService instanciado com sucesso")
        
        # Testar FileService
        file_service = FileService()
        print("✓ FileService instanciado com sucesso")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos serviços: {e}")
        return False

def test_prompts():
    """Testa se os prompts estão funcionando."""
    try:
        from prompts import UserStoryPrompts
        
        # Testar geração de prompt
        prompt = UserStoryPrompts.generate_user_stories_from_requirements("Teste de requisitos")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        print("✓ Prompts funcionando corretamente")
        
        # Testar templates disponíveis
        templates = UserStoryPrompts.get_prompt_templates()
        assert isinstance(templates, dict)
        assert len(templates) > 0
        print(f"✓ {len(templates)} templates de prompt disponíveis")
        
        return True
    except Exception as e:
        print(f"❌ Erro nos prompts: {e}")
        return False

def test_flask_app():
    """Testa se a aplicação Flask pode ser criada."""
    try:
        from app import create_app
        
        # Mock das configurações para evitar erros de validação
        with patch('config.config.validate_config', return_value=[]):
            app = create_app()
            assert app is not None
            print("✓ Aplicação Flask criada com sucesso")
        
        return True
    except Exception as e:
        print(f"❌ Erro na aplicação Flask: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🧪 Executando testes da aplicação...\n")
    
    tests = [
        ("Importações", test_imports),
        ("Configurações", test_config),
        ("Serviços", test_services),
        ("Prompts", test_prompts),
        ("Aplicação Flask", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testando {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}")
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! A aplicação está pronta para uso.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
