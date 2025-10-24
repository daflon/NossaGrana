import React, { createContext, useContext, useState, useCallback } from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Box,
  IconButton,
  Typography,
  Slide,
  Stack
} from '@mui/material';
import {
  Close,
  Warning,
  Error,
  Info,
  CheckCircle,
  Notifications
} from '@mui/icons-material';

const NotificationContext = createContext();

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

const TransitionUp = (props) => {
  return <Slide {...props} direction="up" />;
};

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      type: 'info',
      title: '',
      message: '',
      duration: 6000,
      persistent: false,
      actions: [],
      ...notification
    };

    setNotifications(prev => [...prev, newNotification]);

    // Auto-remove se não for persistente
    if (!newNotification.persistent) {
      setTimeout(() => {
        removeNotification(id);
      }, newNotification.duration);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Funções de conveniência
  const showSuccess = useCallback((message, options = {}) => {
    return addNotification({
      type: 'success',
      message,
      ...options
    });
  }, [addNotification]);

  const showError = useCallback((message, options = {}) => {
    return addNotification({
      type: 'error',
      message,
      duration: 8000,
      ...options
    });
  }, [addNotification]);

  const showWarning = useCallback((message, options = {}) => {
    return addNotification({
      type: 'warning',
      message,
      duration: 7000,
      ...options
    });
  }, [addNotification]);

  const showInfo = useCallback((message, options = {}) => {
    return addNotification({
      type: 'info',
      message,
      ...options
    });
  }, [addNotification]);

  const showBudgetAlert = useCallback((budget, options = {}) => {
    const alertConfig = {
      critical: { type: 'error', duration: 10000 },
      high: { type: 'warning', duration: 8000 },
      medium: { type: 'warning', duration: 7000 },
      low: { type: 'info', duration: 5000 }
    };

    const config = alertConfig[budget.alert_level] || alertConfig.low;

    return addNotification({
      ...config,
      title: `Alerta de Orçamento - ${budget.category_name}`,
      message: budget.alert_message,
      persistent: budget.alert_level === 'critical',
      data: { budget },
      ...options
    });
  }, [addNotification]);

  const getIcon = (type) => {
    const icons = {
      success: CheckCircle,
      error: Error,
      warning: Warning,
      info: Info
    };
    const Icon = icons[type] || Info;
    return <Icon />;
  };

  const value = {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showBudgetAlert
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      
      {/* Renderizar notificações */}
      <Box
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          zIndex: 9999,
          maxWidth: 400,
          width: '100%'
        }}
      >
        <Stack spacing={1}>
          {notifications.map((notification) => (
            <Snackbar
              key={notification.id}
              open={true}
              TransitionComponent={TransitionUp}
              anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
              sx={{ position: 'relative' }}
            >
              <Alert
                severity={notification.type}
                variant="filled"
                onClose={() => removeNotification(notification.id)}
                action={
                  <Box display="flex" alignItems="center" gap={1}>
                    {notification.actions?.map((action, index) => (
                      <IconButton
                        key={index}
                        size="small"
                        color="inherit"
                        onClick={() => {
                          action.onClick(notification);
                          if (action.closeOnClick !== false) {
                            removeNotification(notification.id);
                          }
                        }}
                      >
                        {action.icon}
                      </IconButton>
                    ))}
                    <IconButton
                      size="small"
                      color="inherit"
                      onClick={() => removeNotification(notification.id)}
                    >
                      <Close fontSize="small" />
                    </IconButton>
                  </Box>
                }
                sx={{
                  width: '100%',
                  '& .MuiAlert-message': {
                    width: '100%'
                  }
                }}
              >
                {notification.title && (
                  <AlertTitle>{notification.title}</AlertTitle>
                )}
                <Typography variant="body2">
                  {notification.message}
                </Typography>
                
                {/* Dados adicionais para alertas de orçamento */}
                {notification.data?.budget && (
                  <Box mt={1} pt={1} borderTop={1} borderColor="rgba(255,255,255,0.2)">
                    <Typography variant="caption" display="block">
                      Gasto: R$ {notification.data.budget.spent_amount?.toFixed(2)} / R$ {notification.data.budget.amount?.toFixed(2)}
                    </Typography>
                    <Typography variant="caption" display="block">
                      {notification.data.budget.percentage_used?.toFixed(1)}% utilizado
                    </Typography>
                  </Box>
                )}
              </Alert>
            </Snackbar>
          ))}
        </Stack>
      </Box>
    </NotificationContext.Provider>
  );
};

// Hook para alertas de orçamento específicos
export const useBudgetAlerts = () => {
  const { showBudgetAlert, showWarning, showError } = useNotifications();

  const checkBudgetAlerts = useCallback((budgets) => {
    if (!budgets || !Array.isArray(budgets)) return;

    budgets.forEach(budget => {
      if (budget.alert_level !== 'low') {
        showBudgetAlert(budget);
      }
    });
  }, [showBudgetAlert]);

  const showTransactionAlert = useCallback((transaction, budget) => {
    if (!budget) return;

    // Verificar se a transação causou algum alerta
    if (budget.is_over_budget) {
      showError(
        `Transação de R$ ${transaction.amount.toFixed(2)} excedeu o orçamento de ${budget.category_name}!`,
        {
          title: 'Orçamento Excedido',
          persistent: true
        }
      );
    } else if (budget.is_near_limit) {
      showWarning(
        `Transação de R$ ${transaction.amount.toFixed(2)} aproximou você do limite do orçamento de ${budget.category_name}`,
        {
          title: 'Próximo do Limite'
        }
      );
    }
  }, [showError, showWarning]);

  return {
    checkBudgetAlerts,
    showTransactionAlert
  };
};

export default NotificationProvider;