#!/usr/bin/env python3
"""
Script para aplicar melhorias de UX em todas as páginas HTML
- Logo clicável que retorna para página inicial
- Botão de tema movido para canto superior direito
- Botão "Sair" movido para menu lateral inferior
"""

import os
import re

def apply_improvements_to_file(file_path):
    """Aplica as melhorias a um arquivo HTML específico"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Tornar logo clicável
        logo_pattern = r'<div class="logo">'
        logo_replacement = '<div class="logo" onclick="window.location.href=\'/\'">'
        content = re.sub(logo_pattern, logo_replacement, content)
        
        # 2. Adicionar toggle de tema no header (antes do main-content)
        main_content_pattern = r'(\s*)<!-- Conteúdo Principal -->\s*<main class="main-content">'
        theme_toggle_header = '''        <!-- Toggle de Tema no Header -->
        <div class="theme-toggle theme-toggle-header" onclick="toggleTheme()">
            <span class="theme-icon light">SUN</span>
            <div class="theme-toggle-switch"></div>
            <span class="theme-icon dark">MOON</span>
        </div>

$1<!-- Conteúdo Principal -->
        <main class="main-content">'''
        
        content = re.sub(main_content_pattern, theme_toggle_header, content)
        
        # 3. Remover toggle de tema do page-header se existir
        theme_in_header_pattern = r'<div class="theme-toggle"[^>]*>.*?</div>\s*'
        content = re.sub(theme_in_header_pattern, '', content, flags=re.DOTALL)
        
        # 4. Ajustar page-header para usar page-header-actions
        page_header_pattern = r'(<div class="page-header">.*?</div>\s*)<div class="flex gap-2">'
        page_header_replacement = r'\1<div class="page-header-actions">'
        content = re.sub(page_header_pattern, page_header_replacement, content, flags=re.DOTALL)
        
        # 5. Adicionar botão sair no sidebar footer (antes do fechamento da sidebar)
        sidebar_close_pattern = r'(\s*)</nav>\s*</aside>'
        sidebar_footer = '''$1</nav>
            
            <div class="sidebar-footer">
                <button class="logout-btn" onclick="logout()">
                    <span>EXIT</span>
                    Sair
                </button>
            </div>
        </aside>'''
        
        content = re.sub(sidebar_close_pattern, sidebar_footer, content)
        
        # 6. Remover botões "Sair" existentes do conteúdo principal
        logout_button_patterns = [
            r'<button[^>]*onclick="logout\(\)"[^>]*>.*?Sair.*?</button>',
            r'<button[^>]*class="[^"]*btn-error[^"]*"[^>]*onclick="logout\(\)"[^>]*>.*?</button>'
        ]
        
        for pattern in logout_button_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Salvar arquivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Melhorias aplicadas em: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro ao processar {file_path}: {e}")
        return False

def main():
    """Função principal"""
    
    # Diretório das páginas HTML
    html_dir = "public"
    
    # Páginas que já foram atualizadas manualmente
    updated_files = {'index.html', 'dashboard.html', 'transactions.html'}
    
    # Encontrar todos os arquivos HTML
    html_files = []
    for file in os.listdir(html_dir):
        if file.endswith('.html') and file not in updated_files:
            html_files.append(os.path.join(html_dir, file))
    
    if not html_files:
        print("Nenhum arquivo HTML encontrado para atualizar.")
        return
    
    print(f"Aplicando melhorias em {len(html_files)} arquivos...")
    print("=" * 50)
    
    success_count = 0
    for file_path in html_files:
        if apply_improvements_to_file(file_path):
            success_count += 1
    
    print("=" * 50)
    print(f"Concluído! {success_count}/{len(html_files)} arquivos atualizados com sucesso.")
    
    if success_count == len(html_files):
        print("\n[SUCESSO] Todas as melhorias foram aplicadas com sucesso!")
        print("\nMelhorias implementadas:")
        print("[OK] Logo clicável que retorna para página inicial")
        print("[OK] Botão de tema movido para canto superior direito")
        print("[OK] Botão 'Sair' movido para menu lateral inferior")
    else:
        print(f"\n[AVISO] {len(html_files) - success_count} arquivos tiveram problemas.")

if __name__ == "__main__":
    main()