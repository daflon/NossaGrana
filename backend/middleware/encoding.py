# -*- coding: utf-8 -*-
"""
Middleware para garantir encoding UTF-8 em todas as respostas
"""
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin


class UTF8EncodingMiddleware(MiddlewareMixin):
    """
    Middleware que garante que todas as respostas usem encoding UTF-8
    """
    
    def process_response(self, request, response):
        """
        Processa a resposta para garantir encoding UTF-8
        """
        # Para respostas JSON
        if hasattr(response, 'content') and response.get('Content-Type', '').startswith('application/json'):
            response['Content-Type'] = 'application/json; charset=utf-8'
            
            # Se for JsonResponse, garantir que não escape caracteres unicode
            if isinstance(response, JsonResponse):
                try:
                    # Recriar o conteúdo JSON sem escapar unicode
                    if hasattr(response, '_container'):
                        data = json.loads(b''.join(response._container).decode('utf-8'))
                        response._container = [json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')]
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
        
        # Para respostas HTML
        elif hasattr(response, 'content') and response.get('Content-Type', '').startswith('text/html'):
            response['Content-Type'] = 'text/html; charset=utf-8'
        
        # Para respostas de texto
        elif hasattr(response, 'content') and response.get('Content-Type', '').startswith('text/'):
            content_type = response.get('Content-Type', 'text/plain')
            if 'charset=' not in content_type:
                response['Content-Type'] = f'{content_type}; charset=utf-8'
        
        return response


class JSONResponseMiddleware(MiddlewareMixin):
    """
    Middleware que customiza respostas JSON para melhor suporte a UTF-8
    """
    
    def process_response(self, request, response):
        """
        Processa respostas JSON para garantir encoding correto
        """
        if isinstance(response, JsonResponse):
            # Garantir que o JSON não escape caracteres unicode
            response.json_dumps_params = {
                'ensure_ascii': False,
                'indent': 2 if request.GET.get('pretty') else None,
                'separators': (',', ': ') if request.GET.get('pretty') else (',', ':')
            }
        
        return response