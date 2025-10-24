#!/usr/bin/env python
"""
Teste dos cálculos avançados de progresso de metas - Nossa Grana
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from goals.models import Goal, GoalContribution
from django.utils import timezone

def test_advanced_calculations():
    """Testar cálculos avançados de metas"""
    print("TESTANDO CÁLCULOS AVANÇADOS DE METAS")
    print("=" * 50)
    
    client = APIClient()
    
    # Criar usuário
    user, created = User.objects.get_or_create(
        username='test_advanced',
        defaults={'email': 'advanced@test.com'}
    )
    
    # Limpar metas existentes
    Goal.objects.filter(user=user).delete()
    
    client.force_authenticate(user=user)
    
    # Teste 1: Criar meta e verificar novos campos
    print("Teste 1: Criando meta e verificando novos campos...")
    goal_data = {
        'name': 'Casa Própria',
        'description': 'Economizar para entrada da casa',
        'target_amount': '100000.00',
        'target_date': (date.today() + timedelta(days=1095)).isoformat()  # 3 anos
    }
    response = client.post('/api/goals/goals/', goal_data)
    assert response.status_code == 201
    goal_id = response.json()['id']
    
    # Verificar meta criada
    response = client.get(f'/api/goals/goals/{goal_id}/')
    goal_data = response.json()
    
    print(f"Meta alvo mensal: R$ {goal_data['monthly_target_amount']:.2f}")
    print(f"Meta alvo semanal: R$ {goal_data['weekly_target_amount']:.2f}")
    print(f"Meta alvo diária: R$ {goal_data['daily_target_amount']:.2f}")
    print(f"Análise de ritmo: {goal_data['current_pace_analysis']}")
    print(f"Tendência de contribuições: {goal_data['contribution_trend']}")
    
    # Validar novos campos
    assert 'monthly_target_amount' in goal_data
    assert 'weekly_target_amount' in goal_data
    assert 'daily_target_amount' in goal_data
    assert 'current_pace_analysis' in goal_data
    assert 'contribution_trend' in goal_data
    
    print("OK - Novos campos presentes")
    
    # Teste 2: Adicionar contribuições e verificar análise de ritmo
    print("\nTeste 2: Adicionando contribuições e verificando análise...")
    
    # Contribuições simulando um bom ritmo
    contributions = [
        {'amount': '3000.00', 'description': 'Salário mês 1', 'date': (date.today() - timedelta(days=25)).isoformat()},
        {'amount': '2500.00', 'description': 'Freelance', 'date': (date.today() - timedelta(days=20)).isoformat()},
        {'amount': '3200.00', 'description': 'Salário mês 2', 'date': (date.today() - timedelta(days=15)).isoformat()},
        {'amount': '1800.00', 'description': 'Bonus', 'date': (date.today() - timedelta(days=10)).isoformat()},
        {'amount': '2800.00', 'description': 'Salário mês 3', 'date': (date.today() - timedelta(days=5)).isoformat()},
    ]
    
    for contrib in contributions:
        response = client.post(f'/api/goals/goals/{goal_id}/contribute/', contrib)
        assert response.status_code == 201
    
    # Verificar análise atualizada
    response = client.get(f'/api/goals/goals/{goal_id}/')
    updated_goal = response.json()
    
    print(f"Valor atual: R$ {updated_goal['current_amount']}")
    print(f"Progresso: {updated_goal['percentage_completed']:.1f}%")
    print(f"Análise de ritmo atualizada: {updated_goal['current_pace_analysis']}")
    print(f"Data estimada de conclusão: {updated_goal['estimated_completion_date']}")
    
    pace_analysis = updated_goal['current_pace_analysis']
    assert pace_analysis['status'] in ['on_track', 'slightly_behind', 'behind', 'far_behind', 'no_data']
    assert 'pace_ratio' in pace_analysis
    
    print("OK - Análise de ritmo funcionando")
    
    # Teste 3: Análise detalhada de progresso
    print("\nTeste 3: Testando análise detalhada de progresso...")
    response = client.get(f'/api/goals/goals/{goal_id}/progress_analysis/')
    assert response.status_code == 200
    
    analysis = response.json()
    print(f"Análise de ritmo: {analysis['pace_analysis']['status']}")
    print(f"Tendência 30 dias: {analysis['trend_analysis']['30_days']['trend']}")
    print(f"Tendência 90 dias: {analysis['trend_analysis']['90_days']['trend']}")
    print(f"No ritmo certo: {analysis['is_on_track']}")
    
    assert 'pace_analysis' in analysis
    assert 'trend_analysis' in analysis
    assert 'projections' in analysis
    assert 'monthly_contribution_history' in analysis
    
    print("OK - Análise detalhada funcionando")
    
    # Teste 4: Dashboard de performance
    print("\nTeste 4: Testando dashboard de performance...")
    response = client.get('/api/goals/goals/performance_dashboard/')
    assert response.status_code == 200
    
    dashboard = response.json()
    print(f"Total de metas ativas: {dashboard['total_active_goals']}")
    print(f"Resumo de performance: {dashboard['performance_summary']}")
    print(f"Taxa média de conclusão: {dashboard['average_completion_rate']:.1f}%")
    
    assert 'total_active_goals' in dashboard
    assert 'performance_summary' in dashboard
    assert 'goals_performance' in dashboard
    
    print("OK - Dashboard de performance funcionando")
    
    # Teste 5: Criar meta com ritmo lento para testar alertas
    print("\nTeste 5: Testando meta com ritmo lento...")
    slow_goal_data = {
        'name': 'Viagem Rápida',
        'target_amount': '10000.00',
        'target_date': (date.today() + timedelta(days=60)).isoformat()  # 2 meses
    }
    response = client.post('/api/goals/goals/', slow_goal_data)
    slow_goal_id = response.json()['id']
    
    # Contribuição muito pequena
    response = client.post(f'/api/goals/goals/{slow_goal_id}/contribute/', {
        'amount': '100.00',
        'description': 'Contribuição pequena'
    })
    
    response = client.get(f'/api/goals/goals/{slow_goal_id}/')
    slow_goal = response.json()
    
    print(f"Meta diária necessária: R$ {slow_goal['daily_target_amount']:.2f}")
    print(f"Status do ritmo: {slow_goal['current_pace_analysis']['status']}")
    
    # Deve detectar que está muito atrás
    pace_status = slow_goal['current_pace_analysis']['status']
    assert pace_status in ['behind', 'far_behind', 'no_data']
    
    print("OK - Detecção de ritmo lento funcionando")
    
    # Limpar dados
    Goal.objects.filter(user=user).delete()
    user.delete()
    
    print("\n" + "=" * 50)
    print("TODOS OS TESTES DE CÁLCULOS AVANÇADOS PASSARAM!")
    return True

if __name__ == '__main__':
    try:
        success = test_advanced_calculations()
        if success:
            print("Cálculos avançados de metas funcionando perfeitamente!")
            exit(0)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)