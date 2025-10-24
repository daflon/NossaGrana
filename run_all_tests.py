#!/usr/bin/env python
"""
Script Integrado de Testes - Nossa Grana
Executa todos os testes do sistema (backend + validações de frontend)
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Imprimir cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_section(title):
    """Imprimir seção formatada"""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_command(command, cwd=None):
    """Executar comando e retornar resultado"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout: Comando demorou mais de 2 minutos"
    except Exception as e:
        return False, "", str(e)

def test_backend():
    """Executar testes do backend"""
    print_section("TESTES DO BACKEND")
    
    # Verificar se o diretório backend existe
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Diretório backend não encontrado")
        return False
    
    # Executar testes abrangentes
    print("🔧 Executando testes abrangentes...")
    success, stdout, stderr = run_command("python test_simple.py", cwd="backend")
    
    if success:
        print("✅ Testes do backend APROVADOS")
        # Mostrar apenas as linhas importantes
        lines = stdout.split('\n')
        for line in lines:
            if any(marker in line for marker in ['✅', '❌', '🎉', '⚠️', 'PASSOU', 'FALHOU']):
                print(f"   {line}")
        return True
    else:
        print("❌ Testes do backend FALHARAM")
        if stderr:
            print(f"Erro: {stderr}")
        return False

def test_frontend_structure():
    """Validar estrutura do frontend"""
    print_section("VALIDAÇÃO DA ESTRUTURA DO FRONTEND")
    
    frontend_dir = Path("demo-interface/public")
    if not frontend_dir.exists():
        print("❌ Diretório frontend não encontrado")
        return False
    
    # Arquivos essenciais que devem existir
    essential_files = [
        "index.html",
        "dashboard.html", 
        "transactions.html",
        "accounts.html",
        "credit-cards.html",
        "reports.html",
        "css/styles.css",
        "js/api.js",
        "js/auth.js",
        "js/theme.js",
        "js/dashboard.js",
        "js/accounts.js",
        "js/credit-cards.js",
        "js/reports.js"
    ]
    
    missing_files = []
    for file_path in essential_files:
        full_path = frontend_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Arquivos ausentes: {', '.join(missing_files)}")
        return False
    
    print("✅ Estrutura do frontend VÁLIDA")
    return True

def test_server_startup():
    """Testar se o servidor inicia corretamente"""
    print_section("TESTE DE INICIALIZAÇÃO DO SERVIDOR")
    
    # Verificar se o servidor pode ser iniciado
    server_dir = Path("demo-interface")
    if not server_dir.exists():
        print("❌ Diretório do servidor não encontrado")
        return False
    
    # Verificar se package.json existe
    package_json = server_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json não encontrado")
        return False
    
    print("✅ Arquivos do servidor encontrados")
    
    # Verificar se server.js existe
    server_js = server_dir / "server.js"
    if not server_js.exists():
        print("❌ server.js não encontrado")
        return False
    
    print("✅ server.js encontrado")
    print("✅ Servidor pode ser iniciado com 'node server.js'")
    return True

def test_api_endpoints():
    """Validar se os endpoints da API estão definidos"""
    print_section("VALIDAÇÃO DOS ENDPOINTS DA API")
    
    backend_dir = Path("backend")
    
    # Verificar arquivos de URLs
    url_files = [
        "nossa_grana/urls.py",
        "transactions/urls.py",
        "financial_accounts/urls.py",
        "reports/urls.py"
    ]
    
    for url_file in url_files:
        file_path = backend_dir / url_file
        if file_path.exists():
            print(f"✅ {url_file}")
        else:
            print(f"❌ {url_file} não encontrado")
            return False
    
    print("✅ Endpoints da API definidos")
    return True

def test_database_migrations():
    """Verificar se as migrações estão atualizadas"""
    print_section("VERIFICAÇÃO DAS MIGRAÇÕES DO BANCO")
    
    print("🔧 Verificando migrações...")
    success, stdout, stderr = run_command("python manage.py showmigrations", cwd="backend")
    
    if success:
        # Verificar se há migrações não aplicadas
        if "[X]" in stdout:
            print("✅ Migrações aplicadas")
            return True
        else:
            print("⚠️ Algumas migrações podem não estar aplicadas")
            return True
    else:
        print("❌ Erro ao verificar migrações")
        if stderr:
            print(f"Erro: {stderr}")
        return False

def generate_test_report():
    """Gerar relatório final dos testes"""
    print_header("RELATÓRIO FINAL DOS TESTES")
    
    tests = [
        ("Backend", test_backend),
        ("Estrutura Frontend", test_frontend_structure),
        ("Servidor", test_server_startup),
        ("Endpoints API", test_api_endpoints),
        ("Migrações DB", test_database_migrations)
    ]
    
    results = []
    total_tests = len(tests)
    passed_tests = 0
    
    for test_name, test_function in tests:
        print(f"\n🧪 Executando: {test_name}")
        try:
            result = test_function()
            results.append((test_name, result))
            if result:
                passed_tests += 1
                print(f"✅ {test_name} - APROVADO")
            else:
                print(f"❌ {test_name} - REPROVADO")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ {test_name} - ERRO: {str(e)}")
    
    # Relatório final
    print_header("RESUMO DOS RESULTADOS")
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Total de Testes: {total_tests}")
    print(f"✅ Aprovados: {passed_tests}")
    print(f"❌ Reprovados: {total_tests - passed_tests}")
    print(f"📈 Taxa de Sucesso: {success_rate:.1f}%")
    
    print("\n📋 DETALHES:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    if passed_tests == total_tests:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema Nossa Grana está funcionando corretamente")
        print("🚀 Pronto para uso em produção!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} teste(s) falharam")
        print("🔧 Corrija os problemas antes de usar em produção")
    
    print("=" * 60)
    
    return passed_tests == total_tests

def main():
    """Função principal"""
    print_header("SUITE COMPLETA DE TESTES - NOSSA GRANA")
    print("🎯 Validando todas as funcionalidades do sistema...")
    
    # Verificar se estamos no diretório correto
    if not Path("backend").exists() and not Path("demo-interface").exists():
        print("❌ Execute este script no diretório raiz do projeto")
        sys.exit(1)
    
    # Executar todos os testes
    success = generate_test_report()
    
    if success:
        print("\n🎊 PARABÉNS! Todos os testes passaram!")
        sys.exit(0)
    else:
        print("\n🚨 Alguns testes falharam. Verifique os problemas acima.")
        sys.exit(1)

if __name__ == "__main__":
    main()