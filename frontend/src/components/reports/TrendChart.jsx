import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  ToggleButton,
  ToggleButtonGroup,
  Skeleton,
  Alert,
  Grid,
  Chip
} from '@mui/material';
import {
  ShowChart,
  BarChart as BarChartIcon
} from '@mui/icons-material';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import reportsService from '../../services/reports';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const TrendChart = ({ 
  trend, 
  loading, 
  error, 
  title = "Tendência Mensal",
  chartType = 'line',
  onChartTypeChange 
}) => {
  const [viewMode, setViewMode] = useState('combined'); // 'combined', 'income', 'expense', 'balance'

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Skeleton width="60%" />
          </Typography>
          <Box height={400}>
            <Skeleton variant="rectangular" width="100%" height="100%" />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!trend || trend.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            py={6}
          >
            <ShowChart sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              Dados insuficientes para gerar o gráfico de tendência
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const getChartData = () => {
    const labels = trend.map(item => item.month_name);

    switch (viewMode) {
      case 'income':
        return {
          labels,
          datasets: [{
            label: 'Receitas',
            data: trend.map(item => parseFloat(item.total_income)),
            borderColor: '#4ECDC4',
            backgroundColor: chartType === 'bar' ? '#4ECDC4' : 'rgba(78, 205, 196, 0.1)',
            fill: chartType === 'line',
            tension: 0.4
          }]
        };

      case 'expense':
        return {
          labels,
          datasets: [{
            label: 'Despesas',
            data: trend.map(item => parseFloat(item.total_expense)),
            borderColor: '#FF6B6B',
            backgroundColor: chartType === 'bar' ? '#FF6B6B' : 'rgba(255, 107, 107, 0.1)',
            fill: chartType === 'line',
            tension: 0.4
          }]
        };

      case 'balance':
        return reportsService.prepareBalanceChartData(trend);

      default: // combined
        return reportsService.prepareMonthlyTrendData(trend);
    }
  };

  const chartData = getChartData();
  const chartOptions = {
    ...reportsService.getChartOptions(null, chartType),
    plugins: {
      ...reportsService.getChartOptions(null, chartType).plugins,
      legend: {
        position: 'top',
        labels: {
          padding: 20,
          usePointStyle: true
        }
      }
    },
    scales: {
      ...reportsService.getChartOptions(null, chartType).scales,
      y: {
        ...reportsService.getChartOptions(null, chartType).scales.y,
        beginAtZero: true
      }
    }
  };

  const ChartComponent = chartType === 'bar' ? Bar : Line;

  // Calcular estatísticas
  const totalIncome = trend.reduce((sum, item) => sum + parseFloat(item.total_income), 0);
  const totalExpense = trend.reduce((sum, item) => sum + parseFloat(item.total_expense), 0);
  const avgSavingsRate = trend.reduce((sum, item) => sum + item.savings_rate, 0) / trend.length;
  const lastMonth = trend[trend.length - 1];
  const previousMonth = trend[trend.length - 2];

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            {title}
          </Typography>
          <Box display="flex" gap={2}>
            {/* Seletor de visualização */}
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={(e, newMode) => newMode && setViewMode(newMode)}
              size="small"
            >
              <ToggleButton value="combined">Combinado</ToggleButton>
              <ToggleButton value="income">Receitas</ToggleButton>
              <ToggleButton value="expense">Despesas</ToggleButton>
              <ToggleButton value="balance">Saldo</ToggleButton>
            </ToggleButtonGroup>

            {/* Seletor de tipo de gráfico */}
            {onChartTypeChange && (
              <ToggleButtonGroup
                value={chartType}
                exclusive
                onChange={(e, newType) => newType && onChartTypeChange(newType)}
                size="small"
              >
                <ToggleButton value="line">
                  <ShowChart />
                </ToggleButton>
                <ToggleButton value="bar">
                  <BarChartIcon />
                </ToggleButton>
              </ToggleButtonGroup>
            )}
          </Box>
        </Box>

        {/* Estatísticas rápidas */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} sm={3}>
            <Box textAlign="center">
              <Typography variant="h6" color="success.main">
                {reportsService.formatCurrency(totalIncome)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total de Receitas
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Box textAlign="center">
              <Typography variant="h6" color="error.main">
                {reportsService.formatCurrency(totalExpense)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Total de Despesas
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Box textAlign="center">
              <Typography 
                variant="h6" 
                color={totalIncome - totalExpense >= 0 ? 'success.main' : 'error.main'}
              >
                {reportsService.formatCurrency(totalIncome - totalExpense)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Saldo Total
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Box textAlign="center">
              <Typography 
                variant="h6" 
                color={avgSavingsRate >= 20 ? 'success.main' : avgSavingsRate >= 10 ? 'warning.main' : 'error.main'}
              >
                {reportsService.formatPercentage(avgSavingsRate)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Taxa Média de Poupança
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Gráfico */}
        <Box height={400} mb={3}>
          <ChartComponent data={chartData} options={chartOptions} />
        </Box>

        {/* Insights do último mês */}
        {lastMonth && previousMonth && (
          <Box p={2} sx={{ backgroundColor: 'background.paper', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom>
              Análise do Último Mês ({lastMonth.month_name})
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Chip
                label={`Receitas: ${reportsService.formatCurrency(lastMonth.total_income)}`}
                color="success"
                variant="outlined"
                size="small"
              />
              <Chip
                label={`Despesas: ${reportsService.formatCurrency(lastMonth.total_expense)}`}
                color="error"
                variant="outlined"
                size="small"
              />
              <Chip
                label={`Poupança: ${reportsService.formatPercentage(lastMonth.savings_rate)}`}
                color={lastMonth.savings_rate >= 20 ? 'success' : lastMonth.savings_rate >= 10 ? 'warning' : 'error'}
                variant="outlined"
                size="small"
              />
              {lastMonth.income_growth !== 0 && (
                <Chip
                  label={`Crescimento receitas: ${lastMonth.income_growth > 0 ? '+' : ''}${reportsService.formatPercentage(lastMonth.income_growth)}`}
                  color={lastMonth.income_growth > 0 ? 'success' : 'error'}
                  variant="outlined"
                  size="small"
                />
              )}
              {lastMonth.expense_growth !== 0 && (
                <Chip
                  label={`Crescimento despesas: ${lastMonth.expense_growth > 0 ? '+' : ''}${reportsService.formatPercentage(lastMonth.expense_growth)}`}
                  color={lastMonth.expense_growth > 0 ? 'error' : 'success'}
                  variant="outlined"
                  size="small"
                />
              )}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default TrendChart;