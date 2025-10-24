import { useState, useEffect, useCallback } from 'react';
import transactionsService from '../services/transactions';

export const useTransactions = (initialFilters = {}) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null
  });

  const loadTransactions = useCallback(async (newFilters = filters) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await transactionsService.getTransactions(newFilters);
      
      if (response.results) {
        // Resposta paginada
        setTransactions(response.results);
        setPagination({
          count: response.count,
          next: response.next,
          previous: response.previous
        });
      } else {
        // Resposta simples
        setTransactions(response);
        setPagination({ count: response.length, next: null, previous: null });
      }
    } catch (err) {
      setError(err.message || 'Erro ao carregar transações');
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const createTransaction = async (data) => {
    try {
      const newTransaction = await transactionsService.createTransaction(data);
      setTransactions(prev => [newTransaction, ...prev]);
      return newTransaction;
    } catch (err) {
      throw new Error(err.response?.data?.message || 'Erro ao criar transação');
    }
  };

  const updateTransaction = async (id, data) => {
    try {
      const updatedTransaction = await transactionsService.updateTransaction(id, data);
      setTransactions(prev => 
        prev.map(transaction => 
          transaction.id === id ? updatedTransaction : transaction
        )
      );
      return updatedTransaction;
    } catch (err) {
      throw new Error(err.response?.data?.message || 'Erro ao atualizar transação');
    }
  };

  const deleteTransaction = async (id) => {
    try {
      await transactionsService.deleteTransaction(id);
      setTransactions(prev => prev.filter(transaction => transaction.id !== id));
    } catch (err) {
      throw new Error(err.response?.data?.message || 'Erro ao excluir transação');
    }
  };

  const applyFilters = (newFilters) => {
    setFilters(newFilters);
    loadTransactions(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters = {};
    setFilters(emptyFilters);
    loadTransactions(emptyFilters);
  };

  useEffect(() => {
    loadTransactions();
  }, [loadTransactions]);

  return {
    transactions,
    loading,
    error,
    filters,
    pagination,
    loadTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    applyFilters,
    clearFilters
  };
};

export const useTransactionSummary = (filters = {}) => {
  const [summary, setSummary] = useState({
    total_income: 0,
    total_expense: 0,
    balance: 0,
    transaction_count: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadSummary = useCallback(async (newFilters = filters) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await transactionsService.getSummary(newFilters);
      setSummary(data);
    } catch (err) {
      setError(err.message || 'Erro ao carregar resumo');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  return {
    summary,
    loading,
    error,
    loadSummary
  };
};

export const useCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadCategories = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await transactionsService.getCategories();
      setCategories(data.results || data);
    } catch (err) {
      setError(err.message || 'Erro ao carregar categorias');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  return {
    categories,
    loading,
    error,
    loadCategories
  };
};

export const useTags = () => {
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadTags = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await transactionsService.getTags();
      setTags(data.results || data);
    } catch (err) {
      setError(err.message || 'Erro ao carregar tags');
    } finally {
      setLoading(false);
    }
  }, []);

  const createTag = async (data) => {
    try {
      const newTag = await transactionsService.createTag(data);
      setTags(prev => [...prev, newTag]);
      return newTag;
    } catch (err) {
      throw new Error(err.response?.data?.message || 'Erro ao criar tag');
    }
  };

  const updateTag = async (id, data) => {
    try {
      const updatedTag = await transactionsService.updateTag(id, data);
      setTags(prev => 
        prev.map(tag => tag.id === id ? updatedTag : tag)
      );
      return updatedTag;
    } catch (err) {
      throw new Error(err.response?.data?.message || 'Erro ao atualizar tag');
    }
  };

  const deleteTag = async (id) => {
    try {
      await transactionsService.deleteTag(id);
      setTags(prev => prev.filter(tag => tag.id !== id));
    } catch (err) {
      throw new Error(err.response?.data?.message || 'Erro ao excluir tag');
    }
  };

  useEffect(() => {
    loadTags();
  }, [loadTags]);

  return {
    tags,
    loading,
    error,
    loadTags,
    createTag,
    updateTag,
    deleteTag
  };
};