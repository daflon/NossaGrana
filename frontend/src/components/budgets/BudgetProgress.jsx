import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Card,
  CardContent,
  Chip,
  Grid,
  Alert,
  Skeleton
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import budgetService from '../../services/budgets';

const BudgetProgressCard = ({ budget }) => {
  const getStatusColor = () => {
    if (budget.is_over_budget) return 'error';
    if (budget.is_near_limit) return 'warning';
    return 'success';
  };

  const getStatusIcon = () => {
    if (budget.is_over_budget) return <ErrorIcon />;
    if (budget.is_near_limit) return <WarningIcon />;
    return <CheckCircleIcon />;
  };

  const getStatusText = () => {
    if (budget.is_over_budget) return 'Excedido';
    if (budget.is_near_limit) return 'Atenção';
    return 'Normal';
  };

  const getTrendIcon = () => {
    if (budget.percentage_used > 50) {
      return <TrendingUpIcon color="error" />;
    }
    return <TrendingDownIcon color="success" />;
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                backgroundColor: budget.category_color
              }}
            />
            <Typography variant="h6" component="h3">
              {budget.category_name}
            </Typography>
          </Box>
          
          <Chip
            icon={getStatusIcon()}
            label={getStatusText()}
            color={getStatusColor()}
            size="small"
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Progresso
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              {getTrendIcon()}
              <Typography variant="body2" fontWeight="bold">
                {budget.percentage_used.toFixed(1)}%
              </Typography>
            </Box>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={Math.min(budget.percentage_used, 100)}
            color={getStatusColor()}
            sx={{ 
              height: 12, 
              borderRadius: 6,
              backgroundColor: 'grey.200'
            }}
          />
        </Box>

        <Grid container spacing={2}>
          <Grid item xs={6}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Gasto
              </Typography>
              <Typography variant="body1" fontWeight="bold" color="error.main">
                {budgetService.formatCurrency(budget.spent_amount)}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={6}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Orçado
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {budgetService.formatCurrency(budget.amount)}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12}>
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Restante
              </Typography>
              <Typography 
                variant="body1" 
                fontWeight="bold"
                color={budget.remaining_amount >= 0 ? 'success.main' : 'error.main'}
              >
                {budgetService.formatCurrency(budget.remaining_amount)}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {budget.is_over_budget && (
          <Alert severity="error" sx={{ mt: 2 }}>
            <Typography variant="body2">
              Orçamento excedido em {budgetService.formatCurrency(Math.abs(budget.remaining_amount))}
            </Typography>
          </Alert>
        )}

        {budget.is_near_limit && !budget.is_over_budget && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="body2">
              Atenção! Você já gastou {budget.percentage_used.toFixed(1)}% do orçamento
            </Typography>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

const BudgetProgressSkeleton = () => (
  <Grid container spacing={3}>
    {[1, 2, 3].map((item) => (
      <Grid item xs={12} sm={6} md={4} key={item}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Skeleton variant="text" width={120} />
              <Skeleton variant="rectangular" width={60} height={24} />
            </Box>
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Skeleton variant="text" width={60} />
                <Skeleton variant="text" width={40} />
              </Box>
              <Skeleton variant="rectangular" width="100%" height={12} />
            </Box>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Skeleton variant="text" width={40} />
                <Skeleton variant="text" width={80} />
              </Grid>
              <Grid item xs={6}>
                <Skeleton variant="text" width={50} />
                <Skeleton variant="text" width={80} />
              </Grid>
              <Grid item xs={12}>
                <Skeleton variant="text" width={50} />
                <Skeleton variant="text" width={80} />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    ))}
  </Grid>
);

const BudgetProgress = ({ budgets, loading }) => {
  if (loading) {
    return <BudgetProgressSkeleton />;
  }

  if (!budgets || budgets.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          Nenhum orçamento para exibir
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Crie orçamentos para acompanhar o progresso dos seus gastos
        </Typography>
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      {budgets.map((budget) => (
        <Grid item xs={12} sm={6} md={4} key={budget.id}>
          <BudgetProgressCard budget={budget} />
        </Grid>
      ))}
    </Grid>
  );
};

export default BudgetProgress;
