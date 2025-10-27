import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Avatar,
  Typography,
  Divider
} from '@mui/material';
import { useAuth } from '../../hooks/useAuth';

const UserProfile = ({ open, onClose }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = () => {
    // Implementar salvamento do perfil
    console.log('Salvando perfil:', formData);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar sx={{ width: 56, height: 56, bgcolor: 'primary.main' }}>
            {user?.email?.charAt(0).toUpperCase()}
          </Avatar>
          <Typography variant="h6">Perfil do Usuário</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
          <TextField
            name="name"
            label="Nome"
            value={formData.name}
            onChange={handleChange}
            fullWidth
          />
          <TextField
            name="email"
            label="Email"
            value={formData.email}
            onChange={handleChange}
            fullWidth
            disabled
          />
          <TextField
            name="phone"
            label="Telefone"
            value={formData.phone}
            onChange={handleChange}
            fullWidth
          />
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSave} variant="contained">Salvar</Button>
      </DialogActions>
    </Dialog>
  );
};

export default UserProfile;