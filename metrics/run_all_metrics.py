#!/usr/bin/env python3
# Script principal para executar todas as métricas de sucesso

import sys
import importlib.util

def run_metric(metric_file, metric_name):
    spec = importlib.util.spec_from_file_location("metric", metric_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if hasattr(module, 'check_coverage'):
        return module.check_coverage()
    elif hasattr(module, 'check_performance'):
        return module.check_performance()
    elif hasattr(module, 'check_security'):
        return module.check_security()
    elif hasattr(module, 'check_mobile_responsiveness'):
        return module.check_mobile_responsiveness()
    elif hasattr(module, 'test_main_actions'):
        return module.test_main_actions()

def main():
    print("📊 MÉTRICAS DE SUCESSO - NOSSA GRANA")
    print("=" * 40)
    
    metrics = [
        ("coverage_config.py", "Cobertura de Testes >80%"),
        ("performance_check.py", "Performance <2s"),
        ("security_scan.py", "Segurança 0 vulnerabilidades"),
        ("mobile_check.py", "Responsividade 100%"),
        ("usability_test.py", "Usabilidade <3 cliques")
    ]
    
    results = []
    
    for file, name in metrics:
        try:
            passed, value = run_metric(file, name)
            status = "✅ PASSOU" if passed else "❌ FALHOU"
            results.append((name, status, value))
            print(f"{name}: {status}")
        except Exception as e:
            results.append((name, "❌ ERRO", str(e)))
            print(f"{name}: ❌ ERRO - {e}")
    
    print("\n📈 RESUMO FINAL:")
    passed_count = sum(1 for _, status, _ in results if "PASSOU" in status)
    total_count = len(results)
    
    print(f"Métricas aprovadas: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("🎉 TODAS AS MÉTRICAS FORAM ATENDIDAS!")
        return 0
    else:
        print("⚠️  Algumas métricas precisam de atenção")
        return 1

if __name__ == "__main__":
    sys.exit(main())