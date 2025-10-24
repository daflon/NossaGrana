import { useState, useEffect, useCallback } from 'react';
import reportsService from '../services/reports';

export const useFinancialSummary = (initialParams = {}) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [params, setParams] = useState(initialParams);

  const loadSummary = useCallback(async (newParams = params) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await reportsService.getSummary(newParams);
      setSummary(data);
    } catch (err) {
      setError(err.message || 'Erro ao carregar resumo financeiro');
    } finally {
      setLoading(false);
    }
  }, [params]);

  const updateParams = (newParams) => {
    setParams(newParams);
    loadSummary(newParams);
  };

  useEffect(() => {
    loadSummary();
  }, [loadSummary]);

  return {
    summary,
    loading,
    error,
    params,
    loadSummary,
    updateParams
  };
};

export const useCategoryBreakdown = (initialParams = {}) => {
  const [breakdown, setBreakdown] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [params, setParams] = useState(initialParams);

  const loadBreakdown = useCallback(async (newParams = params) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await reportsService.getCategoryBreakdown(newParams);
      setBreakdown(data);
    } catch (err) {
      setError(err.message || 'Erro ao carregar breakdown por categoria');
    } finally {
      setLoading(false);
    }
  }, [params]);

  const updateParams = (newParams) => {
    setParams(newParams);
    loadBreakdown(newParams);
  };

  useEffect(() => {
    loadBreakdown();
  }, [loadBreakdown]);

  return {
    breakdown,
    loading,
    error,
    params,
    loadBreakdown,
    updateParams
  };
};

export const useMonthlyTrend = (initialParams = {}) => {
  const [trend, setTrend] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [params, setParams] = useState(initialParams);

  const loadTrend = useCallback(async (newParams = params) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await reportsService.getMonthlyTrend(newParams);
      setTrend(data);
    } catch (err) {
      setError(err.message || 'Erro ao carregar tendência mensal');
    } finally {
      setLoading(false);
    }
  }, [params]);

  const updateParams = (newParams) => {
    setParams(newParams);
    loadTrend(newParams);
  };

  useEffect(() => {
    loadTrend();
  }, [loadTrend]);

  return {
    trend,
    loading,
    error,
    params,
    loadTrend,
    updateParams
  };
};

export const useSpendingPatterns = (initialParams = {}) => {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [params, setParams] = useState(initialParams);

  const loadPatterns = useCallback(async (newParams = params) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await reportsService.getSpendingPatterns(newParams);
      setPatterns(data);
    } catch (err) {
      setError(err.message || 'Erro ao carregar padrões de gastos');
    } finally {
      setLoading(false);
    }
  }, [params]);

  const updateParams = (newParams) => {
    setParams(newParams);
    loadPatterns(newParams);
  };

  useEffect(() => {
    loadPatterns();
  }, [loadPatterns]);

  return {
    patterns,
    loading,
    error,
    params,
    loadPatterns,
    updateParams
  };
};

export const useDashboardData = (period = 'current_month') => {
  const [dashboardData, setDashboardData] = useState({
    summary: null,
    categoryBreakdown: [],
    monthlyTrend: [],
    spendingPatterns: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadDashboardData = useCallback(async (selectedPeriod = period) => {
    setLoading(true);
    setError(null);
    
    try {
      const [summaryData, breakdownData, trendData, patternsData] = await Promise.all([
        reportsService.getSummary({ period: selectedPeriod }),
        reportsService.getCategoryBreakdown({ period: selectedPeriod, type: 'expense' }),
        reportsService.getMonthlyTrend({ months: 6 }),
        reportsService.getSpendingPatterns({ type: 'weekly', period: 'last_90_days' })
      ]);

      setDashboardData({
        summary: summaryData,
        categoryBreakdown: breakdownData,
        monthlyTrend: trendData,
        spendingPatterns: patternsData
      });
    } catch (err) {
      setError(err.message || 'Erro ao carregar dados do dashboard');
    } finally {
      setLoading(false);
    }
  }, [period]);

  const refreshData = (newPeriod) => {
    loadDashboardData(newPeriod);
  };

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  return {
    dashboardData,
    loading,
    error,
    refreshData
  };
};