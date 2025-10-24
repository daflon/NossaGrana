#!/usr/bin/env python3
"""
Script para corrigir todos os caminhos nos arquivos HTML
"""
import os
import re
from pathlib import Path

def fix_html_file(file_path):
    """Corrige os caminhos em um arquivo HTML"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir caminhos CSS e JS
    content = re.sub(r'href="/css/', 'href="css/', content)
    content = re.sub(r'src="/js/', 'src="js/', content)
    
    # Corrigir links de navegação
    content = re.sub(r'href="/dashboard"', 'href="dashboard"', content)
    content = re.sub(r'href="/transactions"', 'href="transactions"', content)
    content = re.sub(r'href="/budgets"', 'href="budgets"', content)
    content = re.sub(r'href="/goals"', 'href="goals"', content)
    content = re.sub(r'href="/reports"', 'href="reports"', content)
    content = re.sub(r'href="/alerts"', 'href="alerts"', content)
    content = re.sub(r'href="/"', 'href="index.html"', content)
    
    # Corrigir redirecionamentos JavaScript
    content = re.sub(r"window\.location\.href = '/([^']*)'", r"window.location.href = '\1'", content)
    content = re.sub(r"window\.location\.href = '/'", "window.location.href = 'index.html'", content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Corrigido: {file_path}")

def main():
    public_dir = Path(__file__).parent / "public"
    
    # Corrigir todos os arquivos HTML
    for html_file in public_dir.glob("*.html"):
        fix_html_file(html_file)
    
    print("\n🎉 Todos os caminhos foram corrigidos!")

if __name__ == "__main__":
    main()