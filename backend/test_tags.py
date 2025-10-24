#!/usr/bin/env python
"""
Teste do Sistema de Tags - Nossa Grana
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
from transactions.models import Tag, Transaction, Category
from datetime import date

def test_tags_system():
    """Testar sistema de tags"""
    print("TESTANDO SISTEMA DE TAGS")
    print("=" * 40)
    
    client = APIClient()
    
    # Criar usuário
    user, created = User.objects.get_or_create(
        username='test_tags_user',
        defaults={'email': 'tags@test.com'}
    )
    client.force_authenticate(user=user)
    
    # Teste 1: Criar tag simples
    print("Teste 1: Criando tag simples...")
    tag_data = {
        'name': 'Teste',
        'color': '#007bff',
        'description': 'Tag de teste'
    }
    response = client.post('/api/transactions/tags/', tag_data)
    assert response.status_code == 201, f"Erro ao criar tag: {response.status_code}"
    tag_id = response.json()['id']
    print("OK - Tag criada")
    
    # Teste 2: Listar tags
    print("Teste 2: Listando tags...")
    response = client.get('/api/transactions/tags/')
    assert response.status_code == 200, f"Erro ao listar tags: {response.status_code}"
    tags_data = response.json()
    assert 'results' in tags_data, "Resposta deve conter 'results'"
    assert len(tags_data['results']) > 0, "Deve haver tags listadas"
    print("OK - Tags listadas")
    
    # Teste 3: Criar tag personalizada
    print("Teste 3: Criando tag personalizada...")
    tag_data = {
        'name': 'Viagem',
        'color': '#ff6b6b',
        'description': 'Gastos relacionados a viagens'
    }
    response = client.post('/api/transactions/tags/', tag_data)
    assert response.status_code == 201, f"Erro ao criar tag: {response.status_code}"
    custom_tag_id = response.json()['id']
    print("OK - Tag personalizada criada")
    
    # Teste 4: Buscar sugestões de tags
    print("Teste 4: Testando sugestões...")
    response = client.get('/api/transactions/tags/suggestions/?q=via')
    assert response.status_code == 200, f"Erro nas sugestões: {response.status_code}"
    suggestions = response.json()
    assert len(suggestions) > 0, "Deve haver sugestões"
    print("OK - Sugestões funcionando")
    
    # Teste 5: Obter resumo de tags
    print("Teste 5: Obtendo resumo...")
    response = client.get('/api/transactions/tags/summary/')
    assert response.status_code == 200, f"Erro no resumo: {response.status_code}"
    summary = response.json()
    assert summary['total_tags'] > 0, "Deve haver tags no resumo"
    print("OK - Resumo obtido")
    
    # Teste 6: Tags populares
    print("Teste 6: Testando tags populares...")
    response = client.get('/api/transactions/tags/popular/?limit=5')
    assert response.status_code == 200, f"Erro nas tags populares: {response.status_code}"
    popular = response.json()
    assert isinstance(popular, list), "Deve retornar uma lista"
    print("OK - Tags populares funcionando")
    
    # Limpar dados
    Tag.objects.filter(user=user).delete()
    user.delete()
    
    print("=" * 40)
    print("TODOS OS TESTES DE TAGS PASSARAM!")
    return True

if __name__ == '__main__':
    try:
        success = test_tags_system()
        if success:
            print("Sistema de tags funcionando!")
            exit(0)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        exit(1)