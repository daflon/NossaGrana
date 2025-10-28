const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Servir arquivos estáticos
app.use('/css', express.static(path.join(__dirname, 'public/css')));
app.use('/js', express.static(path.join(__dirname, 'public/js')));
app.use('/assets', express.static(path.join(__dirname, 'public/assets')));

// Rota principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Rotas para diferentes seções
app.get('/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.get('/transactions', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'transactions.html'));
});

app.get('/accounts', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'accounts.html'));
});

app.get('/credit-cards', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'credit-cards.html'));
});

app.get('/budgets', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'budgets.html'));
});

app.get('/goals', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'goals.html'));
});

app.get('/reports', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'reports.html'));
});

app.get('/alerts', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'alerts.html'));
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`🚀 Nossa Grana Demo Interface rodando em http://localhost:${PORT}`);
    console.log(`📊 Dashboard: http://localhost:${PORT}/dashboard`);
    console.log(`💰 Transações: http://localhost:${PORT}/transactions`);
    console.log(`🏦 Contas: http://localhost:${PORT}/accounts`);
    console.log(`💳 Cartões: http://localhost:${PORT}/credit-cards`);
    console.log(`📋 Orçamentos: http://localhost:${PORT}/budgets`);
    console.log(`🎯 Metas: http://localhost:${PORT}/goals`);
    console.log(`📈 Relatórios: http://localhost:${PORT}/reports`);
    console.log(`🚨 Alertas: http://localhost:${PORT}/alerts`);
});