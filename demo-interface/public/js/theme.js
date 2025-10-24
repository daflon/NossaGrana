// Nossa Grana - Sistema de Tema Simples e Funcional

// Definir tema padrão
let currentTheme = localStorage.getItem('theme') || 'light';

// Aplicar tema imediatamente
document.documentElement.setAttribute('data-theme', currentTheme);

// Função para alternar tema
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
    console.log('Tema alterado para:', currentTheme);
}

// Função para obter tema atual
function getCurrentTheme() {
    return currentTheme;
}

// Função para definir tema específico
function setTheme(theme) {
    if (theme === 'light' || theme === 'dark') {
        currentTheme = theme;
        document.documentElement.setAttribute('data-theme', currentTheme);
        localStorage.setItem('theme', currentTheme);
    }
}

console.log('Sistema de tema carregado. Tema atual:', currentTheme);