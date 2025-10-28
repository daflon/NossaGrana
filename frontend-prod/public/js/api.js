// Nossa Grana - API Client

class ApiClient {
    constructor() {
        this.baseURL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('access_token');
    }

    // Configurar headers padrão
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }

    // Fazer requisição HTTP
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            // Se token expirou, tentar renovar
            if (response.status === 401 && this.token) {
                const refreshed = await this.refreshToken();
                if (refreshed) {
                    // Tentar novamente com novo token
                    config.headers = this.getHeaders();
                    const retryResponse = await fetch(url, config);
                    return await this.handleResponse(retryResponse);
                } else {
                    // Refresh falhou, fazer logout
                    this.logout();
                    throw new Error('Sessão expirada. Faça login novamente.');
                }
            }
            
            return await this.handleResponse(response);
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Processar resposta
    async handleResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
            const data = await response.json();
            
            if (!response.ok) {
                const errorMessage = data.message || data.error || data.detail || `HTTP ${response.status}: ${JSON.stringify(data)}`;
                throw new Error(errorMessage);
            }
            
            return data;
        } else {
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
            }
            return response;
        }
    }

    // Renovar token
    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${this.baseURL}/auth/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.token = data.access;
                localStorage.setItem('access_token', data.access);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }

        return false;
    }

    // Fazer logout
    logout() {
        this.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
    }

    // === AUTENTICAÇÃO ===
    
    async login(email, password) {
        const data = await this.request('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        this.token = data.access;
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        
        return data;
    }

    async register(userData) {
        return await this.request('/auth/register/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    // === TRANSAÇÕES ===
    
    async getTransactions(filters = {}) {
        const params = new URLSearchParams(filters);
        const endpoint = `/transactions/transactions/${params.toString() ? '?' + params.toString() : ''}`;
        return await this.request(endpoint);
    }

    async createTransaction(transactionData) {
        return await this.request('/transactions/transactions/', {
            method: 'POST',
            body: JSON.stringify(transactionData)
        });
    }

    async updateTransaction(id, transactionData) {
        return await this.request(`/transactions/transactions/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(transactionData)
        });
    }

    async deleteTransaction(id) {
        return await this.request(`/transactions/transactions/${id}/`, {
            method: 'DELETE'
        });
    }

    async createTransfer(transferData) {
        return await this.request('/transactions/transactions/transfer/', {
            method: 'POST',
            body: JSON.stringify(transferData)
        });
    }

    async getTransactionSummary() {
        return await this.request('/transactions/transactions/summary/');
    }

    // === CATEGORIAS ===
    
    async getCategories() {
        return await this.request('/transactions/categories/');
    }

    // === ORÇAMENTOS ===
    
    async getBudgets(filters = {}) {
        const params = new URLSearchParams(filters);
        const endpoint = `/budgets/budgets/${params.toString() ? '?' + params.toString() : ''}`;
        return await this.request(endpoint);
    }

    async createBudget(budgetData) {
        return await this.request('/budgets/budgets/', {
            method: 'POST',
            body: JSON.stringify(budgetData)
        });
    }

    async updateBudget(id, budgetData) {
        return await this.request(`/budgets/budgets/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(budgetData)
        });
    }

    async deleteBudget(id) {
        return await this.request(`/budgets/budgets/${id}/`, {
            method: 'DELETE'
        });
    }

    async getBudgetStatus(month = null) {
        const params = month ? `?month=${month}` : '';
        return await this.request(`/budgets/status/${params}`);
    }

    async getBudgetProgressAnalysis(month = null) {
        const params = month ? `?month=${month}` : '';
        return await this.request(`/budgets/budgets/progress_analysis/${params}`);
    }

    async generateBudgetAlerts(budgetId = null) {
        if (budgetId) {
            return await this.request(`/budgets/budgets/${budgetId}/generate_alerts/`, {
                method: 'POST'
            });
        } else {
            return await this.request('/budgets/budgets/generate_all_alerts/', {
                method: 'POST'
            });
        }
    }

    async getCategoriesWithoutBudget(month = null) {
        const params = month ? `?month=${month}` : '';
        return await this.request(`/budgets/budgets/categories_without_budget/${params}`);
    }

    // === ALERTAS ===
    
    async getBudgetAlerts(filters = {}) {
        const params = new URLSearchParams(filters);
        const endpoint = `/budgets/alerts/${params.toString() ? '?' + params.toString() : ''}`;
        return await this.request(endpoint);
    }

    async getAlertsSummary() {
        return await this.request('/budgets/alerts/summary/');
    }

    async resolveAlert(alertId) {
        return await this.request(`/budgets/alerts/${alertId}/resolve/`, {
            method: 'POST'
        });
    }

    // === METAS (placeholder para futuras implementações) ===
    
    async getGoals() {
        // Placeholder - será implementado quando a API de metas estiver pronta
        return { results: [] };
    }

    // === RELATÓRIOS (placeholder para futuras implementações) ===
    
    async getReports() {
        // Placeholder - será implementado quando a API de relatórios estiver pronta
        return { results: [] };
    }

    // === CONTAS FINANCEIRAS ===
    
    async getAccounts() {
        return await this.request('/financial/accounts/');
    }

    async createAccount(accountData) {
        return await this.request('/financial/accounts/', {
            method: 'POST',
            body: JSON.stringify(accountData)
        });
    }

    async updateAccount(id, accountData) {
        return await this.request(`/financial/accounts/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(accountData)
        });
    }

    async deleteAccount(id) {
        return await this.request(`/financial/accounts/${id}/`, {
            method: 'DELETE'
        });
    }

    async getAccountsSummary() {
        return await this.request('/financial/accounts/summary/');
    }

    // === UTILITÁRIOS ===
    
    formatCurrency(amount) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(amount);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('pt-BR');
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('pt-BR');
    }

    getCurrentMonth() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        return `${year}-${month}`;
    }

    // Verificar conexão com API
    async checkConnection() {
        try {
            // Tentar fazer uma requisição simples para verificar se a API está respondendo
            const response = await fetch(`${this.baseURL}/transactions/categories/`, {
                method: 'HEAD'
            });
            return response.status !== 500; // Qualquer coisa diferente de erro interno é considerado "conectado"
        } catch (error) {
            return false;
        }
    }
}

// Instância global da API
const api = new ApiClient();