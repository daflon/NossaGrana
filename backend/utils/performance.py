from django.db import connection
from django.conf import settings
from functools import wraps
import time
import logging
from typing import Dict, List, Any


logger = logging.getLogger('nossa_grana.performance')


class DatabaseOptimizer:
    """Otimizações específicas do banco de dados"""
    
    @staticmethod
    def get_db_stats() -> Dict[str, Any]:
        """Estatísticas do banco de dados"""
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(transactions_transaction)")
            return {
                'queries_count': len(connection.queries),
                'db_engine': connection.vendor,
            }
    
    @staticmethod
    def optimize_sqlite():
        """Otimizações específicas para SQLite"""
        with connection.cursor() as cursor:
            # Configurações de performance para SQLite
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=268435456")  # 256MB


class QueryMonitor:
    """Monitor de queries para identificar gargalos"""
    
    def __init__(self):
        self.slow_queries = []
        self.query_count = 0
    
    def log_query(self, query: str, duration: float):
        self.query_count += 1
        if duration > 0.5:  # Queries > 500ms
            self.slow_queries.append({
                'query': query[:200],
                'duration': duration,
                'timestamp': time.time()
            })
            logger.warning(f"Slow query: {duration:.3f}s - {query[:100]}")
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_queries': self.query_count,
            'slow_queries': len(self.slow_queries),
            'recent_slow': self.slow_queries[-5:] if self.slow_queries else []
        }


def monitor_queries(func):
    """Decorator para monitorar queries de uma função"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        initial_queries = len(connection.queries)
        start_time = time.time()
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        final_queries = len(connection.queries)
        
        query_count = final_queries - initial_queries
        duration = end_time - start_time
        
        if query_count > 10 or duration > 1.0:
            logger.warning(
                f"Performance warning in {func.__name__}: "
                f"{query_count} queries, {duration:.3f}s"
            )
        
        return result
    return wrapper


class MemoryOptimizer:
    """Otimizações de memória"""
    
    @staticmethod
    def batch_process(queryset, batch_size: int = 1000):
        """Processa queryset em lotes para economizar memória"""
        total = queryset.count()
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batch = queryset[start:end]
            yield batch
    
    @staticmethod
    def optimize_queryset(queryset, fields: List[str] = None):
        """Otimiza queryset para usar menos memória"""
        if fields:
            return queryset.only(*fields)
        return queryset.defer('created_at', 'updated_at')


class CacheWarmer:
    """Aquecimento de cache para dados frequentemente acessados"""
    
    @staticmethod
    def warm_user_cache(user_id: int):
        """Aquece cache para um usuário específico"""
        from transactions.models import Transaction
        from budgets.models import Budget
        from goals.models import Goal
        
        # Pré-carregar dados mais acessados
        Transaction.objects.filter(user_id=user_id).select_related(
            'category', 'account', 'credit_card'
        ).prefetch_related('tags')[:50]
        
        Budget.objects.filter(user_id=user_id).select_related('category')
        Goal.objects.filter(user_id=user_id).select_related('category')
    
    @staticmethod
    def warm_dashboard_cache(user_id: int):
        """Aquece cache específico para dashboard"""
        from django.core.cache import cache
        from utils.cache import CacheManager
        
        # Estatísticas básicas
        cache_key = CacheManager.get_key('user_stats', user_id, 'dashboard')
        if not cache.get(cache_key):
            # Calcular e cachear estatísticas do dashboard
            stats = {
                'total_income': 0,
                'total_expenses': 0,
                'account_balance': 0,
                'recent_transactions': []
            }
            CacheManager.set(cache_key, stats, 'medium')


# Configuração de índices para melhor performance
DATABASE_INDEXES = {
    'transactions_transaction': [
        ['user_id', 'date'],
        ['user_id', 'type'],
        ['user_id', 'category_id'],
        ['date', 'amount'],
    ],
    'budgets_budget': [
        ['user_id', 'month', 'year'],
        ['user_id', 'category_id'],
    ],
    'goals_goal': [
        ['user_id', 'target_date'],
        ['user_id', 'is_completed'],
    ]
}