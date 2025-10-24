/**
 * Sistema de Gerenciamento de Metas - Nossa Grana
 */

// Estado global das metas
let goalsState = {
    goals: [],
    currentGoal: null,
    editingId: null,
    contributingToId: null,
    filters: {
        status: ''
    }
};

// Inicializar página de metas
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Inicializando página de metas...');
    
    // Verificar autenticação
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // Configurar event listeners
    setupEventListeners();
    
    // Configurar data mínima para meta (amanhã)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('goal-target-date').min = tomorrow.toISOString().split('T')[0];
    
    // Configurar data atual para contribuição
    document.getElementById('contribute-date').value = new Date().toISOString().split('T')[0];
    
    // Carregar dados iniciais
    await loadGoals();
});

// Configurar event listeners
function setupEventListeners() {
    // Filtro por status
    const statusFilter = document.getElementById('goal-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', handleStatusFilter);
    }

    // Formulário de meta
    const goalForm = document.getElementById('goal-form');
    if (goalForm) {
        goalForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveGoal();
        });
    }

    // Formulário de contribuição
    const contributeForm = document.getElementById('contribute-form');
    if (contributeForm) {
        contributeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processContribution();
        });
    }

    // Fechar modais ao clicar fora
    window.addEventListener('click', function(event) {
        const goalModal = document.getElementById('goal-modal');
        const contributeModal = document.getElementById('contribute-modal');
        const deleteModal = document.getElementById('delete-modal');
        
        if (event.target === goalModal) {
            closeGoalModal();
        }
        if (event.target === contributeModal) {
            closeContributeModal();
        }
        if (event.target === deleteModal) {
            closeDeleteModal();
        }
    });
}// Carre
gar metas
async function loadGoals() {
    try {
        showLoading(true);
        
        // Carregar metas da API
        const response = await api.request('/goals/goals/');
        goalsState.goals = response.results || response;
        
        // Carregar resumo
        await loadGoalsSummary();
        
        // Renderizar lista
        renderGoalsList();
        
    } catch (error) {
        console.error('Erro ao carregar metas:', error);
        showMessage('Erro ao carregar metas: ' + error.message, 'error');
        
        // Usar dados mockados para demonstração
        loadMockGoals();
    } finally {
        showLoading(false);
    }
}

// Carregar resumo das metas
async function loadGoalsSummary() {
    try {
        const response = await api.request('/goals/goals/summary/');
        updateSummaryCards(response);
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        // Calcular resumo localmente
        calculateLocalSummary();
    }
}

// Atualizar cards de resumo
function updateSummaryCards(summary) {
    const totalGoalsEl = document.getElementById('total-goals');
    const achievedGoalsEl = document.getElementById('achieved-goals');
    const totalSavedEl = document.getElementById('total-saved');
    const averageProgressEl = document.getElementById('average-progress');
    
    if (totalGoalsEl) totalGoalsEl.textContent = summary.total_goals || 0;
    if (achievedGoalsEl) achievedGoalsEl.textContent = summary.achieved_goals || 0;
    if (totalSavedEl) totalSavedEl.textContent = formatCurrency(summary.total_current_amount || 0);
    if (averageProgressEl) averageProgressEl.textContent = `${(summary.average_completion_percentage || 0).toFixed(1)}%`;
}

// Calcular resumo localmente
function calculateLocalSummary() {
    const totalGoals = goalsState.goals.length;
    const achievedGoals = goalsState.goals.filter(goal => goal.achieved).length;
    const totalSaved = goalsState.goals.reduce((sum, goal) => sum + parseFloat(goal.current_amount || 0), 0);
    const averageProgress = totalGoals > 0 ? 
        goalsState.goals.reduce((sum, goal) => sum + (goal.percentage_completed || 0), 0) / totalGoals : 0;
    
    updateSummaryCards({
        total_goals: totalGoals,
        achieved_goals: achievedGoals,
        total_current_amount: totalSaved,
        average_completion_percentage: averageProgress
    });
}

// Renderizar lista de metas
function renderGoalsList() {
    const container = document.getElementById('goals-list');
    if (!container) return;
    
    let filteredGoals = goalsState.goals;
    
    // Aplicar filtros
    if (goalsState.filters.status === 'active') {
        filteredGoals = filteredGoals.filter(goal => !goal.achieved);
    } else if (goalsState.filters.status === 'achieved') {
        filteredGoals = filteredGoals.filter(goal => goal.achieved);
    } else if (goalsState.filters.status === 'overdue') {
        filteredGoals = filteredGoals.filter(goal => goal.is_overdue);
    }
    
    if (filteredGoals.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🎯</div>
                <h3>Nenhuma meta encontrada</h3>
                <p>Crie sua primeira meta para começar a poupar com objetivo!</p>
                <button class="btn btn-primary" onclick="showGoalForm()">
                    <span class="btn-icon">➕</span>
                    Criar Primeira Meta
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="goals-grid">
            ${filteredGoals.map(goal => createGoalCard(goal)).join('')}
        </div>
    `;
}// 
Criar card de meta
function createGoalCard(goal) {
    const progressPercentage = goal.percentage_completed || 0;
    const progressClass = progressPercentage >= 100 ? 'success' : progressPercentage >= 75 ? 'warning' : 'primary';
    const statusClass = goal.achieved ? 'achieved' : goal.is_overdue ? 'overdue' : 'active';
    
    const daysRemaining = goal.days_remaining || 0;
    const timeInfo = goal.achieved ? 
        `✅ Meta atingida!` : 
        goal.is_overdue ? 
            `⚠️ Atrasada` : 
            `📅 ${daysRemaining} dias restantes`;
    
    return `
        <div class="goal-card ${statusClass}">
            <div class="goal-header">
                <div class="goal-info">
                    <h4 class="goal-name">${goal.name}</h4>
                    <p class="goal-description">${goal.description || 'Sem descrição'}</p>
                </div>
                <div class="goal-actions">
                    ${!goal.achieved ? `
                        <button class="btn-icon" onclick="showContributeModal(${goal.id})" title="Contribuir">
                            💰
                        </button>
                    ` : ''}
                    <button class="btn-icon" onclick="editGoal(${goal.id})" title="Editar">
                        ✏️
                    </button>
                    <button class="btn-icon" onclick="showDeleteModal(${goal.id})" title="Excluir">
                        🗑️
                    </button>
                </div>
            </div>
            
            <div class="goal-progress">
                <div class="progress-info">
                    <div class="progress-amounts">
                        <span class="current-amount">${goal.current_amount_formatted || formatCurrency(goal.current_amount)}</span>
                        <span class="target-amount">de ${goal.target_amount_formatted || formatCurrency(goal.target_amount)}</span>
                    </div>
                    <div class="progress-percentage">${progressPercentage.toFixed(1)}%</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill ${progressClass}" style="width: ${Math.min(progressPercentage, 100)}%"></div>
                </div>
            </div>
            
            <div class="goal-footer">
                <div class="goal-timeline">
                    <span class="time-info">${timeInfo}</span>
                    <span class="target-date">Meta: ${formatDate(goal.target_date)}</span>
                </div>
                ${goal.estimated_completion_date && !goal.achieved ? `
                    <div class="goal-estimate">
                        <span class="estimate-info">📈 Previsão: ${formatDate(goal.estimated_completion_date)}</span>
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Mostrar formulário de meta
function showGoalForm(goalId = null) {
    const modal = document.getElementById('goal-modal');
    const modalTitle = document.getElementById('modal-title');
    const form = document.getElementById('goal-form');
    
    // Resetar formulário
    form.reset();
    clearFormErrors();
    
    // Configurar data mínima
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('goal-target-date').min = tomorrow.toISOString().split('T')[0];
    
    if (goalId) {
        // Modo edição
        const goal = goalsState.goals.find(g => g.id === goalId);
        if (goal) {
            modalTitle.textContent = 'Editar Meta';
            document.getElementById('goal-name').value = goal.name;
            document.getElementById('goal-description').value = goal.description || '';
            document.getElementById('goal-target-amount').value = goal.target_amount;
            document.getElementById('goal-target-date').value = goal.target_date;
            goalsState.editingId = goalId;
        }
    } else {
        // Modo criação
        modalTitle.textContent = 'Nova Meta';
        goalsState.editingId = null;
    }
    
    modal.style.display = 'flex';
}

// Fechar modal de meta
function closeGoalModal() {
    const modal = document.getElementById('goal-modal');
    modal.style.display = 'none';
    goalsState.editingId = null;
}// Sa
lvar meta
async function saveGoal() {
    const form = document.getElementById('goal-form');
    const saveBtn = document.getElementById('save-btn-text');
    
    // Coletar dados do formulário
    const goalData = {
        name: document.getElementById('goal-name').value.trim(),
        description: document.getElementById('goal-description').value.trim(),
        target_amount: parseFloat(document.getElementById('goal-target-amount').value) || 0,
        target_date: document.getElementById('goal-target-date').value
    };
    
    // Validar dados
    if (!validateGoalForm(goalData)) {
        return;
    }
    
    try {
        saveBtn.textContent = 'Salvando...';
        
        let response;
        if (goalsState.editingId) {
            // Atualizar meta existente
            response = await api.request(`/goals/goals/${goalsState.editingId}/`, {
                method: 'PUT',
                body: JSON.stringify(goalData)
            });
            showMessage('Meta atualizada com sucesso!', 'success');
        } else {
            // Criar nova meta
            response = await api.request('/goals/goals/', {
                method: 'POST',
                body: JSON.stringify(goalData)
            });
            showMessage('Meta criada com sucesso!', 'success');
        }
        
        // Fechar modal e recarregar lista
        closeGoalModal();
        await loadGoals();
        
    } catch (error) {
        console.error('Erro ao salvar meta:', error);
        
        if (error.message.includes('400')) {
            // Erro de validação - mostrar erros específicos
            try {
                const errorData = JSON.parse(error.message.split('400: ')[1]);
                showFormErrors(errorData);
            } catch {
                showMessage('Dados inválidos. Verifique os campos.', 'error');
            }
        } else {
            showMessage('Erro ao salvar meta: ' + error.message, 'error');
        }
    } finally {
        saveBtn.textContent = 'Salvar';
    }
}

// Validar formulário de meta
function validateGoalForm(data) {
    clearFormErrors();
    let isValid = true;
    
    if (!data.name) {
        showFieldError('name-error', 'Nome da meta é obrigatório');
        isValid = false;
    }
    
    if (data.target_amount <= 0) {
        showFieldError('target-amount-error', 'Valor alvo deve ser maior que zero');
        isValid = false;
    }
    
    if (!data.target_date) {
        showFieldError('target-date-error', 'Data objetivo é obrigatória');
        isValid = false;
    } else {
        const targetDate = new Date(data.target_date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (targetDate <= today) {
            showFieldError('target-date-error', 'Data objetivo deve ser futura');
            isValid = false;
        }
    }
    
    return isValid;
}

// Mostrar modal de contribuição
function showContributeModal(goalId) {
    const goal = goalsState.goals.find(g => g.id === goalId);
    if (!goal) return;
    
    if (goal.achieved) {
        showMessage('Esta meta já foi atingida!', 'warning');
        return;
    }
    
    goalsState.contributingToId = goalId;
    
    // Atualizar informações da meta
    const goalInfo = document.getElementById('contribute-goal-info');
    goalInfo.innerHTML = `
        <div class="goal-summary">
            <h4>${goal.name}</h4>
            <div class="goal-progress-summary">
                <div class="amounts">
                    <span>Atual: ${goal.current_amount_formatted || formatCurrency(goal.current_amount)}</span>
                    <span>Meta: ${goal.target_amount_formatted || formatCurrency(goal.target_amount)}</span>
                </div>
                <div class="remaining">
                    <span>Restante: ${goal.remaining_amount_formatted || formatCurrency(goal.remaining_amount || 0)}</span>
                </div>
            </div>
        </div>
    `;
    
    // Resetar formulário
    document.getElementById('contribute-form').reset();
    document.getElementById('contribute-date').value = new Date().toISOString().split('T')[0];
    clearContributeErrors();
    
    const modal = document.getElementById('contribute-modal');
    modal.style.display = 'flex';
}

// Fechar modal de contribuição
function closeContributeModal() {
    const modal = document.getElementById('contribute-modal');
    modal.style.display = 'none';
    goalsState.contributingToId = null;
}//
 Processar contribuição
async function processContribution() {
    const contributeBtn = document.getElementById('contribute-btn-text');
    
    // Coletar dados do formulário
    const contributionData = {
        amount: parseFloat(document.getElementById('contribute-amount').value) || 0,
        description: document.getElementById('contribute-description').value.trim(),
        date: document.getElementById('contribute-date').value
    };
    
    // Validar dados
    if (!validateContributionForm(contributionData)) {
        return;
    }
    
    try {
        contributeBtn.textContent = 'Processando...';
        
        // Fazer contribuição
        const response = await api.request(`/goals/goals/${goalsState.contributingToId}/contribute/`, {
            method: 'POST',
            body: JSON.stringify(contributionData)
        });
        
        const result = response;
        
        if (result.goal_achieved) {
            showMessage('🎉 Parabéns! Você atingiu sua meta!', 'success');
        } else {
            showMessage('Contribuição adicionada com sucesso!', 'success');
        }
        
        // Fechar modal e recarregar lista
        closeContributeModal();
        await loadGoals();
        
    } catch (error) {
        console.error('Erro ao processar contribuição:', error);
        
        if (error.message.includes('400')) {
            try {
                const errorData = JSON.parse(error.message.split('400: ')[1]);
                showContributeErrors(errorData);
            } catch {
                showMessage('Dados inválidos. Verifique os campos.', 'error');
            }
        } else {
            showMessage('Erro ao processar contribuição: ' + error.message, 'error');
        }
    } finally {
        contributeBtn.textContent = 'Contribuir';
    }
}

// Validar formulário de contribuição
function validateContributionForm(data) {
    clearContributeErrors();
    let isValid = true;
    
    if (data.amount <= 0) {
        showContributeFieldError('contribute-amount-error', 'Valor deve ser maior que zero');
        isValid = false;
    }
    
    if (!data.date) {
        showContributeFieldError('contribute-date-error', 'Data é obrigatória');
        isValid = false;
    }
    
    return isValid;
}

// Editar meta
function editGoal(goalId) {
    showGoalForm(goalId);
}

// Mostrar modal de exclusão
function showDeleteModal(goalId) {
    const goal = goalsState.goals.find(g => g.id === goalId);
    if (!goal) return;
    
    document.getElementById('delete-goal-name').textContent = goal.name;
    goalsState.currentGoal = goal;
    
    const modal = document.getElementById('delete-modal');
    modal.style.display = 'flex';
}

// Fechar modal de exclusão
function closeDeleteModal() {
    const modal = document.getElementById('delete-modal');
    modal.style.display = 'none';
    goalsState.currentGoal = null;
}

// Confirmar exclusão
async function confirmDelete() {
    if (!goalsState.currentGoal) return;
    
    try {
        await api.request(`/goals/goals/${goalsState.currentGoal.id}/`, {
            method: 'DELETE'
        });
        
        showMessage('Meta excluída com sucesso!', 'success');
        closeDeleteModal();
        await loadGoals();
        
    } catch (error) {
        console.error('Erro ao excluir meta:', error);
        showMessage('Erro ao excluir meta: ' + error.message, 'error');
    }
}

// Filtrar por status
function handleStatusFilter(event) {
    goalsState.filters.status = event.target.value;
    renderGoalsList();
}

// Atualizar metas
async function refreshGoals() {
    showMessage('Atualizando metas...', 'info');
    await loadGoals();
    showMessage('Metas atualizadas!', 'success');
}// 
Carregar dados mockados para demonstração
function loadMockGoals() {
    goalsState.goals = [
        {
            id: 1,
            name: 'Viagem para Europa',
            description: 'Economizar para viagem dos sonhos',
            target_amount: 15000.00,
            current_amount: 8500.00,
            target_date: '2024-12-31',
            achieved: false,
            percentage_completed: 56.7,
            days_remaining: 245,
            is_overdue: false,
            estimated_completion_date: '2024-11-15'
        },
        {
            id: 2,
            name: 'Reserva de Emergência',
            description: 'Fundo para emergências',
            target_amount: 10000.00,
            current_amount: 10000.00,
            target_date: '2024-06-30',
            achieved: true,
            percentage_completed: 100,
            days_remaining: 0,
            is_overdue: false
        },
        {
            id: 3,
            name: 'Carro Novo',
            description: 'Entrada para carro 0km',
            target_amount: 25000.00,
            current_amount: 5200.00,
            target_date: '2024-03-15',
            achieved: false,
            percentage_completed: 20.8,
            days_remaining: -30,
            is_overdue: true
        }
    ];
    
    renderGoalsList();
    calculateLocalSummary();
}

// Utilitários
function formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(amount || 0);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR');
}

function showLoading(show) {
    const loader = document.getElementById('goals-loading');
    if (loader) {
        loader.style.display = show ? 'flex' : 'none';
    }
}

function showMessage(message, type = 'info') {
    // Implementação igual às outras páginas
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

function clearContributeErrors() {
    const errorElements = ['contribute-amount-error', 'contribute-description-error', 'contribute-date-error'];
    errorElements.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.textContent = '';
    });
}

function showFieldError(fieldId, message) {
    const errorElement = document.getElementById(fieldId);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

function showContributeFieldError(fieldId, message) {
    const errorElement = document.getElementById(fieldId);
    if (errorElement) {
        errorElement.textContent = message;
    }
}

function showFormErrors(errors) {
    Object.keys(errors).forEach(field => {
        const errorId = `${field.replace('_', '-')}-error`;
        const message = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
        showFieldError(errorId, message);
    });
}

function showContributeErrors(errors) {
    Object.keys(errors).forEach(field => {
        let errorId = '';
        switch (field) {
            case 'amount':
                errorId = 'contribute-amount-error';
                break;
            case 'description':
                errorId = 'contribute-description-error';
                break;
            case 'date':
                errorId = 'contribute-date-error';
                break;
            case 'non_field_errors':
                showMessage(Array.isArray(errors[field]) ? errors[field][0] : errors[field], 'error');
                return;
        }
        
        if (errorId) {
            const message = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
            showContributeFieldError(errorId, message);
        }
    });
}

console.log('Goals.js carregado com sucesso!');