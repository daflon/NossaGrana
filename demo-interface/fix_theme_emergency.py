#!/usr/bin/env python3
"""
Correção de emergência para o problema de piscadas do tema
"""
import os
import re

def emergency_fix():
    """Substituir sistema de tema complexo pelo simples"""
    
    html_dir = 'public'
    
    # Padrões para encontrar e substituir
    patterns = [
        # Padrão 1: theme-fix.js + theme.js
        (r'(\s*)<script src="js/theme-fix\.js"></script>\s*\n\s*<script src="js/theme\.js"></script>', 
         r'\1<script src="js/theme-simple.js"></script>'),
        
        # Padrão 2: apenas theme.js
        (r'(\s*)<script src="js/theme\.js"></script>', 
         r'\1<script src="js/theme-simple.js"></script>'),
    ]
    
    # Processar todos os arquivos HTML
    for filename in os.listdir(html_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(html_dir, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Aplicar todos os padrões
                for pattern, replacement in patterns:
                    content = re.sub(pattern, replacement, content)
                
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
    print("CORREÇÃO DE EMERGÊNCIA - Removendo piscadas do tema...")
    emergency_fix()
    print("Concluído! Teste agora o dashboard.")