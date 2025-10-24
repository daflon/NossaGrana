import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Alert,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ptBR } from 'date-fns/locale';
import budgetService from '../../services/budgets';
import { useCategoriesWithoutBudget } from '../../hooks/useBudgets';

const BudgetForm = ({ 
  open, 
  onClose, 
  onSubmit, 
  budget = null, 
  loading = false,
  error = null 
}) => {
  const [formData, setFormData] = useState({
    category: '',
    amount: '',
    month: new Date()
  });
  const [formErrors, setFormErrors] = useState({});
  
  const isEditing = Boolean(budget);
  const currentMonth = budgetService.getCurrentMonth();
  
  // Hook para categorias disponíveis (apenas para criação)
  const { 
    categories, 
    loading: categoriesLoading 
  } = useCategoriesWithoutBudget(
    !isEditing ? budgetService.formatMonth(formData.month.toISOString().split('T')[0]) : null
  );

  // Inicializar formulário quando budget mudar
  useEffect(() => {
    if (budget) {
      setFormData({
        category: budget.category,
        amount: budget.amount.toString(),
        month: new Date(budget.month + 'T00:00:00')
      });
    } else {
      setFormData({
        category: '',
        amount: '',
        month: new Date()
      });
    }
    setFormErrors({});
  }, [budget, open]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Limpar erro do campo quando usuário começar a digitar
    if (formErrors[field]) {
      setFormErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.category) {
      errors.category = 'Categoria é obrigatória';
    }

    if (!formData.amount) {
      errors.amount = 'Valor é obrigatório';
    } else {
      const amount = parseFloat(formData.amount);
      if (isNaN(amount) || amount <= 0) {
        errors.amount = 'Valor deve ser positivo';
      }
    }

    if (!formData.month) {
      errors.month = 'Mês é obrigatório';
    } else {
      const selectedMonth = new Date(formData.month);
      const currentDate = new Date();
      const firstDayOfCurrentMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      
      if (selectedMonth < firstDayOfCurrentMonth) {
        errors.month = 'Não é possível criar orçamentos para meses passados';
      }
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      const submitData = {
        category: parseInt(formData.category),
        amount: parseFloat(formData.amount).toFixed(2),
        month: budgetService.getFirstDayOfMonth(
          formData.month.getFullYear(),
          formData.month.getMonth() + 1
        )
      };

      await onSubmit(submitData);
      handleClose();
    } catch (err) {
      console.error('Erro ao submeter formulário:', err);
    }
  };

  const handleClose = () => {
    setFormData({
      category: '',
      amount: '',
      month: new Date()
    });
    setFormErrors({});
    onClose();
  };

  const formatCurrencyInput = (value) => {
    // Remove tudo que não é dígito ou vírgula/ponto
    const numericValue = value.replace(/[^\d.,]/g, '');
    
    // Substitui vírgula por ponto para cálculos
    const normalizedValue = numericValue.replace(',', '.');
    
    return normalizedValue;
  };

  const handleAmountChange = (e) => {
    const value = formatCurrencyInput(e.target.value);
    handleInputChange('amount', value);
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
      <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>
            {isEditing ? 'Editar Orçamento' : 'Novo Orçamento'}
          </DialogTitle>
          
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
              {error && (
                <Alert severity="error">
                  {error}
                </Alert>
              )}

              {!isEditing && (
                <FormControl fullWidth error={Boolean(formErrors.category)}>
                  <InputLabel>Categoria</InputLabel>
                  <Select
                    value={formData.category}
                    label="Categoria"
                    onChange={(e) => handleInputChange('category', e.target.value)}
                    disabled={categoriesLoading}
                  >
                    {categoriesLoading ? (
                      <MenuItem disabled>
                        <CircularProgress size={20} sx={{ mr: 1 }} />
                        Carregando categorias...
                      </MenuItem>
                    ) : (
                      categories.map((category) => (
                        <MenuItem key={category.id} value={category.id}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box
                              sx={{
                                width: 12,
                                height: 12,
                                borderRadius: '50%',
                                backgroundColor: category.color
                              }}
                            />
                            {category.name}
                          </Box>
                        </MenuItem>
                      ))
                    )}
                  </Select>
                  {formErrors.category && (
                    <Box sx={{ color: 'error.main', fontSize: '0.75rem', mt: 0.5 }}>
                      {formErrors.category}
                    </Box>
                  )}
                </FormControl>
              )}

              {isEditing && (
                <TextField
                  label="Categoria"
                  value={budget?.category_name || ''}
                  disabled
                  fullWidth
                />
              )}

              <TextField
                label="Valor do Orçamento"
                value={formData.amount}
                onChange={handleAmountChange}
                error={Boolean(formErrors.amount)}
                helperText={formErrors.amount}
                fullWidth
                InputProps={{
                  startAdornment: <InputAdornment position="start">R$</InputAdornment>,
                }}
                placeholder="0,00"
              />

              <DatePicker
                label="Mês"
                value={formData.month}
                onChange={(newValue) => handleInputChange('month', newValue)}
                views={['year', 'month']}
                format="MM/yyyy"
                disabled={isEditing}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    error: Boolean(formErrors.month),
                    helperText: formErrors.month
                  }
                }}
              />

              {isEditing && (
                <TextField
                  label="Mês"
                  value={budgetService.formatMonth(budget?.month || '')}
                  disabled
                  fullWidth
                  helperText="O mês não pode ser alterado"
                />
              )}
            </Box>
          </DialogContent>
          
          <DialogActions>
            <Button onClick={handleClose} disabled={loading}>
              Cancelar
            </Button>
            <Button 
              type="submit" 
              variant="contained" 
              disabled={loading}
              startIcon={loading && <CircularProgress size={20} />}
            >
              {loading ? 'Salvando...' : (isEditing ? 'Atualizar' : 'Criar')}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </LocalizationProvider>
  );
};

export default BudgetForm;