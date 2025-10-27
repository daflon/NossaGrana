#!/usr/bin/env python3
"""
Script para testar o sistema completo Nossa Grana
"""
import os
import sys
import subprocess
import requests
import time
import json
from pathlib import Path

def test_backend():
    """Testa se o backend está funcionando"""
    print("[TESTE] Testando Backend...")
    
    try:
        # Testa se o servidor está rodando
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("[OK] Backend está rodando")
            data = response.json()
            print(f"   API: {data.get('message', 'N/A')}")
            print(f"   Versão: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"[ERRO] Backend retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERRO] Backend não está rodando (porta 8000)")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao testar backend: {e}")
        return False

def test_frontend():
    """Testa se o frontend está funcionando"""
    print("[TESTE] Testando Frontend...")
    
    try:
        # Testa se o servidor está rodando
        response = requests.get('http://localhost:3000/', timeout=5)
        if response.status_code == 200:
            print("[OK] Frontend está rodando")
            return True
        else:
            print(f"[ERRO] Frontend retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERRO] Frontend não está rodando (porta 3000)")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao testar frontend: {e}")
        return False

def check_database():
    """Verifica se o banco de dados existe"""
    print("[TESTE] Verificando Banco de Dados...")
    
    db_path = Path("backend/db.sqlite3")
    if db_path.exists():
        print("[OK] Banco de dados SQLite encontrado")
        return True
    else:
        print("[ERRO] Banco de dados não encontrado")
        return False

def check_dependencies():
    """Verifica dependências"""
    print("[TESTE] Verificando Dependências...")
    
    # Backend
    backend_deps = Path("backend/requirements.txt")
    if backend_deps.exists():
        print("[OK] Requirements.txt do backend encontrado")
    else:
        print("[ERRO] Requirements.txt do backend não encontrado")
    
    # Frontend
    frontend_deps = Path("frontend/package.json")
    if frontend_deps.exists():
        print("[OK] Package.json do frontend encontrado")
    else:
        print("[ERRO] Package.json do frontend não encontrado")

def test_api_endpoints():
    """Testa endpoints principais da API"""
    print("[TESTE] Testando Endpoints da API...")
    
    endpoints = [
        '/api/transactions/',
        '/api/budgets/',
        '/api/goals/',
        '/api/reports/',
        '/api/financial/'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
            if response.status_code in [200, 401]:  # 401 é esperado sem autenticação
                print(f"[OK] {endpoint}")
            else:
                print(f"[ERRO] {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"[ERRO] {endpoint} - Erro: {e}")

def main():
    """Função principal"""
    print("=" * 50)
    print("TESTE DO SISTEMA NOSSA GRANA")
    print("=" * 50)
    
    # Verificações básicas
    check_dependencies()
    print()
    
    check_database()
    print()
    
    # Testes de serviços
    backend_ok = test_backend()
    print()
    
    frontend_ok = test_frontend()
    print()
    
    # Testes de API (só se backend estiver rodando)
    if backend_ok:
        test_api_endpoints()
        print()
    
    # Resumo
    print("=" * 50)
    print("RESUMO DOS TESTES")
    print("=" * 50)
    
    if backend_ok and frontend_ok:
        print("[SUCESSO] Sistema está funcionando!")
        print("   - Backend: [OK] http://localhost:8000")
        print("   - Frontend: [OK] http://localhost:3000")
    elif backend_ok:
        print("[AVISO] Backend funcionando, Frontend com problemas")
        print("   - Backend: [OK] http://localhost:8000")
        print("   - Frontend: [ERRO] http://localhost:3000")
    elif frontend_ok:
        print("[AVISO] Frontend funcionando, Backend com problemas")
        print("   - Backend: [ERRO] http://localhost:8000")
        print("   - Frontend: [OK] http://localhost:3000")
    else:
        print("[ERRO] Sistema não está funcionando")
        print("   - Backend: [ERRO] http://localhost:8000")
        print("   - Frontend: [ERRO] http://localhost:3000")
    
    print("\n[INFO] Para iniciar os serviços:")
    print("   Backend:  cd backend && python manage.py runserver")
    print("   Frontend: cd frontend && npm start")

if __name__ == "__main__":
    main()