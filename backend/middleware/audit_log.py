import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

audit_logger = logging.getLogger('audit')

class AuditLogMiddleware(MiddlewareMixin):
    """Middleware para logs de auditoria de transações financeiras"""
    
    SENSITIVE_PATHS = [
        '/api/transactions/',
        '/api/budgets/',
        '/api/goals/',
        '/api/accounts/',
        '/api/credit-cards/',
    ]
    
    def process_request(self, request):
        # Armazenar dados da requisição para uso posterior
        request._audit_data = {
            'method': request.method,
            'path': request.path,
            'user': getattr(request, 'user', AnonymousUser()),
            'ip': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        return None
    
    def process_response(self, request, response):
        # Log apenas para paths sensíveis e métodos que modificam dados
        if (hasattr(request, '_audit_data') and 
            any(path in request.path for path in self.SENSITIVE_PATHS) and
            request.method in ['POST', 'PUT', 'PATCH', 'DELETE']):
            
            self.log_audit_event(request, response)
        
        return response
    
    def log_audit_event(self, request, response):
        try:
            audit_data = request._audit_data
            
            log_entry = {
                'timestamp': self.get_timestamp(),
                'user_id': audit_data['user'].id if not isinstance(audit_data['user'], AnonymousUser) else None,
                'username': audit_data['user'].username if not isinstance(audit_data['user'], AnonymousUser) else 'anonymous',
                'method': audit_data['method'],
                'path': audit_data['path'],
                'status_code': response.status_code,
                'ip_address': audit_data['ip'],
                'user_agent': audit_data['user_agent'][:200],  # Limitar tamanho
            }
            
            # Adicionar dados do body para operações críticas
            if request.method in ['POST', 'PUT', 'PATCH'] and response.status_code < 400:
                try:
                    if hasattr(request, 'body') and request.body:
                        body_data = json.loads(request.body.decode('utf-8'))
                        # Remover dados sensíveis do log
                        sanitized_data = self.sanitize_data(body_data)
                        log_entry['request_data'] = sanitized_data
                except:
                    pass
            
            audit_logger.info(json.dumps(log_entry, ensure_ascii=False))
            
        except Exception as e:
            # Não deve quebrar a aplicação se o log falhar
            logging.error(f'Erro no audit log: {str(e)}')
    
    def sanitize_data(self, data):
        """Remove dados sensíveis dos logs"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in ['password', 'token', 'secret', 'key']:
                    sanitized[key] = '***REDACTED***'
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self.sanitize_data(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            return [self.sanitize_data(item) for item in data]
        return data
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()