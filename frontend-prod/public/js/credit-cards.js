/**
 * Sistema de Gerenciamento de Cartões de Crédito - Nossa Grana
 */

// Estado global dos cartões
let creditCardsState = {
    cards: [],
    currentCard: null,
    editingId: null,
    filters: {
        status: ''
    }
};

// Inicializar página de cartões
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Inicializando página de cartões de crédito...');
    
    // Verificar autenticação
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // Mostrar skeleton loading imediatamente
    showSkeletonLoading(true);
    showSummarySkeletonLoading(true);

    // Configurar event listeners
    setupEventListeners();
    
    // Preencher selects de dias
    populateDaySelects();
    
    // Carregar dados iniciais
    await loadCreditCards();
    
    // Escutar mudanças nos saldos de outras páginas
    setupBalanceUpdateListener();
});

// Configurar listener para atualizações de saldo
function setupBalanceUpdateListener() {
    // Listener para eventos de atualização de saldo de outras páginas
    window.addEventListener('balanceUpdated', function() {
        loadCreditCards();
    });
}

// Configurar event listeners
function setupEventListeners() {
    // Filtro por status
    const statusFilter = document.getElementById('card-status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', handleStatusFilter);
    }

    // Formulário de cartão
    const cardForm = document.getElementById('card-form');
    if (cardForm) {
        cardForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveCreditCard();
        });
    }

    // O modal-manager já cuida dos cliques fora e tecla ESC
}

// Preencher selects de dias (1-31)
function populateDaySelects() {
    const closingSelect = document.getElementById('closing-day');
    const dueSelect = document.getElementById('due-day');
    
    for (let day = 1; day <= 31; day++) {
        // Dia de fechamento
        const closingOption = document.createElement('option');
        closingOption.value = day;
        closingOption.textContent = day;
        closingSelect.appendChild(closingOption);
        
        // Dia de vencimento
        const dueOption = document.createElement('option');
        dueOption.value = day;
        dueOption.textContent = day;
        dueSelect.appendChild(dueOption);
    }
}

// Carregar cartões de crédito
async function loadCreditCards() {
    try {
        showSkeletonLoading(true);
        
        // Carregar cartões da API
        const response = await api.request('/financial/credit-cards/');
        creditCardsState.cards = response.results || response;
        
        // Carregar resumo
        await loadCardsSummary();
        
        // Mostrar próximo fechamento
        showNextClosingAlert();
        
        // Renderizar lista
        renderCardsList();
        
    } catch (error) {
        console.error('Erro ao carregar cartões:', error);
        showMessage('Erro ao carregar cartões: ' + error.message, 'error');
        
        // Usar dados mockados para demonstração
        loadMockCreditCards();
    } finally {
        showSkeletonLoading(false);
    }
}

// Carregar resumo dos cartões
async function loadCardsSummary() {
    try {
        showSummarySkeletonLoading(true);
        const response = await api.request('/financial/credit-cards/summary/');
        updateSummaryCards(response);
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        // Calcular resumo localmente
        calculateLocalSummary();
    } finally {
        showSummarySkeletonLoading(false);
    }
}

// Atualizar cards de resumo
function updateSummaryCards(summary) {
    const totalCardsEl = document.getElementById('total-cards');
    const totalLimitEl = document.getElementById('total-limit');
    const availableLimitEl = document.getElementById('available-limit');
    const highestRiskEl = document.getElementById('highest-risk');
    
    if (totalCardsEl) totalCardsEl.textContent = summary.total_cards || 0;
    if (totalLimitEl) totalLimitEl.textContent = formatCurrency(summary.total_limit || 0);
    if (availableLimitEl) availableLimitEl.textContent = formatCurrency(summary.total_available || 0);
    if (highestRiskEl) highestRiskEl.textContent = `${(summary.highest_risk || 0).toFixed(1)}%`;
}

// Calcular resumo localmente
function calculateLocalSummary() {
    const activeCards = creditCardsState.cards.filter(card => card.is_active);
    const totalLimit = activeCards.reduce((sum, card) => sum + parseFloat(card.credit_limit || 0), 0);
    const totalAvailable = activeCards.reduce((sum, card) => sum + parseFloat(card.available_limit || 0), 0);
    const totalUsed = totalLimit - totalAvailable;
    const averageUsage = totalLimit > 0 ? (totalUsed / totalLimit) * 100 : 0;
    const highestRisk = activeCards.length > 0 ? Math.max(...activeCards.map(card => card.usage_percentage || 0)) : 0;
    
    updateSummaryCards({
        total_cards: activeCards.length,
        total_limit: totalLimit,
        total_available: totalAvailable,
        highest_risk: highestRisk
    });
}

// Renderizar lista de cartões
function renderCardsList() {
    const container = document.getElementById('cards-list');
    if (!container) return;
    
    let filteredCards = creditCardsState.cards;
    
    // Aplicar filtros
    if (creditCardsState.filters.status) {
        const isActive = creditCardsState.filters.status === 'active';
        filteredCards = filteredCards.filter(card => card.is_active === isActive);
    }
    
    if (filteredCards.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">💳</div>
                <h3>Nenhum cartão encontrado</h3>
                <p>Adicione seu primeiro cartão para começar a controlar seus gastos.</p>
                <button class="btn btn-primary" onclick="showCreditCardForm()">
                    <span class="btn-icon">➕</span>
                    Criar Primeiro Cartão
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="cards-grid">
            ${filteredCards.map(card => createCreditCardCard(card)).join('')}
        </div>
    `;
}

// Calcular próximas datas do ciclo
function calculateCycleDates(closingDay, dueDay) {
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    // Próximo fechamento
    let nextClosing = new Date(currentYear, currentMonth, closingDay);
    if (nextClosing <= today) {
        nextClosing = new Date(currentYear, currentMonth + 1, closingDay);
    }
    
    // Próximo vencimento (pode ser no mês seguinte ao fechamento)
    let nextDue = new Date(nextClosing.getFullYear(), nextClosing.getMonth(), dueDay);
    if (dueDay <= closingDay) {
        // Vencimento no mês seguinte ao fechamento
        nextDue = new Date(nextClosing.getFullYear(), nextClosing.getMonth() + 1, dueDay);
    }
    
    // Melhor dia para compra (dia seguinte ao fechamento)
    const bestPurchase = new Date(nextClosing);
    bestPurchase.setDate(bestPurchase.getDate() + 1);
    
    return {
        nextClosing,
        nextDue,
        bestPurchase
    };
}

// Formatar data para DD/MMM
function formatDateShort(date) {
    const months = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 
                   'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'];
    const day = date.getDate().toString().padStart(2, '0');
    const month = months[date.getMonth()];
    return `${day}/${month}`;
}

// Mostrar Top Card de Próximo Fechamento
function showNextClosingAlert() {
    const activeCards = creditCardsState.cards.filter(card => card.is_active);
    if (activeCards.length === 0) return;
    
    const today = new Date();
    let nextCard = null;
    let minDays = Infinity;
    
    activeCards.forEach(card => {
        const cycleDates = calculateCycleDates(card.closing_day, card.due_day);
        const daysUntilClosing = Math.ceil((cycleDates.nextClosing - today) / (1000 * 60 * 60 * 24));
        
        if (daysUntilClosing < minDays) {
            minDays = daysUntilClosing;
            nextCard = { ...card, daysUntilClosing, nextClosing: cycleDates.nextClosing };
        }
    });
    
    if (nextCard) {
        const alertCard = document.getElementById('next-closing-card');
        const messageEl = document.getElementById('next-closing-message');
        
        const dayText = nextCard.daysUntilClosing === 1 ? 'amanhã' : `em ${nextCard.daysUntilClosing} dias`;
        messageEl.textContent = `${nextCard.name} fecha ${dayText} - ${formatDateShort(nextCard.nextClosing)}`;
        
        if (nextCard.daysUntilClosing <= 7) {
            alertCard.classList.add('urgent');
        }
        
        alertCard.style.display = 'block';
    }
}

// Criar card de cartão de crédito
function createCreditCardCard(card) {
    const usagePercentage = card.usage_percentage || 0;
    const usageClass = usagePercentage >= 80 ? 'danger' : usagePercentage >= 60 ? 'warning' : 'success';
    
    // Garantir que temos os dias necessários
    const closingDay = card.closing_day || 1;
    const dueDay = card.due_day || 10;
    
    // Calcular datas do ciclo
    const cycleDates = calculateCycleDates(closingDay, dueDay);
    
    return `
        <div class="credit-card-item ${card.is_active ? '' : 'inactive'}">
            <div class="card-header">
                <div class="card-icon">💳</div>
                <div class="card-info">
                    <h4 class="card-name">${card.name}</h4>
                    <p class="card-bank">${card.bank}</p>
                </div>
                <div class="card-actions">
                    <button class="btn-icon" onclick="viewCardReport(${card.id})" title="Ver Relatório">
                        📊
                    </button>
                    <button class="btn-icon" onclick="editCreditCard(${card.id})" title="Editar">
                        ✏️
                    </button>
                    <button class="btn-icon" onclick="showDeleteModal(${card.id})" title="Excluir">
                        🗑️
                    </button>
                </div>
            </div>
            
            <div class="card-limits">
                <div class="limit-info">
                    <div class="limit-label">Limite Total</div>
                    <div class="limit-value">${formatCurrency(card.credit_limit || 0)}</div>
                </div>
                <div class="limit-info">
                    <div class="limit-label">Disponível</div>
                    <div class="limit-value available">${formatCurrency(card.available_limit || 0)}</div>
                </div>
            </div>
            
            <div class="usage-section">
                <div class="usage-header">
                    <span class="usage-label">Uso do Limite</span>
                    <span class="usage-percentage ${usageClass}">${usagePercentage.toFixed(1)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${usageClass}" style="width: ${Math.min(usagePercentage, 100)}%"></div>
                </div>
            </div>
            
            <div class="card-cycle">
                <div class="cycle-row">
                    <div class="cycle-info">
                        <span class="cycle-label">Próximo Fechamento:</span>
                        <span class="cycle-value">${formatDateShort(cycleDates.nextClosing)}</span>
                    </div>
                </div>
                <div class="cycle-row">
                    <div class="cycle-info">
                        <span class="cycle-label">Próximo Vencimento:</span>
                        <span class="cycle-value">${formatDateShort(cycleDates.nextDue)}</span>
                    </div>
                </div>
                <div class="cycle-row">
                    <div class="cycle-info best-purchase">
                        <span class="cycle-label">Melhor Compra:</span>
                        <span class="cycle-value best">${formatDateShort(cycleDates.bestPurchase)}</span>
                    </div>
                </div>
            </div>
            
            <div class="card-footer">
                <div class="card-status">
                    <span class="status-indicator ${card.is_active ? 'active' : 'inactive'}">
                        ${card.is_active ? '🟢 Ativo' : '🔴 Inativo'}
                    </span>
                </div>
                <button class="btn btn-sm btn-secondary" onclick="viewCardDetails(${card.id})">
                    Ver Detalhes
                </button>
                <button class="btn btn-sm btn-pay" onclick="payInvoice(${card.id})">
                    💳 Pagar Fatura
                </button>
            </div>
        </div>
    `;
}

// Mostrar formulário de cartão
function showCreditCardForm(cardId = null) {
    const modal = document.getElementById('card-modal');
    const modalTitle = document.getElementById('modal-title');
    const form = document.getElementById('card-form');
    
    // Resetar formulário
    form.reset();
    clearFormErrors();
    
    if (cardId) {
        // Modo edição
        const card = creditCardsState.cards.find(c => c.id === cardId);
        if (card) {
            modalTitle.textContent = 'Editar Cartão';
            document.getElementById('card-name').value = card.name;
            document.getElementById('card-bank').value = card.bank;
            document.getElementById('credit-limit').value = card.credit_limit;
            document.getElementById('closing-day').value = card.closing_day;
            document.getElementById('due-day').value = card.due_day;
            document.getElementById('is-active').checked = card.is_active;
            creditCardsState.editingId = cardId;
        }
    } else {
        // Modo criação
        modalTitle.textContent = 'Novo Cartão';
        document.getElementById('is-active').checked = true;
        creditCardsState.editingId = null;
    }
    
    modalManager.openModal('card-modal');
}

// Fechar modal de cartão
function closeCreditCardModal() {
    modalManager.closeModal('card-modal');
    creditCardsState.editingId = null;
}

// Salvar cartão
async function saveCreditCard() {
    const form = document.getElementById('card-form');
    const saveBtn = document.getElementById('save-btn-text');
    
    // Coletar dados do formulário
    const cardData = {
        name: document.getElementById('card-name').value.trim(),
        bank: document.getElementById('card-bank').value.trim(),
        credit_limit: parseFloat(document.getElementById('credit-limit').value) || 0,
        closing_day: parseInt(document.getElementById('closing-day').value),
        due_day: parseInt(document.getElementById('due-day').value),
        is_active: document.getElementById('is-active').checked
    };
    
    // Validar dados
    if (!validateCardForm(cardData)) {
        return;
    }
    
    try {
        saveBtn.textContent = 'Salvando...';
        
        let response;
        if (creditCardsState.editingId) {
            // Atualizar cartão existente
            response = await api.request(`/financial/credit-cards/${creditCardsState.editingId}/`, {
                method: 'PUT',
                body: JSON.stringify(cardData)
            });
            showMessage('Cartão atualizado com sucesso!', 'success');
        } else {
            // Criar novo cartão
            response = await api.request('/financial/credit-cards/', {
                method: 'POST',
                body: JSON.stringify(cardData)
            });
            showMessage('Cartão criado com sucesso!', 'success');
        }
        
        // Fechar modal e recarregar lista
        closeCreditCardModal();
        await loadCreditCards();
        
    } catch (error) {
        console.error('Erro ao salvar cartão:', error);
        
        if (error.message.includes('400')) {
            // Erro de validação - mostrar erros específicos
            try {
                const errorData = JSON.parse(error.message.split('400: ')[1]);
                showFormErrors(errorData);
            } catch {
                showMessage('Dados inválidos. Verifique os campos.', 'error');
            }
        } else {
            showMessage('Erro ao salvar cartão: ' + error.message, 'error');
        }
    } finally {
        saveBtn.textContent = 'Salvar';
    }
}

// Validar formulário de cartão
function validateCardForm(data) {
    clearFormErrors();
    let isValid = true;
    
    if (!data.name) {
        showFieldError('name-error', 'Nome do cartão é obrigatório');
        isValid = false;
    }
    
    if (!data.bank) {
        showFieldError('bank-error', 'Banco é obrigatório');
        isValid = false;
    }
    
    if (data.credit_limit <= 0) {
        showFieldError('limit-error', 'Limite de crédito deve ser maior que zero');
        isValid = false;
    }
    
    if (!data.closing_day || data.closing_day < 1 || data.closing_day > 31) {
        showFieldError('closing-error', 'Dia de fechamento inválido');
        isValid = false;
    }
    
    if (!data.due_day || data.due_day < 1 || data.due_day > 31) {
        showFieldError('due-error', 'Dia de vencimento inválido');
        isValid = false;
    }
    
    return isValid;
}

// Visualizar relatório do cartão
function viewCardReport(cardId) {
    const card = creditCardsState.cards.find(c => c.id === cardId);
    if (!card) {
        showMessage('Cartão não encontrado', 'error');
        return;
    }
    
    // Redirecionar para página de relatórios com filtro do cartão
    const reportUrl = `reports?card=${cardId}&card_name=${encodeURIComponent(card.name)}`;
    window.location.href = reportUrl;
}

// Editar cartão
function editCreditCard(cardId) {
    showCreditCardForm(cardId);
}

// Mostrar modal de exclusão
function showDeleteModal(cardId) {
    const card = creditCardsState.cards.find(c => c.id === cardId);
    if (!card) return;
    
    document.getElementById('delete-card-name').textContent = card.name;
    creditCardsState.currentCard = card;
    
    modalManager.openModal('delete-modal');
}

// Fechar modal de exclusão
function closeDeleteModal() {
    modalManager.closeModal('delete-modal');
    creditCardsState.currentCard = null;
}

// Confirmar exclusão
async function confirmDelete() {
    if (!creditCardsState.currentCard) return;
    
    try {
        await api.request(`/financial/credit-cards/${creditCardsState.currentCard.id}/`, {
            method: 'DELETE'
        });
        
        showMessage('Cartão excluído com sucesso!', 'success');
        closeDeleteModal();
        await loadCreditCards();
        
    } catch (error) {
        console.error('Erro ao excluir cartão:', error);
        showMessage('Erro ao excluir cartão: ' + error.message, 'error');
    }
}

// Ver detalhes do cartão
function viewCardDetails(cardId) {
    const card = creditCardsState.cards.find(c => c.id === cardId);
    if (!card) return;
    
    // Por enquanto, mostrar informações em um alert
    // Futuramente, pode ser uma página separada ou modal
    alert(`
Detalhes do Cartão: ${card.name}

Banco: ${card.bank}
Limite Total: ${formatCurrency(card.credit_limit)}
Limite Disponível: ${formatCurrency(card.available_limit)}
Uso: ${(card.usage_percentage || 0).toFixed(1)}%

Fechamento: Dia ${card.closing_day}
Vencimento: Dia ${card.due_day}
Status: ${card.is_active ? 'Ativo' : 'Inativo'}

Criado em: ${new Date(card.created_at).toLocaleDateString('pt-BR')}
    `);
}

// Filtrar por status
function handleStatusFilter(event) {
    creditCardsState.filters.status = event.target.value;
    renderCardsList();
}

// Atualizar cartões
async function refreshCreditCards() {
    showMessage('Atualizando cartões...', 'info');
    await loadCreditCards();
    showMessage('Cartões atualizados!', 'success');
}

// Pagar fatura do cartão
function payInvoice(cardId) {
    const card = creditCardsState.cards.find(c => c.id === cardId);
    if (!card) return;
    
    const cycleDates = calculateCycleDates(card.closing_day, card.due_day);
    const invoiceAmount = (card.credit_limit - card.available_limit) || 0;
    
    if (invoiceAmount <= 0) {
        showMessage('Não há fatura para pagar neste cartão.', 'info');
        return;
    }
    
    const confirmPay = confirm(`
Pagar fatura do cartão: ${card.name}
Valor: ${formatCurrency(invoiceAmount)}
Vencimento: ${formatDateShort(cycleDates.nextDue)}

Deseja prosseguir com o pagamento?
    `);
    
    if (confirmPay) {
        showMessage('Redirecionando para pagamento...', 'info');
        // Aqui seria redirecionado para página de pagamento ou integração bancária
        setTimeout(() => {
            showMessage('Funcionalidade de pagamento será implementada em breve!', 'warning');
        }, 1500);
    }
}

// Carregar dados mockados para demonstração
function loadMockCreditCards() {
    creditCardsState.cards = [
        {
            id: 1,
            name: 'Cartão Visa Gold',
            bank: 'Banco do Brasil',
            credit_limit: 3000.00,
            available_limit: 2866.10,
            usage_percentage: 4.46,
            closing_day: 29,
            due_day: 5,
            is_active: true,
            created_at: '2024-01-15T10:00:00Z'
        },
        {
            id: 2,
            name: 'Mastercard Platinum',
            bank: 'Itaú',
            credit_limit: 8000.00,
            available_limit: 1500.00,
            usage_percentage: 81.25,
            closing_day: 15,
            due_day: 25,
            is_active: true,
            created_at: '2024-02-01T14:30:00Z'
        },
        {
            id: 3,
            name: 'Cartão Elo',
            bank: 'Caixa Econômica',
            credit_limit: 2500.00,
            available_limit: 2300.00,
            usage_percentage: 8.0,
            closing_day: 10,
            due_day: 20,
            is_active: true,
            created_at: '2024-03-10T09:15:00Z'
        }
    ];
    
    renderCardsList();
    calculateLocalSummary();
    showNextClosingAlert();
}

// Utilitários
function formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount || 0);
}

// Skeleton Loading Functions
function showSkeletonLoading(show) {
    const container = document.getElementById('cards-list');
    if (!container) return;
    
    if (show) {
        // Usar SkeletonLoader global se disponível, senão usar implementação local
        if (window.SkeletonLoader) {
            container.innerHTML = `
                <div class="cards-grid">
                    ${Array(3).fill(0).map(() => window.SkeletonLoader.createCreditCardSkeleton()).join('')}
                </div>
            `;
        } else {
            container.innerHTML = createCardsSkeletonHTML();
        }
    }
}

function showSummarySkeletonLoading(show) {
    if (show) {
        const summaryElements = {
            'total-cards': document.getElementById('total-cards'),
            'total-limit': document.getElementById('total-limit'),
            'available-limit': document.getElementById('available-limit'),
            'highest-risk': document.getElementById('highest-risk')
        };
        
        Object.values(summaryElements).forEach(el => {
            if (el) {
                if (window.SkeletonLoader) {
                    el.innerHTML = window.SkeletonLoader.createSummarySkeleton();
                } else {
                    el.innerHTML = '<div class="skeleton-text"></div>';
                }
            }
        });
    }
}

function createCardsSkeletonHTML() {
    return `
        <div class="cards-grid">
            ${Array(3).fill(0).map(() => createCardSkeletonHTML()).join('')}
        </div>
    `;
}

function createCardSkeletonHTML() {
    return `
        <div class="credit-card-item skeleton-card">
            <div class="card-header">
                <div class="skeleton-icon"></div>
                <div class="card-info">
                    <div class="skeleton-text skeleton-title"></div>
                    <div class="skeleton-text skeleton-subtitle"></div>
                </div>
                <div class="card-actions">
                    <div class="skeleton-button"></div>
                    <div class="skeleton-button"></div>
                    <div class="skeleton-button"></div>
                </div>
            </div>
            
            <div class="card-limits">
                <div class="limit-info">
                    <div class="skeleton-text skeleton-small"></div>
                    <div class="skeleton-text skeleton-value"></div>
                </div>
                <div class="limit-info">
                    <div class="skeleton-text skeleton-small"></div>
                    <div class="skeleton-text skeleton-value"></div>
                </div>
            </div>
            
            <div class="usage-section">
                <div class="usage-header">
                    <div class="skeleton-text skeleton-small"></div>
                    <div class="skeleton-text skeleton-percentage"></div>
                </div>
                <div class="skeleton-progress-bar"></div>
            </div>
            
            <div class="card-cycle">
                <div class="cycle-row">
                    <div class="skeleton-text skeleton-cycle"></div>
                </div>
                <div class="cycle-row">
                    <div class="skeleton-text skeleton-cycle"></div>
                </div>
                <div class="cycle-row">
                    <div class="skeleton-text skeleton-cycle"></div>
                </div>
            </div>
            
            <div class="card-footer">
                <div class="skeleton-text skeleton-status"></div>
                <div class="skeleton-button skeleton-btn-detail"></div>
                <div class="skeleton-button skeleton-btn-pay"></div>
            </div>
        </div>
    `;
}

function showLoading(show) {
    const loader = document.getElementById('cards-loading');
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

console.log('Credit-cards.js carregado com sucesso!');