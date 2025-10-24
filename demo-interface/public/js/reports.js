/**
 * Sistema de Relatórios - Nossa Grana
 * Gerencia gráficos, análises e exportação de relatórios
 */

// Estado global dos relatórios
let reportsState = {
    currentPeriod: 'current_month',
    currentType: 'expense',
    charts: {},
    data: {
        summary: null,
        categoryBreakdown: [],
        monthlyTrend: [],
        spendingPatterns: []
    }
};

// Configurações de cores para gráficos
const CHART_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F1948A', '#BDC3C7', '#F8C471', '#82E0AA', '#AED6F1'
];

// Inicializar página de relatórios
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Inicializando página de relatórios...');
    
    // Verificar autenticação
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/index.html';
        return;
    }

    // Processar parâmetros da URL
    processUrlParameters();

    // Configurar event listeners
    setupEventListeners();
    
    // Carregar contas e cartões para filtros
    await loadAccountsAndCards();
    
    // Carregar dados iniciais
    await loadAllReports();
});

// Processar parâmetros da URL
function processUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Verificar se há filtro de conta
    const accountId = urlParams.get('account');
    const accountName = urlParams.get('account_name');
    
    if (accountId) {
        reportsState.selectedAccount = accountId;
        if (accountName) {
            // Atualizar título da página
            const pageTitle = document.querySelector('.page-title');
            if (pageTitle) {
                pageTitle.textContent = `Relatórios - ${decodeURIComponent(accountName)}`;
            }
        }
    }
    
    // Verificar se há filtro de cartão
    const cardId = urlParams.get('card');
    const cardName = urlParams.get('card_name');
    
    if (cardId) {
        reportsState.selectedCard = cardId;
        if (cardName) {
            // Atualizar título da página
            const pageTitle = document.querySelector('.page-title');
            if (pageTitle) {
                pageTitle.textContent = `Relatórios - ${decodeURIComponent(cardName)}`;
            }
        }
    }
}

// Carregar contas e cartões para os filtros
async function loadAccountsAndCards() {
    try {
        // Carregar contas
        const accountsResponse = await api.request('/financial/accounts/');
        const accounts = accountsResponse.results || accountsResponse;
        
        const accountSelect = document.getElementById('account-select');
        if (accountSelect) {
            // Limpar opções existentes (exceto a primeira)
            while (accountSelect.children.length > 1) {
                accountSelect.removeChild(accountSelect.lastChild);
            }
            
            accounts.filter(acc => acc.is_active).forEach(account => {
                const option = document.createElement('option');
                option.value = account.id;
                option.textContent = account.name;
                accountSelect.appendChild(option);
            });
            
            // Selecionar conta se especificada na URL
            if (reportsState.selectedAccount) {
                accountSelect.value = reportsState.selectedAccount;
            }
        }
        
        // Carregar cartões
        const cardsResponse = await api.request('/financial/credit-cards/');
        const cards = cardsResponse.results || cardsResponse;
        
        const cardSelect = document.getElementById('card-select');
        if (cardSelect) {
            // Limpar opções existentes (exceto a primeira)
            while (cardSelect.children.length > 1) {
                cardSelect.removeChild(cardSelect.lastChild);
            }
            
            cards.filter(card => card.is_active).forEach(card => {
                const option = document.createElement('option');
                option.value = card.id;
                option.textContent = card.name;
                cardSelect.appendChild(option);
            });
            
            // Selecionar cartão se especificado na URL
            if (reportsState.selectedCard) {
                cardSelect.value = reportsState.selectedCard;
            }
        }
        
    } catch (error) {
        console.error('Erro ao carregar contas e cartões:', error);
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Filtros de período
    const periodSelect = document.getElementById('period-select');
    if (periodSelect) {
        periodSelect.addEventListener('change', handlePeriodChange);
    }
    
    // Filtros de tipo
    const typeSelect = document.getElementById('type-select');
    if (typeSelect) {
        typeSelect.addEventListener('change', handleTypeChange);
    }
    
    // Filtros de conta
    const accountSelect = document.getElementById('account-select');
    if (accountSelect) {
        accountSelect.addEventListener('change', handleAccountChange);
    }
    
    // Filtros de cartão
    const cardSelect = document.getElementById('card-select');
    if (cardSelect) {
        cardSelect.addEventListener('change', handleCardChange);
    }

    // Filtros de tipo
    const typeSelect = document.getElementById('type-select');
    if (typeSelect) {
        typeSelect.addEventListener('change', handleTypeChange);
    }

    // Botão de atualizar
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', handleRefresh);
    }

    // Botão de exportar
    const exportBtn = document.getElementById('export-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', handleExport);
    }

    // Filtros de data customizada
    const dateFromInput = document.getElementById('date-from');
    const dateToInput = document.getElementById('date-to');
    const applyDatesBtn = document.getElementById('apply-dates-btn');
    
    if (applyDatesBtn) {
        applyDatesBtn.addEventListener('click', handleCustomDateRange);
    }
}

// Manipular mudança de período
async function handlePeriodChange(event) {
    reportsState.currentPeriod = event.target.value;
    
    // Limpar datas customizadas
    const dateFromInput = document.getElementById('date-from');
    const dateToInput = document.getElementById('date-to');
    if (dateFromInput) dateFromInput.value = '';
    if (dateToInput) dateToInput.value = '';
    
    await loadAllReports();
}

// Manipular mudança de tipo
async function handleTypeChange(event) {
    reportsState.currentType = event.target.value;
    await loadCategoryBreakdown();
}

// Manipular mudança de conta
async function handleAccountChange(event) {
    reportsState.selectedAccount = event.target.value || null;
    
    // Se selecionou uma conta, limpar seleção de cartão
    if (reportsState.selectedAccount) {
        reportsState.selectedCard = null;
        const cardSelect = document.getElementById('card-select');
        if (cardSelect) cardSelect.value = '';
    }
    
    await loadAllReports();
}

// Manipular mudança de cartão
async function handleCardChange(event) {
    reportsState.selectedCard = event.target.value || null;
    
    // Se selecionou um cartão, limpar seleção de conta
    if (reportsState.selectedCard) {
        reportsState.selectedAccount = null;
        const accountSelect = document.getElementById('account-select');
        if (accountSelect) accountSelect.value = '';
    }
    
    await loadAllReports();
}

// Manipular atualização
async function handleRefresh() {
    showMessage('Atualizando relatórios...', 'info');
    await loadAllReports();
    showMessage('Relatórios atualizados!', 'success');
}

// Manipular exportação
function handleExport() {
    showMessage('Funcionalidade de exportação será implementada em breve!', 'info');
}

// Manipular intervalo de datas customizado
async function handleCustomDateRange() {
    const dateFrom = document.getElementById('date-from').value;
    const dateTo = document.getElementById('date-to').value;
    
    if (!dateFrom || !dateTo) {
        showMessage('Por favor, selecione ambas as datas', 'error');
        return;
    }
    
    if (new Date(dateFrom) > new Date(dateTo)) {
        showMessage('A data inicial deve ser anterior à data final', 'error');
        return;
    }
    
    // Usar datas customizadas
    reportsState.customDateRange = { dateFrom, dateTo };
    await loadAllReports();
}

// Carregar todos os relatórios
async function loadAllReports() {
    try {
        showLoading(true);
        
        // Carregar dados em paralelo
        const promises = [
            loadSummaryReport(),
            loadCategoryBreakdown(),
            loadMonthlyTrend(),
            loadSpendingPatterns()
        ];
        
        await Promise.all(promises);
        
        // Renderizar gráficos
        renderAllCharts();
        
    } catch (error) {
        console.error('Erro ao carregar relatórios:', error);
        showMessage('Erro ao carregar relatórios: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

// Carregar resumo financeiro
async function loadSummaryReport() {
    try {
        const params = getApiParams();
        const response = await api.request(`/reports/summary/?${params}`);
        reportsState.data.summary = response;
        
        // Atualizar cards de resumo
        updateSummaryCards(response);
        
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        // Usar dados mockados para demonstração
        const mockSummary = {
            total_income: 15750.00,
            total_expense: 12340.00,
            net_balance: 3410.00,
            savings_rate: 21.6,
            transaction_count: 127,
            average_transaction: 97.20,
            income_change: 12.5,
            expense_change: -5.2,
            balance_change: 45.8
        };
        reportsState.data.summary = mockSummary;
        updateSummaryCards(mockSummary);
    }
}

// Carregar breakdown por categoria
async function loadCategoryBreakdown() {
    try {
        const params = getApiParams();
        const typeParam = `type=${reportsState.currentType}`;
        const response = await api.request(`/reports/category-breakdown/?${params}&${typeParam}`);
        reportsState.data.categoryBreakdown = response;
        
    } catch (error) {
        console.error('Erro ao carregar breakdown:', error);
        // Usar dados mockados para demonstração
        const mockBreakdown = [
            {
                category_name: 'Alimentação',
                total_amount: 4250.00,
                percentage: 34.4,
                transaction_count: 42,
                average_transaction: 101.19,
                amount_change: -8.2,
                trend: 'down',
                category_color: '#FF6B6B'
            },
            {
                category_name: 'Transporte',
                total_amount: 2890.00,
                percentage: 23.4,
                transaction_count: 28,
                average_transaction: 103.21,
                amount_change: 15.7,
                trend: 'up',
                category_color: '#4ECDC4'
            },
            {
                category_name: 'Lazer',
                total_amount: 1850.00,
                percentage: 15.0,
                transaction_count: 18,
                average_transaction: 102.78,
                amount_change: 2.1,
                trend: 'neutral',
                category_color: '#45B7D1'
            },
            {
                category_name: 'Saúde',
                total_amount: 1200.00,
                percentage: 9.7,
                transaction_count: 12,
                average_transaction: 100.00,
                amount_change: -3.5,
                trend: 'down',
                category_color: '#96CEB4'
            },
            {
                category_name: 'Educação',
                total_amount: 950.00,
                percentage: 7.7,
                transaction_count: 8,
                average_transaction: 118.75,
                amount_change: 22.3,
                trend: 'up',
                category_color: '#FFEAA7'
            },
            {
                category_name: 'Outros',
                total_amount: 1200.00,
                percentage: 9.7,
                transaction_count: 19,
                average_transaction: 63.16,
                amount_change: 5.8,
                trend: 'up',
                category_color: '#DDA0DD'
            }
        ];
        reportsState.data.categoryBreakdown = mockBreakdown;
    }
}

// Carregar tendência mensal
async function loadMonthlyTrend() {
    try {
        const response = await api.request('/reports/monthly-trend/?months=12');
        reportsState.data.monthlyTrend = response;
        
    } catch (error) {
        console.error('Erro ao carregar tendência:', error);
        // Usar dados mockados para demonstração
        const mockTrend = [
            { month_name: 'Jan', total_income: 15000, total_expense: 12000, net_balance: 3000 },
            { month_name: 'Fev', total_income: 15500, total_expense: 11800, net_balance: 3700 },
            { month_name: 'Mar', total_income: 14800, total_expense: 13200, net_balance: 1600 },
            { month_name: 'Abr', total_income: 16200, total_expense: 12500, net_balance: 3700 },
            { month_name: 'Mai', total_income: 15750, total_expense: 12340, net_balance: 3410 }
        ];
        reportsState.data.monthlyTrend = mockTrend;
    }
}

// Carregar padrões de gastos
async function loadSpendingPatterns() {
    try {
        const response = await api.request('/reports/spending-patterns/?type=weekly&period=last_90_days');
        reportsState.data.spendingPatterns = response;
        
    } catch (error) {
        console.error('Erro ao carregar padrões:', error);
        // Usar dados mockados para demonstração
        const mockPatterns = [
            { period_label: 'Semana 1', average_amount: 850.00, transaction_count: 25 },
            { period_label: 'Semana 2', average_amount: 920.00, transaction_count: 28 },
            { period_label: 'Semana 3', average_amount: 780.00, transaction_count: 22 },
            { period_label: 'Semana 4', average_amount: 1100.00, transaction_count: 32 }
        ];
        reportsState.data.spendingPatterns = mockPatterns;
    }
    
    // Renderizar padrões
    renderSpendingPatterns();
}

// Renderizar padrões de gastos
function renderSpendingPatterns() {
    const container = document.getElementById('spending-patterns-container');
    if (!container || !reportsState.data.spendingPatterns || reportsState.data.spendingPatterns.length === 0) {
        if (container) {
            container.innerHTML = '<p class="text-muted">Nenhum padrão de gastos encontrado</p>';
        }
        return;
    }

    container.innerHTML = reportsState.data.spendingPatterns.map(pattern => `
        <div class="pattern-card">
            <div class="pattern-period">${pattern.period_label}</div>
            <div class="pattern-amount">${formatCurrency(pattern.average_amount)}</div>
            <div class="pattern-count">${pattern.transaction_count} transações</div>
        </div>
    `).join('');
}

// Obter parâmetros da API baseado no estado atual
function getApiParams() {
    const params = new URLSearchParams();
    
    if (reportsState.customDateRange) {
        params.append('date_from', reportsState.customDateRange.dateFrom);
        params.append('date_to', reportsState.customDateRange.dateTo);
    } else {
        params.append('period', reportsState.currentPeriod);
    }
    
    // Adicionar filtro de conta se selecionado
    if (reportsState.selectedAccount) {
        params.append('account', reportsState.selectedAccount);
    }
    
    // Adicionar filtro de cartão se selecionado
    if (reportsState.selectedCard) {
        params.append('credit_card', reportsState.selectedCard);
    }
    
    return params.toString();
}

// Atualizar cards de resumo
function updateSummaryCards(summary) {
    // Total de receitas
    const incomeElement = document.getElementById('total-income');
    if (incomeElement) {
        incomeElement.textContent = formatCurrency(summary.total_income);
    }
    
    // Total de despesas
    const expenseElement = document.getElementById('total-expense');
    if (expenseElement) {
        expenseElement.textContent = formatCurrency(summary.total_expense);
    }
    
    // Saldo líquido
    const balanceElement = document.getElementById('net-balance');
    if (balanceElement) {
        balanceElement.textContent = formatCurrency(summary.net_balance);
        balanceElement.className = `metric-value ${summary.net_balance >= 0 ? 'text-success' : 'text-error'}`;
    }
    
    // Taxa de poupança
    const savingsElement = document.getElementById('savings-rate');
    if (savingsElement) {
        savingsElement.textContent = formatPercentage(summary.savings_rate);
        savingsElement.className = `metric-value ${getSavingsRateColor(summary.savings_rate)}`;
    }
    
    // Transações
    const countElement = document.getElementById('transaction-count');
    if (countElement) {
        countElement.textContent = summary.transaction_count;
    }
    
    // Transação média
    const avgElement = document.getElementById('average-transaction');
    if (avgElement) {
        avgElement.textContent = formatCurrency(summary.average_transaction);
    }
    
    // Mudanças percentuais
    updateChangeIndicators(summary);
}

// Atualizar indicadores de mudança
function updateChangeIndicators(summary) {
    const indicators = [
        { id: 'income-change', value: summary.income_change },
        { id: 'expense-change', value: summary.expense_change },
        { id: 'balance-change', value: summary.balance_change }
    ];
    
    indicators.forEach(indicator => {
        const element = document.getElementById(indicator.id);
        if (element) {
            const isPositive = indicator.value > 0;
            const isNegative = indicator.value < 0;
            
            element.innerHTML = `
                <span class="${isPositive ? 'text-success' : isNegative ? 'text-error' : 'text-muted'}">
                    ${isPositive ? '↗️' : isNegative ? '↘️' : '➡️'} ${formatPercentage(Math.abs(indicator.value))}
                </span>
            `;
        }
    });
}

// Renderizar todos os gráficos
function renderAllCharts() {
    renderCategoryChart();
    renderTrendChart();
    renderBalanceChart();
}

// Renderizar gráfico de categorias
function renderCategoryChart() {
    const canvas = document.getElementById('category-chart');
    if (!canvas || !reportsState.data.categoryBreakdown.length) return;
    
    // Destruir gráfico anterior se existir
    if (reportsState.charts.category) {
        reportsState.charts.category.destroy();
    }
    
    const ctx = canvas.getContext('2d');
    const data = reportsState.data.categoryBreakdown;
    
    reportsState.charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.category_name),
            datasets: [{
                data: data.map(item => parseFloat(item.total_amount)),
                backgroundColor: data.map((item, index) => 
                    item.category_color || CHART_COLORS[index % CHART_COLORS.length]
                ),
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${reportsState.currentType === 'expense' ? 'Despesas' : 'Receitas'} por Categoria`,
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'bottom',
                    labels: { padding: 20, usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = formatCurrency(context.parsed);
                            const percentage = ((context.parsed / context.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    // Atualizar tabela de detalhes
    updateCategoryDetailsTable(data);
}

// Atualizar tabela de detalhes por categoria
function updateCategoryDetailsTable(data) {
    const tbody = document.getElementById('category-details-body');
    if (!tbody || !data || data.length === 0) {
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        Nenhum dado encontrado para o período selecionado
                    </td>
                </tr>
            `;
        }
        return;
    }

    tbody.innerHTML = data.map(item => {
        const trendIcon = item.trend === 'up' ? '📈' : item.trend === 'down' ? '📉' : '➡️';
        const trendClass = item.trend === 'up' ? 'text-success' : item.trend === 'down' ? 'text-error' : 'text-muted';
        
        return `
            <tr>
                <td>
                    <div class="category-cell">
                        <div class="category-color" style="background-color: ${item.category_color || '#007bff'}"></div>
                        <span>${item.category_name}</span>
                    </div>
                </td>
                <td class="text-right">${formatCurrency(item.total_amount)}</td>
                <td class="text-right">${item.percentage.toFixed(1)}%</td>
                <td class="text-right">${item.transaction_count}</td>
                <td class="text-right">${formatCurrency(item.average_transaction)}</td>
                <td class="text-center">
                    <span class="${trendClass}">
                        ${trendIcon} ${Math.abs(item.amount_change || 0).toFixed(1)}%
                    </span>
                </td>
            </tr>
        `;
    }).join('');
}

// Renderizar gráfico de tendências
function renderTrendChart() {
    const canvas = document.getElementById('trend-chart');
    if (!canvas || !reportsState.data.monthlyTrend.length) return;
    
    // Destruir gráfico anterior se existir
    if (reportsState.charts.trend) {
        reportsState.charts.trend.destroy();
    }
    
    const ctx = canvas.getContext('2d');
    const data = reportsState.data.monthlyTrend;
    
    reportsState.charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.month_name),
            datasets: [
                {
                    label: 'Receitas',
                    data: data.map(item => parseFloat(item.total_income)),
                    borderColor: '#4ECDC4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Despesas',
                    data: data.map(item => parseFloat(item.total_expense)),
                    borderColor: '#FF6B6B',
                    backgroundColor: 'rgba(255, 107, 107, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Tendência Mensal - Receitas vs Despesas',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'top',
                    labels: { padding: 20, usePointStyle: true }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { maxRotation: 45 }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

// Renderizar gráfico de saldo
function renderBalanceChart() {
    const canvas = document.getElementById('balance-chart');
    if (!canvas || !reportsState.data.monthlyTrend.length) return;
    
    // Destruir gráfico anterior se existir
    if (reportsState.charts.balance) {
        reportsState.charts.balance.destroy();
    }
    
    const ctx = canvas.getContext('2d');
    const data = reportsState.data.monthlyTrend;
    
    reportsState.charts.balance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.month_name),
            datasets: [{
                label: 'Saldo Mensal',
                data: data.map(item => parseFloat(item.net_balance)),
                backgroundColor: data.map(item => 
                    parseFloat(item.net_balance) >= 0 ? 'rgba(69, 183, 209, 0.7)' : 'rgba(255, 107, 107, 0.7)'
                ),
                borderColor: data.map(item => 
                    parseFloat(item.net_balance) >= 0 ? '#45B7D1' : '#FF6B6B'
                ),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Evolução do Saldo Mensal',
                    font: { size: 16, weight: 'bold' }
                },
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { maxRotation: 45 }
                },
                y: {
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

// Utilitários
function getSavingsRateColor(rate) {
    if (rate >= 20) return 'text-success';
    if (rate >= 10) return 'text-warning';
    return 'text-error';
}

function formatPercentage(value) {
    return `${(value || 0).toFixed(1)}%`;
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount || 0);
}

function showMessage(message, type = 'info') {
    // Criar elemento de toast se não existir
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(toastContainer);
    }

    // Criar toast
    const toast = document.createElement('div');
    toast.style.cssText = `
        padding: 12px 16px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;

    // Definir cor baseada no tipo
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    toast.style.backgroundColor = colors[type] || colors.info;
    toast.textContent = message;

    // Adicionar ao container
    toastContainer.appendChild(toast);

    // Animar entrada
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);

    // Remover após 3 segundos
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

function showLoading(show) {
    const loadingElements = document.querySelectorAll('.loading');
    loadingElements.forEach(element => {
        element.style.display = show ? 'block' : 'none';
    });
    
    const contentElements = document.querySelectorAll('.chart-container, .summary-cards');
    contentElements.forEach(element => {
        element.style.opacity = show ? '0.5' : '1';
    });
}

// Sistema de abas
function switchTab(tabName) {
    // Remover classe ativa de todos os botões e conteúdos
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Adicionar classe ativa ao botão e conteúdo selecionados
    const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
    const activeContent = document.getElementById(`${tabName}-tab`);
    
    if (activeButton) activeButton.classList.add('active');
    if (activeContent) activeContent.classList.add('active');
    
    // Carregar dados específicos da aba se necessário
    switch (tabName) {
        case 'summary':
            // Já carregado no início
            break;
        case 'categories':
            renderCategoryChart();
            break;
        case 'trends':
            renderTrendChart();
            renderBalanceChart();
            break;
        case 'patterns':
            renderSpendingPatterns();
            break;
    }
}

// Exportar funções globais
window.reportsModule = {
    loadAllReports,
    handleRefresh,
    handleExport,
    switchTab,
    reportsState
};

// Tornar switchTab global
window.switchTab = switchTab;

console.log('Reports.js carregado com sucesso!');