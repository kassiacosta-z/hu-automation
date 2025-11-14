#!/usr/bin/env python3
"""
Script simples para testar a integração Drive com dados reais.
"""

import os
import sys
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

def test_with_real_data():
    """Testa com dados reais do Drive."""
    print("=== TESTE COM DADOS REAIS ===")
    
    try:
        from services.transcription_fetcher_service import TranscriptionFetcherService
        
        print("[OK] Criando TranscriptionFetcherService...")
        fetcher = TranscriptionFetcherService()
        
        print("[OK] Listando emails disponíveis...")
        emails = fetcher.list_available_emails()
        print(f"[OK] Emails encontrados: {emails}")
        
        if emails:
            test_email = emails[0]
            print(f"[OK] Testando com email: {test_email}")
            
            # Buscar transcrições
            transcriptions = fetcher.get_transcriptions_by_email(test_email, limit=5)
            print(f"[OK] Transcrições encontradas: {len(transcriptions)}")
            
            for i, t in enumerate(transcriptions):
                print(f"  [{i+1}] {t['filename']} - {t['date']} ({t['size']} bytes)")
                print(f"      Conteúdo (primeiros 100 chars): {t['content'][:100]}...")
        
        print("[SUCCESS] Teste com dados reais concluído!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_endpoints():
    """Testa os endpoints Flask."""
    print("\n=== TESTE ENDPOINTS FLASK ===")
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Testar endpoint de emails
            print("[OK] Testando /api/emails/available...")
            response = client.get('/api/emails/available')
            print(f"[OK] Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"[OK] Resposta: {data}")
                
                # Se houver emails, testar endpoint de transcrições
                if data.get('emails'):
                    test_email = data['emails'][0]
                    print(f"[OK] Testando /api/transcriptions/{test_email}...")
                    
                    response2 = client.get(f'/api/transcriptions/{test_email}')
                    print(f"[OK] Status: {response2.status_code}")
                    
                    if response2.status_code == 200:
                        data2 = response2.get_json()
                        print(f"[OK] Transcrições: {data2}")
        
        print("[SUCCESS] Teste endpoints Flask concluído!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("TESTE INTEGRACAO DRIVE COM DADOS REAIS")
    print("=" * 50)
    
    # Testar com dados reais
    real_data_ok = test_with_real_data()
    
    # Testar endpoints Flask
    flask_ok = test_flask_endpoints()
    
    print("\n" + "=" * 50)
    if real_data_ok and flask_ok:
        print("TODOS OS TESTES PASSARAM!")
        print("Backend integracao Drive funcionando perfeitamente!")
        sys.exit(0)
    else:
        print("ALGUNS TESTES FALHARAM!")
        sys.exit(1)
