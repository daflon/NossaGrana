#!/usr/bin/env python3
"""
Servidor de produção para o Nossa Grana
Serve arquivos estáticos com roteamento correto
"""
import http.server
import socketserver
import os
import urllib.parse
from pathlib import Path

PORT = 3001

class ProductionHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / "public"), **kwargs)
    
    def end_headers(self):
        # Headers CORS para desenvolvimento
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_GET(self):
        # Parse da URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Roteamento de páginas principais
        routes = {
            '/': '/index.html',
            '/login': '/index.html',
            '/dashboard': '/dashboard.html',
            '/transactions': '/transactions.html',
            '/budgets': '/budgets.html',
            '/goals': '/goals.html',
            '/reports': '/reports.html',
            '/alerts': '/alerts.html',
            '/settings': '/settings.html',
            '/accounts': '/accounts.html',
            '/credit-cards': '/credit-cards.html'
        }
        
        # Se é uma rota conhecida, redireciona para o arquivo correto
        if path in routes:
            self.path = routes[path]
        
        # Se não tem extensão e não é uma rota, assume que é HTML
        elif '.' not in path and path != '/':
            self.path = path + '.html'
        
        # Serve o arquivo
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Log mais limpo
        print(f"[{self.address_string()}] {format % args}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), ProductionHandler) as httpd:
        print(f"Nossa Grana - Servidor de Producao")
        print(f"Acesse: http://localhost:{PORT}")
        print(f"API Backend: http://localhost:8000")
        print(f"Pressione Ctrl+C para parar")
        print()
        print("Paginas disponiveis:")
        print("  - http://localhost:3001/          (Login)")
        print("  - http://localhost:3001/dashboard (Dashboard)")
        print("  - http://localhost:3001/transactions (Transacoes)")
        print("  - http://localhost:3001/budgets   (Orcamentos)")
        print("  - http://localhost:3001/goals     (Metas)")
        print("  - http://localhost:3001/reports   (Relatorios)")
        print("  - http://localhost:3001/alerts    (Alertas)")
        print("  - http://localhost:3001/settings  (Configuracoes)")
        print("  - http://localhost:3001/demo-profile-settings.html (DEMO)")
        print()
        httpd.serve_forever()