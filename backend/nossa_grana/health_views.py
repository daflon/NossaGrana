"""
Health Check Views para Nossa Grana
Endpoints para verificar status da aplicação
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from datetime import datetime
import redis

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint básico de health check
    Retorna status geral da aplicação
    """
    try:
        # Teste básico do banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'service': 'nossa-grana-api'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }, status=503)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_detailed(request):
    """
    Health check detalhado
    Verifica todos os componentes
    """
    results = {}
    overall_healthy = True
    
    # Verificar banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            migration_count = cursor.fetchone()[0]
        results['database'] = {
            'status': 'healthy',
            'migrations': migration_count
        }
    except Exception as e:
        results['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_healthy = False
    
    # Verificar cache
    try:
        test_key = 'health_check_cache_test'
        cache.set(test_key, 'test_value', 10)
        cached_value = cache.get(test_key)
        cache.delete(test_key)
        
        results['cache'] = {
            'status': 'healthy' if cached_value == 'test_value' else 'unhealthy'
        }
        if cached_value != 'test_value':
            overall_healthy = False
    except Exception as e:
        results['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_healthy = False
    
    # Verificar Redis (se configurado)
    try:
        redis_url = getattr(settings, 'REDIS_URL', None)
        if redis_url:
            r = redis.from_url(redis_url)
            r.ping()
            results['redis'] = {'status': 'healthy'}
        else:
            results['redis'] = {'status': 'not_configured'}
    except Exception as e:
        results['redis'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        overall_healthy = False
    
    # Verificar configurações críticas
    critical_settings = ['SECRET_KEY', 'DEBUG']
    settings_status = {}
    for setting in critical_settings:
        if hasattr(settings, setting):
            if setting == 'SECRET_KEY':
                settings_status[setting] = 'configured' if getattr(settings, setting) != 'django-insecure-change-me-in-production' else 'default'
            else:
                settings_status[setting] = getattr(settings, setting)
        else:
            settings_status[setting] = 'not_set'
            overall_healthy = False
    
    results['settings'] = settings_status
    
    response_data = {
        'status': 'healthy' if overall_healthy else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'service': 'nossa-grana-api',
        'components': results
    }
    
    status_code = 200 if overall_healthy else 503
    return JsonResponse(response_data, status=status_code)

@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check para Kubernetes/Docker
    Verifica se a aplicação está pronta para receber tráfego
    """
    try:
        # Verificar se consegue conectar no banco
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Verificar se as migrações foram aplicadas
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            return JsonResponse({
                'status': 'not_ready',
                'reason': 'pending_migrations',
                'pending_migrations': len(plan)
            }, status=503)
        
        return JsonResponse({
            'status': 'ready',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=503)

@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check para Kubernetes/Docker
    Verifica se a aplicação está viva (não travada)
    """
    return JsonResponse({
        'status': 'alive',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'unknown'  # Poderia calcular uptime se necessário
    })