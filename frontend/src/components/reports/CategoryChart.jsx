import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Skeleton,
  Alert,
  ToggleButton,
  ToggleButtonGroup
} from '@mui/material';
import {
  PieChart as PieChartIcon,
  DonutLarge,
  TrendingUp,
  TrendingDown,
  Remove
} from '@mui/icons-material';
import { Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import reportsService from '../../services/reports';

ChartJS.register(ArcElement, Tooltip, Legend);

const CategoryChart = ({ 
  breakdown, 
  loading, 
  error, 
  title = "Gastos por Categoria",
  chartType = 'doughnut',
  onChartTypeChange,
  showLegend = true 
}) => {
  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <Skeleton width="60%" />
          </Typography>
          <Box display="flex" justifyContent="center" mb={3}>
            <Skeleton variant="circular" width={200} height={200} />
          </Box>
          <List>
            {[...Array(5)].map((_, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Skeleton variant="circular" width={24} height={24} />
                </ListItemIcon>
                <ListItemText
                  primary={<Skeleton width="60%" />}
                  secondary={<Skeleton width="40%" />}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
      </Alert>
    );
  }

  if (!breakdown || breakdown.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            py={6}
          >
            <PieChartIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              Nenhum dado encontrado para o período selecionado
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const chartData = reportsService.prepareCategoryChartData(breakdown);
  const chartOptions = reportsService.getChartOptions(null, chartType);

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return <TrendingUp sx={{ color: 'error.main', fontSize: 16 }} />;
      case 'down':
        return <TrendingDown sx={{ color: 'success.main', fontSize: 16 }} />;
      default:
        return <Remove sx={{ color: 'text.secondary', fontSize: 16 }} />;
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up': return 'error';
      case 'down': return 'success';
      default: return 'default';
    }
  };

  const ChartComponent = chartType === 'pie' ? Pie : Doughnut;

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">
            {title}
          </Typography>
          {onChartTypeChange && (
            <ToggleButtonGroup
              value={chartType}
              exclusive
              onChange={(e, newType) => newType && onChartTypeChange(newType)}
              size="small"
            >
              <ToggleButton value="pie">
                <PieChartIcon />
              </ToggleButton>
              <ToggleButton value="doughnut">
                <DonutLarge />
              </ToggleButton>
            </ToggleButtonGroup>
          )}
        </Box>

        <Box display="flex" flexDirection={{ xs: 'column', md: 'row' }} gap={3}>
          {/* Gráfico */}
          <Box flex={1} display="flex" justifyContent="center" alignItems="center">
            <Box sx={{ width: '100%', maxWidth: 300, height: 300 }}>
              <ChartComponent data={chartData} options={chartOptions} />
            </Box>
          </Box>

          {/* Lista de categorias */}
          {showLegend && (
            <Box flex={1} minWidth={300}>
              <Typography variant="subtitle2" gutterBottom>
                Detalhamento por Categoria
              </Typography>
              <List dense>
                {breakdown.map((item, index) => (
                  <ListItem key={item.category_id} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          borderRadius: '50%',
                          backgroundColor: item.category_color || reportsService.getChartColors()[index]
                        }}
                      />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2" fontWeight="medium">
                            {item.category_name}
                          </Typography>
                          {getTrendIcon(item.trend)}
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {reportsService.formatCurrency(item.total_amount)} ({reportsService.formatPercentage(item.percentage)})
                          </Typography>
                          <Box display="flex" gap={1} mt={0.5}>
                            <Chip
                              label={`${item.transaction_count} transações`}
                              size="small"
                              variant="outlined"
                            />
                            {item.amount_change !== 0 && (
                              <Chip
                                label={`${item.amount_change > 0 ? '+' : ''}${reportsService.formatPercentage(item.amount_change)}`}
                                size="small"
                                color={getTrendColor(item.trend)}
                                variant="outlined"
                              />
                            )}
                          </Box>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>

              {/* Resumo */}
              <Box mt={2} p={2} sx={{ backgroundColor: 'background.paper', borderRadius: 1 }}>
                <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                  Resumo
                </Typography>
                <Typography variant="body2">
                  Total: {reportsService.formatCurrency(breakdown.reduce((sum, item) => sum + parseFloat(item.total_amount), 0))}
                </Typography>
                <Typography variant="body2">
                  Categorias: {breakdown.length}
                </Typography>
                <Typography variant="body2">
                  Transações: {breakdown.reduce((sum, item) => sum + item.transaction_count, 0)}
                </Typography>
              </Box>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default CategoryChart;