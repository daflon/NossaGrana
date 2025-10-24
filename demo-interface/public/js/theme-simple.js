// Nossa Grana - Sistema de Tema Simplificado (sem piscadas)

// Aplicar tema imediatamente sem esperar DOM
(function() {
    'use strict';
    
    // Definir tema padrão
    const DEFAULT_THEME = 'light';
    
    // Obter tema armazenado ou usar padrão
    let currentTheme = localStorage.getItem('theme') || DEFAULT_THEME;
    
    // Aplicar tema imediatamente
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    
    // Função simples para alternar tema
    window.toggleTheme = function() {
        currentTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        localStorage.setItem('theme', currentTheme);
        updateToggleIcon();
        console.log('Tema alterado para:', currentTheme);
    };
    
    // Função para obter tema atual
    window.getCurrentTheme = function() {
        return currentTheme;
    };
    
    // Função para definir tema específico
    window.setTheme = function(theme) {
        if (theme === 'light' || theme === 'dark') {
            currentTheme = theme;
            document.documentElement.setAttribute('data-theme', currentTheme);
            localStorage.setItem('theme', currentTheme);
            updateToggleIcon();
        }
    };
    
    // Atualizar ícones do toggle
    function updateToggleIcon() {
        const lightIcon = document.querySelector('.theme-icon.light');
        const darkIcon = document.querySelector('.theme-icon.dark');
        
        if (lightIcon && darkIcon) {
            if (currentTheme === 'dark') {
                lightIcon.style.opacity = '0.5';
                darkIcon.style.opacity = '1';
            } else {
                lightIcon.style.opacity = '1';
                darkIcon.style.opacity = '0.5';
            }
        }
    }
    
    // Criar toggle de tema
    function createThemeToggle() {
        const toggle = document.createElement('div');
        toggle.className = 'theme-toggle';
        toggle.onclick = toggleTheme;
        toggle.style.cssText = `
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 12px;
            background: var(--bg-tertiary);
            border-radius: 20px;
            cursor: pointer;
            user-select: none;
            border: 1px solid var(--border-color);
        `;
        
        toggle.innerHTML = `
            <span class="theme-icon light" style="font-size: 1rem;">☀️</span>
            <div style="
                width: 24px;
                height: 12px;
                background: var(--text-primary);
                border-radius: 6px;
                position: relative;
            ">
                <div style="
                    width: 10px;
                    height: 10px;
                    background: var(--bg-primary);
                    border-radius: 50%;
                    position: absolute;
                    top: 1px;
                    left: ${currentTheme === 'dark' ? '13px' : '1px'};
                    box-shadow: var(--shadow-sm);
                "></div>
            </div>
            <span class="theme-icon dark" style="font-size: 1rem;">🌙</span>
        `;
        
        return toggle;
    }
    
    // Adicionar toggle quando DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        // Garantir tema correto
        document.documentElement.setAttribute('data-theme', currentTheme);
        
        // Adicionar toggle à sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            const toggle = createThemeToggle();
            toggle.style.marginTop = 'auto';
            toggle.style.marginBottom = '1rem';
            sidebar.appendChild(toggle);
        }
        
        // Atualizar ícones
        updateToggleIcon();
        
        console.log('Sistema de tema simplificado carregado. Tema atual:', currentTheme);
    });
    
})();