const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const cookieParser = require('cookie-parser');
const session = require('express-session');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

// Configurações do Express
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(cookieParser());
app.use(session({
    secret: 'nossa-grana-secret-key',
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false, maxAge: 24 * 60 * 60 * 1000 } // 24 horas
}));

// Middleware para verificar autenticação
const requireAuth = (req, res, next) => {
    if (!req.session.accessToken) {
        return res.redirect('/login');
    }
    next();
};

// Middleware para adicionar token nas requisições
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000
});

// Interceptor para adicionar token automaticamente
apiClient.interceptors.request.use((config) => {
    if (config.session && config.session.accessToken) {
        config.headers.Authorization = `Bearer ${config.session.accessToken}`;
    }
    return config;
});

// Interceptor para lidar com erros de autenticação
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expirado, tentar refresh
            // Por simplicidade, vamos apenas redirecionar para login
            throw new Error('Token expirado');
        }
        throw error;
    }
);

// Função helper para fazer requisições autenticadas
const makeAuthenticatedRequest = async (req, method, endpoint, data = null) => {
    try {
        const config = {
            method,
            url: endpoint,
            session: req.session
        };
        
        if (data) {
            config.data = data;
        }
        
        const response = await apiClient(config);
        return response.data;
    } catch (error) {
        console.error(`Erro na requisição ${method} ${endpoint}:`, error.message);
        throw error;
    }
};

// Rotas de Autenticação
app.get('/', (req, res) => {
    if (req.session.accessToken) {
        res.redirect('/dashboard');
    } else {
        res.redirect('/login');
    }
});

app.get('/login', (req, res) => {
    res.render('auth/login', { error: null });
});

app.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        const response = await apiClient.post('/auth/login/', { email, password });
        
        req.session.accessToken = response.data.access;
        req.session.refreshToken = response.data.refresh;
        req.session.user = response.data.user;
        
        res.redirect('/dashboard');
    } catch (error) {
        const errorMessage = error.response?.data?.detail || 'Erro no login';
        res.render('auth/login', { error: errorMessage });
    }
});

app.get('/register', (req, res) => {
    res.render('auth/register', { error: null, success: null });
});

app.post('/register', async (req, res) => {
    try {
        const userData = req.body;
        await apiClient.post('/auth/register/', userData);
        res.render('auth/register', { 
            error: null, 
            success: 'Usuário registrado com sucesso! Faça login.' 
        });
    } catch (error) {
        const errorMessage = error.response?.data?.detail || 'Erro no registro';
        res.render('auth/register', { error: errorMessage, success: null });
    }
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login');
});

// Dashboard Principal
app.get('/dashboard', requireAuth, async (req, res) => {
    try {
        // Carregar dados do dashboard
        const [transactionsSummary, budgetStatus, recentTransactions] = await Promise.all([
            makeAuthenticatedRequest(req, 'GET', '/transactions/transactions/summary/'),
            makeAuthenticatedRequest(req, 'GET', '/budgets/status/').catch(() => null),
            makeAuthenticatedRequest(req, 'GET', '/transactions/transactions/?limit=5')
        ]);

        res.render('dashboard/index', {
            user: req.session.user,
            summary: transactionsSummary,
            budgetStatus,
            recentTransactions: recentTransactions.results || recentTransactions
        });
    } catch (error) {
        console.error('Erro no dashboard:', error.message);
        res.render('dashboard/index', {
            user: req.session.user,
            summary: null,
            budgetStatus: null,
            recentTransactions: [],
            error: 'Erro ao carregar dados do dashboard'
        });
    }
});

// Rotas de Transações
app.get('/transactions', requireAuth, async (req, res) => {
    try {
        const page = req.query.page || 1;
        const type = req.query.type || '';
        const category = req.query.category || '';
        
        let endpoint = `/transactions/transactions/?page=${page}`;
        if (type) endpoint += `&type=${type}`;
        if (category) endpoint += `&category=${category}`;
        
        const [transactions, categories] = await Promise.all([
            makeAuthenticatedRequest(req, 'GET', endpoint),
            makeAuthenticatedRequest(req, 'GET', '/transactions/categories/')
        ]);

        res.render('transactions/index', {
            transactions: transactions.results || transactions,
            categories: categories.results || categories,
            pagination: transactions.count ? {
                count: transactions.count,
                next: transactions.next,
                previous: transactions.previous,
                currentPage: parseInt(page)
            } : null,
            filters: { type, category }
        });
    } catch (error) {
        console.error('Erro ao carregar transações:', error.message);
        res.render('transactions/index', {
            transactions: [],
            categories: [],
            pagination: null,
            filters: { type: '', category: '' },
            error: 'Erro ao carregar transações'
        });
    }
});

app.get('/transactions/new', requireAuth, async (req, res) => {
    try {
        const categories = await makeAuthenticatedRequest(req, 'GET', '/transactions/categories/');
        res.render('transactions/form', {
            transaction: null,
            categories: categories.results || categories,
            error: null
        });
    } catch (error) {
        res.render('transactions/form', {
            transaction: null,
            categories: [],
            error: 'Erro ao carregar categorias'
        });
    }
});

app.post('/transactions', requireAuth, async (req, res) => {
    try {
        await makeAuthenticatedRequest(req, 'POST', '/transactions/transactions/', req.body);
        res.redirect('/transactions?success=Transação criada com sucesso');
    } catch (error) {
        const categories = await makeAuthenticatedRequest(req, 'GET', '/transactions/categories/').catch(() => []);
        res.render('transactions/form', {
            transaction: req.body,
            categories: categories.results || categories,
            error: error.response?.data?.detail || 'Erro ao criar transação'
        });
    }
});

// Rotas de Orçamentos
app.get('/budgets', requireAuth, async (req, res) => {
    try {
        const month = req.query.month || new Date().toISOString().slice(0, 7);
        
        const [budgets, budgetStatus, categories] = await Promise.all([
            makeAuthenticatedRequest(req, 'GET', `/budgets/budgets/?month=${month}`),
            makeAuthenticatedRequest(req, 'GET', `/budgets/status/?month=${month}`).catch(() => null),
            makeAuthenticatedRequest(req, 'GET', `/budgets/budgets/categories_without_budget/?month=${month}`).catch(() => [])
        ]);

        res.render('budgets/index', {
            budgets: budgets.results || budgets,
            budgetStatus,
            availableCategories: categories,
            selectedMonth: month,
            error: null
        });
    } catch (error) {
        console.error('Erro ao carregar orçamentos:', error.message);
        res.render('budgets/index', {
            budgets: [],
            budgetStatus: null,
            availableCategories: [],
            selectedMonth: req.query.month || new Date().toISOString().slice(0, 7),
            error: 'Erro ao carregar orçamentos'
        });
    }
});

app.get('/budgets/new', requireAuth, async (req, res) => {
    try {
        const month = req.query.month || new Date().toISOString().slice(0, 7);
        const categories = await makeAuthenticatedRequest(req, 'GET', `/budgets/budgets/categories_without_budget/?month=${month}`);
        
        res.render('budgets/form', {
            budget: null,
            categories,
            selectedMonth: month,
            error: null
        });
    } catch (error) {
        res.render('budgets/form', {
            budget: null,
            categories: [],
            selectedMonth: req.query.month || new Date().toISOString().slice(0, 7),
            error: 'Erro ao carregar categorias'
        });
    }
});

app.post('/budgets', requireAuth, async (req, res) => {
    try {
        await makeAuthenticatedRequest(req, 'POST', '/budgets/budgets/', req.body);
        res.redirect('/budgets?success=Orçamento criado com sucesso');
    } catch (error) {
        const categories = await makeAuthenticatedRequest(req, 'GET', `/budgets/budgets/categories_without_budget/?month=${req.body.month}`).catch(() => []);
        res.render('budgets/form', {
            budget: req.body,
            categories,
            selectedMonth: req.body.month,
            error: error.response?.data?.detail || 'Erro ao criar orçamento'
        });
    }
});

// Rota para análise de progresso de orçamentos
app.get('/budgets/analysis', requireAuth, async (req, res) => {
    try {
        const month = req.query.month || new Date().toISOString().slice(0, 7);
        const analysis = await makeAuthenticatedRequest(req, 'GET', `/budgets/budgets/progress_analysis/?month=${month}`);
        
        res.render('budgets/analysis', {
            analysis,
            selectedMonth: month,
            error: null
        });
    } catch (error) {
        console.error('Erro ao carregar análise:', error.message);
        res.render('budgets/analysis', {
            analysis: null,
            selectedMonth: req.query.month || new Date().toISOString().slice(0, 7),
            error: 'Erro ao carregar análise de orçamentos'
        });
    }
});

// Rotas de Alertas
app.get('/alerts', requireAuth, async (req, res) => {
    try {
        const [alerts, alertsSummary] = await Promise.all([
            makeAuthenticatedRequest(req, 'GET', '/budgets/alerts/?is_active=true'),
            makeAuthenticatedRequest(req, 'GET', '/budgets/alerts/summary/')
        ]);

        res.render('alerts/index', {
            alerts: alerts.results || alerts,
            summary: alertsSummary,
            error: null
        });
    } catch (error) {
        console.error('Erro ao carregar alertas:', error.message);
        res.render('alerts/index', {
            alerts: [],
            summary: null,
            error: 'Erro ao carregar alertas'
        });
    }
});

// Rota para resolver alerta
app.post('/alerts/:id/resolve', requireAuth, async (req, res) => {
    try {
        await makeAuthenticatedRequest(req, 'POST', `/budgets/alerts/${req.params.id}/resolve/`);
        res.redirect('/alerts?success=Alerta resolvido com sucesso');
    } catch (error) {
        res.redirect('/alerts?error=Erro ao resolver alerta');
    }
});

// Rotas de Relatórios
app.get('/reports', requireAuth, async (req, res) => {
    try {
        const period = req.query.period || 'monthly';
        const month = req.query.month || new Date().toISOString().slice(0, 7);
        
        // Por enquanto, usar dados básicos - pode ser expandido com endpoints específicos de relatórios
        const [summary, transactions] = await Promise.all([
            makeAuthenticatedRequest(req, 'GET', '/transactions/transactions/summary/'),
            makeAuthenticatedRequest(req, 'GET', `/transactions/transactions/?date_after=${month}-01&date_before=${month}-31`)
        ]);

        res.render('reports/index', {
            summary,
            transactions: transactions.results || transactions,
            period,
            selectedMonth: month,
            error: null
        });
    } catch (error) {
        console.error('Erro ao carregar relatórios:', error.message);
        res.render('reports/index', {
            summary: null,
            transactions: [],
            period: 'monthly',
            selectedMonth: req.query.month || new Date().toISOString().slice(0, 7),
            error: 'Erro ao carregar relatórios'
        });
    }
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`🚀 Servidor Nossa Grana rodando na porta ${PORT}`);
    console.log(`📱 Acesse: http://localhost:${PORT}`);
    console.log(`🔗 API Backend: ${API_BASE_URL}`);
});