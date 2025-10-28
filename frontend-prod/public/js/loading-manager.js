/**
 * Gerenciador Global de Loading States - Nossa Grana
 */

class LoadingManager {
    constructor() {
        this.activeLoaders = new Set();
        this.createGlobalLoader();
    }

    createGlobalLoader() {
        const loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.innerHTML = `
            <div class="loader-backdrop">
                <div class="loader-content">
                    <div class="loader-spinner"></div>
                    <div class="loader-text">Carregando...</div>
                </div>
            </div>
        `;
        
        const styles = `
            #global-loader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 9999;
                display: none;
            }
            .loader-backdrop {
                width: 100%;
                height: 100%;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .loader-content {
                text-align: center;
                padding: 2rem;
                background: var(--bg-primary);
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            .loader-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid var(--border-color);
                border-top: 3px solid var(--primary-color);
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem auto;
            }
            .loader-text {
                color: var(--text-primary);
                font-weight: 500;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
        document.body.appendChild(loader);
    }

    show(id = 'default') {
        this.activeLoaders.add(id);
        document.getElementById('global-loader').style.display = 'flex';
    }

    hide(id = 'default') {
        this.activeLoaders.delete(id);
        if (this.activeLoaders.size === 0) {
            document.getElementById('global-loader').style.display = 'none';
        }
    }

    hideAll() {
        this.activeLoaders.clear();
        document.getElementById('global-loader').style.display = 'none';
    }
}

// Instância global
const loadingManager = new LoadingManager();
window.loadingManager = loadingManager;