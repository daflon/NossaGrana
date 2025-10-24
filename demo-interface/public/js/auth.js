// Nossa Grana - Autenticação

// Verificar status de autenticação
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    
    if (token) {
        showDashboard();
    } else {
        showAuth();
    }
}

// Mostrar seção de autenticação
function showAuth() {
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('dashboard-section').style.display = 'none';
    
    // Atualizar navegação
    updateNavigation(false);
}

// Mostrar dashboard
function showDashboard() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'block';
    
    // Atualizar navegação
    updateNavigation(true);
    
    // Carregar dados do dashboard
    loadDashboardData();
}

// Atualizar navegação baseada no status de login
function updateNavigation(isLoggedIn) {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (isLoggedIn) {
            link.style.pointerEvents = 'auto';
            link.style.opacity = '1';
        } else {
            if (!link.href.includes('dashboard') && !link.href.includes('/')) {
                link.style.pointerEvents = 'none';
                link.style.opacity = '0.5';
            }
        }
    });
}

// Mostrar formulário de registro
function showRegister() {
    document.getElementById('register-section').style.display = 'block';
}

// Ocultar formulário de registro
function hideRegister() {
    document.getElementById('register-section').style.display = 'none';
}

// Fazer login
document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    if (!email || !password) {
        showMessage('Por favor, preencha todos os campos.', 'error');
        return;
    }
    
    try {
        showMessage('Fazendo login...', 'info');
        
        const data = await api.login(email, password);
        
        showMessage('Login realizado com sucesso!', 'success');
        showDashboard();
        
    } catch (error) {
        showMessage(`Erro no login: ${error.message}`, 'error');
    }
});

// Fazer registro
document.getElementById('register-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = {
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        first_name: document.getElementById('reg-first-name').value,
        last_name: document.getElementById('reg-last-name').value,
        family_name: document.getElementById('reg-family-name').value,
        password: document.getElementById('reg-password').value,
        password_confirm: document.getElementById('reg-password-confirm').value
    };
    
    // Validações básicas
    if (!formData.username || !formData.email || !formData.password) {
        showMessage('Por favor, preencha todos os campos obrigatórios.', 'error');
        return;
    }
    
    if (formData.password !== formData.password_confirm) {
        showMessage('As senhas não coincidem.', 'error');
        return;
    }
    
    if (formData.password.length < 6) {
        showMessage('A senha deve ter pelo menos 6 caracteres.', 'error');
        return;
    }
    
    try {
        showMessage('Criando conta...', 'info');
        
        await api.register(formData);
        
        showMessage('Conta criada com sucesso! Faça login para continuar.', 'success');
        hideRegister();
        
        // Limpar formulário
        document.getElementById('register-form').reset();
        
    } catch (error) {
        showMessage(`Erro ao criar conta: ${error.message}`, 'error');
    }
});

// Fazer logout
function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        api.logout();
        showAuth();
        showMessage('Logout realizado com sucesso!', 'success');
        
        // Limpar dados do dashboard
        clearDashboardData();
    }
}

// Limpar dados do dashboard
function clearDashboardData() {
    document.getElementById('total-income').textContent = 'R$ 0,00';
    document.getElementById('total-expense').textContent = 'R$ 0,00';
    document.getElementById('balance').textContent = 'R$ 0,00';
    document.getElementById('budget-usage').textContent = '0%';
    
    document.getElementById('recent-transactions').innerHTML = '<div class="empty-state">Nenhuma transação encontrada</div>';
    document.getElementById('budget-alerts').innerHTML = '<div class="empty-state">Nenhum alerta ativo</div>';
}

// Mostrar mensagem
function showMessage(message, type = 'info') {
    const container = document.getElementById('message-container');
    
    // Remover mensagens anteriores
    container.innerHTML = '';
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    container.appendChild(alertDiv);
    
    // Remover mensagem após 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Verificar conexão com API
async function checkApiConnection() {
    const statusElement = document.getElementById('api-status');
    
    try {
        const isConnected = await api.checkConnection();
        
        if (isConnected) {
            statusElement.className = 'badge badge-success';
            statusElement.textContent = 'Conectado';
        } else {
            statusElement.className = 'badge badge-error';
            statusElement.textContent = 'Desconectado';
        }
    } catch (error) {
        statusElement.className = 'badge badge-error';
        statusElement.textContent = 'Erro';
    }
}