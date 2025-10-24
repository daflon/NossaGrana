#!/usr/bin/env python
"""
Teste do sistema de recomendações de metas - Nossa Grana
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

def test_recommendations():
    """Testar sistema de recomendações"""
    print("TESTANDO SISTEMA DE RECOMENDAÇÕES")
    print("=" * 40)
    
    client = APIClient()
    
    # Criar usuário
    user, created = User.objects.get_or_create(
        username='test_recommendations',
        defaults={'email': 'rec@test.com'}
    )
    
    # Limpar metas existentes
    Goal.objects.filter(user=user).delete()
    
    client.force_authenticate(user=user)
    
    # Teste 1: Meta com bom progresso
    print("Teste 1: Meta com bom progresso...")
    good_goal_data = {
        'name': 'Meta Boa',
        'target_amount': '5000.00',
        'target_date': (date.today() + timedelta(days=180)).isoformat()
    }
    response = client.post('/api/goals/goals/', good_goal_data)
    good_goal_id = response.json()['id']
    
    # Adicionar contribuições boas
    for i in range(5):
        response = client.post(f'/api/goals/goals/{good_goal_id}/contribute/', {
            'amount': '500.00',
            'description': f'Contribuição {i+1}',
            'date': (date.today() - timedelta(days=i*7)).isoformat()
        })
    
    # Obter recomendações
    response = client.get(f'/api/goals/goals/{good_goal_id}/recommendations/')
    assert response.status_code == 200
    
    recommendations = response.json()
    print(f"Status: {recommendations['current_status']}")
    print(f"Número de recomendações: {len(recommendations['recommendations'])}")
    
    for rec in recommendations['recommendations']:
        print(f"- {rec['type']}: {rec['title']}")
        print(f"  {rec['message']}")
    
    assert len(recommendations['recommendations']) > 0
    print("OK - Recomendações para meta boa geradas")
    
    # Teste 2: Meta atrasada
    print("\nTeste 2: Meta atrasada...")
    urgent_goal_data = {
        'name': 'Meta Urgente',
        'target_amount': '10000.00',
        'target_date': (date.today() + timedelta(days=30)).isoformat()
    }
    response = client.post('/api/goals/goals/', urgent_goal_data)
    urgent_goal_id = response.json()['id']
    
    # Contribuição pequena
    response = client.post(f'/api/goals/goals/{urgent_goal_id}/contribute/', {
        'amount': '200.00',
        'description': 'Contribuição pequena'
    })
    
    response = client.get(f'/api/goals/goals/{urgent_goal_id}/recommendations/')
    urgent_recs = response.json()
    
    print(f"Status: {urgent_recs['current_status']}")
    print("Recomendações urgentes:")
    
    urgent_found = False
    for rec in urgent_recs['recommendations']:
        print(f"- {rec['type']}: {rec['title']}")
        if rec['type'] == 'urgent':
            urgent_found = True
    
    assert urgent_found, "Deveria haver recomendações urgentes"
    print("OK - Recomendações urgentes geradas")
    
    # Teste 3: Meta quase completa
    print("\nTeste 3: Meta quase completa...")
    almost_goal_data = {
        'name': 'Meta Quase Pronta',
        'target_amount': '1000.00',
        'target_date': (date.today() + timedelta(days=90)).isoformat()
    }
    response = client.post('/api/goals/goals/', almost_goal_data)
    almost_goal_id = response.json()['id']
    
    # Contribuir 85% da meta
    response = client.post(f'/api/goals/goals/{almost_goal_id}/contribute/', {
        'amount': '850.00',
        'description': 'Quase lá!'
    })
    
    response = client.get(f'/api/goals/goals/{almost_goal_id}/recommendations/')
    almost_recs = response.json()
    
    print(f"Progresso: {almost_recs['quick_stats']['percentage_completed']:.1f}%")
    
    almost_complete_found = False
    for rec in almost_recs['recommendations']:
        print(f"- {rec['type']}: {rec['title']}")
        if 'Quase' in rec['title']:
            almost_complete_found = True
    
    assert almost_complete_found, "Deveria haver recomendação de quase completa"
    print("OK - Recomendações para meta quase completa geradas")
    
    # Limpar dados
    Goal.objects.filter(user=user).delete()
    user.delete()
    
    print("\n" + "=" * 40)
    print("TODOS OS TESTES DE RECOMENDAÇÕES PASSARAM!")
    return True

if __name__ == '__main__':
    try:
        success = test_recommendations()
        if success:
            print("Sistema de recomendações funcionando!")
            exit(0)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)