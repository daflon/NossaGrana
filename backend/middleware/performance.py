from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.db import connection
import time
import json
import hashlib

class PerformanceMiddleware(MiddlewareMixin):
    """Middleware para otimização de performance"""
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.cache_timeout = 300  # 5 minutos
        self.cacheable_methods = ['GET']
        self.cacheable_paths = [
            '/api/transactions/',
            '/api/budgets/',
            '/api/goals/',
            '/api/reports/',
            '/api/accounts/'
        ]
    
    def process_request(self, request):
        # Marcar início da requisição
        request._start_time = time.time()
        
        # Cache para requisições GET
        if self._should_cache(request):
            cached_response = self._get_cached_response(request)
            if cached_response:
                return cached_response
        
        return None
    
    def process_response(self, request, response):
        # Calcular tempo de resposta
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        # Cache da resposta se aplicável
        if self._should_cache(request) and response.status_code == 200:
            self._cache_response(request, response)
        
        # Adicionar headers de performance
        response['X-DB-Queries'] = len(connection.queries)
        
        return response
    
    def _should_cache(self, request):
        """Verifica se a requisição deve ser cacheada"""
        return (
            request.method in self.cacheable_methods and
            any(request.path.startswith(path) for path in self.cacheable_paths) and
            request.user.is_authenticated
        )
    
    def _get_cache_key(self, request):
        """Gera chave única para cache"""
        key_data = f"{request.user.id}:{request.path}:{request.GET.urlencode()}"
        return f"api_cache:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _get_cached_response(self, request):
        """Recupera resposta do cache"""
        cache_key = self._get_cache_key(request)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            response = JsonResponse(cached_data['content'])
            response['X-Cache'] = 'HIT'
            return response
        
        return None
    
    def _cache_response(self, request, response):
        """Armazena resposta no cache"""
        try:
            if hasattr(response, 'content'):
                content = json.loads(response.content.decode())
                cache_key = self._get_cache_key(request)
                
                cache.set(cache_key, {
                    'content': content,
                    'timestamp': time.time()
                }, self.cache_timeout)
                
                response['X-Cache'] = 'MISS'
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass

class DatabaseOptimizationMiddleware(MiddlewareMixin):
    """Middleware para otimização de banco de dados"""
    
    def process_request(self, request):
        # Reset das queries para monitoramento
        connection.queries_log.clear()
        return None
    
    def process_response(self, request, response):
        # Log de queries lentas
        slow_queries = [
            query for query in connection.queries 
            if float(query['time']) > 0.1  # Queries > 100ms
        ]
        
        if slow_queries:
            import logging
            logger = logging.getLogger('nossa_grana')
            logger.warning(f"Slow queries detected ({len(slow_queries)}): {request.path}")
        
        return response

class CompressionMiddleware(MiddlewareMixin):
    """Middleware para compressão de respostas"""
    
    def process_response(self, request, response):
        # Adicionar headers para compressão
        if 'gzip' in request.META.get('HTTP_ACCEPT_ENCODING', ''):
            response['Vary'] = 'Accept-Encoding'
        
        return response