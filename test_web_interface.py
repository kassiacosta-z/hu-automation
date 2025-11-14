#!/usr/bin/env python3
"""
Script para testar a nova interface web com busca por email.
Testa os endpoints e a funcionalidade da interface.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# URL base do Flask app
FLASK_BASE_URL = f"http://{os.getenv('FLASK_HOST', '127.0.0.1')}:{os.getenv('FLASK_PORT', '5000')}"

def test_web_interface():
    """Testa a interface web completa."""
    print("=== TESTE INTERFACE WEB ===")
    
    try:
        # Testar página principal
        print(f"[OK] Testando página principal: {FLASK_BASE_URL}")
        response = requests.get(FLASK_BASE_URL)
        print(f"[OK] Status: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Verificar se contém elementos da nova interface
            checks = [
                ('Abas', 'Buscar por Email' in html_content and 'Upload Manual' in html_content),
                ('Campo de busca', 'emailInput' in html_content),
                ('Autocomplete', 'autocompleteDropdown' in html_content),
                ('Botão buscar', 'searchTranscriptions' in html_content),
                ('Lista de transcrições', 'transcriptionsList' in html_content),
                ('JavaScript', 'loadAvailableEmails' in html_content),
                ('CSS das abas', 'tab-content' in html_content),
                ('CSS do autocomplete', 'autocomplete-dropdown' in html_content)
            ]
            
            print("\n[OK] Verificando elementos da interface:")
            all_checks_passed = True
            for check_name, check_result in checks:
                status = "OK" if check_result else "FALHOU"
                print(f"  {status} {check_name}")
                if not check_result:
                    all_checks_passed = False
            
            if all_checks_passed:
                print("\n[SUCCESS] Interface web implementada corretamente!")
                return True
            else:
                print("\n[WARNING] Alguns elementos da interface podem estar faltando")
                return False
        else:
            print(f"[ERROR] Erro ao acessar página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erro ao testar interface: {e}")
        return False

def test_api_endpoints():
    """Testa os endpoints da API."""
    print("\n=== TESTE ENDPOINTS API ===")
    
    try:
        # Testar endpoint de emails disponíveis
        print(f"[OK] Testando {FLASK_BASE_URL}/api/emails/available...")
        response = requests.get(f"{FLASK_BASE_URL}/api/emails/available")
        print(f"[OK] Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Resposta: {data}")
            
            if data['success']:
                print(f"[OK] {data['count']} emails disponíveis")
                
                # Se houver emails, testar outros endpoints
                if data['emails']:
                    test_email = data['emails'][0]
                    print(f"[OK] Testando com email: {test_email}")
                    
                    # Testar endpoint de transcrições
                    response2 = requests.get(f"{FLASK_BASE_URL}/api/transcriptions/{test_email}")
                    print(f"[OK] Status transcrições: {response2.status_code}")
                    
                    if response2.status_code == 200:
                        data2 = response2.json()
                        print(f"[OK] Transcrições encontradas: {data2['count']}")
                        
                        # Testar endpoint de última transcrição
                        response3 = requests.get(f"{FLASK_BASE_URL}/api/transcriptions/{test_email}/latest")
                        print(f"[OK] Status última transcrição: {response3.status_code}")
                        
                        if response3.status_code == 200:
                            data3 = response3.json()
                            print(f"[OK] Última transcrição: {data3['transcription']['filename']}")
                else:
                    print("[INFO] Nenhum email disponível para testar endpoints de transcrições")
                
                print("[SUCCESS] Endpoints API funcionando corretamente!")
                return True
            else:
                print(f"[ERROR] API retornou erro: {data}")
                return False
        else:
            print(f"[ERROR] Erro HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erro ao testar endpoints: {e}")
        return False

def test_responsive_design():
    """Testa se a interface é responsiva."""
    print("\n=== TESTE DESIGN RESPONSIVO ===")
    
    try:
        response = requests.get(FLASK_BASE_URL)
        html_content = response.text
        
        # Verificar elementos responsivos
        responsive_checks = [
            ('Media queries', '@media' in html_content),
            ('Flexbox', 'display: flex' in html_content),
            ('Grid', 'grid-template-columns' in html_content),
            ('Viewport meta', 'viewport' in html_content),
            ('Mobile styles', 'max-width: 768px' in html_content)
        ]
        
        print("[OK] Verificando elementos responsivos:")
        responsive_passed = True
        for check_name, check_result in responsive_checks:
            status = "OK" if check_result else "FALHOU"
            print(f"  {status} {check_name}")
            if not check_result:
                responsive_passed = False
        
        if responsive_passed:
            print("[SUCCESS] Interface responsiva implementada!")
            return True
        else:
            print("[WARNING] Alguns elementos responsivos podem estar faltando")
            return False
            
    except Exception as e:
        print(f"[ERROR] Erro ao testar responsividade: {e}")
        return False

def main():
    """Função principal de teste."""
    print("TESTE INTERFACE WEB - FASE 2")
    print("=" * 50)
    
    # Testar interface web
    interface_ok = test_web_interface()
    
    # Testar endpoints API
    api_ok = test_api_endpoints()
    
    # Testar design responsivo
    responsive_ok = test_responsive_design()
    
    print("\n" + "=" * 50)
    print("RESULTADO DOS TESTES:")
    print(f"Interface Web: {'PASSOU' if interface_ok else 'FALHOU'}")
    print(f"Endpoints API: {'PASSOU' if api_ok else 'FALHOU'}")
    print(f"Design Responsivo: {'PASSOU' if responsive_ok else 'FALHOU'}")
    
    if interface_ok and api_ok and responsive_ok:
        print("\nTODOS OS TESTES PASSARAM!")
        print("Fase 2 - Frontend implementada com sucesso!")
        print("Interface com 2 abas funcionando!")
        print("Busca por email implementada!")
        print("Upload manual mantido!")
        print("Design responsivo!")
        print("\nPronto para Fase 3 - Processamento Automático!")
        return True
    else:
        print("\nALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima e corrija antes de prosseguir.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
