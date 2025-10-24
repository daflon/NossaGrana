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
        const response = await api.request('/financial/accounts/');
        accountsState.accounts = response.results || response;
        
        // Carregar resumo
        await loadAccountsSummary();
        
        // Renderizar lista
        renderAccountsList();
        
    } catch (error) {
        console.error('Erro ao carregar contas:', error);
        showMessage('Erro ao carregar contas: ' + error.message, 'error');
        
        // Usar dados mockados para demonstração
        loadMockAccounts();
    } finally {
        showLoading(false);
    }
}

// Carregar resumo das contas
async function loadAccountsSummary() {
    try {
        const response = await api.request('/financial/accounts/summary/');
        updateSummaryCards(response);
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        // Calcular resumo localmente
        calculateLocalSummary();
    }
}

// Atualizar cards de resumo
function updateSummaryCards(summary) {
    const totalAccountsEl = document.getElementById('total-accounts');
    const totalBalanceEl = document.getElementById('total-balance');
    const checkingBalanceEl = document.getElementById('checking-balance');
    const savingsBalanceEl = document.getElementById('savings-balance');
    
    if (totalAccountsEl) totalAccountsEl.textContent = summary.total_accounts || 0;
    if (totalBalanceEl) totalBalanceEl.textContent = summary.total_balance_formatted || 'R$ 0,00';
    
    // Atualizar por tipo
    const accountsByType = summary.accounts_by_type || {};
    if (checkingBalanceEl) {
        const checking = accountsByType['Conta Corrente'];
        checkingBalanceEl.textContent = checking ? formatCurrency(checking.total_balance) : 'R$ 0,00';
    }
    if (savingsBalanceEl) {
        const savings = accountsByType['Poupança'];
        savingsBalanceEl.textContent = savings ? formatCurrency(savings.total_balance) : 'R$ 0,00';
    }
}

// Calcular resumo localmente
function calculateLocalSummary() {
    const activeAccounts = accountsState.accounts.filter(acc => acc.is_active);
    const totalBalance = activeAccounts.reduce((sum, acc) => sum + parseFloat(acc.current_balance || 0), 0);
    
    const checkingBalance = activeAccounts
        .filter(acc => acc.type === 'checking')
        .reduce((sum, acc) => sum + parseFloat(acc.current_balance || 0), 0);
    
    const savingsBalance = activeAccounts
        .filter(acc => acc.type === 'savings')
        .reduce((sum, acc) => sum + parseFloat(acc.current_balance || 0), 0);
    
    updateSummaryCards({
        total_accounts: activeAccounts.length,
        total_balance_formatted: formatCurrency(totalBalance),
        accounts_by_type: {
            'Conta Corrente': { total_balance: checkingBalance },
            'Poupança': { total_balance: savingsBalance }
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
    
    const balanceClass = parseFloat(account.current_balance) >= 0 ? 'positive' : 'negative';
    
    return `
        <div class="account-card ${account.is_active ? '' : 'inactive'}">
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
            response = await api.request(`/financial/accounts/${accountsState.editingId}/`, {
                method: 'PUT',
                body: JSON.stringify(accountData)
            });
            showMessage('Conta atualizada com sucesso!', 'success');
        } else {
            // Criar nova conta
            response = await api.request('/financial/accounts/', {
                method: 'POST',
                body: JSON.stringify(accountData)
            });
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
        await api.request(`/financial/accounts/${accountsState.currentAccount.id}/`, {
            method: 'DELETE'
        });
        
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

Criada em: ${new Date(account.created_at).toLocaleDateString('pt-BR')}
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
            created_at: '2024-01-15T10:00:00Z'
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
            created_at: '2024-01-10T14:30:00Z'
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
            created_at: '2024-02-01T09:15:00Z'
        },
        {
            id: 4,
            name: 'Dinheiro',
            type: 'cash',
            type_display: 'Dinheiro',
            bank: '',
            initial_balance: 500.00,
            current_balance: 320.00,
            balance_formatted: 'R$ 320,00',
            is_active: true,
            created_at: '2024-01-01T00:00:00Z'
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
    if (event.target === transferModal) {
        closeTransferModal();
    }
});

console.log('Accounts.js carregado com sucesso!');