import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Grid,
  TextField,
  MenuItem,
  Button,
  Box,
  Chip,
  FormControl,
  InputLabel,
  Select,
  OutlinedInput,
  Typography,
  Collapse,
  IconButton
} from '@mui/material';
import {
  FilterList,
  Clear,
  ExpandMore,
  ExpandLess
} from '@mui/icons-material';
import { useCategories, useTags } from '../../hooks/useTransactions';

const TransactionFilter = ({ filters, onFiltersChange, onClear }) => {
  const [localFilters, setLocalFilters] = useState(filters);
  const [expanded, setExpanded] = useState(false);
  const { categories } = useCategories();
  const { tags } = useTags();

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleFilterChange = (field, value) => {
    setLocalFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleApplyFilters = () => {
    onFiltersChange(localFilters);
  };

  const handleClearFilters = () => {
    const emptyFilters = {};
    setLocalFilters(emptyFilters);
    onClear();
  };

  const getActiveFiltersCount = () => {
    return Object.values(localFilters).filter(value => 
      value !== null && value !== undefined && value !== '' && 
      (!Array.isArray(value) || value.length > 0)
    ).length;
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
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <FilterList />
            <Typography variant="h6">
              Filtros
              {getActiveFiltersCount() > 0 && (
                <Chip 
                  label={getActiveFiltersCount()} 
                  size="small" 
                  color="primary" 
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
          </Box>
          <IconButton onClick={() => setExpanded(!expanded)}>
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>

        <Collapse in={expanded}>
          <Grid container spacing={2}>
            {/* Tipo */}
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                label="Tipo"
                value={localFilters.type || ''}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                size="small"
              >
                <MenuItem value="">Todos</MenuItem>
                <MenuItem value="income">Receitas</MenuItem>
                <MenuItem value="expense">Despesas</MenuItem>
              </TextField>
            </Grid>

            {/* Categoria */}
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                select
                fullWidth
                label="Categoria"
                value={localFilters.category || ''}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                size="small"
              >
                <MenuItem value="">Todas</MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category.id} value={category.id}>
                    {category.name}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Data Inicial */}
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                type="date"
                fullWidth
                label="Data Inicial"
                value={localFilters.date_from || ''}
                onChange={(e) => handleFilterChange('date_from', e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
            </Grid>

            {/* Data Final */}
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                type="date"
                fullWidth
                label="Data Final"
                value={localFilters.date_to || ''}
                onChange={(e) => handleFilterChange('date_to', e.target.value)}
                InputLabelProps={{ shrink: true }}
                size="small"
              />
            </Grid>

            {/* Tags */}
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Tags</InputLabel>
                <Select
                  multiple
                  value={localFilters.tags || []}
                  onChange={(e) => handleFilterChange('tags', e.target.value)}
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
            </Grid>

            {/* Valor Mínimo */}
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                type="number"
                fullWidth
                label="Valor Mínimo"
                value={localFilters.amount_min || ''}
                onChange={(e) => handleFilterChange('amount_min', e.target.value)}
                inputProps={{ step: '0.01', min: '0' }}
                size="small"
              />
            </Grid>

            {/* Valor Máximo */}
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                type="number"
                fullWidth
                label="Valor Máximo"
                value={localFilters.amount_max || ''}
                onChange={(e) => handleFilterChange('amount_max', e.target.value)}
                inputProps={{ step: '0.01', min: '0' }}
                size="small"
              />
            </Grid>

            {/* Busca */}
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Buscar"
                placeholder="Descrição ou categoria..."
                value={localFilters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                size="small"
              />
            </Grid>
          </Grid>

          <Box display="flex" gap={2} mt={3}>
            <Button
              variant="contained"
              startIcon={<FilterList />}
              onClick={handleApplyFilters}
            >
              Aplicar Filtros
            </Button>
            <Button
              variant="outlined"
              startIcon={<Clear />}
              onClick={handleClearFilters}
            >
              Limpar
            </Button>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default TransactionFilter;