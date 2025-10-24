import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Skeleton
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Receipt
} from '@mui/icons-material';

const TransactionSummary = ({ summary, loading }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const getBalanceColor = (balance) => {
    if (balance > 0) return 'success.main';
    if (balance < 0) return 'error.main';
    return 'text.primary';
  };

  const metrics = [
    {
      title: 'Total de Receitas',
      value: summary.total_income,
      icon: TrendingUp,
      color: 'success.main',
      bgColor: 'success.light'
    },
    {
      title: 'Total de Despesas',
      value: summary.total_expense,
      icon: TrendingDown,
      color: 'error.main',
      bgColor: 'error.light'
    },
    {
      title: 'Saldo',
      value: summary.balance,
      icon: AccountBalance,
      color: getBalanceColor(summary.balance),
      bgColor: 'primary.light'
    },
    {
      title: 'Total de Transações',
      value: summary.transaction_count,
      icon: Receipt,
      color: 'info.main',
      bgColor: 'info.light',
      isCount: true
    }
  ];

  return (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      {metrics.map((metric, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h6" component="div" sx={{ color: metric.color }}>
                    {loading ? (
                      <Skeleton width={80} />
                    ) : metric.isCount ? (
                      metric.value
                    ) : (
                      formatCurrency(metric.value)
                    )}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {loading ? <Skeleton width={120} /> : metric.title}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 1,
                    backgroundColor: metric.bgColor,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  <metric.icon sx={{ color: metric.color }} />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default TransactionSummary;