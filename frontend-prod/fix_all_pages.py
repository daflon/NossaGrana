#!/usr/bin/env python3
"""
Corrigir todas as páginas para usar o sistema de tema simples
"""
import os
import re

def fix_all_pages():
    """Corrigir todas as páginas HTML"""
    
    html_dir = 'public'
    
    # Processar todos os arquivos HTML
    for filename in os.listdir(html_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(html_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Substituir theme-simple.js por theme.js
                content = content.replace('js/theme-simple.js', 'js/theme.js')
                
                # Remover referências ao theme-stable.css
                content = re.sub(r'\s*<link rel="stylesheet" href="css/theme-stable\.css">', '', content)
                
                # Salvar se houve mudanças
                if content != original_content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✓ {filename} - corrigido")
                else:
                    print(f"- {filename} - sem mudanças")
                    
            except Exception as e:
                print(f"✗ {filename} - erro: {e}")

if __name__ == '__main__':
    print("Corrigindo todas as páginas...")
    fix_all_pages()
    print("Concluído!")