#!/usr/bin/env python3
"""
Servidor HTTP simples para servir o frontend de teste
"""
import http.server
import socketserver
import os

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Servidor frontend rodando em: http://localhost:{PORT}")
        print(f"📁 Acesse: http://localhost:{PORT}/test.html")
        print("⏹️  Pressione Ctrl+C para parar")
        httpd.serve_forever()