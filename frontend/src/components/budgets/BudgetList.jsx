import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Grid,
  Alert,
  Skeleton
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import budgetService from '../../services/budgets';

const BudgetCard = ({ budget, onEdit, onDelete }) => {
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleEdit = () => {
    onEdit(budget);
    handleMenuClose();
  };

  const handleDelete = () => {
    onDelete(budget);
    handleMenuClose();
  };

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

  return (
    <Card sx={{ height: '100%', position: 'relative' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 12,
                height: 12,
                borderRadius: '50%',
                backgroundColor: budget.category_color
              }}
            />
            <Typography variant="h6" component="h3">
              {budget.category_name}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              icon={getStatusIcon()}
              label={getStatusText()}
              color={getStatusColor()}
              size="small"
            />
            <IconButton size="small" onClick={handleMenuOpen}>
              <MoreVertIcon />
            </IconButton>
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {budget.month_display}
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2">
              Gasto: {budgetService.formatCurrency(budget.spent_amount)}
            </Typography>
            <Typography variant="body2">
              Orçado: {budgetService.formatCurrency(budget.amount)}
            </Typography>
          </Box>
          
          <LinearProgress
            variant="determinate"
            value={Math.min(budget.percentage_used, 100)}
            color={getStatusColor()}
            sx={{ height: 8, borderRadius: 4 }}
          />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {budget.percentage_used.toFixed(1)}% usado
            </Typography>
            <Typography 
              variant="caption" 
              color={budget.remaining_amount >= 0 ? 'success.main' : 'error.main'}
            >
              Restante: {budgetService.formatCurrency(budget.remaining_amount)}
            </Typography>
          </Box>
        </Box>

        {budget.is_over_budget && (
          <Alert severity="error" sx={{ mt: 1 }}>
            Orçamento excedido em {budgetService.formatCurrency(Math.abs(budget.remaining_amount))}
          </Alert>
        )}

        {budget.is_near_limit && !budget.is_over_budget && (
          <Alert severity="warning" sx={{ mt: 1 }}>
            Próximo do limite ({budget.percentage_used.toFixed(1)}%)
          </Alert>
        )}
      </CardContent>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleEdit}>
          <EditIcon sx={{ mr: 1 }} />
          Editar
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} />
          Excluir
        </MenuItem>
      </Menu>
    </Card>
  );
};

const BudgetListSkeleton = () => (
  <Grid container spacing={3}>
    {[1, 2, 3, 4].map((item) => (
      <Grid item xs={12} sm={6} md={4} key={item}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Skeleton variant="text" width={120} />
              <Skeleton variant="rectangular" width={60} height={24} />
            </Box>
            <Skeleton variant="text" width={80} />
            <Box sx={{ mt: 2 }}>
              <Skeleton variant="text" width="100%" />
              <Skeleton variant="rectangular" width="100%" height={8} sx={{ mt: 1 }} />
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Skeleton variant="text" width={80} />
                <Skeleton variant="text" width={100} />
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    ))}
  </Grid>
);

const BudgetList = ({ budgets, loading, onEdit, onDelete }) => {
  if (loading) {
    return <BudgetListSkeleton />;
  }

  if (!budgets || budgets.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h6" color="text.secondary">
          Nenhum orçamento encontrado
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Crie seu primeiro orçamento para começar a controlar seus gastos
        </Typography>
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      {budgets.map((budget) => (
        <Grid item xs={12} sm={6} md={4} key={budget.id}>
          <BudgetCard
            budget={budget}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        </Grid>
      ))}
    </Grid>
  );
};

export default BudgetList;