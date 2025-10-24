import time
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class RateLimitMiddleware(MiddlewareMixin):
    """Middleware para rate limiting das APIs"""
    
    # Configurações de rate limiting por endpoint
    RATE_LIMITS = {
        '/api/auth/login/': {'requests': 5, 'window': 300},  # 5 tentativas por 5 min
        '/api/auth/register/': {'requests': 3, 'window': 3600},  # 3 registros por hora
        '/api/transactions/': {'requests': 100, 'window': 3600},  # 100 transações por hora
        '/api/budgets/': {'requests': 50, 'window': 3600},
        '/api/goals/': {'requests': 50, 'window': 3600},
        'default': {'requests': 200, 'window': 3600}  # Limite padrão
    }
    
    def process_request(self, request):
        # Aplicar rate limiting apenas para APIs
        if not request.path.startswith('/api/'):
            return None
        
        # Obter IP do cliente
        client_ip = self.get_client_ip(request)
        
        # Verificar rate limit
        if self.is_rate_limited(request.path, client_ip, request.method):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Muitas requisições. Tente novamente mais tarde.',
                'retry_after': 60
            }, status=429)
        
        return None
    
    def is_rate_limited(self, path, client_ip, method):
        # Aplicar rate limiting mais restritivo para métodos que modificam dados
        multiplier = 0.5 if method in ['POST', 'PUT', 'PATCH', 'DELETE'] else 1.0
        
        # Encontrar configuração de rate limit
        config = None
        for endpoint, limit_config in self.RATE_LIMITS.items():
            if endpoint != 'default' and path.startswith(endpoint):
                config = limit_config.copy()
                break
        
        if not config:
            config = self.RATE_LIMITS['default'].copy()
        
        # Aplicar multiplicador
        config['requests'] = int(config['requests'] * multiplier)
        
        # Chave do cache
        cache_key = f'rate_limit:{client_ip}:{path}:{method}'
        
        # Obter dados do cache
        current_time = int(time.time())
        requests_data = cache.get(cache_key, [])
        
        # Filtrar requisições dentro da janela de tempo
        window_start = current_time - config['window']
        requests_data = [req_time for req_time in requests_data if req_time > window_start]
        
        # Verificar se excedeu o limite
        if len(requests_data) >= config['requests']:
            return True
        
        # Adicionar requisição atual
        requests_data.append(current_time)
        
        # Salvar no cache
        cache.set(cache_key, requests_data, config['window'])
        
        return False
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip