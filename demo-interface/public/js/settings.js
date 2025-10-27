// Configurações - Nossa Grana
class SettingsManager {
    constructor() {
        this.currentTab = 'profile';
        this.init();
    }

    init() {
        this.loadUserData();
        this.setupEventListeners();
        this.loadNotificationPreferences();
        this.updateBackupStatus();
    }

    setupEventListeners() {
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => this.handleProfileSubmit(e));
        }
        
        const securityForm = document.getElementById('security-form');
        if (securityForm) {
            securityForm.addEventListener('submit', (e) => this.handleSecuritySubmit(e));
        }
        
        const preferencesForm = document.getElementById('preferences-form');
        if (preferencesForm) {
            preferencesForm.addEventListener('submit', (e) => this.handlePreferencesSubmit(e));
        }
    }

    // Gerenciamento de Abas
    switchTab(tabName) {
        // Remove active de todas as abas
        document.querySelectorAll('.settings-tab').forEach(tab => tab.classList.remove('active'));
        document.querySelectorAll('.settings-content').forEach(content => content.classList.remove('active'));

        // Ativa a aba selecionada
        document.querySelector(`[onclick="switchSettingsTab('${tabName}')"]`).classList.add('active');
        document.getElementById(`${tabName}-settings`).classList.add('active');
        
        this.currentTab = tabName;
        
        // Carrega dados específicos da aba
        if (tabName === 'preferences') {
            this.loadPreferences();
        }
    }

    // Carregamento de dados do usuário
    loadUserData() {
        const userData = JSON.parse(localStorage.getItem('userData') || '{}');
        
        if (userData.name) {
            document.getElementById('user-name').value = userData.name;
            document.getElementById('user-display-name').textContent = userData.name;
        }
        
        if (userData.email) {
            document.getElementById('user-email').value = userData.email;
        }
    }

    // Submissão do formulário de perfil
    async handleProfileSubmit(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('user-name').value,
            email: document.getElementById('user-email').value
        };

        if (!this.validateProfileForm(formData)) return;

        try {
            const saveBtn = document.getElementById('save-profile-text');
            const originalText = saveBtn.textContent;
            saveBtn.textContent = '💾 Salvando...';

            // Simula salvamento
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Salva no localStorage
            const userData = JSON.parse(localStorage.getItem('userData') || '{}');
            userData.name = formData.name;
            userData.email = formData.email;
            localStorage.setItem('userData', JSON.stringify(userData));

            this.showSuccess('Perfil atualizado com sucesso!');
            
        } catch (error) {
            this.showError('Erro ao salvar perfil. Tente novamente.');
        } finally {
            document.getElementById('save-profile-text').textContent = '💾 Salvar Alterações';
        }
    }
    
    // Submissão do formulário de segurança
    async handleSecuritySubmit(e) {
        e.preventDefault();
        
        const formData = {
            currentPassword: document.getElementById('current-password').value,
            newPassword: document.getElementById('new-password').value,
            confirmPassword: document.getElementById('confirm-password').value
        };

        if (!this.validateSecurityForm(formData)) return;

        try {
            const saveBtn = document.getElementById('save-security-text');
            saveBtn.textContent = '🔒 Alterando...';

            // Simula alteração de senha
            await new Promise(resolve => setTimeout(resolve, 1500));

            this.showSuccess('Senha alterada com sucesso!');
            this.clearPasswordFields();
            
        } catch (error) {
            this.showError('Erro ao alterar senha. Tente novamente.');
        } finally {
            document.getElementById('save-security-text').textContent = '🔒 Alterar Senha';
        }
    }
    
    // Submissão do formulário de preferências
    async handlePreferencesSubmit(e) {
        e.preventDefault();
        
        try {
            const saveBtn = document.getElementById('save-preferences-text');
            saveBtn.textContent = '⚙️ Salvando...';

            // Coleta dados das preferências
            const preferences = {
                theme: document.querySelector('input[name="theme"]:checked').value,
                currency: document.getElementById('default-currency').value,
                notifications: {
                    budgetAlerts: document.getElementById('budget-alerts').checked,
                    goalUpdates: document.getElementById('goal-updates').checked,
                    transactionAlerts: document.getElementById('transaction-alerts').checked
                }
            };

            // Simula salvamento
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Salva no localStorage
            localStorage.setItem('userPreferences', JSON.stringify(preferences));
            
            // Aplica tema se mudou
            if (preferences.theme !== this.getCurrentTheme()) {
                this.applyTheme(preferences.theme);
            }

            this.showSuccess('Preferências salvas com sucesso!');
            
        } catch (error) {
            this.showError('Erro ao salvar preferências. Tente novamente.');
        } finally {
            document.getElementById('save-preferences-text').textContent = '⚙️ Salvar Preferências';
        }
    }

    validateProfileForm(data) {
        let isValid = true;

        // Limpa erros anteriores
        document.querySelectorAll('#profile-settings .error-message').forEach(el => el.textContent = '');

        if (!data.name.trim()) {
            document.getElementById('name-error').textContent = 'Nome é obrigatório';
            isValid = false;
        }

        if (!data.email.trim() || !this.isValidEmail(data.email)) {
            document.getElementById('email-error').textContent = 'E-mail válido é obrigatório';
            isValid = false;
        }

        return isValid;
    }

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    clearPasswordFields() {
        const currentPassword = document.getElementById('current-password');
        const newPassword = document.getElementById('new-password');
        const confirmPassword = document.getElementById('confirm-password');
        
        if (currentPassword) currentPassword.value = '';
        if (newPassword) newPassword.value = '';
        if (confirmPassword) confirmPassword.value = '';
    }

    resetProfileForm() {
        this.loadUserData();
        document.querySelectorAll('#profile-settings .error-message').forEach(el => el.textContent = '');
    }
    
    resetSecurityForm() {
        this.clearPasswordFields();
        document.querySelectorAll('#security-settings .error-message').forEach(el => el.textContent = '');
    }
    
    resetPreferencesForm() {
        this.loadPreferences();
    }

    // Backup
    async performManualBackup() {
        const backupBtn = document.getElementById('backup-btn-text');
        const originalText = backupBtn.textContent;
        
        try {
            backupBtn.textContent = 'Realizando Backup...';
            document.getElementById('backup-status').textContent = 'Em andamento';

            // Simula backup
            await new Promise(resolve => setTimeout(resolve, 2000));

            const backupData = {
                userData: JSON.parse(localStorage.getItem('userData') || '{}'),
                transactions: JSON.parse(localStorage.getItem('transactions') || '[]'),
                accounts: JSON.parse(localStorage.getItem('accounts') || '[]'),
                budgets: JSON.parse(localStorage.getItem('budgets') || '[]'),
                goals: JSON.parse(localStorage.getItem('goals') || '[]'),
                timestamp: new Date().toISOString()
            };

            localStorage.setItem('lastBackup', JSON.stringify(backupData));
            localStorage.setItem('lastBackupDate', new Date().toISOString());

            this.updateBackupStatus();
            this.showSuccess('Backup realizado com sucesso!');

        } catch (error) {
            document.getElementById('backup-status').textContent = 'Erro';
            this.showError('Erro ao realizar backup');
        } finally {
            backupBtn.textContent = originalText;
        }
    }

    updateBackupStatus() {
        const lastBackupDate = localStorage.getItem('lastBackupDate');
        const statusElement = document.getElementById('backup-status');
        const dateElement = document.getElementById('last-backup-date');

        if (lastBackupDate) {
            const date = new Date(lastBackupDate);
            dateElement.textContent = date.toLocaleString('pt-BR');
            statusElement.textContent = 'Concluído';
        } else {
            dateElement.textContent = 'Nunca realizado';
            statusElement.textContent = 'Aguardando';
        }
    }

    downloadBackup() {
        const backupData = localStorage.getItem('lastBackup');
        if (!backupData) {
            this.showError('Nenhum backup disponível para download');
            return;
        }

        const blob = new Blob([backupData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `nossa-grana-backup-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Validação do formulário de segurança
    validateSecurityForm(data) {
        let isValid = true;

        // Limpa erros anteriores
        document.querySelectorAll('#security-settings .error-message').forEach(el => el.textContent = '');

        if (!data.currentPassword.trim()) {
            document.getElementById('current-password-error').textContent = 'Senha atual é obrigatória';
            isValid = false;
        }

        if (!data.newPassword.trim()) {
            document.getElementById('new-password-error').textContent = 'Nova senha é obrigatória';
            isValid = false;
        } else if (data.newPassword.length < 8) {
            document.getElementById('new-password-error').textContent = 'Nova senha deve ter pelo menos 8 caracteres';
            isValid = false;
        }

        if (data.newPassword !== data.confirmPassword) {
            document.getElementById('confirm-password-error').textContent = 'Senhas não coincidem';
            isValid = false;
        }

        return isValid;
    }
    
    // Carregamento de preferências
    loadPreferences() {
        const preferences = JSON.parse(localStorage.getItem('userPreferences') || '{}');
        
        // Tema
        const theme = preferences.theme || 'light';
        document.querySelector(`input[name="theme"][value="${theme}"]`).checked = true;
        
        // Moeda
        const currency = preferences.currency || 'BRL';
        document.getElementById('default-currency').value = currency;
        
        // Notificações
        const notifications = preferences.notifications || {};
        document.getElementById('budget-alerts').checked = notifications.budgetAlerts !== false;
        document.getElementById('goal-updates').checked = notifications.goalUpdates !== false;
        document.getElementById('transaction-alerts').checked = notifications.transactionAlerts === true;
    }
    
    getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }
    
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }

    saveNotificationPreferences() {
        const prefs = {
            budgetAlerts: document.getElementById('budget-alerts').checked,
            goalUpdates: document.getElementById('goal-updates').checked,
            transactionAlerts: document.getElementById('transaction-alerts').checked
        };

        localStorage.setItem('notificationPreferences', JSON.stringify(prefs));
        this.showSuccess('Preferências de notificação salvas!');
    }

    // Utilitários
    showSuccess(message) {
        // Implementação simples de toast
        const toast = document.createElement('div');
        toast.className = 'toast success';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 1000;
            background: #10b981; color: white; padding: 12px 20px;
            border-radius: 8px; font-weight: 500;
        `;
        document.body.appendChild(toast);
        setTimeout(() => document.body.removeChild(toast), 3000);
    }

    showError(message) {
        const toast = document.createElement('div');
        toast.className = 'toast error';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 1000;
            background: #ef4444; color: white; padding: 12px 20px;
            border-radius: 8px; font-weight: 500;
        `;
        document.body.appendChild(toast);
        setTimeout(() => document.body.removeChild(toast), 3000);
    }
}

// Funções globais para compatibilidade com HTML
function switchSettingsTab(tabName) {
    window.settingsManager.switchTab(tabName);
}

function resetProfileForm() {
    window.settingsManager.resetProfileForm();
}

function resetSecurityForm() {
    window.settingsManager.resetSecurityForm();
}

function resetPreferencesForm() {
    window.settingsManager.resetPreferencesForm();
}

function performManualBackup() {
    window.settingsManager.performManualBackup();
}

function downloadBackup() {
    window.settingsManager.downloadBackup();
}



function showBackupSection() {
    switchSettingsTab('backup');
    toggleUserMenu();
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    window.settingsManager = new SettingsManager();
});