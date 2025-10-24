import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Typography,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Card,
  CardContent,
  Collapse,
  IconButton
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  TrendingUp,
  TrendingDown,
  Timeline,
  ExpandMore,
  ExpandLess,
  Lightbulb
} from '@mui/icons-material';
import { useState } from 'react';

const BudgetAlert = ({ budget, compact = false }) => {
  const [expanded, setExpanded] = useState(false);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const getAlertConfig = (alertLevel) => {
    const configs = {
      critical: {
        severity: 'error',
        icon: Error,
        color: 'error.main',
        bgColor: 'error.light'
      },
      high: {
        severity: 'warning',
        icon: Warning,
        color: 'warning.main',
        bgColor: 'warning.light'
      },
      medium: {
        severity: 'warning',
        icon: Warning,
        color: 'warning.main',
        bgColor: 'warning.light'
      },
      low: {
        severity: 'info',
        icon: CheckCircle,
        color: 'success.main',
        bgColor: 'success.light'
      }
    };
    return configs[alertLevel] || configs.low;
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'accelerating':
        return <TrendingUp sx={{ color: 'error.main' }} />;
      case 'decelerating':
        return <TrendingDown sx={{ color: 'success.main' }} />;
      case 'stable':
        return <Timeline sx={{ color: 'info.main' }} />;
      default:
        return <Info sx={{ color: 'text.secondary' }} />;
    }
  };

  const getTrendText = (trend) => {
    const texts = {
      accelerating: 'Gastos acelerando',
      decelerating: 'Gastos desacelerando',
      stable: 'Gastos estáveis',
      completed: 'Período concluído',
      insufficient_data: 'Dados insuficientes'
    };
    return texts[trend] || 'Tendência desconhecida';
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 100) return 'error';
    if (percentage >= 90) return 'error';
    if (percentage >= 80) return 'warning';
    return 'primary';
  };

  const alertConfig = getAlertConfig(budget.alert_level);
  const AlertIcon = alertConfig.icon;

  if (compact) {
    return (
      <Box display="flex" alignItems="center" gap={1}>
        <AlertIcon sx={{ color: alertConfig.color, fontSize: 20 }} />
        <Typography variant="body2" sx={{ color: alertConfig.color }}>
          {budget.alert_message}
        </Typography>
        {budget.percentage_used >= 80 && (
          <Chip
            label={`${budget.percentage_used.toFixed(1)}%`}
            size="small"
            color={budget.percentage_used >= 100 ? 'error' : 'warning'}
          />
        )}
      </Box>
    );
  }

  return (
    <Card sx={{ mb: 2 }}>
      <Alert 
        severity={alertConfig.severity}
        sx={{ 
          borderRadius: 0,
          '& .MuiAlert-message': { width: '100%' }
        }}
      >
        <AlertTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {budget.category_name} - {new Date(budget.month).toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
            </Typography>
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </AlertTitle>

        <Typography variant="body1" sx={{ mb: 2 }}>
          {budget.alert_message}
        </Typography>

        {/* Barra de Progresso */}
        <Box sx={{ mb: 2 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2">
              Gasto: {formatCurrency(budget.spent_amount)} de {formatCurrency(budget.amount)}
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
            sx={{ height: 8, borderRadius: 4 }}
          />
          {budget.percentage_used > 100 && (
            <Typography variant="caption" color="error.main" sx={{ mt: 0.5, display: 'block' }}>
              Excesso: {formatCurrency(budget.spent_amount - budget.amount)}
            </Typography>
          )}
        </Box>

        <Collapse in={expanded}>
          <CardContent sx={{ pt: 0 }}>
            {/* Métricas Detalhadas */}
            <Box display="grid" gridTemplateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={2} mb={3}>
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Restante
                </Typography>
                <Typography variant="h6" color={budget.remaining_amount >= 0 ? 'success.main' : 'error.main'}>
                  {formatCurrency(budget.remaining_amount)}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Média Diária
                </Typography>
                <Typography variant="h6">
                  {formatCurrency(budget.daily_average_spent)}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Projeção Mensal
                </Typography>
                <Typography 
                  variant="h6" 
                  color={budget.projected_monthly_spending > budget.amount ? 'error.main' : 'text.primary'}
                >
                  {formatCurrency(budget.projected_monthly_spending)}
                </Typography>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Tendência
                </Typography>
                <Box display="flex" alignItems="center" gap={1}>
                  {getTrendIcon(budget.spending_trend)}
                  <Typography variant="body2">
                    {getTrendText(budget.spending_trend)}
                  </Typography>
                </Box>
              </Box>
            </Box>

            {/* Projeção de Excesso */}
            {budget.projected_overspend > 0 && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Atenção:</strong> Baseado no padrão atual de gastos, você pode exceder o orçamento em {formatCurrency(budget.projected_overspend)}.
                </Typography>
              </Alert>
            )}

            {/* Dias até o Limite */}
            {budget.days_until_limit > 0 && budget.days_until_limit <= 10 && (
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <strong>Aviso:</strong> Com o padrão atual de gastos, você atingirá o limite em aproximadamente {budget.days_until_limit} dias.
                </Typography>
              </Alert>
            )}

            {/* Recomendações */}
            {budget.recommendations && budget.recommendations.length > 0 && (
              <Box>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <Lightbulb sx={{ color: 'info.main' }} />
                  <Typography variant="subtitle2" color="info.main">
                    Recomendações
                  </Typography>
                </Box>
                <List dense>
                  {budget.recommendations.map((recommendation, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <Box
                          sx={{
                            width: 6,
                            height: 6,
                            borderRadius: '50%',
                            backgroundColor: 'info.main'
                          }}
                        />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography variant="body2">
                            {recommendation}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </CardContent>
        </Collapse>
      </Alert>
    </Card>
  );
};

export default BudgetAlert;