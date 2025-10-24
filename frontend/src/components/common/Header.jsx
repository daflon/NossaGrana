import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const Header = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAuthenticated } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Nossa Grana
        </Typography>
        
        {isAuthenticated && !isAuthPage && (
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button color="inherit" onClick={() => navigate('/')}>
              Dashboard
            </Button>
            <Button color="inherit" onClick={() => navigate('/transactions')}>
              Transações
            </Button>
            <Button color="inherit" onClick={() => navigate('/budgets')}>
              Orçamentos
            </Button>
            <Button color="inherit" onClick={() => navigate('/goals')}>
              Metas
            </Button>
            <Button color="inherit" onClick={() => navigate('/reports')}>
              Relatórios
            </Button>
            <Button color="inherit" onClick={handleLogout}>
              Sair ({user?.email})
            </Button>
          </Box>
        )}
        
        {!isAuthenticated && !isAuthPage && (
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button color="inherit" onClick={() => navigate('/login')}>
              Entrar
            </Button>
            <Button color="inherit" onClick={() => navigate('/register')}>
              Cadastrar
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;