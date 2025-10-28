"""
Middleware de segurança personalizado para headers SSL/TLS
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware que adiciona headers de segurança personalizados
    """
    
    def process_response(self, request, response):
        """
        Adiciona headers de segurança à resposta
        """
        # Content Security Policy
        if hasattr(settings, 'CSP_DEFAULT_SRC'):
            csp_parts = []
            
            if hasattr(settings, 'CSP_DEFAULT_SRC'):
                csp_parts.append(f"default-src {' '.join(settings.CSP_DEFAULT_SRC)}")
            
            if hasattr(settings, 'CSP_SCRIPT_SRC'):
                csp_parts.append(f"script-src {' '.join(settings.CSP_SCRIPT_SRC)}")
            
            if hasattr(settings, 'CSP_STYLE_SRC'):
                csp_parts.append(f"style-src {' '.join(settings.CSP_STYLE_SRC)}")
            
            if hasattr(settings, 'CSP_IMG_SRC'):
                csp_parts.append(f"img-src {' '.join(settings.CSP_IMG_SRC)}")
            
            if hasattr(settings, 'CSP_FONT_SRC'):
                csp_parts.append(f"font-src {' '.join(settings.CSP_FONT_SRC)}")
            
            if hasattr(settings, 'CSP_CONNECT_SRC'):
                csp_parts.append(f"connect-src {' '.join(settings.CSP_CONNECT_SRC)}")
            
            if hasattr(settings, 'CSP_FRAME_ANCESTORS'):
                csp_parts.append(f"frame-ancestors {' '.join(settings.CSP_FRAME_ANCESTORS)}")
            
            if hasattr(settings, 'CSP_BASE_URI'):
                csp_parts.append(f"base-uri {' '.join(settings.CSP_BASE_URI)}")
            
            if hasattr(settings, 'CSP_FORM_ACTION'):
                csp_parts.append(f"form-action {' '.join(settings.CSP_FORM_ACTION)}")
            
            if hasattr(settings, 'CSP_UPGRADE_INSECURE_REQUESTS') and settings.CSP_UPGRADE_INSECURE_REQUESTS:
                csp_parts.append("upgrade-insecure-requests")
            
            if csp_parts:
                response['Content-Security-Policy'] = '; '.join(csp_parts)
        
        # Permissions Policy (Feature Policy)
        if hasattr(settings, 'PERMISSIONS_POLICY'):
            permissions_parts = []
            for feature, allowlist in settings.PERMISSIONS_POLICY.items():
                if allowlist:
                    permissions_parts.append(f"{feature}=({' '.join(allowlist)})")
                else:
                    permissions_parts.append(f"{feature}=()")
            
            if permissions_parts:
                response['Permissions-Policy'] = ', '.join(permissions_parts)
        
        # Headers de segurança adicionais
        if not settings.DEBUG:
            # Expect-CT header para Certificate Transparency
            response['Expect-CT'] = 'max-age=86400, enforce'
            
            # NEL (Network Error Logging) para monitoramento
            response['NEL'] = '{"report_to":"default","max_age":31536000,"include_subdomains":true}'
            
            # Report-To para relatórios de segurança
            response['Report-To'] = '{"group":"default","max_age":31536000,"endpoints":[{"url":"/security-reports/"}],"include_subdomains":true}'
            
            # Clear-Site-Data em logout (se aplicável)
            if request.path.endswith('/logout/'):
                response['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        
        # Headers sempre presentes
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response


class SSLRedirectMiddleware(MiddlewareMixin):
    """
    Middleware personalizado para redirecionamento SSL com exceções
    """
    
    def process_request(self, request):
        """
        Verifica se deve redirecionar para HTTPS
        """
        if not settings.DEBUG and getattr(settings, 'SECURE_SSL_REDIRECT', False):
            # Verifica se já está usando HTTPS
            if not request.is_secure():
                # Verifica exceções de redirecionamento
                exempt_paths = getattr(settings, 'SECURE_REDIRECT_EXEMPT', [])
                
                for pattern in exempt_paths:
                    import re
                    if re.match(pattern, request.path):
                        return None
                
                # Redireciona para HTTPS
                from django.http import HttpResponsePermanentRedirect
                return HttpResponsePermanentRedirect(
                    f"https://{request.get_host()}{request.get_full_path()}"
                )
        
        return None