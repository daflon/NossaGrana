import api from './api';

const reportsService = {
  // Relatório de resumo financeiro
  async getSummary(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });

    const response = await api.get(`/reports/summary/?${queryParams.toString()}`);
    return response.data;
  },

  // Breakdown por categoria
  async getCategoryBreakdown(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });

    const response = await api.get(`/reports/category-breakdown/?${queryParams.toString()}`);
    return response.data;
  },

  // Tendências mensais
  async getMonthlyTrend(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });

    const response = await api.get(`/reports/monthly-trend/?${queryParams.toString()}`);
    return response.data;
  },

  // Padrões de gastos
  async getSpendingPatterns(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });

    const response = await api.get(`/reports/spending-patterns/?${queryParams.toString()}`);
    return response.data;
  },

  // Exportar relatório
  async exportReport(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        queryParams.append(key, params[key]);
      }
    });

    const response = await api.get(`/reports/export/?${queryParams.toString()}`);
    return response.data;
  },

  // Utilitários
  formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  },

  formatPercentage(value, decimals = 1) {
    return `${(value || 0).toFixed(decimals)}%`;
  },

  formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR');
  },

  getChangeColor(value) {
    if (value > 0) return 'success.main';
    if (value < 0) return 'error.main';
    return 'text.secondary';
  },

  getChangeIcon(value) {
    if (value > 0) return '↗️';
    if (value < 0) return '↘️';
    return '➡️';
  },

  getTrendColor(trend) {
    switch (trend) {
      case 'up': return 'error.main';
      case 'down': return 'success.main';
      case 'stable': return 'info.main';
      default: return 'text.secondary';
    }
  },

  // Configurações de gráficos
  getChartColors() {
    return [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
      '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
      '#F1948A', '#BDC3C7', '#F8C471', '#82E0AA', '#AED6F1'
    ];
  },

  getChartOptions(title, type = 'line') {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: !!title,
          text: title,
          font: {
            size: 16,
            weight: 'bold'
          }
        },
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: 'white',
          bodyColor: 'white',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          cornerRadius: 8,
          displayColors: true,
          callbacks: {
            label: function(context) {
              const label = context.dataset.label || '';
              const value = reportsService.formatCurrency(context.parsed.y || context.parsed);
              return `${label}: ${value}`;
            }
          }
        }
      }
    };

    if (type === 'line' || type === 'bar') {
      baseOptions.scales = {
        x: {
          grid: {
            display: false
          },
          ticks: {
            maxRotation: 45
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            callback: function(value) {
              return reportsService.formatCurrency(value);
            }
          }
        }
      };
    }

    if (type === 'pie' || type === 'doughnut') {
      baseOptions.plugins.tooltip.callbacks.label = function(context) {
        const label = context.label || '';
        const value = reportsService.formatCurrency(context.parsed);
        const percentage = ((context.parsed / context.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1);
        return `${label}: ${value} (${percentage}%)`;
      };
    }

    return baseOptions;
  },

  // Preparar dados para gráficos
  prepareCategoryChartData(categoryData) {
    const colors = this.getChartColors();
    
    return {
      labels: categoryData.map(item => item.category_name),
      datasets: [{
        data: categoryData.map(item => parseFloat(item.total_amount)),
        backgroundColor: categoryData.map((item, index) => 
          item.category_color || colors[index % colors.length]
        ),
        borderWidth: 2,
        borderColor: '#fff'
      }]
    };
  },

  prepareMonthlyTrendData(monthlyData) {
    return {
      labels: monthlyData.map(item => item.month_name),
      datasets: [
        {
          label: 'Receitas',
          data: monthlyData.map(item => parseFloat(item.total_income)),
          borderColor: '#4ECDC4',
          backgroundColor: 'rgba(78, 205, 196, 0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Despesas',
          data: monthlyData.map(item => parseFloat(item.total_expense)),
          borderColor: '#FF6B6B',
          backgroundColor: 'rgba(255, 107, 107, 0.1)',
          fill: true,
          tension: 0.4
        }
      ]
    };
  },

  prepareBalanceChartData(monthlyData) {
    return {
      labels: monthlyData.map(item => item.month_name),
      datasets: [{
        label: 'Saldo',
        data: monthlyData.map(item => parseFloat(item.net_balance)),
        borderColor: '#45B7D1',
        backgroundColor: monthlyData.map(item => 
          parseFloat(item.net_balance) >= 0 ? 'rgba(69, 183, 209, 0.2)' : 'rgba(255, 107, 107, 0.2)'
        ),
        fill: true,
        tension: 0.4
      }]
    };
  }
};

export default reportsService;