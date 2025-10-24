import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions
} from '@mui/material';
import { Add, Refresh } from '@mui/icons-material';
import TransactionSummary from '../components/transactions/TransactionSummary';
import TransactionFilter from '../components/transactions/TransactionFilter';
import TransactionList from '../components/transactions/TransactionList';
import TransactionForm from '../components/transactions/TransactionForm';
import { useTransactions, useTransactionSummary } from '../hooks/useTransactions';

const Transactions = () => {
  const [filters, setFilters] = useState({});
  const [formOpen, setFormOpen] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formLoading, setFormLoading] = useState(false);

  const {
    transactions,
    loading: transactionsLoading,
    error: transactionsError,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    applyFilters,
    clearFilters,
    loadTransactions
  } = useTransactions(filters);

  const {
    summary,
    loading: summaryLoading,
    loadSummary
  } = useTransactionSummary(filters);

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
    applyFilters(newFilters);
    loadSummary(newFilters);
  };

  const handleClearFilters = () => {
    setFilters({});
    clearFilters();
    loadSummary({});
  };

  const handleAddTransaction = () => {
    setEditingTransaction(null);
    setFormOpen(true);
  };

  const handleEditTransaction = (transaction) => {
    setEditingTransaction(transaction);
    setFormOpen(true);
  };

  const handleFormSubmit = async (data) => {
    setFormLoading(true);
    try {
      if (editingTransaction) {
        await updateTransaction(editingTransaction.id, data);
        showSnackbar('Transação atualizada com sucesso!');
      } else {
        await createTransaction(data);
        showSnackbar('Transação criada com sucesso!');
      }
      
      // Recarregar resumo
      loadSummary(filters);
      setFormOpen(false);
    } catch (error) {
      showSnackbar(error.message, 'error');
      throw error; // Re-throw para que o form possa lidar com o erro
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteClick = (id) => {
    setDeletingId(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteTransaction(deletingId);
      showSnackbar('Transação excluída com sucesso!');
      loadSummary(filters);
    } catch (error) {
      showSnackbar(error.message, 'error');
    } finally {
      setDeleteDialogOpen(false);
      setDeletingId(null);
    }
  };

  const handleRefresh = () => {
    loadTransactions();
    loadSummary(filters);
  };

  return (
    <Box>
      {/* Cabeçalho */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Transações
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gerencie suas receitas e despesas
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
          >
            Atualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddTransaction}
          >
            Nova Transação
          </Button>
        </Box>
      </Box>

      {/* Resumo Financeiro */}
      <TransactionSummary 
        summary={summary} 
        loading={summaryLoading} 
      />

      {/* Filtros */}
      <TransactionFilter
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onClear={handleClearFilters}
      />

      {/* Lista de Transações */}
      <TransactionList
        transactions={transactions}
        loading={transactionsLoading}
        error={transactionsError}
        onEdit={handleEditTransaction}
        onDelete={handleDeleteClick}
        onAdd={handleAddTransaction}
      />

      {/* Formulário de Transação */}
      <TransactionForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleFormSubmit}
        transaction={editingTransaction}
        loading={formLoading}
      />

      {/* Dialog de Confirmação de Exclusão */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirmar Exclusão</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Tem certeza que deseja excluir esta transação? Esta ação não pode ser desfeita.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancelar
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Excluir
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar para mensagens */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Transactions;