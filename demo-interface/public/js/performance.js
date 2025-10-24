// Performance Optimization - <2s carregamento inicial
class PerformanceOptimizer {
    constructor() {
        this.loadStartTime = performance.now();
        this.criticalResources = [];
        this.deferredTasks = [];
        this.init();
    }

    init() {
        // Preload crítico
        this.preloadCriticalResources();
        
        // Lazy loading
        this.setupLazyLoading();
        
        // Cache estratégico
        this.setupCaching();
        
        // Métricas
        this.trackPerformance();
    }

    preloadCriticalResources() {
        const criticalCSS = document.createElement('link');
        criticalCSS.rel = 'preload';
        criticalCSS.href = 'css/styles.css';
        criticalCSS.as = 'style';
        document.head.appendChild(criticalCSS);

        const criticalJS = document.createElement('link');
        criticalJS.rel = 'preload';
        criticalJS.href = 'js/api.js';
        criticalJS.as = 'script';
        document.head.appendChild(criticalJS);
    }

    setupLazyLoading() {
        // Lazy load de componentes não críticos
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadComponent(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        // Observar cards não críticos
        document.querySelectorAll('.card:nth-child(n+3)').forEach(card => {
            observer.observe(card);
        });
    }

    setupCaching() {
        // Cache de API responses
        this.apiCache = new Map();
        
        // Service Worker para cache offline
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js').catch(console.error);
        }
    }

    // Cache inteligente para API
    async cachedRequest(url, options = {}) {
        const cacheKey = `${url}_${JSON.stringify(options)}`;
        const cached = this.apiCache.get(cacheKey);
        
        if (cached && Date.now() - cached.timestamp < 30000) { // 30s cache
            return cached.data;
        }

        try {
            const response = await fetch(url, options);
            const data = await response.json();
            
            this.apiCache.set(cacheKey, {
                data,
                timestamp: Date.now()
            });
            
            return data;
        } catch (error) {
            if (cached) return cached.data; // Fallback para cache expirado
            throw error;
        }
    }

    // Carregamento progressivo de dados
    async loadDashboardProgressive() {
        // 1. Dados críticos primeiro (métricas principais)
        await this.loadCriticalData();
        
        // 2. Dados secundários (transações recentes)
        setTimeout(() => this.loadSecondaryData(), 100);
        
        // 3. Dados terciários (gráficos, relatórios)
        setTimeout(() => this.loadTertiaryData(), 500);
    }

    async loadCriticalData() {
        // Apenas dados essenciais para primeira renderização
        const summary = await this.cachedRequest('/api/transactions/summary/');
        this.updateMetrics(summary);
    }

    async loadSecondaryData() {
        // Dados importantes mas não críticos
        const [transactions, budgets] = await Promise.all([
            this.cachedRequest('/api/transactions/?limit=5'),
            this.cachedRequest('/api/budgets/?limit=3')
        ]);
        
        this.updateTransactions(transactions);
        this.updateBudgets(budgets);
    }

    async loadTertiaryData() {
        // Dados complementares
        const [accounts, alerts] = await Promise.all([
            this.cachedRequest('/api/accounts/summary/'),
            this.cachedRequest('/api/alerts/?is_active=true&limit=3')
        ]);
        
        this.updateAccounts(accounts);
        this.updateAlerts(alerts);
    }

    // Otimização de DOM
    batchDOMUpdates(updates) {
        requestAnimationFrame(() => {
            updates.forEach(update => update());
        });
    }

    // Debounce para eventos frequentes
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Throttle para scroll events
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }

    trackPerformance() {
        // Métricas de performance
        window.addEventListener('load', () => {
            const loadTime = performance.now() - this.loadStartTime;
            
            // Log performance
            console.log(`🚀 Carregamento completo: ${loadTime.toFixed(2)}ms`);
            
            // Enviar métricas se necessário
            if (loadTime > 2000) {
                console.warn('⚠️ Carregamento acima de 2s:', loadTime);
            }
            
            // Core Web Vitals
            this.measureWebVitals();
        });
    }

    measureWebVitals() {
        // Largest Contentful Paint
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            console.log('LCP:', lastEntry.startTime);
        }).observe({entryTypes: ['largest-contentful-paint']});

        // First Input Delay
        new PerformanceObserver((entryList) => {
            const firstInput = entryList.getEntries()[0];
            console.log('FID:', firstInput.processingStart - firstInput.startTime);
        }).observe({entryTypes: ['first-input']});

        // Cumulative Layout Shift
        let clsValue = 0;
        new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                }
            }
            console.log('CLS:', clsValue);
        }).observe({entryTypes: ['layout-shift']});
    }

    // Otimização de imagens
    optimizeImages() {
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            // Lazy loading nativo
            img.loading = 'lazy';
            
            // WebP fallback
            if (this.supportsWebP()) {
                const webpSrc = img.src.replace(/\.(jpg|jpeg|png)$/, '.webp');
                img.src = webpSrc;
            }
        });
    }

    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }

    // Cleanup de recursos
    cleanup() {
        // Limpar cache antigo
        const now = Date.now();
        for (const [key, value] of this.apiCache.entries()) {
            if (now - value.timestamp > 300000) { // 5 minutos
                this.apiCache.delete(key);
            }
        }
    }
}

// Inicializar otimizador
const performanceOptimizer = new PerformanceOptimizer();

// Cleanup periódico
setInterval(() => performanceOptimizer.cleanup(), 300000); // 5 minutos

// Export para uso global
window.performanceOptimizer = performanceOptimizer;