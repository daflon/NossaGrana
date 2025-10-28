// Mobile Optimization - 100% mobile-friendly
class MobileOptimizer {
    constructor() {
        this.isMobile = this.detectMobile();
        this.touchStartX = 0;
        this.touchStartY = 0;
        this.init();
    }

    init() {
        this.setupViewport();
        this.optimizeTouch();
        this.setupGestures();
        this.optimizeLayout();
        this.setupMobileNavigation();
    }

    detectMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               window.innerWidth <= 768;
    }

    setupViewport() {
        // Viewport otimizado
        let viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            viewport = document.createElement('meta');
            viewport.name = 'viewport';
            document.head.appendChild(viewport);
        }
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';

        // Prevenir zoom em inputs
        if (this.isMobile) {
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('focus', () => {
                    viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
                });
                input.addEventListener('blur', () => {
                    viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes';
                });
            });
        }
    }

    optimizeTouch() {
        // Aumentar área de toque
        const style = document.createElement('style');
        style.textContent = `
            @media (max-width: 768px) {
                .btn, .nav-link, button, a {
                    min-height: 44px !important;
                    min-width: 44px !important;
                    padding: 12px 16px !important;
                }
                
                .form-input, .form-select {
                    min-height: 44px !important;
                    font-size: 16px !important; /* Previne zoom no iOS */
                }
                
                .metric-card, .card {
                    padding: 16px !important;
                }
                
                .table td, .table th {
                    padding: 12px 8px !important;
                }
            }
        `;
        document.head.appendChild(style);

        // Touch feedback
        document.addEventListener('touchstart', (e) => {
            if (e.target.matches('.btn, button, .nav-link, a')) {
                e.target.style.opacity = '0.7';
            }
        });

        document.addEventListener('touchend', (e) => {
            if (e.target.matches('.btn, button, .nav-link, a')) {
                setTimeout(() => {
                    e.target.style.opacity = '';
                }, 150);
            }
        });
    }

    setupGestures() {
        // Swipe para navegação
        document.addEventListener('touchstart', (e) => {
            this.touchStartX = e.touches[0].clientX;
            this.touchStartY = e.touches[0].clientY;
        });

        document.addEventListener('touchend', (e) => {
            if (!this.touchStartX || !this.touchStartY) return;

            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;

            const diffX = this.touchStartX - touchEndX;
            const diffY = this.touchStartY - touchEndY;

            // Swipe horizontal (sidebar)
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    this.closeMobileSidebar();
                } else {
                    this.openMobileSidebar();
                }
            }

            this.touchStartX = 0;
            this.touchStartY = 0;
        });

        // Pull to refresh
        let startY = 0;
        let pullDistance = 0;
        const refreshThreshold = 80;

        document.addEventListener('touchstart', (e) => {
            if (window.scrollY === 0) {
                startY = e.touches[0].clientY;
            }
        });

        document.addEventListener('touchmove', (e) => {
            if (startY && window.scrollY === 0) {
                pullDistance = e.touches[0].clientY - startY;
                if (pullDistance > 0) {
                    e.preventDefault();
                    this.showPullToRefresh(pullDistance);
                }
            }
        });

        document.addEventListener('touchend', () => {
            if (pullDistance > refreshThreshold) {
                this.refreshPage();
            }
            this.hidePullToRefresh();
            startY = 0;
            pullDistance = 0;
        });
    }

    optimizeLayout() {
        if (!this.isMobile) return;

        // Layout mobile-first
        const mobileStyles = document.createElement('style');
        mobileStyles.textContent = `
            @media (max-width: 768px) {
                .sidebar {
                    position: fixed;
                    left: -280px;
                    top: 0;
                    height: 100vh;
                    z-index: 1000;
                    transition: left 0.3s ease;
                    box-shadow: 2px 0 10px rgba(0,0,0,0.1);
                }
                
                .sidebar.open {
                    left: 0;
                }
                
                .main-content {
                    margin-left: 0;
                    padding: 12px;
                }
                
                .page-header {
                    flex-direction: column;
                    align-items: stretch;
                    gap: 12px;
                    padding: 12px 0;
                }
                
                .page-title {
                    font-size: 1.5rem;
                }
                
                .metrics-grid {
                    grid-template-columns: repeat(2, 1fr);
                    gap: 12px;
                }
                
                .cards-grid {
                    grid-template-columns: 1fr;
                    gap: 16px;
                }
                
                .metric-card {
                    padding: 12px;
                }
                
                .metric-value {
                    font-size: 1.25rem;
                }
                
                .card-header {
                    flex-direction: column;
                    align-items: stretch;
                    gap: 8px;
                }
                
                .card-header .btn {
                    align-self: flex-end;
                }
                
                .table-container {
                    overflow-x: auto;
                    -webkit-overflow-scrolling: touch;
                }
                
                .modal-content {
                    width: 95vw;
                    max-width: none;
                    margin: 20px auto;
                    max-height: calc(100vh - 40px);
                }
                
                .form-group {
                    margin-bottom: 16px;
                }
                
                .btn {
                    width: 100%;
                    justify-content: center;
                }
                
                .btn + .btn {
                    margin-top: 8px;
                }
                
                .flex.gap-2 {
                    flex-direction: column;
                    gap: 8px;
                }
                
                .theme-toggle {
                    align-self: flex-end;
                }
            }
            
            @media (max-width: 480px) {
                .metrics-grid {
                    grid-template-columns: 1fr;
                }
                
                .page-title {
                    font-size: 1.25rem;
                }
                
                .metric-value {
                    font-size: 1.1rem;
                }
            }
        `;
        document.head.appendChild(mobileStyles);
    }

    setupMobileNavigation() {
        // Botão de menu mobile
        const mobileMenuBtn = document.createElement('button');
        mobileMenuBtn.className = 'mobile-menu-btn';
        mobileMenuBtn.innerHTML = '☰';
        mobileMenuBtn.style.cssText = `
            position: fixed;
            top: 20px;
            left: 20px;
            z-index: 1001;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            width: 44px;
            height: 44px;
            font-size: 18px;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            display: none;
        `;

        // Overlay para sidebar
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0,0,0,0.5);
            z-index: 999;
            display: none;
        `;

        document.body.appendChild(mobileMenuBtn);
        document.body.appendChild(overlay);

        // Mostrar botão mobile
        if (this.isMobile) {
            mobileMenuBtn.style.display = 'block';
        }

        // Event listeners
        mobileMenuBtn.addEventListener('click', () => this.toggleMobileSidebar());
        overlay.addEventListener('click', () => this.closeMobileSidebar());

        // Fechar sidebar ao clicar em link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                if (this.isMobile) {
                    this.closeMobileSidebar();
                }
            });
        });

        // Responsive menu button
        window.addEventListener('resize', () => {
            const isMobileNow = window.innerWidth <= 768;
            mobileMenuBtn.style.display = isMobileNow ? 'block' : 'none';
            
            if (!isMobileNow) {
                this.closeMobileSidebar();
            }
        });
    }

    toggleMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (sidebar.classList.contains('open')) {
            this.closeMobileSidebar();
        } else {
            this.openMobileSidebar();
        }
    }

    openMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        sidebar.classList.add('open');
        overlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    closeMobileSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        sidebar.classList.remove('open');
        overlay.style.display = 'none';
        document.body.style.overflow = '';
    }

    showPullToRefresh(distance) {
        let refreshIndicator = document.querySelector('.pull-refresh-indicator');
        if (!refreshIndicator) {
            refreshIndicator = document.createElement('div');
            refreshIndicator.className = 'pull-refresh-indicator';
            refreshIndicator.innerHTML = '↓ Puxe para atualizar';
            refreshIndicator.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: var(--primary-color);
                color: white;
                text-align: center;
                padding: 10px;
                transform: translateY(-100%);
                transition: transform 0.3s ease;
                z-index: 1000;
            `;
            document.body.appendChild(refreshIndicator);
        }

        const progress = Math.min(distance / 80, 1);
        refreshIndicator.style.transform = `translateY(${-100 + (progress * 100)}%)`;
        
        if (progress >= 1) {
            refreshIndicator.innerHTML = '↑ Solte para atualizar';
        } else {
            refreshIndicator.innerHTML = '↓ Puxe para atualizar';
        }
    }

    hidePullToRefresh() {
        const refreshIndicator = document.querySelector('.pull-refresh-indicator');
        if (refreshIndicator) {
            refreshIndicator.style.transform = 'translateY(-100%)';
            setTimeout(() => {
                refreshIndicator.remove();
            }, 300);
        }
    }

    refreshPage() {
        if (typeof refreshDashboard === 'function') {
            refreshDashboard();
        } else {
            window.location.reload();
        }
    }

    // Otimização de scroll
    optimizeScroll() {
        let ticking = false;
        
        function updateScrollPosition() {
            // Scroll otimizado para mobile
            ticking = false;
        }
        
        document.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateScrollPosition);
                ticking = true;
            }
        }, { passive: true });
    }

    // Feedback háptico (se disponível)
    hapticFeedback(type = 'light') {
        if (navigator.vibrate) {
            const patterns = {
                light: [10],
                medium: [20],
                heavy: [30]
            };
            navigator.vibrate(patterns[type] || patterns.light);
        }
    }

    // Orientação da tela
    handleOrientationChange() {
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                // Reajustar layout após mudança de orientação
                this.optimizeLayout();
            }, 100);
        });
    }
}

// Inicializar otimizador mobile
const mobileOptimizer = new MobileOptimizer();

// Export para uso global
window.mobileOptimizer = mobileOptimizer;