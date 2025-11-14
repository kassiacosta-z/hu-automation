"""
Script de instalação e configuração rápida do sistema de coleta de transcrições.
"""

import os
import sys
import subprocess
import shutil


def check_python_version():
    """Verifica se a versão do Python é compatível."""
    print("🐍 Verificando versão do Python...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} não é compatível. Necessário Python 3.8+")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatível")
    return True


def create_virtual_environment():
    """Cria ambiente virtual se não existir."""
    print("\n🔧 Verificando ambiente virtual...")
    
    if os.path.exists("venv"):
        print("✅ Ambiente virtual já existe")
        return True
    
    try:
        print("📦 Criando ambiente virtual...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Ambiente virtual criado")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao criar ambiente virtual")
        return False


def install_dependencies():
    """Instala dependências do projeto."""
    print("\n📦 Instalando dependências...")
    
    # Determinar comando pip baseado no OS
    if os.name == 'nt':  # Windows
        pip_cmd = os.path.join("venv", "Scripts", "pip")
    else:  # Linux/Mac
        pip_cmd = os.path.join("venv", "bin", "pip")
    
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependências instaladas")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False


def setup_configuration():
    """Configura arquivo .env se não existir."""
    print("\n⚙️ Configurando arquivo .env...")
    
    if os.path.exists(".env"):
        print("✅ Arquivo .env já existe")
        return True
    
    if os.path.exists("env.example"):
        try:
            shutil.copy("env.example", ".env")
            print("✅ Arquivo .env criado a partir do template")
            print("⚠️ IMPORTANTE: Edite o arquivo .env com suas configurações!")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar .env: {e}")
            return False
    else:
        print("⚠️ Arquivo env.example não encontrado")
        return False


def check_credentials():
    """Verifica se arquivo de credenciais existe."""
    print("\n🔐 Verificando credenciais...")
    
    if os.path.exists("credentials.json"):
        print("✅ Arquivo credentials.json encontrado")
        return True
    else:
        print("⚠️ Arquivo credentials.json não encontrado")
        print("💡 Você precisa:")
        print("   1. Baixar o arquivo JSON da Service Account")
        print("   2. Renomear para 'credentials.json'")
        print("   3. Colocar na raiz do projeto")
        return False


def main():
    """Executa instalação completa."""
    print("=" * 80)
    print("🚀 INSTALAÇÃO - COLETA DE TRANSCRIÇÕES GEMINI")
    print("=" * 80)
    
    steps_completed = 0
    total_steps = 5
    
    # Passo 1: Verificar Python
    if check_python_version():
        steps_completed += 1
    
    # Passo 2: Criar ambiente virtual
    if create_virtual_environment():
        steps_completed += 1
    
    # Passo 3: Instalar dependências
    if install_dependencies():
        steps_completed += 1
    
    # Passo 4: Configurar .env
    if setup_configuration():
        steps_completed += 1
    
    # Passo 5: Verificar credenciais
    if check_credentials():
        steps_completed += 1
    
    # Resultado final
    print("\n" + "=" * 80)
    print("📊 RESULTADO DA INSTALAÇÃO")
    print("=" * 80)
    print(f"✅ Passos completados: {steps_completed}/{total_steps}")
    
    if steps_completed >= 4:  # Credenciais são opcionais na instalação
        print("🎉 INSTALAÇÃO CONCLUÍDA!")
        print("\n📋 Próximos passos:")
        print("   1. Configure o arquivo .env com seus dados")
        print("   2. Adicione o arquivo credentials.json")
        print("   3. Execute: python test_integration.py")
        print("   4. Se tudo OK, execute: python main.py")
        
        print("\n💡 Comandos úteis:")
        if os.name == 'nt':  # Windows
            print("   • Ativar ambiente virtual: venv\\Scripts\\activate")
        else:  # Linux/Mac
            print("   • Ativar ambiente virtual: source venv/bin/activate")
        print("   • Testar integração: python test_integration.py")
        print("   • Executar coleta: python main.py")
    else:
        print("⚠️ Instalação incompleta. Verifique os erros acima.")
    
    return steps_completed >= 4


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
