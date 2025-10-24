import { useState, useEffect, useCallback } from 'react';
import budgetService from '../services/budgets';

export const useBudgets = (initialFilters = {}) => {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState(initialFilters);

  // Carregar orçamentos
  const loadBudgets = useCallback(async (customFilters = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const filtersToUse = customFilters || filters;
      const data = await budgetService.getBudgets(filtersToUse);
      setBudgets(data);
    } catch (err) {
      setError(err.response?.data?.message || 'Erro ao carregar orçamentos');
      console.error('Erro ao carregar orçamentos:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Criar orçamento
  const createBudget = async (budgetData) => {
    setLoading(true);
    setError(null);
    
    try {
      const newBudget = await budgetService.createBudget(budgetData);
      setBudgets(prev => [...prev, newBudget]);
      return newBudget;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.message || 
                          'Erro ao criar orçamento';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar orçamento
  const updateBudget = async (id, budgetData) => {
    setLoading(true);
    setError(null);
    
    try {
      const updatedBudget = await budgetService.updateBudget(id, budgetData);
      setBudgets(prev => prev.map(budget => 
        budget.id === id ? updatedBudget : budget
      ));
      return updatedBudget;
    } catch (err) {
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.message || 
                          'Erro ao atualizar orçamento';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Deletar orçamento
  const deleteBudget = async (id) => {
    setLoading(true);
    setError(null);
    
    try {
      await budgetService.deleteBudget(id);
      setBudgets(prev => prev.filter(budget => budget.id !== id));
    } catch (err) {
      const errorMessage = err.response?.data?.error || 
                          err.response?.data?.message || 
                          'Erro ao deletar orçamento';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Atualizar filtros
  const updateFilters = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  // Limpar filtros
  const clearFilters = () => {
    setFilters({});
  };

  // Carregar orçamentos quando filtros mudarem
  useEffect(() => {
    loadBudgets();
  }, [loadBudgets]);

  return {
    budgets,
    loading,
    error,
    filters,
    loadBudgets,
    createBudget,
    updateBudget,
    deleteBudget,
    updateFilters,
    clearFilters,
    setError
  };
};

export const useBudgetStatus = (month = null) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadStatus = useCallback(async (customMonth = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const monthToUse = customMonth || month;
      const data = await budgetService.getBudgetStatus(monthToUse);
      setStatus(data);
    } catch (err) {
      setError(err.response?.data?.message || 'Erro ao carregar status dos orçamentos');
      console.error('Erro ao carregar status:', err);
    } finally {
      setLoading(false);
    }
  }, [month]);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  return {
    status,
    loading,
    error,
    loadStatus
  };
};

export const useCategoriesWithoutBudget = (month = null) => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadCategories = useCallback(async (customMonth = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const monthToUse = customMonth || month;
      const data = await budgetService.getCategoriesWithoutBudget(monthToUse);
      setCategories(data);
    } catch (err) {
      setError(err.response?.data?.message || 'Erro ao carregar categorias');
      console.error('Erro ao carregar categorias:', err);
    } finally {
      setLoading(false);
    }
  }, [month]);

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

export default useBudgets;