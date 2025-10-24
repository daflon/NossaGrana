import api from './api';

const transactionsService = {
  // Listar transações com filtros
  async getTransactions(filters = {}) {
    const params = new URLSearchParams();
    
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
        if (Array.isArray(filters[key])) {
          filters[key].forEach(value => params.append(key, value));
        } else {
          params.append(key, filters[key]);
        }
      }
    });

    const response = await api.get(`/transactions/?${params.toString()}`);
    return response.data;
  },

  // Obter transação por ID
  async getTransaction(id) {
    const response = await api.get(`/transactions/${id}/`);
    return response.data;
  },

  // Criar nova transação
  async createTransaction(data) {
    const response = await api.post('/transactions/', data);
    return response.data;
  },

  // Atualizar transação
  async updateTransaction(id, data) {
    const response = await api.put(`/transactions/${id}/`, data);
    return response.data;
  },

  // Deletar transação
  async deleteTransaction(id) {
    await api.delete(`/transactions/${id}/`);
  },

  // Obter resumo financeiro
  async getSummary(filters = {}) {
    const params = new URLSearchParams();
    
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
        params.append(key, filters[key]);
      }
    });

    const response = await api.get(`/transactions/summary/?${params.toString()}`);
    return response.data;
  },

  // Obter transações por categoria
  async getByCategory(filters = {}) {
    const params = new URLSearchParams();
    
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
        params.append(key, filters[key]);
      }
    });

    const response = await api.get(`/transactions/by_category/?${params.toString()}`);
    return response.data;
  },

  // Criar múltiplas transações
  async bulkCreate(transactions) {
    const response = await api.post('/transactions/bulk_create/', transactions);
    return response.data;
  },

  // Obter categorias
  async getCategories() {
    const response = await api.get('/categories/');
    return response.data;
  },

  // Obter tags
  async getTags() {
    const response = await api.get('/tags/');
    return response.data;
  },

  // Criar tag
  async createTag(data) {
    const response = await api.post('/tags/', data);
    return response.data;
  },

  // Atualizar tag
  async updateTag(id, data) {
    const response = await api.put(`/tags/${id}/`, data);
    return response.data;
  },

  // Deletar tag
  async deleteTag(id) {
    await api.delete(`/tags/${id}/`);
  }
};

export default transactionsService;