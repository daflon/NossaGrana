import { useState, useEffect } from 'react';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    // Simular carregamento de notificações
    const mockNotifications = [
      { id: 1, message: 'Orçamento de alimentação atingiu 80%', read: false, type: 'warning' },
      { id: 2, message: 'Nova transação adicionada', read: true, type: 'info' },
      { id: 3, message: 'Meta de economia próxima do prazo', read: false, type: 'alert' }
    ];
    setNotifications(mockNotifications);
  }, []);

  const markAsRead = (id) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  };

  const addNotification = (message, type = 'info') => {
    const newNotification = {
      id: Date.now(),
      message,
      read: false,
      type
    };
    setNotifications(prev => [newNotification, ...prev]);
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    addNotification
  };
};