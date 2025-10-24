import React, { useState } from 'react';
import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Tabs,
  Tab,
  TextField,
  Alert
} from '@mui/material';
import {
  Refresh,
  Download,
  DateRange
} from '@mui/icons-material';
import {
  useFinancialSummary,
  useCategoryBreakdown,
  useMonthlyTrend,
  useSpendingPatterns
} from '../hooks/useReports';
import FinancialSummaryCard from '../components/reports/FinancialSummaryCard';
import CategoryChart from '../components/reports/CategoryChart';
import TrendChart from '../components/reports/TrendChart';

const Reports = () => {
  const [tabValue, setTabValue] = useState(0);
  const [period, setPeriod] = useState('current_month');
  const [transactionType, setTransactionType] = useState('expense');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [categoryChartType, setCategoryChartType] = useState('doughnut');
  const [trendChartType, setTrendChartType] = useState('line');

  // Parâmetros baseados na aba ativa
  const getParams = () => {
    const baseParams = {};
    
    if (dateFrom && dateTo) {
      baseParams.date_from = dateFrom;
      baseParams.date_to = dateTo;
    } else {
      baseParams.period = period;
    }
    
    return baseParams;
  };

  const getCategoryParams = () => ({
    ...getParams(),
    type: transactionType
  });

  // Hooks para dados
  const summaryHook = useFinancialSummary(getParams());
  const categoryHook = useCategoryBreakdown(getCategoryParams());
  const trendHook = useMonthlyTrend({ months: 12 });
  const patternsHook = useSpendingPatterns({ 
    type: 'weekly', 
    period: 'last_90_days' 
  });

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handlePeriodChange = (event) => {
    const newPeriod = event.target.value;
    setPeriod(newPeriod);
    
    // Limpar datas customizadas
    setDateFrom('');
    setDateTo('');
    
    // Atualizar dados
    const params = { period: newPeriod };
    summaryHook.updateParams(params);
    categoryHook.updateParams({ ...params, type: transactionType });
  };

  const handleDateRangeChange = () => {
    if (dateFrom && dateTo) {
      const params = { date_from: dateFrom, date_to: dateTo };
      summaryHook.updateParams(params);
      categoryHook.updateParams({ ...params, type: transactionType });
    }
  };

  const handleTransactionTypeChange = (event) => {
    const newType = event.target.value;
    setTransactionType(newType);
    categoryHook.updateParams({ ...getParams(), type: newType });
  };

  const handleRefresh = () => {
    summaryHook.loadSummary();
    categoryHook.loadBreakdown();
    trendHook.loadTrend();
    patternsHook.loadPatterns();
  };

  const handleExport = () => {
    // Placeholder para funcionalidade de exportação
    alert('Funcionalidade de exportação será implementada em breve!');
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
          Relatórios
        </Typography>
        
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
          >
            Atualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={handleExport}
          >
            Exportar
          </Button>
        </Box>
      </Box>

      {/* Filtros */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Filtros
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Período</InputLabel>
                <Select
                  value={period}
                  label="Período"
                  onChange={handlePeriodChange}
                  disabled={dateFrom && dateTo}
                >
                  {periodOptions.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                type="date"
                label="Data Inicial"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
                fullWidth
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <TextField
                type="date"
                label="Data Final"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
                fullWidth
              />
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <Button
                variant="outlined"
                startIcon={<DateRange />}
                onClick={handleDateRangeChange}
                disabled={!dateFrom || !dateTo}
                size="small"
                fullWidth
              >
                Aplicar Datas
              </Button>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Tipo (para categorias)</InputLabel>
                <Select
                  value={transactionType}
                  label="Tipo (para categorias)"
                  onChange={handleTransactionTypeChange}
                >
                  <MenuItem value="expense">Despesas</MenuItem>
                  <MenuItem value="income">Receitas</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Resumo Geral" />
          <Tab label="Por Categoria" />
          <Tab label="Tendências" />
          <Tab label="Análise Detalhada" />
        </Tabs>
      </Box>

      {/* Conteúdo das Tabs */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FinancialSummaryCard
              summary={summaryHook.summary}
              loading={summaryHook.loading}
              error={summaryHook.error}
            />
          </Grid>
          
          <Grid item xs={12} lg={6}>
            <CategoryChart
              breakdown={categoryHook.breakdown}
              loading={categoryHook.loading}
              error={categoryHook.error}
              title={`${transactionType === 'expense' ? 'Despesas' : 'Receitas'} por Categoria`}
              chartType={categoryChartType}
              onChartTypeChange={setCategoryChartType}
              showLegend={true}
            />
          </Grid>
          
          <Grid item xs={12} lg={6}>
            <TrendChart
              trend={trendHook.trend}
              loading={trendHook.loading}
              error={trendHook.error}
              title="Tendência dos Últimos 12 Meses"
              chartType={trendChartType}
              onChartTypeChange={setTrendChartType}
            />
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <CategoryChart
              breakdown={categoryHook.breakdown}
              loading={categoryHook.loading}
              error={categoryHook.error}
              title={`Análise Detalhada - ${transactionType === 'expense' ? 'Despesas' : 'Receitas'} por Categoria`}
              chartType={categoryChartType}
              onChartTypeChange={setCategoryChartType}
              showLegend={true}
            />
          </Grid>
        </Grid>
      )}

      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TrendChart
              trend={trendHook.trend}
              loading={trendHook.loading}
              error={trendHook.error}
              title="Análise de Tendências - 12 Meses"
              chartType={trendChartType}
              onChartTypeChange={setTrendChartType}
            />
          </Grid>
        </Grid>
      )}

      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Alert severity="info">
              Análise detalhada com padrões de gastos, previsões e insights será implementada na próxima fase.
            </Alert>
          </Grid>
          
          <Grid item xs={12} lg={6}>
            <FinancialSummaryCard
              summary={summaryHook.summary}
              loading={summaryHook.loading}
              error={summaryHook.error}
            />
          </Grid>
          
          <Grid item xs={12} lg={6}>
            <CategoryChart
              breakdown={categoryHook.breakdown}
              loading={categoryHook.loading}
              error={categoryHook.error}
              title="Distribuição de Gastos"
              chartType="pie"
              showLegend={false}
            />
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default Reports;