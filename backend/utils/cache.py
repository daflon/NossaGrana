from django.core.cache import cache
from functools import wraps
import hashlib
from typing import Any, Optional, Callable


class CacheManager:
    """Sistema de cache avançado"""
    
    CACHE_TIMES = {
        'short': 300,      # 5 minutos
        'medium': 1800,    # 30 minutos
        'long': 3600,      # 1 hora
        'daily': 86400,    # 24 horas
    }
    
    PREFIXES = {
        'user_stats': 'us',
        'transactions': 'tx',
        'budgets': 'bg',
        'goals': 'gl',
        'reports': 'rp',
        'accounts': 'ac',
    }
    
    @classmethod
    def get_key(cls, prefix: str, user_id: int, *args) -> str:
        key_parts = [cls.PREFIXES.get(prefix, prefix), str(user_id)]
        key_parts.extend(str(arg) for arg in args)
        key = ':'.join(key_parts)
        
        if len(key) > 200:
            key = hashlib.md5(key.encode()).hexdigest()
        
        return key
    
    @classmethod
    def set(cls, key: str, value: Any, timeout: str = 'medium') -> bool:
        timeout_seconds = cls.CACHE_TIMES.get(timeout, cls.CACHE_TIMES['medium'])
        return cache.set(key, value, timeout_seconds)
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        return cache.get(key, default)
    
    @classmethod
    def delete(cls, key: str) -> bool:
        return cache.delete(key)
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> None:
        for prefix in cls.PREFIXES.values():
            for suffix in ['stats', 'list', 'detail']:
                cls.delete(f"{prefix}:{user_id}:{suffix}")


def cache_result(prefix: str, timeout: str = 'medium'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = None
            if args:
                if hasattr(args[0], 'user_id'):
                    user_id = args[0].user_id
                elif hasattr(args[0], 'user'):
                    user_id = args[0].user.id if args[0].user else None
            
            if not user_id:
                return func(*args, **kwargs)
            
            func_args = str(args[1:]) + str(sorted(kwargs.items()))
            cache_key = CacheManager.get_key(prefix, user_id, func.__name__, func_args)
            
            result = CacheManager.get(cache_key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


class QueryOptimizer:
    @staticmethod
    def optimize_transaction_queries(queryset):
        return queryset.select_related(
            'user', 'category', 'account', 'credit_card',
            'transfer_from_account', 'transfer_to_account'
        ).prefetch_related('tags')
    
    @staticmethod
    def optimize_budget_queries(queryset):
        return queryset.select_related('user', 'category').prefetch_related(
            'transactions', 'transactions__tags'
        )
    
    @staticmethod
    def optimize_goal_queries(queryset):
        return queryset.select_related('user', 'category')
    
    @staticmethod
    def optimize_account_queries(queryset):
        return queryset.select_related('user').prefetch_related(
            'transaction_set', 'transfers_received', 'transfers_sent'
        )


def cache_user_stats(timeout: str = 'medium'):
    return cache_result('user_stats', timeout)

def cache_transactions(timeout: str = 'short'):
    return cache_result('transactions', timeout)

def cache_budgets(timeout: str = 'medium'):
    return cache_result('budgets', timeout)

def cache_reports(timeout: str = 'long'):
    return cache_result('reports', timeout)