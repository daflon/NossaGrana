#!/usr/bin/env python
"""
Teste da API de Metas - Nossa Grana
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nossa_grana.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from goals.models import Goal, GoalContribution
from datetime import date, timedelta

def test_goals_api():
    """Testar API de metas"""
    print("TESTANDO API DE METAS")
    print("=" * 40)
    
    client = APIClient()
    
    # Criar usuário
    user, created = User.objects.get_or_create(
        username='test_goals',
        defaults={'email': 'goals@test.com'}
    )
    client.force_authenticate(user=user)
    
    # Teste 1: Criar meta
    print("Teste 1: Criando meta...")
    goal_data = {
        'name': 'Viagem para Europa',
        'description': 'Economizar para viagem dos sonhos',
        'target_amount': '15000.00',
        'target_date': (date.today() + timedelta(days=365)).isoformat()
    }
    response = client.post('/api/goals/goals/', goal_data)
    assert response.status_code == 201, f"Erro ao criar meta: {response.status_code}"
    goal_id = response.json()['id']
    print("OK - Meta criada")
    
    # Teste 2: Listar metas
    print("Teste 2: Listando metas...")
    response = client.get('/api/goals/goals/')
    assert response.status_code == 200, f"Erro ao listar metas: {response.status_code}"
    goals_data = response.json()
    assert 'results' in goals_data, "Resposta deve conter 'results'"
    assert len(goals_data['results']) > 0, "Deve haver metas listadas"
    print("OK - Metas listadas")
    
    # Teste 3: Contribuir para meta
    print("Teste 3: Contribuindo para meta...")
    contribution_data = {
        'amount': '1000.00',
        'description': 'Primeira contribuição',
        'date': date.today().isoformat()
    }
    response = client.post(f'/api/goals/goals/{goal_id}/contribute/', contribution_data)
    assert response.status_code == 201, f"Erro ao contribuir: {response.status_code}"
    print("OK - Contribuição adicionada")
    
    # Teste 4: Verificar progresso
    print("Teste 4: Verificando progresso...")
    response = client.get(f'/api/goals/goals/{goal_id}/')
    goal_data = response.json()
    assert float(goal_data['current_amount']) == 1000.00, "Valor atual incorreto"
    assert goal_data['percentage_completed'] > 0, "Porcentagem deve ser maior que 0"
    print(f"OK - Progresso: {goal_data['percentage_completed']:.1f}%")
    
    # Teste 5: Resumo de metas
    print("Teste 5: Obtendo resumo...")
    response = client.get('/api/goals/goals/summary/')
    assert response.status_code == 200, f"Erro ao obter resumo: {response.status_code}"
    summary = response.json()
    assert summary['total_goals'] > 0, "Deve haver metas no resumo"
    print("OK - Resumo obtido")
    
    # Teste 6: Contribuir até atingir meta
    print("Teste 6: Atingindo meta...")
    final_contribution = {
        'amount': '14000.00',  # Completar a meta
        'description': 'Contribuição final'
    }
    response = client.post(f'/api/goals/goals/{goal_id}/contribute/', final_contribution)
    assert response.status_code == 201, f"Erro na contribuição final: {response.status_code}"
    result = response.json()
    assert result['goal_achieved'] == True, "Meta deveria estar atingida"
    print("OK - Meta atingida!")
    
    # Limpar dados
    Goal.objects.filter(user=user).delete()
    user.delete()
    
    print("=" * 40)
    print("TODOS OS TESTES DE METAS PASSARAM!")
    return True

if __name__ == '__main__':
    try:
        success = test_goals_api()
        if success:
            print("API de metas funcionando!")
            exit(0)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)