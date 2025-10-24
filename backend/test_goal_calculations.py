#!/usr/bin/env python
"""
Teste detalhado dos cálculos de progresso de metas - Nossa Grana
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

def test_goal_calculations():
    """Testar cálculos avançados de metas"""
    print("TESTANDO CÁLCULOS DE PROGRESSO DE METAS")
    print("=" * 50)
    
    client = APIClient()
    
    # Criar usuário
    user, created = User.objects.get_or_create(
        username='test_calculations',
        defaults={'email': 'calc@test.com'}
    )
    
    # Limpar metas existentes
    Goal.objects.filter(user=user).delete()
    
    client.force_authenticate(user=user)
    
    # Teste 1: Meta com progresso parcial
    print("Teste 1: Criando meta com progresso parcial...")
    goal_data = {
        'name': 'Carro Novo',
        'description': 'Economizar para carro',
        'target_amount': '50000.00',
        'target_date': (date.today() + timedelta(days=730)).isoformat()  # 2 anos
    }
    response = client.post('/api/goals/goals/', goal_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201, f"Erro ao criar meta: {response.status_code} - {response.json()}"
    goal_id = response.json()['id']
    
    # Adicionar algumas contribuições
    contributions = [
        {'amount': '5000.00', 'description': 'Salário mês 1'},
        {'amount': '3000.00', 'description': 'Freelance'},
        {'amount': '2000.00', 'description': 'Salário mês 2'},
    ]
    
    for contrib in contributions:
        response = client.post(f'/api/goals/goals/{goal_id}/contribute/', contrib)
        assert response.status_code == 201
    
    # Verificar cálculos
    response = client.get(f'/api/goals/goals/{goal_id}/')
    goal_data = response.json()
    
    print(f"Valor alvo: R$ {goal_data['target_amount_formatted']}")
    print(f"Valor atual: R$ {goal_data['current_amount_formatted']}")
    print(f"Valor restante: R$ {goal_data['remaining_amount_formatted']}")
    print(f"Progresso: {goal_data['percentage_completed']:.1f}%")
    print(f"Dias restantes: {goal_data['days_remaining']}")
    print(f"Data estimada de conclusão: {goal_data['estimated_completion_date']}")
    print(f"Meta atrasada: {goal_data['is_overdue']}")
    
    # Validar cálculos
    assert float(goal_data['current_amount']) == 10000.00, "Valor atual incorreto"
    assert goal_data['percentage_completed'] == 20.0, "Porcentagem incorreta"
    assert float(goal_data['remaining_amount']) == 40000.00, "Valor restante incorreto"
    
    print("OK - Cálculos básicos corretos")
    
    # Teste 2: Meta próxima do vencimento
    print("\nTeste 2: Meta próxima do vencimento...")
    urgent_goal_data = {
        'name': 'Viagem Urgente',
        'target_amount': '5000.00',
        'target_date': (date.today() + timedelta(days=15)).isoformat()  # 15 dias
    }
    response = client.post('/api/goals/goals/', urgent_goal_data)
    urgent_goal_id = response.json()['id']
    
    # Contribuir parcialmente
    response = client.post(f'/api/goals/goals/{urgent_goal_id}/contribute/', {
        'amount': '1000.00',
        'description': 'Contribuição inicial'
    })
    
    response = client.get(f'/api/goals/goals/{urgent_goal_id}/')
    urgent_data = response.json()
    
    print(f"Dias restantes: {urgent_data['days_remaining']}")
    print(f"Meta atrasada: {urgent_data['is_overdue']}")
    
    assert urgent_data['days_remaining'] <= 15, "Dias restantes incorretos"
    assert not urgent_data['is_overdue'], "Meta não deveria estar atrasada ainda"
    
    print("OK - Cálculos de prazo corretos")
    
    # Teste 3: Meta atrasada
    print("\nTeste 3: Meta atrasada...")
    
    # Criar meta com data futura primeiro, depois alterar para passada
    overdue_goal = Goal(
        user=user,
        name='Meta Atrasada',
        target_amount=Decimal('1000.00'),
        target_date=date.today() + timedelta(days=30)  # Criar com data futura
    )
    overdue_goal.save()
    
    # Agora alterar para data passada diretamente no banco
    Goal.objects.filter(id=overdue_goal.id).update(
        target_date=date.today() - timedelta(days=30)
    )
    overdue_goal.refresh_from_db()
    
    response = client.get(f'/api/goals/goals/{overdue_goal.id}/')
    overdue_data = response.json()
    
    print(f"Dias restantes: {overdue_data['days_remaining']}")
    print(f"Meta atrasada: {overdue_data['is_overdue']}")
    
    assert overdue_data['days_remaining'] == 0, "Dias restantes deveria ser 0"
    assert overdue_data['is_overdue'], "Meta deveria estar atrasada"
    
    print("OK - Detecção de atraso correta")
    
    # Teste 4: Resumo geral
    print("\nTeste 4: Resumo geral...")
    response = client.get('/api/goals/goals/summary/')
    summary = response.json()
    
    print(f"Total de metas: {summary['total_goals']}")
    print(f"Metas atingidas: {summary['achieved_goals']}")
    print(f"Metas ativas: {summary['active_goals']}")
    print(f"Metas atrasadas: {summary['overdue_goals']}")
    print(f"Valor total alvo: R$ {summary['total_target_amount']}")
    print(f"Valor total atual: R$ {summary['total_current_amount']}")
    print(f"Porcentagem média: {summary['average_completion_percentage']}%")
    print(f"Metas próximas do prazo: {summary['goals_near_deadline']}")
    
    assert summary['total_goals'] >= 3, "Deveria haver pelo menos 3 metas"
    assert summary['overdue_goals'] >= 1, "Deveria haver pelo menos 1 meta atrasada"
    
    print("OK - Resumo correto")
    
    # Teste 5: Estatísticas detalhadas
    print("\nTeste 5: Estatísticas detalhadas...")
    response = client.get('/api/goals/goals/statistics/')
    stats = response.json()
    
    print(f"Total de contribuições: {stats['total_contributions']}")
    print(f"Valor total contribuído: R$ {stats['total_contributed_amount']}")
    print(f"Distribuição por valor: {stats['value_distribution']}")
    
    assert stats['total_contributions'] > 0, "Deveria haver contribuições"
    assert float(stats['total_contributed_amount']) > 0, "Valor contribuído deveria ser > 0"
    
    print("OK - Estatísticas corretas")
    
    # Limpar dados
    Goal.objects.filter(user=user).delete()
    user.delete()
    
    print("\n" + "=" * 50)
    print("TODOS OS TESTES DE CÁLCULOS PASSARAM!")
    return True

if __name__ == '__main__':
    try:
        success = test_goal_calculations()
        if success:
            print("Cálculos de metas funcionando perfeitamente!")
            exit(0)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)