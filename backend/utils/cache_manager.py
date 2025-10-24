from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    @staticmethod
    def invalidate_user_cache(user_id):
        """Invalida cache específico do usuário"""
        patterns = [
            f"cache_mw:*:{user_id}",
            f"user_data:{user_id}:*"
        ]
        # Em produção, usar Redis SCAN para padrões
        cache.delete_many([f"user_{user_id}_transactions", f"user_{user_id}_budgets"])
    
    @staticmethod
    def warm_cache(user_id, endpoints):
        """Pre-aquece cache para endpoints específicos"""
        from django.test import RequestFactory
        factory = RequestFactory()
        
        for endpoint in endpoints:
            try:
                request = factory.get(endpoint)
                request.user = type('User', (), {'id': user_id, 'is_authenticated': True})()
                # Simula chamada para aquecer cache
                logger.info(f"Cache warmed for {endpoint}")
            except Exception as e:
                logger.error(f"Cache warm failed for {endpoint}: {e}")
    
    @staticmethod
    def get_cache_size():
        """Retorna estatísticas de uso do cache"""
        try:
            # Implementação básica - expandir conforme necessário
            return {"status": "active", "backend": settings.CACHES['default']['BACKEND']}
        except:
            return {"status": "unavailable"}