from django.http import JsonResponse
from django.urls import resolve
from django.core.cache import cache
from django.utils import timezone
import logging
import hashlib
import json

logger = logging.getLogger('financial_security')

class FinancialSecurityMiddleware:
    """
    Middleware avançado para validações de segurança em operações financeiras
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.financial_endpoints = [
            'transactions', 'budgets', 'goals', 'accounts', 
            'credit-cards', 'reports', 'financial'
        ]
        self.rate_limit_window = 300  # 5 minutos
        self.max_requests_per_window = 100

    def __call__(self, request):
        # Rate limiting por usuário
        if request.user.is_authenticated and self._is_financial_endpoint(request):
            if not self._check_rate_limit(request):
                logger.warning(
                    f"Rate limit exceeded: {request.user.id} from {self._get_client_ip(request)}"
                )
                return JsonResponse(
                    {'error': 'Muitas requisições. Tente novamente em alguns minutos.'}, 
                    status=429
                )
            
            # Validar acesso a dados financeiros
            if not self._validate_financial_access(request):
                logger.warning(
                    f"Unauthorized financial access: {request.user.id} to {request.path} from {self._get_client_ip(request)}"
                )
                return JsonResponse(
                    {'error': 'Acesso não autorizado aos dados financeiros'}, 
                    status=403
                )
            
            # Log de auditoria para operações críticas
            self._log_financial_operation(request)

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _check_rate_limit(self, request):
        """Implementa rate limiting por usuário"""
        user_id = request.user.id
        cache_key = f"rate_limit_financial_{user_id}"
        
        current_requests = cache.get(cache_key, 0)
        if current_requests >= self.max_requests_per_window:
            return False
        
        cache.set(cache_key, current_requests + 1, self.rate_limit_window)
        return True

    def _is_financial_endpoint(self, request):
        """Verifica se é um endpoint financeiro"""
        return any(endpoint in request.path for endpoint in self.financial_endpoints)

    def _validate_financial_access(self, request):
        """Valida se o usuário tem acesso aos dados solicitados"""
        try:
            url_match = resolve(request.path_info)
            resource_id = url_match.kwargs.get('pk')
            
            if resource_id:
                return self._validate_resource_ownership(request, resource_id, url_match.url_name)
            
            # Para operações em lote, validar dados do body
            if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'data'):
                return self._validate_bulk_operations(request)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating financial access: {e}")
            return False

    def _validate_resource_ownership(self, request, resource_id, url_name):
        """Valida se o recurso pertence ao usuário com cache"""
        cache_key = f"ownership_{request.user.id}_{url_name}_{resource_id}"
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        try:
            result = False
            
            if 'transaction' in url_name:
                from transactions.models import Transaction
                result = Transaction.objects.filter(
                    id=resource_id, user=request.user
                ).exists()
            elif 'budget' in url_name:
                from budgets.models import Budget
                result = Budget.objects.filter(
                    id=resource_id, user=request.user
                ).exists()
            elif 'goal' in url_name:
                from goals.models import Goal
                result = Goal.objects.filter(
                    id=resource_id, user=request.user
                ).exists()
            elif 'account' in url_name:
                from financial_accounts.models import Account
                result = Account.objects.filter(
                    id=resource_id, user=request.user
                ).exists()
            elif 'credit' in url_name:
                from financial_accounts.models import CreditCard
                result = CreditCard.objects.filter(
                    id=resource_id, user=request.user
                ).exists()
            else:
                result = True
            
            # Cache por 5 minutos
            cache.set(cache_key, result, 300)
            return result
            
        except Exception as e:
            logger.error(f"Error validating resource ownership: {e}")
            return False

    def _validate_bulk_operations(self, request):
        """Valida operações em lote"""
        try:
            # Implementar validações específicas para operações em lote
            # Por exemplo, verificar se todas as contas/cartões pertencem ao usuário
            return True
        except Exception as e:
            logger.error(f"Error validating bulk operations: {e}")
            return False

    def _log_financial_operation(self, request):
        """Log de auditoria para operações financeiras críticas"""
        critical_operations = ['POST', 'PUT', 'PATCH', 'DELETE']
        
        if request.method in critical_operations:
            log_data = {
                'user_id': request.user.id,
                'method': request.method,
                'path': request.path,
                'ip': self._get_client_ip(request),
                'timestamp': timezone.now().isoformat(),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200]
            }
            
            logger.info(f"Financial operation: {json.dumps(log_data)}")


class SecurityAuditMiddleware:
    """
    Middleware para auditoria de segurança
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            'union select', 'drop table', 'delete from',
            '<script', 'javascript:', 'eval(',
            '../', '..\\', 'cmd.exe'
        ]

    def __call__(self, request):
        # Detectar tentativas de injeção
        if self._detect_injection_attempts(request):
            logger.critical(
                f"Injection attempt detected from {self._get_client_ip(request)}: "
                f"User: {getattr(request.user, 'id', 'anonymous')}, "
                f"Path: {request.path}, "
                f"Data: {str(request.body)[:200]}"
            )
            return JsonResponse(
                {'error': 'Requisição bloqueada por motivos de segurança'}, 
                status=400
            )

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _detect_injection_attempts(self, request):
        """Detecta tentativas de injeção SQL/XSS"""
        try:
            # Verificar parâmetros GET
            for key, value in request.GET.items():
                if self._contains_suspicious_content(value.lower()):
                    return True
            
            # Verificar dados POST
            if hasattr(request, 'body') and request.body:
                body_str = request.body.decode('utf-8', errors='ignore').lower()
                if self._contains_suspicious_content(body_str):
                    return True
            
            return False
            
        except Exception:
            return False

    def _contains_suspicious_content(self, content):
        """Verifica se o conteúdo contém padrões suspeitos"""
        return any(pattern in content for pattern in self.suspicious_patterns)