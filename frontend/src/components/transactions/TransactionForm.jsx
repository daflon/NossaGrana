import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Grid,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  OutlinedInput,
  Chip,
  Box,
  Alert,
  CircularProgress,
  Typography,
  IconButton
} from '@mui/material';
import {
  Close,
  Add as AddIcon
} from '@mui/icons-material';
import { useCategories, useTags } from '../../hooks/useTransactions';

const TransactionForm = ({ 
  open, 
  onClose, 
  onSubmit, 
  transaction = null,
  loading = false 
}) => {
  const { categories } = useCategories();
  const { tags, createTag } = useTags();
  const [formData, setFormData] = useState({
    type: 'expense',
    amount: '',
    description: '',
    category: '',
    date: new Date().toISOString().split('T')[0],
    tag_ids: []
  });
  const [errors, setErrors] = useState({});
  const [newTagName, setNewTagName] = useState('');
  const [showNewTagField, setShowNewTagField] = useState(false);

  useEffect(() => {
    if (transaction) {
      setFormData({
        type: transaction.type,
        amount: transaction.amount.toString(),
        description: transaction.description,
        category: transaction.category,
        date: transaction.date,
        tag_ids: transaction.tags_list ? transaction.tags_list.map(tag => tag.id) : []
      });
    } else {
      setFormData({
        type: 'expense',
        amount: '',
        description: '',
        category: '',
        date: new Date().toISOString().split('T')[0],
        tag_ids: []
      });
    }
    setErrors({});
  }, [transaction, open]);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Limpar erro do campo quando o usuário começar a digitar
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = 'Valor deve ser maior que zero';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Descrição é obrigatória';
    } else if (formData.description.trim().length < 3) {
      newErrors.description = 'Descrição deve ter pelo menos 3 caracteres';
    }

    if (!formData.category) {
      newErrors.category = 'Categoria é obrigatória';
    }

    if (!formData.date) {
      newErrors.date = 'Data é obrigatória';
    } else if (new Date(formData.date) > new Date()) {
      newErrors.date = 'Data não pode ser futura';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    const submitData = {
      ...formData,
      amount: parseFloat(formData.amount),
      description: formData.description.trim()
    };

    try {
      await onSubmit(submitData);
      onClose();
    } catch (error) {
      setErrors({ submit: error.message });
    }
  };

  const handleAddNewTag = async () => {
    if (!newTagName.trim()) return;

    try {
      const newTag = await createTag({
        name: newTagName.trim(),
        color: '#' + Math.floor(Math.random()*16777215).toString(16)
      });
      
      setFormData(prev => ({
        ...prev,
        tag_ids: [...prev.tag_ids, newTag.id]
      }));
      
      setNewTagName('');
      setShowNewTagField(false);
    } catch (error) {
      setErrors({ newTag: error.message });
    }
  };

  const renderTagChips = (selected) => {
    return (
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
        {selected.map((tagId) => {
          const tag = tags.find(t => t.id === tagId);
          return (
            <Chip
              key={tagId}
              label={tag?.name || tagId}
              size="small"
              sx={{
                backgroundColor: tag?.color || 'primary.main',
                color: 'white'
              }}
            />
          );
        })}
      </Box>
    );
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            {transaction ? 'Editar Transação' : 'Nova Transação'}
          </Typography>
          <IconButton onClick={onClose}>
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <form onSubmit={handleSubmit}>
        <DialogContent>
          {errors.submit && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {errors.submit}
            </Alert>
          )}

          <Grid container spacing={2}>
            {/* Tipo */}
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Tipo *"
                value={formData.type}
                onChange={(e) => handleChange('type', e.target.value)}
                error={!!errors.type}
                helperText={errors.type}
              >
                <MenuItem value="expense">Despesa</MenuItem>
                <MenuItem value="income">Receita</MenuItem>
              </TextField>
            </Grid>

            {/* Valor */}
            <Grid item xs={12} sm={6}>
              <TextField
                type="number"
                fullWidth
                label="Valor *"
                value={formData.amount}
                onChange={(e) => handleChange('amount', e.target.value)}
                inputProps={{ step: '0.01', min: '0.01' }}
                error={!!errors.amount}
                helperText={errors.amount}
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1 }}>R$</Typography>
                }}
              />
            </Grid>

            {/* Descrição */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Descrição *"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                error={!!errors.description}
                helperText={errors.description}
                placeholder="Ex: Compra no supermercado"
              />
            </Grid>

            {/* Categoria */}
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Categoria *"
                value={formData.category}
                onChange={(e) => handleChange('category', e.target.value)}
                error={!!errors.category}
                helperText={errors.category}
              >
                <MenuItem value="">Selecione uma categoria</MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category.id} value={category.id}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          borderRadius: '50%',
                          backgroundColor: category.color
                        }}
                      />
                      {category.name}
                    </Box>
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Data */}
            <Grid item xs={12} sm={6}>
              <TextField
                type="date"
                fullWidth
                label="Data *"
                value={formData.date}
                onChange={(e) => handleChange('date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                error={!!errors.date}
                helperText={errors.date}
              />
            </Grid>

            {/* Tags */}
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Tags</InputLabel>
                <Select
                  multiple
                  value={formData.tag_ids}
                  onChange={(e) => handleChange('tag_ids', e.target.value)}
                  input={<OutlinedInput label="Tags" />}
                  renderValue={(selected) => renderTagChips(selected)}
                >
                  {tags.map((tag) => (
                    <MenuItem key={tag.id} value={tag.id}>
                      <Chip
                        label={tag.name}
                        size="small"
                        sx={{
                          backgroundColor: tag.color,
                          color: 'white'
                        }}
                      />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Nova Tag */}
              <Box mt={1}>
                {!showNewTagField ? (
                  <Button
                    size="small"
                    startIcon={<AddIcon />}
                    onClick={() => setShowNewTagField(true)}
                  >
                    Criar Nova Tag
                  </Button>
                ) : (
                  <Box display="flex" gap={1} alignItems="center">
                    <TextField
                      size="small"
                      label="Nome da nova tag"
                      value={newTagName}
                      onChange={(e) => setNewTagName(e.target.value)}
                      error={!!errors.newTag}
                      helperText={errors.newTag}
                    />
                    <Button
                      size="small"
                      variant="contained"
                      onClick={handleAddNewTag}
                      disabled={!newTagName.trim()}
                    >
                      Adicionar
                    </Button>
                    <Button
                      size="small"
                      onClick={() => {
                        setShowNewTagField(false);
                        setNewTagName('');
                        setErrors(prev => ({ ...prev, newTag: null }));
                      }}
                    >
                      Cancelar
                    </Button>
                  </Box>
                )}
              </Box>
            </Grid>
          </Grid>
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
            startIcon={loading && <CircularProgress size={20} />}
          >
            {transaction ? 'Atualizar' : 'Salvar'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default TransactionForm;