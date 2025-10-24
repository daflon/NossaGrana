import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Tabs,
  Tab,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Paper,
  Grid
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useBudgets, useBudgetStatus } from '../hooks/useBudgets';
import { useNotifications, useBudgetAlerts } from '../components/common/NotificationSystem';
import BudgetList from '../components/budgets/BudgetList';
import BudgetProgress from '../components/budgets/BudgetProgress';
import BudgetForm from '../components/budgets/BudgetForm';
import BudgetAlertCenter from '../components/budgets/BudgetAlertCenter';
import BudgetProgressCard from '../components/budgets/BudgetProgressCard';
import budgetService from '../services/budgets';

const Budgets = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedMonth, setSelectedMonth] = useState(budgetService.getCurrentMonth());
  const [formOpen, setFormOpen] = useState(false);
  const [editingBudget, setEditingBudget] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [budgetToDelete, setBudgetToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Hooks para notificações e alertas
  const { showSuccess, showError, showWarning } = useNotifications();
  const { checkBudgetAlerts } = useBudgetAlerts();

  // Hooks para gerenciar orçamentos
  const {
    budgets,
    loading: budgetsLoading,
    error: budgetsError,
    loadBudgets,
    createBudget,
    updateBudget,
    deleteBudget,
    updateFilters,
    setError: setBudgetsError
  } = useBudgets({ month: selectedMonth });

  const {
    status,
    loading: statusLoading,
    error: statusError,
    loadStatus
  } = useBudgetStatus(selectedMonth);

  // Atualizar filtros quando mês mudar
  useEffect(() => {
    updateFilters({ month: selectedMonth });
  }, [selectedMonth, updateFilters]);

  // Verificar alertas quando orçamentos mudarem
  useEffect(() => {
    if (budgets && budgets.length > 0) {
      checkBudgetAlerts(budgets);
    }
  }, [budgets, checkBudgetAlerts]);

  // Gerar opções de meses (atual + próximos 11 meses)
  const getMonthOptions = () => {
    const options = [];
    const currentDate = new Date();
    
    for (let i = 0; i < 12; i++) {
      const date = new Date(currentDate.getFullYear(), currentDate.getMonth() + i, 1);
      const value = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      const label = date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
      options.push({ value, label });
    }
    
    return options;
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleMonthChange = (event) => {
    setSelectedMonth(event.target.value);
  };

  const handleCreateBudget = () => {
    setEditingBudget(null);
    setFormOpen(true);
  };

  const handleEditBudget = (budget) => {
    setEditingBudget(budget);
    setFormOpen(true);
  };

  const handleDeleteBudget = (budget) => {
    setBudgetToDelete(budget);
    setDeleteDialogOpen(true);
  };

  const handleFormSubmit = async (budgetData) => {
    try {
      if (editingBudget) {
        await updateBudget(editingBudget.id, budgetData);
        showSuccess('Orçamento atualizado com sucesso!');
      } else {
        await createBudget(budgetData);
        showSuccess('Orçamento criado com sucesso!');
      }
      
      // Recarregar status se necessário
      if (budgetData.month === selectedMonth) {
        loadStatus(selectedMonth);
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          'Erro ao salvar orçamento';
      showError(errorMessage);
    }
  };

  const handleConfirmDelete = async () => {
    if (!budgetToDelete) return;

    try {
      await deleteBudget(budgetToDelete.id);
      showSuccess('Orçamento excluído com sucesso!');
      
      // Recarregar status
      loadStatus(selectedMonth);
    } catch (error) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          'Erro ao excluir orçamento';
      showError(errorMessage);
    } finally {
      setDeleteDialogOpen(false);
      setBudgetToDelete(null);
    }
  };

  const handleRefresh = () => {
    loadBudgets();
    loadStatus(selectedMonth);
    setBudgetsError(null);
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const monthOptions = getMonthOptions();
  const currentMonthLabel = monthOptions.find(option => option.value === selectedMonth)?.label || '';

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Orçamentos
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Mês</InputLabel>
            <Select
              value={selectedMonth}
              label="Mês"
              onChange={handleMonthChange}
            >
              {monthOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={handleRefresh}
            disabled={budgetsLoading}
          >
            Atualizar
          </Button>
          
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreateBudget}
          >
            Novo Orçamento
          </Button>
        </Box>
      </Box>

      {/* Status Summary */}
      {status && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Resumo - {currentMonthLabel}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Total Orçado
              </Typography>
              <Typography variant="h6" color="primary">
                {budgetService.formatCurrency(status.summary.total_budgeted)}
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="body2" color="text.secondary">
                Total Gasto
              </Typography>
              <Typography variant="h6" color="error">
                {budgetService.formatCurrency(status.summary.total_spent)}
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="body2" color="text.secondary">
                Restante
              </Typography>
              <Typography 
                variant="h6" 
                color={status.summary.total_remaining >= 0 ? 'success.main' : 'error.main'}
              >
                {budgetService.formatCurrency(status.summary.total_remaining)}
              </Typography>
            </Box>
            
            <Box>
              <Typography variant="body2" color="text.secondary">
                Orçamentos
              </Typography>
              <Typography variant="body1">
                <span style={{ color: '#4caf50' }}>{status.summary.budgets_ok} OK</span> • 
                <span style={{ color: '#ff9800', marginLeft: 4 }}>{status.summary.budgets_warning} Atenção</span> • 
                <span style={{ color: '#f44336', marginLeft: 4 }}>{status.summary.budgets_exceeded} Excedidos</span>
              </Typography>
            </Box>
          </Box>
        </Paper>
      )}

      {/* Error Alerts */}
      {budgetsError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setBudgetsError(null)}>
          {budgetsError}
        </Alert>
      )}

      {statusError && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Erro ao carregar resumo: {statusError}
        </Alert>
      )}

      {/* Central de Alertas */}
      <BudgetAlertCenter />

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Lista de Orçamentos" />
          <Tab label="Progresso Visual" />
          <Tab label="Cards de Progresso" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {tabValue === 0 && (
        <BudgetList
          budgets={budgets}
          loading={budgetsLoading}
          onEdit={handleEditBudget}
          onDelete={handleDeleteBudget}
        />
      )}

      {tabValue === 1 && (
        <BudgetProgress
          budgets={budgets}
          loading={budgetsLoading}
        />
      )}

      {tabValue === 2 && (
        <Grid container spacing={3}>
          {budgets.map((budget) => (
            <Grid item xs={12} sm={6} md={4} key={budget.id}>
              <BudgetProgressCard
                budget={budget}
                onClick={() => handleEditBudget(budget)}
              />
            </Grid>
          ))}
          {budgets.length === 0 && !budgetsLoading && (
            <Grid item xs={12}>
              <Paper sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Nenhum orçamento encontrado
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Crie seu primeiro orçamento para começar a controlar seus gastos
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleCreateBudget}
                >
                  Criar Orçamento
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}

      {/* Budget Form Dialog */}
      <BudgetForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        budget={editingBudget}
        loading={budgetsLoading}
        error={budgetsError}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirmar Exclusão</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Tem certeza que deseja excluir o orçamento de{' '}
            <strong>{budgetToDelete?.category_name}</strong> para{' '}
            <strong>{budgetToDelete?.month_display}</strong>?
          </DialogContentText>
          <DialogContentText sx={{ mt: 1, color: 'text.secondary' }}>
            Esta ação não pode ser desfeita.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancelar
          </Button>
          <Button 
            onClick={handleConfirmDelete} 
            color="error" 
            variant="contained"
            disabled={budgetsLoading}
          >
            Excluir
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert 
          onClose={handleCloseSnackbar} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Budgets;