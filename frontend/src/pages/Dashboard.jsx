import React, { useState } from 'react';
import {
  Typography,
  Grid,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { useDashboardData } from '../hooks/useReports';
import { useTransactions } from '../hooks/useTransactions';
import FinancialSummaryCard from '../components/reports/FinancialSummaryCard';
import CategoryChart from '../components/reports/CategoryChart';
import TrendChart from '../components/reports/TrendChart';
import BudgetAlertCenter from '../components/budgets/BudgetAlertCenter';
import TransactionList from '../components/transactions/TransactionList';

const Dashboard = () => {
  const [period, setPeriod] = useState('current_month');
  const [categoryChartType, setCategoryChartType] = useState('doughnut');
  const [trendChartType, setTrendChartType] = useState('line');

  // Hooks para dados
  const { dashboardData, loading, error, refreshData } = useDashboardData(period);
  
  // Transações recentes
  const { 
    transactions: recentTransactions = [], 
    loading: transactionsLoading 
  } = useTransactions({ ordering: '-created_at', page_size: 5 });

  const handlePeriodChange = (event) => {
    const newPeriod = event.target.value;
    setPeriod(newPeriod);
    refreshData(newPeriod);
  };

  const handleRefresh = () => {
    refreshData(period);
  };

  const periodOptions = [
    { value: 'current_month', label: 'Mês Atual' },
    { value: 'last_month', label: 'Mês Passado' },
    { value: 'last_30_days', label: 'Últimos 30 dias' },
    { value: 'last_90_days', label: 'Últimos 90 dias' },
    { value: 'current_year', label: 'Ano Atual' }
  ];

  return (
    <Box>
      {/* Cabeçalho */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Dashboard
        </Typography>
        
        <Box display="flex" gap={2} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Período</InputLabel>
            <Select
              value={period}
              label="Período"
              onChange={handlePeriodChange}
            >
              {periodOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
          >
            Atualizar
          </Button>
        </Box>
      </Box>

      {/* Erro geral */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Central de Alertas */}
        <Grid item xs={12}>
          <BudgetAlertCenter compact={false} />
        </Grid>



        {/* Resumo Financeiro */}
        <Grid item xs={12}>
          <FinancialSummaryCard
            summary={dashboardData.summary}
            loading={loading}
            error={error}
          />
        </Grid>

        {/* Gráfico de Categorias */}
        <Grid item xs={12} lg={6}>
          <CategoryChart
            breakdown={dashboardData.categoryBreakdown}
            loading={loading}
            error={error}
            title="Gastos por Categoria"
            chartType={categoryChartType}
            onChartTypeChange={setCategoryChartType}
            showLegend={true}
          />
        </Grid>

        {/* Gráfico de Tendências */}
        <Grid item xs={12} lg={6}>
          <TrendChart
            trend={dashboardData.monthlyTrend}
            loading={loading}
            error={error}
            title="Tendência dos Últimos 6 Meses"
            chartType={trendChartType}
            onChartTypeChange={setTrendChartType}
          />
        </Grid>

        {/* Transações Recentes */}
        <Grid item xs={12}>
          <TransactionList
            transactions={Array.isArray(recentTransactions) ? recentTransactions.slice(0, 5) : []}
            loading={transactionsLoading}
            error={null}
            onEdit={() => {}} // Desabilitado no dashboard
            onDelete={() => {}} // Desabilitado no dashboard
            onAdd={() => window.location.href = '/transactions'}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;