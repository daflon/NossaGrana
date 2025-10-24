import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Badge,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Button,
  Divider,
  Alert,
  Skeleton
} from '@mui/material';
import {
  Notifications,
  NotificationsActive,
  ExpandMore,
  ExpandLess,
  Warning,
  Error,
  Info,
  CheckCircle,
  Close,
  Refresh
} from '@mui/icons-material';
import { useBudgets } from '../../hooks/useBudgets';

const BudgetAlertCenter = ({ compact = false }) => {
  const [expanded, setExpanded] = useState(false);
  const { budgets, loading, error, loadBudgets } = useBudgets();
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    if (budgets && budgets.length > 0) {
      // Processar alertas dos orçamentos
      const processedAlerts = [];
      
      budgets.forEach(budget => {
        if (budget.alert_level !== 'low') {
          processedAlerts.push({
            id: `budget-${budget.id}`,
            type: 'budget',
            level: budget.alert_level,
            title: `${budget.category_name} - ${new Date(budget.month).toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })}`,
            message: budget.alert_message,
            budget: budget,
            timestamp: new Date(),
            isRead: false
          });
        }
      });

      // Ordenar por nível de prioridade e data
      const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
      processedAlerts.sort((a, b) => {
        if (priorityOrder[a.level] !== priorityOrder[b.level]) {
          return priorityOrder[b.level] - priorityOrder[a.level];
        }
        return b.timestamp - a.timestamp;
      });

      setAlerts(processedAlerts);
    }
  }, [budgets]);

  const getAlertIcon = (level) => {
    const icons = {
      critical: Error,
      high: Warning,
      medium: Warning,
      low: Info
    };
    const Icon = icons[level] || Info;
    return <Icon />;
  };

  const getAlertColor = (level) => {
    const colors = {
      critical: 'error',
      high: 'warning',
      medium: 'warning',
      low: 'info'
    };
    return colors[level] || 'info';
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const getActiveAlertsCount = () => {
    return alerts.filter(alert => !alert.isRead).length;
  };

  const markAsRead = (alertId) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId ? { ...alert, isRead: true } : alert
      )
    );
  };

  const markAllAsRead = () => {
    setAlerts(prev => prev.map(alert => ({ ...alert, isRead: true })));
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2}>
            <Skeleton variant="circular" width={40} height={40} />
            <Box flex={1}>
              <Skeleton variant="text" width="60%" />
              <Skeleton variant="text" width="40%" />
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Erro ao carregar alertas: {error}
      </Alert>
    );
  }

  const activeAlertsCount = getActiveAlertsCount();

  if (compact) {
    return (
      <Box display="flex" alignItems="center" gap={1}>
        <Badge badgeContent={activeAlertsCount} color="error">
          <IconButton
            onClick={() => setExpanded(!expanded)}
            color={activeAlertsCount > 0 ? 'error' : 'default'}
          >
            {activeAlertsCount > 0 ? <NotificationsActive /> : <Notifications />}
          </IconButton>
        </Badge>
        {activeAlertsCount > 0 && (
          <Typography variant="body2" color="error.main">
            {activeAlertsCount} alerta{activeAlertsCount > 1 ? 's' : ''}
          </Typography>
        )}
      </Box>
    );
  }

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <Badge badgeContent={activeAlertsCount} color="error">
              {activeAlertsCount > 0 ? (
                <NotificationsActive color="error" />
              ) : (
                <Notifications color="action" />
              )}
            </Badge>
            <Typography variant="h6">
              Central de Alertas
            </Typography>
            {activeAlertsCount > 0 && (
              <Chip
                label={`${activeAlertsCount} ativo${activeAlertsCount > 1 ? 's' : ''}`}
                color="error"
                size="small"
              />
            )}
          </Box>
          <Box display="flex" gap={1}>
            <IconButton size="small" onClick={loadBudgets}>
              <Refresh />
            </IconButton>
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </Box>

        {activeAlertsCount === 0 && !expanded && (
          <Box display="flex" alignItems="center" gap={1}>
            <CheckCircle sx={{ color: 'success.main' }} />
            <Typography variant="body2" color="success.main">
              Todos os orçamentos estão sob controle
            </Typography>
          </Box>
        )}

        <Collapse in={expanded || activeAlertsCount > 0}>
          {alerts.length === 0 ? (
            <Box textAlign="center" py={3}>
              <CheckCircle sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" color="success.main" gutterBottom>
                Nenhum alerta ativo
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Todos os seus orçamentos estão sob controle
              </Typography>
            </Box>
          ) : (
            <>
              {activeAlertsCount > 1 && (
                <Box mb={2}>
                  <Button
                    size="small"
                    onClick={markAllAsRead}
                    startIcon={<CheckCircle />}
                  >
                    Marcar todos como lidos
                  </Button>
                </Box>
              )}

              <List>
                {alerts.map((alert, index) => (
                  <React.Fragment key={alert.id}>
                    <ListItem
                      sx={{
                        bgcolor: alert.isRead ? 'transparent' : 'action.hover',
                        borderRadius: 1,
                        mb: 1,
                        border: 1,
                        borderColor: alert.isRead ? 'divider' : `${getAlertColor(alert.level)}.main`,
                        opacity: alert.isRead ? 0.7 : 1
                      }}
                    >
                      <ListItemIcon>
                        {getAlertIcon(alert.level)}
                      </ListItemIcon>
                      
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle2">
                              {alert.title}
                            </Typography>
                            <Chip
                              label={alert.level}
                              size="small"
                              color={getAlertColor(alert.level)}
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              {alert.message}
                            </Typography>
                            {alert.budget && (
                              <Box display="flex" gap={2} flexWrap="wrap">
                                <Typography variant="caption" color="text.secondary">
                                  Gasto: {formatCurrency(alert.budget.spent_amount)} / {formatCurrency(alert.budget.amount)}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {alert.budget.percentage_used.toFixed(1)}% utilizado
                                </Typography>
                                {alert.budget.projected_overspend > 0 && (
                                  <Typography variant="caption" color="error.main">
                                    Projeção de excesso: {formatCurrency(alert.budget.projected_overspend)}
                                  </Typography>
                                )}
                              </Box>
                            )}
                          </Box>
                        }
                      />

                      <ListItemSecondaryAction>
                        {!alert.isRead && (
                          <IconButton
                            edge="end"
                            size="small"
                            onClick={() => markAsRead(alert.id)}
                          >
                            <Close />
                          </IconButton>
                        )}
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < alerts.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </>
          )}
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default BudgetAlertCenter;