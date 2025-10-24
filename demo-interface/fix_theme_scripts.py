#!/usr/bin/env python3
"""
Script para corrigir o carregamento do theme-fix.js em todas as páginas HTML
"""
import os
import re

def fix_theme_scripts():
    """Adicionar theme-fix.js antes de theme.js em todas as páginas HTML"""
    
    html_dir = 'public'
    
    # Padrão para encontrar a linha do theme.js
    pattern = r'(\s*)<script src="js/theme\.js"></script>'
    replacement = r'\1<script src="js/theme-fix.js"></script>\n\1<script src="js/theme.js"></script>'
    
    # Processar todos os arquivos HTML
    for filename in os.listdir(html_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(html_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar se já tem o theme-fix.js
                if 'theme-fix.js' in content:
                    print(f"✓ {filename} - já corrigido")
                    continue
                
                # Aplicar correção
                new_content = re.sub(pattern, replacement, content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✓ {filename} - corrigido")
                else:
                    print(f"- {filename} - não encontrou theme.js")
                    
            except Exception as e:
                print(f"✗ {filename} - erro: {e}")

if __name__ == '__main__':
    print("Corrigindo scripts de tema...")
    fix_theme_scripts()
    print("Concluído!")