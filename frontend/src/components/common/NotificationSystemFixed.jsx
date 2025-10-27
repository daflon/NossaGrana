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
  Close
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

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

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
  }, [removeNotification]);

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

  const value = {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    showSuccess,
    showError,
    showWarning,
    showInfo
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
                  <IconButton
                    size="small"
                    color="inherit"
                    onClick={() => removeNotification(notification.id)}
                  >
                    <Close fontSize="small" />
                  </IconButton>
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
              </Alert>
            </Snackbar>
          ))}
        </Stack>
      </Box>
    </NotificationContext.Provider>
  );
};

export default NotificationProvider;