/**
 * Sistema de Gerenciamento de Contas Bancárias - Nossa Grana
 */

// Estado global das contas
let accountsState = {
    accounts: [],
    currentAccount: null,
    editingId: null,
    filters: {
        type: ''
    }
};

// Inicializar página de contas
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Inicializando página de contas...');
    
    // Verificar autenticação
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // Configurar event listeners
    setupEventListeners();
    
    // Carregar dados iniciais
    await loadAccounts();
    
    // Escutar mudanças nos saldos de outras páginas
    setupBalanceUpdateListener();
});

// Configurar event listeners
function setupEventListeners() {
    // Filtro por tipo
    const typeFilter = document.getElementById('account-type-filter');
    if (typeFilter) {
        typeFilter.addEventListener('change', handleTypeFilter);
    }

    // Formulário de conta
    const accountForm = document.getElementById('account-form');
    if (accountForm) {
        accountForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveAccount();
        });
    }

    // Fechar modais ao clicar fora
    window.addEventListener('click', function(event) {
        const accountModal = document.getElementById('account-modal');
        const deleteModal = document.getElementById('delete-modal');
        
        if (event.target === accountModal) {
            closeAccountModal();
        }
        if (event.target === deleteModal) {
            closeDeleteModal();
        }
    });
}

// Carregar contas
async function loadAccounts() {
    try {
        showLoading(true);
        
        // Carregar contas da API
        const response = await api.getAccounts();
        accountsState.accounts = response.results || response;
        
        console.log('Contas carregadas:', accountsState.accounts);
        
        // Carregar resumo
        await loadAccountsSummary();
        
        // Renderizar lista
        renderAccountsList();
        
    } catch (error) {
        console.error('Erro ao carregar contas:', error);
        showMessage('Erro ao carregar contas: ' + error.message, 'error');
        
        // Usar dados mockados para demonstração
        loadMockAccounts();
        calculateLocalSummary();
    } finally {
        showLoading(false);
    }
}

// Carregar resumo das contas
async function loadAccountsSummary() {
    try {
        const response = await api.getAccountsSummary();
        updateSummaryCards(response);
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        // Calcular resumo localmente
        calculateLocalSummary();
    }
}

// Atualizar cards de resumo
function updateSummaryCards(summary) {
    const netWorthEl = document.getElementById('net-worth');
    const totalDebtEl = document.getElementById('total-debt');
    const checkingBalanceEl = document.getElementById('checking-balance');
    const savingsInvestmentBalanceEl = document.getElementById('savings-investment-balance');
    const debtCard = document.getElementById('debt-card');
    
    // Calcular patrimônio líquido disponível (contas positivas)
    const netWorth = summary.net_worth || 0;
    if (netWorthEl) {
        netWorthEl.textContent = formatCurrency(netWorth);
        netWorthEl.className = `summary-value ${netWorth >= 0 ? 'positive' : 'negative'}`;
    }
    
    // Calcular passivo total (contas negativas)
    const totalDebt = summary.total_debt || 0;
    if (totalDebtEl) {
        totalDebtEl.textContent = formatCurrency(Math.abs(totalDebt));
        totalDebtEl.className = `summary-value ${totalDebt > 0 ? 'negative' : 'neutral'}`;
    }
    
    // Mostrar/ocultar card de dívidas baseado na existência de passivos
    if (debtCard) {
        if (totalDebt > 0) {
            debtCard.style.display = 'flex';
            debtCard.classList.add('alert');
        } else {
            debtCard.style.display = 'none';
        }
    }
    
    // Atualizar por tipo
    const accountsByType = summary.accounts_by_type || {};
    if (checkingBalanceEl) {
        const checking = accountsByType['Conta Corrente'];
        checkingBalanceEl.textContent = checking ? formatCurrency(checking.total_balance) : 'R$ 0,00';
    }
    if (savingsInvestmentBalanceEl) {
        const savings = accountsByType['Poupança'] || { total_balance: 0 };
        const investment = accountsByType['Investimento'] || { total_balance: 0 };
        const total = savings.total_balance + investment.total_balance;
        savingsInvestmentBalanceEl.textContent = formatCurrency(total);
    }
}

// Calcular resumo localmente
function calculateLocalSummary() {
    const activeAccounts = accountsState.accounts.filter(acc => acc.is_active);
    
    // Calcular patrimônio líquido disponível (contas positivas)
    const netWorth = activeAccounts
        .filter(acc => parseFloat(acc.current_balance || 0) > 0)
        .reduce((sum, acc) => sum + parseFloat(acc.current_balance || 0), 0);
    
    console.log('Contas ativas:', activeAccounts);
    console.log('Patrimônio líquido calculado:', netWorth);
    
    // Calcular passivo total (contas negativas)
    const totalDebt = activeAccounts
        .filter(acc => parseFloat(acc.current_balance || 0) < 0)
        .reduce((sum, acc) => sum + Math.abs(parseFloat(acc.current_balance || 0)), 0);
    
    const checkingBalance = activeAccounts
        .filter(acc => acc.type === 'checking')
        .reduce((sum, acc) => sum + parseFloat(acc.current_balance || 0), 0);
    
    const savingsBalance = activeAccounts
        .filter(acc => acc.type === 'savings')
        .reduce((sum, acc) => sum + parseFloat(acc.current_balance || 0), 0);
    
    const investmentBalance = activeAccounts
        .filter(acc => acc.type === 'investment')
        .reduce((sum, acc) => sum + parseFloat(acc.current_balance || 0), 0);
    
    updateSummaryCards({
        net_worth: netWorth,
        total_debt: totalDebt,
        accounts_by_type: {
            'Conta Corrente': { total_balance: checkingBalance },
            'Poupança': { total_balance: savingsBalance },
            'Investimento': { total_balance: investmentBalance }
        }
    });
}

// Renderizar lista de contas
function renderAccountsList() {
    const container = document.getElementById('accounts-list');
    if (!container) return;
    
    let filteredAccounts = accountsState.accounts;
    
    // Aplicar filtros
    if (accountsState.filters.type) {
        filteredAccounts = filteredAccounts.filter(acc => acc.type === accountsState.filters.type);
    }
    
    if (filteredAccounts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🏦</div>
                <h3>Nenhuma conta encontrada</h3>
                <p>Adicione sua primeira conta para começar a controlar suas finanças.</p>
                <button class="btn btn-primary" onclick="showAccountForm()">
                    <span class="btn-icon">➕</span>
                    Criar Primeira Conta
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="accounts-grid">
            ${filteredAccounts.map(account => createAccountCard(account)).join('')}
        </div>
    `;
}

// Criar card de conta
function createAccountCard(account) {
    const typeIcons = {
        checking: '🏦',
        savings: '🏛️',
        investment: '📈',
        cash: '💵'
    };
    
    const typeLabels = {
        checking: 'Conta Corrente',
        savings: 'Poupança',
        investment: 'Investimento',
        cash: 'Dinheiro'
    };
    
    const currentBalance = parseFloat(account.current_balance || 0);
    const balanceClass = currentBalance >= 0 ? 'positive' : 'negative';
    const isNegative = currentBalance < 0;
    
    return `
        <div class="account-card ${account.is_active ? '' : 'inactive'} ${isNegative ? 'alert-card' : ''}">
            <div class="account-header">
                <div class="account-icon">${typeIcons[account.type] || '🏦'}</div>
                <div class="account-info">
                    <h4 class="account-name">${account.name}</h4>
                    <p class="account-type">${typeLabels[account.type] || account.type}</p>
                    ${account.bank ? `<p class="account-bank">${account.bank}</p>` : ''}
                </div>
                <div class="account-actions">
                    <button class="btn-icon" onclick="viewAccountReport(${account.id})" title="Ver Relatório">
                        📊
                    </button>
                    <button class="btn-icon" onclick="editAccount(${account.id})" title="Editar">
                        ✏️
                    </button>
                    <button class="btn-icon" onclick="showDeleteModal(${account.id})" title="Excluir">
                        🗑️
                    </button>
                </div>
            </div>
            
            <div class="account-balance">
                <div class="balance-label">Saldo Atual</div>
                <div class="balance-value ${balanceClass}">
                    ${account.balance_formatted || formatCurrency(account.current_balance)}
                </div>
                ${isNegative ? '<div class="alert-badge">⚠️ Alerta: Cheque Especial</div>' : ''}
            </div>
            
            <div class="quick-actions">
                <div class="quick-actions-label">Ações Rápidas:</div>
                <div class="quick-actions-buttons">
                    <button class="btn btn-sm btn-success" onclick="showQuickTransaction(${account.id}, 'income')" title="Adicionar Receita">
                        <span class="btn-icon">+</span>
                        Receita
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="showQuickTransaction(${account.id}, 'expense')" title="Adicionar Despesa">
                        <span class="btn-icon">-</span>
                        Despesa
                    </button>
                </div>
            </div>
            
            <div class="account-footer">
                <div class="account-status">
                    <span class="status-indicator ${account.is_active ? 'active' : 'inactive'}">
                        ${account.is_active ? '🟢 Ativa' : '🔴 Inativa'}
                    </span>
                </div>
                <button class="btn btn-sm btn-secondary" onclick="viewAccountDetails(${account.id})">
                    Ver Detalhes
                </button>
            </div>
        </div>
    `;
}

// Mostrar formulário de conta
function showAccountForm(accountId = null) {
    const modal = document.getElementById('account-modal');
    const modalTitle = document.getElementById('modal-title');
    const form = document.getElementById('account-form');
    
    // Resetar formulário
    form.reset();
    clearFormErrors();
    
    if (accountId) {
        // Modo edição
        const account = accountsState.accounts.find(acc => acc.id === accountId);
        if (account) {
            modalTitle.textContent = 'Editar Conta';
            document.getElementById('account-name').value = account.name;
            document.getElementById('account-type').value = account.type;
            document.getElementById('account-bank').value = account.bank || '';
            document.getElementById('initial-balance').value = account.initial_balance;
            document.getElementById('is-active').checked = account.is_active;
            accountsState.editingId = accountId;
        }
    } else {
        // Modo criação
        modalTitle.textContent = 'Nova Conta';
        document.getElementById('is-active').checked = true;
        accountsState.editingId = null;
    }
    
    modal.style.display = 'flex';
}

// Fechar modal de conta
function closeAccountModal() {
    const modal = document.getElementById('account-modal');
    modal.style.display = 'none';
    accountsState.editingId = null;
}

// Salvar conta
async function saveAccount() {
    const form = document.getElementById('account-form');
    const saveBtn = document.getElementById('save-btn-text');
    
    // Coletar dados do formulário
    const accountData = {
        name: document.getElementById('account-name').value.trim(),
        type: document.getElementById('account-type').value,
        bank: document.getElementById('account-bank').value.trim(),
        initial_balance: parseFloat(document.getElementById('initial-balance').value) || 0,
        is_active: document.getElementById('is-active').checked
    };
    
    // Validar dados
    if (!validateAccountForm(accountData)) {
        return;
    }
    
    try {
        saveBtn.textContent = 'Salvando...';
        
        let response;
        if (accountsState.editingId) {
            // Atualizar conta existente
            response = await api.updateAccount(accountsState.editingId, accountData);
            showMessage('Conta atualizada com sucesso!', 'success');
        } else {
            // Criar nova conta
            response = await api.createAccount(accountData);
            showMessage('Conta criada com sucesso!', 'success');
        }
        
        // Fechar modal e recarregar lista
        closeAccountModal();
        await loadAccounts();
        
    } catch (error) {
        console.error('Erro ao salvar conta:', error);
        
        if (error.message.includes('400')) {
            // Erro de validação - mostrar erros específicos
            try {
                const errorData = JSON.parse(error.message.split('400: ')[1]);
                showFormErrors(errorData);
            } catch {
                showMessage('Dados inválidos. Verifique os campos.', 'error');
            }
        } else {
            showMessage('Erro ao salvar conta: ' + error.message, 'error');
        }
    } finally {
        saveBtn.textContent = 'Salvar';
    }
}

// Validar formulário de conta
function validateAccountForm(data) {
    clearFormErrors();
    let isValid = true;
    
    if (!data.name) {
        showFieldError('name-error', 'Nome da conta é obrigatório');
        isValid = false;
    }
    
    if (!data.type) {
        showFieldError('type-error', 'Tipo da conta é obrigatório');
        isValid = false;
    }
    
    if (data.initial_balance < 0) {
        showFieldError('balance-error', 'Saldo inicial não pode ser negativo');
        isValid = false;
    }
    
    return isValid;
}

// Editar conta
function editAccount(accountId) {
    showAccountForm(accountId);
}

// Mostrar modal de exclusão
function showDeleteModal(accountId) {
    const account = accountsState.accounts.find(acc => acc.id === accountId);
    if (!account) return;
    
    document.getElementById('delete-account-name').textContent = account.name;
    accountsState.currentAccount = account;
    
    const modal = document.getElementById('delete-modal');
    modal.style.display = 'flex';
}

// Fechar modal de exclusão
function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    modal.style.display = 'none';
    accountsState.currentAccount = null;
}

// Confirmar exclusão
async function confirmDelete() {
    if (!accountsState.currentAccount) return;
    
    try {
        await api.deleteAccount(accountsState.currentAccount.id);
        
        showMessage('Conta excluída com sucesso!', 'success');
        closeDeleteModal();
        await loadAccounts();
        
    } catch (error) {
        console.error('Erro ao excluir conta:', error);
        showMessage('Erro ao excluir conta: ' + error.message, 'error');
    }
}

// Ver detalhes da conta
function viewAccountDetails(accountId) {
    const account = accountsState.accounts.find(acc => acc.id === accountId);
    if (!account) return;
    
    // Por enquanto, mostrar informações em um alert
    // Futuramente, pode ser uma página separada ou modal
    alert(`
Detalhes da Conta: ${account.name}

Tipo: ${account.type_display || account.type}
Banco: ${account.bank || 'Não informado'}
Saldo Inicial: ${formatCurrency(account.initial_balance)}
Saldo Atual: ${formatCurrency(account.current_balance)}
Status: ${account.is_active ? 'Ativa' : 'Inativa'}

Criada em: ${account.created_at ? new Date(account.created_at).toLocaleDateString('pt-BR') : 'Não informado'}
    `);
}

// Filtrar por tipo
function handleTypeFilter(event) {
    accountsState.filters.type = event.target.value;
    renderAccountsList();
}

// Atualizar contas
async function refreshAccounts() {
    showMessage('Atualizando contas...', 'info');
    await loadAccounts();
    showMessage('Contas atualizadas!', 'success');
}

// Carregar dados mockados para demonstração
function loadMockAccounts() {
    accountsState.accounts = [
        {
            id: 1,
            name: 'Conta Corrente Principal',
            type: 'checking',
            type_display: 'Conta Corrente',
            bank: 'Banco do Brasil',
            initial_balance: 5000.00,
            current_balance: 4250.50,
            balance_formatted: 'R$ 4.250,50',
            is_active: true,
            created_at: new Date().toISOString()
        },
        {
            id: 2,
            name: 'Poupança',
            type: 'savings',
            type_display: 'Poupança',
            bank: 'Caixa Econômica',
            initial_balance: 10000.00,
            current_balance: 12500.75,
            balance_formatted: 'R$ 12.500,75',
            is_active: true,
            created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: 3,
            name: 'Investimentos',
            type: 'investment',
            type_display: 'Investimento',
            bank: 'XP Investimentos',
            initial_balance: 15000.00,
            current_balance: 16800.25,
            balance_formatted: 'R$ 16.800,25',
            is_active: true,
            created_at: new Date(Date.now() - 22 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: 4,
            name: 'Conta Corrente Itaú',
            type: 'checking',
            type_display: 'Conta Corrente',
            bank: 'Itaú',
            initial_balance: 1000.00,
            current_balance: -450.75,
            balance_formatted: 'R$ -450,75',
            is_active: true,
            created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
            id: 5,
            name: 'Dinheiro',
            type: 'cash',
            type_display: 'Dinheiro',
            bank: '',
            initial_balance: 500.00,
            current_balance: 320.00,
            balance_formatted: 'R$ 320,00',
            is_active: true,
            created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
        }
    ];
    
    renderAccountsList();
    calculateLocalSummary();
}

// Utilitários
function formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount || 0);
}

function showLoading(show) {
    const loader = document.getElementById('accounts-loading');
    if (loader) {
        loader.style.display = show ? 'flex' : 'none';
    }
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

    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    toast.style.backgroundColor = colors[type] || colors.info;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);

    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

function clearFormErrors() {
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(el => el.textContent = '');
}

function showFieldError(fieldId, message) {
    const errorElement = document.getElementById(fieldId);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

function showFormErrors(errors) {
    Object.keys(errors).forEach(field => {
        const errorId = `${field}-error`;
        const message = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
        showFieldError(errorId, message);
    });
}

// Configurar listener para atualizações de saldo
function setupBalanceUpdateListener() {
    // Listener para mudanças no localStorage (entre abas/páginas)
    window.addEventListener('storage', function(e) {
        if (e.key === 'balance_update') {
            console.log('Saldos atualizados em outra página, recarregando...');
            loadAccounts();
        }
    });
    
    // Listener para eventos na mesma página
    window.addEventListener('balanceUpdated', function(e) {
        console.log('Saldos atualizados na mesma página, recarregando...');
        loadAccounts();
    });
}

// Funções de Transferência
function showTransferModal() {
    const modal = document.getElementById('transfer-modal');
    const form = document.getElementById('transfer-form');
    
    // Resetar formulário
    form.reset();
    clearTransferErrors();
    
    // Configurar data atual
    document.getElementById('transfer-date').value = new Date().toISOString().split('T')[0];
    
    // Preencher selects de contas
    populateTransferAccounts();
    
    modal.style.display = 'flex';
}

function closeTransferModal() {
    const modal = document.getElementById('transfer-modal');
    modal.style.display = 'none';
}

function populateTransferAccounts() {
    const fromSelect = document.getElementById('transfer-from');
    const toSelect = document.getElementById('transfer-to');
    
    // Limpar opções existentes (exceto a primeira)
    while (fromSelect.children.length > 1) {
        fromSelect.removeChild(fromSelect.lastChild);
    }
    while (toSelect.children.length > 1) {
        toSelect.removeChild(toSelect.lastChild);
    }
    
    // Adicionar contas ativas
    accountsState.accounts.filter(acc => acc.is_active).forEach(account => {
        const fromOption = document.createElement('option');
        fromOption.value = account.id;
        fromOption.textContent = `${account.name} (${account.balance_formatted || formatCurrency(account.current_balance)})`;
        fromSelect.appendChild(fromOption);
        
        const toOption = document.createElement('option');
        toOption.value = account.id;
        toOption.textContent = `${account.name} (${account.balance_formatted || formatCurrency(account.current_balance)})`;
        toSelect.appendChild(toOption);
    });
}

async function processTransfer() {
    const transferBtn = document.getElementById('transfer-btn-text');
    
    // Coletar dados do formulário
    const transferData = {
        from_account: parseInt(document.getElementById('transfer-from').value),
        to_account: parseInt(document.getElementById('transfer-to').value),
        amount: parseFloat(document.getElementById('transfer-amount').value),
        description: document.getElementById('transfer-description').value.trim(),
        date: document.getElementById('transfer-date').value
    };
    
    // Validar dados básicos
    if (!validateTransferForm(transferData)) {
        return;
    }
    
    try {
        transferBtn.textContent = 'Processando...';
        
        // Fazer requisição para API de transferência
        const response = await api.createTransfer(transferData);
        
        showMessage('Transferência realizada com sucesso!', 'success');
        closeTransferModal();
        
        // Recarregar dados das contas
        await loadAccounts();
        
        // Notificar outras páginas sobre mudança nos saldos
        notifyBalanceUpdate();
        
    } catch (error) {
        console.error('Erro ao processar transferência:', error);
        
        if (error.message.includes('400')) {
            // Erro de validação - mostrar erros específicos
            try {
                const errorData = JSON.parse(error.message.split('400: ')[1]);
                showTransferErrors(errorData);
            } catch {
                showMessage('Dados inválidos. Verifique os campos.', 'error');
            }
        } else {
            showMessage('Erro ao processar transferência: ' + error.message, 'error');
        }
    } finally {
        transferBtn.textContent = 'Transferir';
    }
}

function validateTransferForm(data) {
    clearTransferErrors();
    let isValid = true;
    
    if (!data.from_account) {
        showTransferFieldError('from-error', 'Selecione a conta origem');
        isValid = false;
    }
    
    if (!data.to_account) {
        showTransferFieldError('to-error', 'Selecione a conta destino');
        isValid = false;
    }
    
    if (data.from_account === data.to_account) {
        showTransferFieldError('to-error', 'Conta origem e destino devem ser diferentes');
        isValid = false;
    }
    
    if (!data.amount || data.amount <= 0) {
        showTransferFieldError('amount-error', 'Valor deve ser maior que zero');
        isValid = false;
    }
    
    if (!data.description) {
        showTransferFieldError('description-error', 'Descrição é obrigatória');
        isValid = false;
    }
    
    if (!data.date) {
        showTransferFieldError('date-error', 'Data é obrigatória');
        isValid = false;
    }
    
    return isValid;
}

function clearTransferErrors() {
    const errorElements = ['from-error', 'to-error', 'amount-error', 'description-error', 'date-error'];
    errorElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = '';
    });
}

function showTransferFieldError(fieldId, message) {
    const errorElement = document.getElementById(fieldId);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

function showTransferErrors(errors) {
    Object.keys(errors).forEach(field => {
        let errorId = '';
        switch (field) {
            case 'from_account':
                errorId = 'from-error';
                break;
            case 'to_account':
                errorId = 'to-error';
                break;
            case 'amount':
                errorId = 'amount-error';
                break;
            case 'description':
                errorId = 'description-error';
                break;
            case 'date':
                errorId = 'date-error';
                break;
            case 'non_field_errors':
                // Mostrar erro geral
                showMessage(Array.isArray(errors[field]) ? errors[field][0] : errors[field], 'error');
                return;
        }
        
        if (errorId) {
            const message = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
            showTransferFieldError(errorId, message);
        }
    });
}

// Função para visualizar relatório da conta
function viewAccountReport(accountId) {
    const account = accountsState.accounts.find(acc => acc.id === accountId);
    if (!account) {
        showMessage('Conta não encontrada', 'error');
        return;
    }
    
    // Redirecionar para página de relatórios com filtro da conta
    const reportUrl = `reports?account=${accountId}&account_name=${encodeURIComponent(account.name)}`;
    window.location.href = reportUrl;
}

// Notificar outras páginas sobre mudanças nos saldos
function notifyBalanceUpdate() {
    const timestamp = Date.now();
    localStorage.setItem('balance_update', timestamp.toString());
    
    // Disparar evento customizado para a própria página
    window.dispatchEvent(new CustomEvent('balanceUpdated', { 
        detail: { timestamp } 
    }));
}

// Fechar modal ao clicar fora
window.addEventListener('click', function(event) {
    const transferModal = document.getElementById('transfer-modal');
    const quickTransactionModal = document.getElementById('quick-transaction-modal');
    
    if (event.target === transferModal) {
        closeTransferModal();
    }
    if (event.target === quickTransactionModal) {
        closeQuickTransactionModal();
    }
});

// Funções de Transação Rápida
let quickTransactionState = {
    selectedAccountId: null,
    selectedType: null,
    categories: []
};

// Mostrar modal de transação rápida
function showQuickTransaction(accountId, type) {
    const account = accountsState.accounts.find(acc => acc.id === accountId);
    if (!account) {
        showMessage('Conta não encontrada', 'error');
        return;
    }
    
    quickTransactionState.selectedAccountId = accountId;
    quickTransactionState.selectedType = type;
    
    const modal = document.getElementById('quick-transaction-modal');
    const title = document.getElementById('quick-transaction-title');
    const form = document.getElementById('quick-transaction-form');
    const typeSelect = document.getElementById('quick-transaction-type');
    const accountSelect = document.getElementById('quick-transaction-account');
    
    // Resetar formulário
    form.reset();
    clearQuickTransactionErrors();
    
    // Configurar título e tipo
    const typeLabel = type === 'income' ? 'Receita' : 'Despesa';
    title.textContent = `Nova ${typeLabel} - ${account.name}`;
    typeSelect.value = type;
    
    // Configurar conta (pré-selecionada e desabilitada)
    accountSelect.innerHTML = `<option value="${accountId}">${account.name}</option>`;
    accountSelect.value = accountId;
    
    // Configurar data atual
    document.getElementById('quick-transaction-date').value = new Date().toISOString().split('T')[0];
    
    // Carregar categorias
    loadQuickTransactionCategories();
    
    modal.style.display = 'flex';
}

// Fechar modal de transação rápida
function closeQuickTransactionModal() {
    const modal = document.getElementById('quick-transaction-modal');
    modal.style.display = 'none';
    quickTransactionState.selectedAccountId = null;
    quickTransactionState.selectedType = null;
}

// Carregar categorias para transação rápida
async function loadQuickTransactionCategories() {
    const categorySelect = document.getElementById('quick-transaction-category');
    
    try {
        const response = await api.getCategories();
        quickTransactionState.categories = response.results || response;
        
        categorySelect.innerHTML = '<option value="">Selecione uma categoria</option>';
        quickTransactionState.categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category.id;
            option.textContent = category.name;
            categorySelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Erro ao carregar categorias:', error);
        // Usar categorias mockadas
        loadMockCategories();
    }
}

// Carregar categorias mockadas
function loadMockCategories() {
    const mockCategories = [
        { id: 1, name: 'Alimentação' },
        { id: 2, name: 'Transporte' },
        { id: 3, name: 'Saúde' },
        { id: 4, name: 'Educação' },
        { id: 5, name: 'Lazer' },
        { id: 6, name: 'Casa' },
        { id: 7, name: 'Salário' },
        { id: 8, name: 'Freelance' },
        { id: 9, name: 'Investimentos' },
        { id: 10, name: 'Outros' }
    ];
    
    const categorySelect = document.getElementById('quick-transaction-category');
    categorySelect.innerHTML = '<option value="">Selecione uma categoria</option>';
    
    mockCategories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.id;
        option.textContent = category.name;
        categorySelect.appendChild(option);
    });
    
    quickTransactionState.categories = mockCategories;
}

// Salvar transação rápida
async function saveQuickTransaction() {
    const saveBtn = document.getElementById('quick-save-btn-text');
    
    // Coletar dados do formulário
    const transactionData = {
        type: document.getElementById('quick-transaction-type').value,
        amount: parseFloat(document.getElementById('quick-transaction-amount').value) || 0,
        description: document.getElementById('quick-transaction-description').value.trim(),
        category: parseInt(document.getElementById('quick-transaction-category').value),
        account: parseInt(quickTransactionState.selectedAccountId),
        date: document.getElementById('quick-transaction-date').value
    };
    
    // Validar dados
    if (!validateQuickTransactionForm(transactionData)) {
        return;
    }
    
    try {
        saveBtn.textContent = 'Salvando...';
        
        console.log('Enviando dados da transação:', transactionData);
        
        // Verificar se temos token de autenticação
        const token = localStorage.getItem('access_token');
        if (!token) {
            // Simular sucesso para demonstração
            console.log('Sem token - simulando transação para demonstração');
            await simulateQuickTransaction(transactionData);
            return;
        }
        
        // Fazer requisição para API
        const response = await api.createTransaction(transactionData);
        
        const typeLabel = transactionData.type === 'income' ? 'Receita' : 'Despesa';
        showMessage(`${typeLabel} adicionada com sucesso!`, 'success');
        
        // Fechar modal
        closeQuickTransactionModal();
        
        // Recarregar dados das contas
        await loadAccounts();
        
        // Notificar outras páginas sobre mudança nos saldos
        notifyBalanceUpdate();
        
    } catch (error) {
        console.error('Erro ao salvar transação:', error);
        console.error('Dados enviados:', transactionData);
        
        // Tentar simular se for erro de API
        if (error.message.includes('405') || error.message.includes('404') || error.message.includes('fetch')) {
            console.log('Erro de API - simulando transação para demonstração');
            await simulateQuickTransaction(transactionData);
            return;
        }
        
        if (error.message.includes('400')) {
            try {
                const errorData = JSON.parse(error.message.split(': ')[1]);
                showQuickTransactionErrors(errorData);
            } catch {
                showMessage('Dados inválidos. Verifique os campos e tente novamente.', 'error');
            }
        } else {
            showMessage('Erro ao salvar transação: ' + error.message, 'error');
        }
    } finally {
        saveBtn.textContent = 'Salvar';
    }
}

// Simular transação para demonstração
async function simulateQuickTransaction(transactionData) {
    // Simular delay da API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Encontrar a conta
    const account = accountsState.accounts.find(acc => acc.id === transactionData.account);
    if (!account) {
        showMessage('Conta não encontrada', 'error');
        return;
    }
    
    // Atualizar saldo localmente
    const amount = transactionData.amount;
    if (transactionData.type === 'income') {
        account.current_balance = parseFloat(account.current_balance) + amount;
    } else {
        account.current_balance = parseFloat(account.current_balance) - amount;
    }
    
    // Atualizar formato
    account.balance_formatted = formatCurrency(account.current_balance);
    
    const typeLabel = transactionData.type === 'income' ? 'Receita' : 'Despesa';
    showMessage(`${typeLabel} adicionada com sucesso! (Modo demonstração)`, 'success');
    
    // Fechar modal
    closeQuickTransactionModal();
    
    // Recarregar dados das contas
    renderAccountsList();
    calculateLocalSummary();
    
    // Notificar outras páginas sobre mudança nos saldos
    notifyBalanceUpdate();
}

// Validar formulário de transação rápida
function validateQuickTransactionForm(data) {
    clearQuickTransactionErrors();
    let isValid = true;
    
    if (!data.amount || data.amount <= 0) {
        showQuickTransactionFieldError('quick-amount-error', 'Valor deve ser maior que zero');
        isValid = false;
    }
    
    if (!data.description) {
        showQuickTransactionFieldError('quick-description-error', 'Descrição é obrigatória');
        isValid = false;
    }
    
    if (!data.category) {
        showQuickTransactionFieldError('quick-category-error', 'Categoria é obrigatória');
        isValid = false;
    }
    
    if (!data.date) {
        showQuickTransactionFieldError('quick-date-error', 'Data é obrigatória');
        isValid = false;
    }
    
    return isValid;
}

// Limpar erros de transação rápida
function clearQuickTransactionErrors() {
    const errorElements = ['quick-amount-error', 'quick-description-error', 'quick-category-error', 'quick-account-error', 'quick-date-error'];
    errorElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = '';
    });
}

// Mostrar erro em campo específico
function showQuickTransactionFieldError(fieldId, message) {
    const errorElement = document.getElementById(fieldId);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

// Mostrar erros do servidor
function showQuickTransactionErrors(errors) {
    Object.keys(errors).forEach(field => {
        let errorId = '';
        switch (field) {
            case 'amount':
                errorId = 'quick-amount-error';
                break;
            case 'description':
                errorId = 'quick-description-error';
                break;
            case 'category':
                errorId = 'quick-category-error';
                break;
            case 'account':
                errorId = 'quick-account-error';
                break;
            case 'date':
                errorId = 'quick-date-error';
                break;
            case 'non_field_errors':
                showMessage(Array.isArray(errors[field]) ? errors[field][0] : errors[field], 'error');
                return;
        }
        
        if (errorId) {
            const message = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
            showQuickTransactionFieldError(errorId, message);
        }
    });
}

console.log('Accounts.js carregado com sucesso!');