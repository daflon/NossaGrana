from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
import hashlib
import json
import time
import logging

logger = logging.getLogger(__name__)

class CacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache_stats = {'hits': 0, 'misses': 0}
        self.default_timeout = getattr(settings, 'CACHE_TIMEOUT', 300)

    def __call__(self, request):
        if request.method == 'GET' and self._should_cache(request):
            cache_key = self._get_cache_key(request)
            cached_response = cache.get(cache_key)
            
            if cached_response:
                self.cache_stats['hits'] += 1
                response = HttpResponse(cached_response['content'], 
                                      content_type=cached_response['content_type'])
                response['X-Cache'] = 'HIT'
                return response
            
            self.cache_stats['misses'] += 1
        
        response = self.get_response(request)
        
        if (request.method == 'GET' and 
            self._should_cache(request) and 
            response.status_code == 200):
            
            cache_key = self._get_cache_key(request)
            cache_data = {
                'content': response.content.decode('utf-8'),
                'content_type': response.get('Content-Type', 'text/html')
            }
            timeout = self._get_cache_timeout(request)
            cache.set(cache_key, cache_data, timeout)
            response['X-Cache'] = 'MISS'
        
        return response

    def _should_cache(self, request):
        if not getattr(settings, 'USE_CACHE_MIDDLEWARE', True):
            return False
        
        cacheable_paths = ['/api/transactions/', '/api/budgets/', '/api/reports/', '/api/goals/']
        skip_params = ['nocache', 'refresh']
        
        return (any(request.path.startswith(path) for path in cacheable_paths) and
                not any(param in request.GET for param in skip_params))

    def _get_cache_key(self, request):
        key_data = f"{request.path}:{request.GET.urlencode()}:{request.user.id if request.user.is_authenticated else 'anon'}"
        return f"cache_mw:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _get_cache_timeout(self, request):
        timeouts = {
            '/api/reports/': 600,  # 10 min
            '/api/budgets/': 180,  # 3 min
            '/api/transactions/': 120,  # 2 min
            '/api/goals/': 300  # 5 min
        }
        
        for path, timeout in timeouts.items():
            if request.path.startswith(path):
                return timeout
        return self.default_timeout
    
    def invalidate_cache(self, pattern=None):
        """Invalida cache por padrão"""
        if pattern:
            # Implementação simplificada - em produção usar Redis SCAN
            pass
        else:
            cache.clear()
    
    def get_stats(self):
        """Retorna estatísticas do cache"""
        total = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total * 100) if total > 0 else 0
        return {
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': f"{hit_rate:.1f}%"
        }