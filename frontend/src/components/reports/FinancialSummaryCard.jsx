import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Skeleton,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Receipt,
  Savings,
  PieChart
} from '@mui/icons-material';
import reportsService from '../../services/reports';

const FinancialSummaryCard = ({ summary, loading, error }) => {
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Skeleton width="60%" />
          </Typography>
          <Grid container spacing={3}>
            {[...Array(6)].map((_, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Box>
                  <Skeleton variant="text" width="80%" />
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="text" width="40%" />
                </Box>
              </Grid>
            ))}
          </Grid>
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

  if (!summary) {
    return null;
  }

  const getChangeColor = (value) => {
    if (value > 0) return 'success.main';
    if (value < 0) return 'error.main';
    return 'text.secondary';
  };

  const getChangeIcon = (value) => {
    if (value > 0) return <TrendingUp sx={{ fontSize: 16 }} />;
    if (value < 0) return <TrendingDown sx={{ fontSize: 16 }} />;
    return null;
  };

  const metrics = [
    {
      title: 'Total de Receitas',
      value: summary.total_income,
      change: summary.income_change,
      icon: TrendingUp,
      color: 'success.main',
      bgColor: 'success.light'
    },
    {
      title: 'Total de Despesas',
      value: summary.total_expense,
      change: summary.expense_change,
      icon: TrendingDown,
      color: 'error.main',
      bgColor: 'error.light'
    },
    {
      title: 'Saldo Líquido',
      value: summary.net_balance,
      change: summary.balance_change,
      icon: AccountBalance,
      color: summary.net_balance >= 0 ? 'success.main' : 'error.main',
      bgColor: summary.net_balance >= 0 ? 'success.light' : 'error.light'
    },
    {
      title: 'Total de Transações',
      value: summary.transaction_count,
      icon: Receipt,
      color: 'info.main',
      bgColor: 'info.light',
      isCount: true
    },
    {
      title: 'Taxa de Poupança',
      value: summary.savings_rate,
      icon: Savings,
      color: summary.savings_rate >= 20 ? 'success.main' : summary.savings_rate >= 10 ? 'warning.main' : 'error.main',
      bgColor: summary.savings_rate >= 20 ? 'success.light' : summary.savings_rate >= 10 ? 'warning.light' : 'error.light',
      isPercentage: true
    },
    {
      title: 'Transação Média',
      value: summary.average_transaction,
      icon: PieChart,
      color: 'primary.main',
      bgColor: 'primary.light'
    }
  ];

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            Resumo Financeiro - {summary.period}
          </Typography>
          <Chip
            label={`Taxa de Poupança: ${reportsService.formatPercentage(summary.savings_rate)}`}
            color={summary.savings_rate >= 20 ? 'success' : summary.savings_rate >= 10 ? 'warning' : 'error'}
            variant="outlined"
          />
        </Box>

        <Grid container spacing={3}>
          {metrics.map((metric, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Box
                sx={{
                  p: 2,
                  borderRadius: 2,
                  border: 1,
                  borderColor: 'divider',
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}
              >
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                  <Typography variant="body2" color="text.secondary">
                    {metric.title}
                  </Typography>
                  <Box
                    sx={{
                      p: 0.5,
                      borderRadius: 1,
                      backgroundColor: metric.bgColor,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <metric.icon sx={{ color: metric.color, fontSize: 20 }} />
                  </Box>
                </Box>

                <Typography variant="h5" sx={{ color: metric.color, fontWeight: 'bold', mb: 1 }}>
                  {metric.isCount ? (
                    metric.value
                  ) : metric.isPercentage ? (
                    reportsService.formatPercentage(metric.value)
                  ) : (
                    reportsService.formatCurrency(metric.value)
                  )}
                </Typography>

                {metric.change !== undefined && (
                  <Box display="flex" alignItems="center" gap={0.5}>
                    {getChangeIcon(metric.change)}
                    <Typography
                      variant="caption"
                      sx={{ color: getChangeColor(metric.change) }}
                    >
                      {reportsService.formatPercentage(Math.abs(metric.change))} vs período anterior
                    </Typography>
                  </Box>
                )}
              </Box>
            </Grid>
          ))}
        </Grid>

        {/* Insights adicionais */}
        <Box mt={3} p={2} sx={{ backgroundColor: 'background.paper', borderRadius: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Insights Rápidos
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                • Proporção de gastos: {reportsService.formatPercentage(summary.expense_ratio)} da receita
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                • Média por transação: {reportsService.formatCurrency(summary.average_transaction)}
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </Card>
  );
};

export default FinancialSummaryCard;