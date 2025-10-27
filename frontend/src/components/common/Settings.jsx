import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Switch,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction
} from '@mui/material';

const Settings = ({ open, onClose }) => {
  const [settings, setSettings] = useState({
    notifications: true,
    emailAlerts: false,
    darkMode: false,
    autoBackup: true
  });

  const handleSettingChange = (setting) => {
    setSettings(prev => ({
      ...prev,
      [setting]: !prev[setting]
    }));
  };

  const handleSave = () => {
    console.log('Salvando configurações:', settings);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Configurações</DialogTitle>
      
      <DialogContent>
        <List>
          <ListItem>
            <ListItemText 
              primary="Notificações Push" 
              secondary="Receber notificações no navegador"
            />
            <ListItemSecondaryAction>
              <Switch
                checked={settings.notifications}
                onChange={() => handleSettingChange('notifications')}
              />
            </ListItemSecondaryAction>
          </ListItem>
          
          <ListItem>
            <ListItemText 
              primary="Alertas por Email" 
              secondary="Receber alertas importantes por email"
            />
            <ListItemSecondaryAction>
              <Switch
                checked={settings.emailAlerts}
                onChange={() => handleSettingChange('emailAlerts')}
              />
            </ListItemSecondaryAction>
          </ListItem>
          
          <Divider />
          
          <ListItem>
            <ListItemText 
              primary="Modo Escuro" 
              secondary="Usar tema escuro na interface"
            />
            <ListItemSecondaryAction>
              <Switch
                checked={settings.darkMode}
                onChange={() => handleSettingChange('darkMode')}
              />
            </ListItemSecondaryAction>
          </ListItem>
          
          <ListItem>
            <ListItemText 
              primary="Backup Automático" 
              secondary="Fazer backup dos dados automaticamente"
            />
            <ListItemSecondaryAction>
              <Switch
                checked={settings.autoBackup}
                onChange={() => handleSettingChange('autoBackup')}
              />
            </ListItemSecondaryAction>
          </ListItem>
        </List>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSave} variant="contained">Salvar</Button>
      </DialogActions>
    </Dialog>
  );
};

export default Settings;