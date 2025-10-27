/**
 * Error Boundary Manager - Nossa Grana
 */

class ErrorBoundary {
    constructor() {
        this.setupGlobalErrorHandlers();
        this.createErrorUI();
    }

    setupGlobalErrorHandlers() {
        // Capturar erros JavaScript não tratados
        window.addEventListener('error', (event) => {
            this.handleError(event.error, 'JavaScript Error');
        });

        // Capturar promises rejeitadas não tratadas
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, 'Promise Rejection');
        });
    }

    createErrorUI() {
        const errorContainer = document.createElement('div');
        errorContainer.id = 'error-boundary';
        errorContainer.innerHTML = `
            <div class="error-backdrop">
                <div class="error-content">
                    <div class="error-icon">⚠️</div>
                    <h2 class="error-title">Ops! Algo deu errado</h2>
                    <p class="error-message">Encontramos um problema inesperado. Nossa equipe foi notificada.</p>
                    <div class="error-actions">
                        <button class="btn btn-primary" onclick="errorBoundary.reload()">
                            🔄 Recarregar Página
                        </button>
                        <button class="btn btn-secondary" onclick="errorBoundary.goHome()">
                            🏠 Ir para Início
                        </button>
                    </div>
                    <details class="error-details">
                        <summary>Detalhes técnicos</summary>
                        <pre id="error-stack"></pre>
                    </details>
                </div>
            </div>
        `;

        const styles = `
            #error-boundary {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: none;
            }
            .error-backdrop {
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }
            .error-content {
                background: var(--bg-primary);
                border-radius: 16px;
                padding: 2rem;
                max-width: 500px;
                width: 100%;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            .error-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            .error-title {
                color: var(--text-primary);
                margin-bottom: 1rem;
                font-size: 1.5rem;
            }
            .error-message {
                color: var(--text-secondary);
                margin-bottom: 2rem;
                line-height: 1.5;
            }
            .error-actions {
                display: flex;
                gap: 1rem;
                justify-content: center;
                margin-bottom: 2rem;
            }
            .error-details {
                text-align: left;
                margin-top: 1rem;
            }
            .error-details summary {
                cursor: pointer;
                color: var(--text-secondary);
                font-size: 0.9rem;
            }
            .error-details pre {
                background: var(--bg-secondary);
                padding: 1rem;
                border-radius: 8px;
                font-size: 0.8rem;
                color: var(--text-primary);
                overflow-x: auto;
                margin-top: 0.5rem;
            }
        `;

        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
        document.body.appendChild(errorContainer);
    }

    handleError(error, type = 'Error') {
        console.error(`${type}:`, error);
        
        // Mostrar UI de erro
        this.showError(error);
        
        // Log para monitoramento (em produção, enviaria para serviço de logging)
        this.logError(error, type);
    }

    showError(error) {
        const errorBoundary = document.getElementById('error-boundary');
        const errorStack = document.getElementById('error-stack');
        
        if (errorStack && error) {
            errorStack.textContent = error.stack || error.message || error.toString();
        }
        
        errorBoundary.style.display = 'flex';
        
        // Esconder loading se estiver ativo
        if (window.loadingManager) {
            window.loadingManager.hideAll();
        }
    }

    hideError() {
        document.getElementById('error-boundary').style.display = 'none';
    }

    reload() {
        window.location.reload();
    }

    goHome() {
        window.location.href = '/';
    }

    logError(error, type) {
        // Em produção, enviaria para serviço de monitoramento
        const errorLog = {
            timestamp: new Date().toISOString(),
            type: type,
            message: error.message || error.toString(),
            stack: error.stack,
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        console.log('Error logged:', errorLog);
    }

    // Método para capturar erros de API
    handleApiError(error, context = 'API Call') {
        if (error.message.includes('Failed to fetch') || 
            error.message.includes('Network Error') ||
            error.message.includes('500')) {
            this.handleError(error, context);
            return true;
        }
        return false;
    }
}

// Instância global
const errorBoundary = new ErrorBoundary();
window.errorBoundary = errorBoundary;