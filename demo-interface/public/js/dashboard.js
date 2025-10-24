// Nossa Grana - Dashboard

// Carregar dados do dashboard
async function loadDashboardData() {
    try {
        // Carregar dados em paralelo
        await Promise.all([
            loadFinancialSummary(),
            loadRecentTransactions(),
            loadBudgetAlerts()
        ]);
        
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
        showMessage('Erro ao carregar dados do dashboard', 'error');
    }
}

// Carregar resumo financeiro
async function loadFinancialSummary() {
    try {
        const summary = await api.getTransactionSummary();
        
        // Atualizar métricas
        document.getElementById('total-income').textContent = api.formatCurrency(summary.total_income || 0);
        document.getElementById('total-expense').textContent = api.formatCurrency(summary.total_expense || 0);
        
        const balance = (summary.total_income || 0) - (summary.total_expense || 0);
        const balanceElement = document.getElementById('balance');
        balanceElement.textContent = api.formatCurrency(balance);
        
        // Colorir saldo baseado no valor
        if (balance > 0) {
            balanceElement.className = 'metric-value text-success';
        } else if (balance < 0) {
            balanceElement.className = 'metric-value text-error';
        } else {
            balanceElement.className = 'metric-value';
        }
        
        // Carregar status do orçamento
        await loadBudgetSummary();
        
    } catch (error) {
        console.error('Erro ao carregar resumo financeiro:', error);
    }
}

// Carregar resumo do orçamento
async function loadBudgetSummary() {
    try {
        const budgetStatus = await api.getBudgetStatus();
        
        if (budgetStatus && budgetStatus.summary) {
            const summary = budgetStatus.summary;
            const totalBudgeted = summary.total_budgeted || 0;
            const totalSpent = summary.total_spent || 0;
            
            let usagePercentage = 0;
            if (totalBudgeted > 0) {
                usagePercentage = (totalSpent / totalBudgeted) * 100;
            }
            
            const usageElement = document.getElementById('budget-usage');
            usageElement.textContent = `${usagePercentage.toFixed(1)}%`;
            
            // Colorir baseado na porcentagem
            if (usagePercentage >= 100) {
                usageElement.className = 'metric-value text-error';
                document.getElementById('budget-status').textContent = 'Orçamento excedido';
                document.getElementById('budget-status').className = 'metric-change metric-negative';
            } else if (usagePercentage >= 80) {
                usageElement.className = 'metric-value text-warning';
                document.getElementById('budget-status').textContent = 'Próximo do limite';
                document.getElementById('budget-status').className = 'metric-change metric-negative';
            } else {
                usageElement.className = 'metric-value text-success';
                document.getElementById('budget-status').textContent = 'Dentro do limite';
                document.getElementById('budget-status').className = 'metric-change metric-positive';
            }
        }
        
    } catch (error) {
        console.error('Erro ao carregar resumo do orçamento:', error);
        // Não mostrar erro para o usuário, pois pode não ter orçamentos ainda
    }
}

// Carregar transações recentes
async function loadRecentTransactions() {
    try {
        const response = await api.getTransactions({ limit: 5 });
        const transactions = response.results || response;
        
        const container = document.getElementById('recent-transactions');
        
        if (!transactions || transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">💰</div>
                    <p>Nenhuma transação encontrada</p>
                    <button class="btn btn-primary mt-3" onclick="window.location.href='/transactions'">
                        Adicionar Primeira Transação
                    </button>
                </div>
            `;
            return;
        }
        
        let html = '';
        transactions.forEach(transaction => {
            const typeIcon = transaction.type === 'income' ? '📈' : '📉';
            const typeClass = transaction.type === 'income' ? 'text-success' : 'text-error';
            const typeText = transaction.type === 'income' ? 'Receita' : 'Despesa';
            
            html += `
                <div class="transaction-item" style="display: flex; justify-content: space-between; align-items: center; padding: 12px; margin-bottom: 8px; background: var(--bg-secondary); border-radius: var(--border-radius);">
                    <div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span>${typeIcon}</span>
                            <strong>${transaction.description}</strong>
                        </div>
                        <div class="text-muted" style="font-size: 0.875rem;">
                            ${transaction.category_name} • ${api.formatDate(transaction.date)}
                        </div>
                    </div>
                    <div class="${typeClass}" style="font-weight: 600;">
                        ${api.formatCurrency(transaction.amount)}
                    </div>
                </div>
            `;
        });
        
        html += `
            <div class="text-center mt-3">
                <button class="btn btn-secondary" onclick="window.location.href='/transactions'">
                    Ver Todas as Transações
                </button>
            </div>
        `;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar transações recentes:', error);
        document.getElementById('recent-transactions').innerHTML = `
            <div class="alert alert-error">
                Erro ao carregar transações recentes
            </div>
        `;
    }
}

// Carregar alertas de orçamento
async function loadBudgetAlerts() {
    try {
        const alertsResponse = await api.getBudgetAlerts({ is_active: true, limit: 5 });
        const alerts = alertsResponse.results || alertsResponse;
        
        const container = document.getElementById('budget-alerts');
        
        if (!alerts || alerts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">✅</div>
                    <p>Nenhum alerta ativo</p>
                    <p class="text-muted">Seus orçamentos estão sob controle!</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        alerts.forEach(alert => {
            let alertClass = 'alert-info';
            let alertIcon = 'ℹ️';
            
            switch (alert.alert_level) {
                case 'critical':
                    alertClass = 'alert-error';
                    alertIcon = '🚨';
                    break;
                case 'high':
                    alertClass = 'alert-error';
                    alertIcon = '⚠️';
                    break;
                case 'medium':
                    alertClass = 'alert-warning';
                    alertIcon = '⚠️';
                    break;
                case 'low':
                    alertClass = 'alert-info';
                    alertIcon = 'ℹ️';
                    break;
            }
            
            html += `
                <div class="alert ${alertClass}" style="margin-bottom: 12px;">
                    <div style="display: flex; align-items: flex-start; gap: 8px;">
                        <span>${alertIcon}</span>
                        <div style="flex: 1;">
                            <strong>${alert.budget_category}</strong>
                            <p style="margin: 4px 0 0 0; font-size: 0.875rem;">${alert.message}</p>
                            <div class="text-muted" style="font-size: 0.75rem; margin-top: 4px;">
                                ${alert.alert_type_display} • ${api.formatDateTime(alert.created_at)}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
            <div class="text-center mt-3">
                <button class="btn btn-secondary" onclick="window.location.href='/alerts'">
                    Ver Todos os Alertas
                </button>
            </div>
        `;
        
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Erro ao carregar alertas:', error);
        document.getElementById('budget-alerts').innerHTML = `
            <div class="alert alert-warning">
                Não foi possível carregar alertas
            </div>
        `;
    }
}

// Gerar alertas automáticos
async function generateAlerts() {
    try {
        showMessage('Gerando alertas automáticos...', 'info');
        
        const result = await api.generateBudgetAlerts();
        
        showMessage(`${result.total_alerts_generated} alertas gerados/atualizados`, 'success');
        
        // Recarregar alertas
        await loadBudgetAlerts();
        
    } catch (error) {
        console.error('Erro ao gerar alertas:', error);
        showMessage('Erro ao gerar alertas automáticos', 'error');
    }
}

// Atualizar dashboard
async function refreshDashboard() {
    showMessage('Atualizando dashboard...', 'info');
    
    // Mostrar loading
    document.getElementById('recent-transactions').innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    document.getElementById('budget-alerts').innerHTML = '<div class="loading"><div class="spinner"></div></div>';
    
    await loadDashboardData();
    
    showMessage('Dashboard atualizado!', 'success');
}