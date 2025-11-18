"""
Script para verificar dependências do Whisper
"""
import sys

print("=" * 60)
print("VERIFICACAO DE DEPENDENCIAS DO WHISPER")
print("=" * 60)

# Verificar openai-whisper
try:
    import whisper
    print("\n[OK] openai-whisper instalado")
    try:
        print(f"    Versao: {whisper.__version__}")
    except:
        print("    Versao: N/A")
except ImportError as e:
    print("\n[ERRO] openai-whisper NAO instalado")
    print(f"    Erro: {e}")
    print("    Solucao: pip install openai-whisper")
    sys.exit(1)

# Verificar ffmpeg-python
try:
    import ffmpeg
    print("\n[OK] ffmpeg-python instalado")
except ImportError:
    print("\n[AVISO] ffmpeg-python NAO instalado (opcional)")
    print("    Solucao: pip install ffmpeg-python")

# Verificar FFmpeg no sistema
import subprocess
import shutil

ffmpeg_path = shutil.which('ffmpeg')
if ffmpeg_path:
    print(f"\n[OK] FFmpeg encontrado no sistema")
    print(f"    Caminho: {ffmpeg_path}")
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"    Versao: {version_line}")
    except Exception as e:
        print(f"    [AVISO] Nao foi possivel verificar versao: {e}")
else:
    print("\n[ERRO] FFmpeg NAO encontrado no PATH do sistema")
    print("    O Whisper requer FFmpeg instalado no sistema")
    print("    Solucao:")
    print("    Windows: Baixe de https://ffmpeg.org/download.html")
    print("    Ou use: winget install FFmpeg")
    print("    Ou use: choco install ffmpeg")
    sys.exit(1)

# Testar carregamento do modelo
print("\n" + "=" * 60)
print("TESTANDO CARREGAMENTO DO MODELO WHISPER")
print("=" * 60)

try:
    from config import config
    model_name = config.WHISPER_MODEL
    print(f"\nTentando carregar modelo: {model_name}")
    print("(Isso pode demorar na primeira vez - o modelo sera baixado)")
    
    model = whisper.load_model(model_name)
    print(f"\n[OK] Modelo {model_name} carregado com sucesso!")
    
except Exception as e:
    print(f"\n[ERRO] Falha ao carregar modelo: {e}")
    print("\nPossiveis causas:")
    print("1. FFmpeg nao instalado corretamente")
    print("2. Problemas de conexao (modelo precisa ser baixado)")
    print("3. Espaco em disco insuficiente")
    sys.exit(1)

print("\n" + "=" * 60)
print("[OK] TODAS AS DEPENDENCIAS ESTAO OK!")
print("=" * 60)

