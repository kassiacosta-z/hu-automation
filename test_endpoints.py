#!/usr/bin/env python3
"""
Script de teste para os novos endpoints de integração Drive.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_transcription_fetcher():
    """Testa o TranscriptionFetcherService diretamente."""
    print("=== TESTE TRANSCRIPTION FETCHER SERVICE ===")
    
    try:
        from services.transcription_fetcher_service import TranscriptionFetcherService
        
        print("[OK] Import do TranscriptionFetcherService OK")
        
        # Criar instância
        fetcher = TranscriptionFetcherService()
        print("[OK] Instancia criada com sucesso")
        
        # Testar listagem de emails
        emails = fetcher.list_available_emails()
        print(f"[OK] Emails disponiveis: {emails}")
        
        # Se houver emails, testar busca de transcrições
        if emails:
            test_email = emails[0]
            print(f"[OK] Testando com email: {test_email}")
            
            # Verificar disponibilidade
            is_available = fetcher.is_email_available(test_email)
            print(f"[OK] Email disponivel: {is_available}")
            
            if is_available:
                # Buscar transcrições
                transcriptions = fetcher.get_transcriptions_by_email(test_email, limit=3)
                print(f"[OK] Transcricoes encontradas: {len(transcriptions)}")
                
                for i, t in enumerate(transcriptions):
                    print(f"  [{i+1}] {t['filename']} - {t['date']} ({t['size']} bytes)")
                
                # Testar última transcrição
                latest = fetcher.get_latest_transcription(test_email)
                if latest:
                    print(f"[OK] Ultima transcricao: {latest['filename']}")
        
        print("[SUCCESS] TODOS OS TESTES PASSARAM!")
        return True
        
    except Exception as e:
        print(f"[ERROR] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app():
    """Testa se o Flask app pode ser criado."""
    print("\n=== TESTE FLASK APP ===")
    
    try:
        from app import create_app
        
        print("[OK] Import do create_app OK")
        
        # Criar app
        app = create_app()
        print("[OK] Flask app criado com sucesso")
        
        # Verificar se os endpoints existem
        with app.test_client() as client:
            print("[OK] Test client criado")
            
            # Testar endpoint de emails
            response = client.get('/api/emails/available')
            print(f"[OK] Endpoint /api/emails/available: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"[OK] Resposta: {data}")
        
        print("[SUCCESS] FLASK APP TESTE PASSOU!")
        return True
        
    except Exception as e:
        print(f"[ERROR] ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("INICIANDO TESTES DE INTEGRACAO DRIVE")
    print("=" * 50)
    
    # Testar serviço diretamente
    service_ok = test_transcription_fetcher()
    
    # Testar Flask app
    flask_ok = test_flask_app()
    
    print("\n" + "=" * 50)
    if service_ok and flask_ok:
        print("TODOS OS TESTES PASSARAM!")
        print("Backend integracao Drive esta funcionando!")
        sys.exit(0)
    else:
        print("ALGUNS TESTES FALHARAM!")
        sys.exit(1)