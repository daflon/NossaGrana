import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material';
import {
  Warning,
  Error,
  TrendingUp,
  TrendingDown,
  Timeline,
  Info,
  CheckCircle
} from '@mui/icons-material';

const BudgetProgressCard = ({ budget, onClick }) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 100) return 'error';
    if (percentage >= 90) return 'error';
    if (percentage >= 80) return 'warning';
    return 'primary';
  };

  const getAlertIcon = (alertLevel) => {
    const icons = {
      critical: Error,
      high: Warning,
      medium: Warning,
      low: CheckCircle
    };
    const Icon = icons[alertLevel] || CheckCircle;
    return <Icon />;
  };

  const getAlertColor = (alertLevel) => {
    const colors = {
      critical: 'error.main',
      high: 'warning.main',
      medium: 'warning.main',
      low: 'success.main'
    };
    return colors[alertLevel] || 'success.main';
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'accelerating':
        return <TrendingUp sx={{ color: 'error.main', fontSize: 16 }} />;
      case 'decelerating':
        return <TrendingDown sx={{ color: 'success.main', fontSize: 16 }} />;
      case 'stable':
        return <Timeline sx={{ color: 'info.main', fontSize: 16 }} />;
      default:
        return <Info sx={{ color: 'text.secondary', fontSize: 16 }} />;
    }
  };

  const AlertIcon = getAlertIcon(budget.alert_level);

  return (
    <Card 
      sx={{ 
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.2s',
        '&:hover': onClick ? {
          transform: 'translateY(-2px)',
          boxShadow: 3
        } : {},
        border: budget.alert_level !== 'low' ? 2 : 1,
        borderColor: budget.alert_level !== 'low' ? getAlertColor(budget.alert_level) : 'divider'
      }}
      onClick={onClick}
    >
      <CardContent>
        {/* Cabeçalho */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box flex={1}>
            <Typography variant="h6" gutterBottom>
              {budget.category_name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {new Date(budget.month).toLocaleDateString('pt-BR', { 
                month: 'long', 
                year: 'numeric' 
              })}
            </Typography>
          </Box>
          
          <Box display="flex" alignItems="center" gap={1}>
            {budget.spending_trend && budget.spending_trend !== 'insufficient_data' && (
              <Tooltip title={`Tendência: ${budget.spending_trend}`}>
                <Box>
                  {getTrendIcon(budget.spending_trend)}
                </Box>
              </Tooltip>
            )}
            
            <Tooltip title={budget.alert_message}>
              <IconButton size="small" sx={{ color: getAlertColor(budget.alert_level) }}>
                <AlertIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Valores */}
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Gasto
            </Typography>
            <Typography variant="h6" color={budget.is_over_budget ? 'error.main' : 'text.primary'}>
              {formatCurrency(budget.spent_amount)}
            </Typography>
          </Box>
          
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Orçamento
            </Typography>
            <Typography variant="body2">
              {formatCurrency(budget.amount)}
            </Typography>
          </Box>
          
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="body2" color="text.secondary">
              Restante
            </Typography>
            <Typography 
              variant="body2" 
              color={budget.remaining_amount >= 0 ? 'success.main' : 'error.main'}
            >
              {formatCurrency(budget.remaining_amount)}
            </Typography>
          </Box>
        </Box>

        {/* Barra de Progresso */}
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Progresso
            </Typography>
            <Chip
              label={`${budget.percentage_used.toFixed(1)}%`}
              size="small"
              color={getProgressColor(budget.percentage_used)}
            />
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={Math.min(budget.percentage_used, 100)}
            color={getProgressColor(budget.percentage_used)}
            sx={{ 
              height: 8, 
              borderRadius: 4,
              '& .MuiLinearProgress-bar': {
                borderRadius: 4
              }
            }}
          />
          
          {budget.percentage_used > 100 && (
            <Typography variant="caption" color="error.main" sx={{ mt: 0.5, display: 'block' }}>
              Excesso: {formatCurrency(budget.spent_amount - budget.amount)}
            </Typography>
          )}
        </Box>

        {/* Alertas Específicos */}
        {budget.alert_level !== 'low' && (
          <Alert 
            severity={budget.alert_level === 'critical' ? 'error' : 'warning'}
            size="small"
            sx={{ mb: 1 }}
          >
            <Typography variant="caption">
              {budget.alert_message}
            </Typography>
          </Alert>
        )}

        {/* Projeção */}
        {budget.projected_overspend > 0 && (
          <Box>
            <Typography variant="caption" color="warning.main">
              Projeção de excesso: {formatCurrency(budget.projected_overspend)}
            </Typography>
          </Box>
        )}

        {/* Métricas Adicionais */}
        <Box display="flex" justifyContent="space-between" mt={2} pt={1} borderTop={1} borderColor="divider">
          <Box textAlign="center">
            <Typography variant="caption" color="text.secondary" display="block">
              Média Diária
            </Typography>
            <Typography variant="body2">
              {formatCurrency(budget.daily_average_spent)}
            </Typography>
          </Box>
          
          {budget.days_until_limit > 0 && budget.days_until_limit <= 30 && (
            <Box textAlign="center">
              <Typography variant="caption" color="text.secondary" display="block">
                Dias até Limite
              </Typography>
              <Typography 
                variant="body2" 
                color={budget.days_until_limit <= 7 ? 'error.main' : 'text.primary'}
              >
                {budget.days_until_limit}
              </Typography>
            </Box>
          )}
          
          <Box textAlign="center">
            <Typography variant="caption" color="text.secondary" display="block">
              Projeção
            </Typography>
            <Typography 
              variant="body2"
              color={budget.projected_monthly_spending > budget.amount ? 'error.main' : 'text.primary'}
            >
              {formatCurrency(budget.projected_monthly_spending)}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default BudgetProgressCard;