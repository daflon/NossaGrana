import api from './api';

const BUDGETS_ENDPOINT = '/budgets/budgets';
const BUDGET_STATUS_ENDPOINT = '/budgets/status';

export const budgetService = {
  // Listar orçamentos com filtros opcionais
  async getBudgets(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.month) params.append('month', filters.month);
    if (filters.category) params.append('category', filters.category);
    if (filters.status) params.append('status', filters.status);
    
    const queryString = params.toString();
    const url = queryString ? `${BUDGETS_ENDPOINT}/?${queryString}` : `${BUDGETS_ENDPOINT}/`;
    
    const response = await api.get(url);
    return response.data;
  },

  // Obter orçamento específico
  async getBudget(id) {
    const response = await api.get(`${BUDGETS_ENDPOINT}/${id}/`);
    return response.data;
  },

  // Criar novo orçamento
  async createBudget(budgetData) {
    const response = await api.post(`${BUDGETS_ENDPOINT}/`, budgetData);
    return response.data;
  },

  // Atualizar orçamento
  async updateBudget(id, budgetData) {
    const response = await api.put(`${BUDGETS_ENDPOINT}/${id}/`, budgetData);
    return response.data;
  },

  // Atualizar parcialmente orçamento
  async patchBudget(id, budgetData) {
    const response = await api.patch(`${BUDGETS_ENDPOINT}/${id}/`, budgetData);
    return response.data;
  },

  // Deletar orçamento
  async deleteBudget(id) {
    await api.delete(`${BUDGETS_ENDPOINT}/${id}/`);
  },

  // Obter orçamentos do mês atual
  async getCurrentMonthBudgets() {
    const response = await api.get(`${BUDGETS_ENDPOINT}/current_month/`);
    return response.data;
  },

  // Obter categorias sem orçamento
  async getCategoriesWithoutBudget(month) {
    const params = month ? `?month=${month}` : '';
    const response = await api.get(`${BUDGETS_ENDPOINT}/categories_without_budget/${params}`);
    return response.data;
  },

  // Obter status dos orçamentos
  async getBudgetStatus(month) {
    const params = month ? `?month=${month}` : '';
    const response = await api.get(`${BUDGET_STATUS_ENDPOINT}/${params}`);
    return response.data;
  },

  // Utilitários para formatação
  formatCurrency(amount) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(amount);
  },

  formatMonth(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('pt-BR', { 
      month: '2-digit', 
      year: 'numeric' 
    });
  },

  getCurrentMonth() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    return `${year}-${month}`;
  },

  getFirstDayOfMonth(year, month) {
    return `${year}-${String(month).padStart(2, '0')}-01`;
  }
};

export default budgetService;