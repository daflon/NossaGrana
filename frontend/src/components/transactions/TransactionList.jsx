import React from 'react';
import {
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Box,
  Chip,
  Skeleton,
  Alert,
  Button,
  Divider
} from '@mui/material';
import {
  Edit,
  Delete,
  TrendingUp,
  TrendingDown,
  Add
} from '@mui/icons-material';

const TransactionList = ({ 
  transactions, 
  loading, 
  error, 
  onEdit, 
  onDelete, 
  onAdd 
}) => {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const getTransactionIcon = (type) => {
    return type === 'income' ? (
      <TrendingUp sx={{ color: 'success.main' }} />
    ) : (
      <TrendingDown sx={{ color: 'error.main' }} />
    );
  };

  const getTransactionColor = (type) => {
    return type === 'income' ? 'success.main' : 'error.main';
  };

  const getTransactionTypeText = (type) => {
    return type === 'income' ? 'Receita' : 'Despesa';
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Lista de Transações
          </Typography>
          <List>
            {[...Array(5)].map((_, index) => (
              <ListItem key={index}>
                <Box display="flex" alignItems="center" width="100%">
                  <Skeleton variant="circular" width={40} height={40} sx={{ mr: 2 }} />
                  <Box flex={1}>
                    <Skeleton variant="text" width="60%" />
                    <Skeleton variant="text" width="40%" />
                  </Box>
                  <Skeleton variant="text" width={80} />
                </Box>
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const transactionsToRender = Array.isArray(transactions) ? transactions : [];

  if (transactionsToRender.length === 0) {
    return (
      <Card>
        <CardContent>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            py={6}
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Nenhuma transação encontrada
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Comece adicionando sua primeira transação
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={onAdd}
            >
              Adicionar Transação
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Lista de Transações ({transactionsToRender.length})
          </Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={onAdd}
            size="small"
          >
            Nova Transação
          </Button>
        </Box>

        <List>
          {transactionsToRender.map((transaction, index) => (
            <React.Fragment key={transaction.id}>
              <ListItem
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 1,
                  '&:hover': {
                    backgroundColor: 'action.hover'
                  }
                }}
              >
                <Box display="flex" alignItems="center" mr={2}>
                  {getTransactionIcon(transaction.type)}
                </Box>

                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle1" component="span">
                        {transaction.description}
                      </Typography>
                      <Chip
                        label={getTransactionTypeText(transaction.type)}
                        size="small"
                        color={transaction.type === 'income' ? 'success' : 'error'}
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {transaction.category_name} • {formatDate(transaction.date)}
                      </Typography>
                      {transaction.tags_list && transaction.tags_list.length > 0 && (
                        <Box display="flex" gap={0.5} mt={0.5}>
                          {transaction.tags_list.map((tag) => (
                            <Chip
                              key={tag.id}
                              label={tag.name}
                              size="small"
                              sx={{
                                backgroundColor: tag.color,
                                color: 'white',
                                fontSize: '0.7rem',
                                height: 20
                              }}
                            />
                          ))}
                        </Box>
                      )}
                    </Box>
                  }
                />

                <Box display="flex" alignItems="center" gap={2}>
                  <Typography
                    variant="h6"
                    sx={{
                      color: getTransactionColor(transaction.type),
                      fontWeight: 'bold'
                    }}
                  >
                    {formatCurrency(transaction.amount)}
                  </Typography>

                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => onEdit(transaction)}
                      size="small"
                      sx={{ mr: 1 }}
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      edge="end"
                      onClick={() => onDelete(transaction.id)}
                      size="small"
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  </ListItemSecondaryAction>
                </Box>
              </ListItem>
              {index < transactionsToRender.length - 1 && <Divider sx={{ my: 1 }} />}
            </React.Fragment>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default TransactionList;