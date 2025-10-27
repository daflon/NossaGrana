// Sistema de Notificações - Nossa Grana

class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.isDropdownOpen = false;
        this.refreshInterval = null;
        
        this.init();
    }

    // Inicializar sistema
    init() {
        this.createNotificationElements();
        this.bindEvents();
        this.startAutoRefresh();
        this.loadNotifications();
    }

    // Criar elementos HTML do sistema de notificações
    createNotificationElements() {
        // Verificar se já existe
        if (document.getElementById('notification-system')) {
            return;
        }

        // Criar container do sistema de notificações
        const notificationHTML = `
            <div id="notification-system" class="notification-system">
                <button id="notification-bell" class="notification-bell" title="Notificações">
                    <span class="bell-icon">🔔</span>
                    <span id="notification-badge" class="notification-badge" style="display: none;">0</span>
                </button>
                
                <div id="notification-dropdown" class="notification-dropdown" style="display: none;">
                    <div class="notification-header">
                        <h4>Notificações</h4>
                        <button id="mark-all-read" class="btn-text">Marcar todas como lidas</button>
                    </div>
                    
                    <div id="notification-list" class="notification-list">
                        <div class="notification-loading">
                            <div class="spinner-small"></div>
                            <span>Carregando...</span>
                        </div>
                    </div>
                    
                    <div class="notification-footer">
                        <button id="view-all-notifications" class="btn btn-primary btn-sm">
                            Ver Todos os Alertas
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Inserir no header actions (ao lado do toggle de tema)
        const headerActions = document.querySelector('.header-actions');
        if (headerActions) {
            // Inserir antes do toggle de tema
            const themeToggle = headerActions.querySelector('.theme-toggle');
            if (themeToggle) {
                themeToggle.insertAdjacentHTML('beforebegin', notificationHTML);
            } else {
                headerActions.insertAdjacentHTML('beforeend', notificationHTML);
            }
        }
    }

    // Vincular eventos
    bindEvents() {
        const bell = document.getElementById('notification-bell');
        const dropdown = document.getElementById('notification-dropdown');
        const markAllRead = document.getElementById('mark-all-read');
        const viewAll = document.getElementById('view-all-notifications');

        if (bell) {
            bell.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }

        if (markAllRead) {
            markAllRead.addEventListener('click', () => {
                this.markAllAsRead();
            });
        }

        if (viewAll) {
            viewAll.addEventListener('click', () => {
                window.location.href = '/alerts';
            });
        }

        // Fechar dropdown ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#notification-system')) {
                this.closeDropdown();
            }
        });

        // Fechar dropdown com ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isDropdownOpen) {
                this.closeDropdown();
            }
        });
    }

    // Alternar dropdown
    toggleDropdown() {
        if (this.isDropdownOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }

    // Abrir dropdown
    openDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
            dropdown.style.display = 'block';
            this.isDropdownOpen = true;
            
            // Marcar notificações como visualizadas
            this.markAsViewed();
        }
    }

    // Fechar dropdown
    closeDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (dropdown) {
            dropdown.style.display = 'none';
            this.isDropdownOpen = false;
        }
    }

    // Carregar notificações da API
    async loadNotifications() {
        try {
            // Buscar alertas ativos (últimos 10)
            const response = await api.getBudgetAlerts({ 
                is_active: true, 
                limit: 10,
                ordering: '-created_at'
            });
            
            const alerts = response.results || response;
            this.notifications = alerts;
            this.updateNotificationDisplay();
            
        } catch (error) {
            console.error('Erro ao carregar notificações:', error);
            this.showErrorInDropdown();
        }
    }

    // Atualizar exibição das notificações
    updateNotificationDisplay() {
        this.updateBadge();
        this.updateDropdownContent();
    }

    // Atualizar badge de contagem
    updateBadge() {
        const badge = document.getElementById('notification-badge');
        const bell = document.getElementById('notification-bell');
        
        if (!badge || !bell) return;

        // Contar notificações não lidas (críticas e altas)
        const unreadCount = this.notifications.filter(notification => 
            ['critical', 'high'].includes(notification.alert_level)
        ).length;

        this.unreadCount = unreadCount;

        if (unreadCount > 0) {
            badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
            badge.style.display = 'block';
            bell.classList.add('has-notifications');
        } else {
            badge.style.display = 'none';
            bell.classList.remove('has-notifications');
        }
    }

    // Atualizar conteúdo do dropdown
    updateDropdownContent() {
        const list = document.getElementById('notification-list');
        if (!list) return;

        if (this.notifications.length === 0) {
            list.innerHTML = `
                <div class="notification-empty">
                    <div class="empty-icon">✅</div>
                    <p>Nenhuma notificação</p>
                    <span>Suas finanças estão sob controle!</span>
                </div>
            `;
            return;
        }

        let html = '';
        
        // Mostrar apenas as 7 mais recentes no dropdown
        const recentNotifications = this.notifications.slice(0, 7);
        
        recentNotifications.forEach(notification => {
            const config = this.getNotificationConfig(notification);
            const timeAgo = this.getTimeAgo(notification.created_at);
            
            html += `
                <div class="notification-item ${config.priority}" data-id="${notification.id}">
                    <div class="notification-icon">${config.icon}</div>
                    <div class="notification-content">
                        <div class="notification-title">${notification.budget_category}</div>
                        <div class="notification-message">${notification.message}</div>
                        <div class="notification-time">${timeAgo}</div>
                    </div>
                    <div class="notification-actions">
                        <button class="btn-icon-small" onclick="notificationSystem.resolveNotification(${notification.id})" title="Resolver">
                            ✓
                        </button>
                    </div>
                </div>
            `;
        });

        list.innerHTML = html;
    }

    // Configuração visual por tipo de notificação
    getNotificationConfig(notification) {
        const configs = {
            critical: { 
                icon: '🚨', 
                priority: 'critical',
                color: '#ef4444'
            },
            high: { 
                icon: '⚠️', 
                priority: 'high',
                color: '#f59e0b'
            },
            medium: { 
                icon: '⚠️', 
                priority: 'medium',
                color: '#f59e0b'
            },
            low: { 
                icon: 'ℹ️', 
                priority: 'low',
                color: '#06b6d4'
            }
        };
        
        return configs[notification.alert_level] || configs.low;
    }

    // Calcular tempo relativo
    getTimeAgo(dateString) {
        const now = new Date();
        const date = new Date(dateString);
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) {
            return 'Agora mesmo';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes}m atrás`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours}h atrás`;
        } else {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days}d atrás`;
        }
    }

    // Resolver notificação individual
    async resolveNotification(notificationId) {
        try {
            await api.resolveAlert(notificationId);
            
            // Remover da lista local
            this.notifications = this.notifications.filter(n => n.id !== notificationId);
            this.updateNotificationDisplay();
            
            // Mostrar feedback
            this.showToast('Alerta resolvido!', 'success');
            
        } catch (error) {
            console.error('Erro ao resolver notificação:', error);
            this.showToast('Erro ao resolver alerta', 'error');
        }
    }

    // Marcar todas como lidas
    async markAllAsRead() {
        try {
            // Resolver todos os alertas críticos e altos
            const criticalAndHigh = this.notifications.filter(n => 
                ['critical', 'high'].includes(n.alert_level)
            );
            
            for (const notification of criticalAndHigh) {
                await api.resolveAlert(notification.id);
            }
            
            // Recarregar notificações
            await this.loadNotifications();
            
            this.showToast('Todas as notificações foram marcadas como lidas!', 'success');
            
        } catch (error) {
            console.error('Erro ao marcar todas como lidas:', error);
            this.showToast('Erro ao marcar notificações como lidas', 'error');
        }
    }

    // Marcar como visualizadas (não resolve, apenas remove do badge)
    markAsViewed() {
        // Esta função pode ser expandida para marcar como "visualizada" sem resolver
        // Por enquanto, mantemos o comportamento atual
    }

    // Mostrar erro no dropdown
    showErrorInDropdown() {
        const list = document.getElementById('notification-list');
        if (list) {
            list.innerHTML = `
                <div class="notification-error">
                    <div class="error-icon">⚠️</div>
                    <p>Erro ao carregar notificações</p>
                    <button class="btn btn-sm btn-secondary" onclick="notificationSystem.loadNotifications()">
                        Tentar Novamente
                    </button>
                </div>
            `;
        }
    }

    // Iniciar atualização automática
    startAutoRefresh() {
        // Atualizar a cada 2 minutos
        this.refreshInterval = setInterval(() => {
            this.loadNotifications();
        }, 120000);
    }

    // Parar atualização automática
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // Mostrar toast notification
    showToast(message, type = 'info') {
        // Usar o sistema de mensagens existente se disponível
        if (typeof showMessage === 'function') {
            showMessage(message, type);
        } else {
            // Fallback simples
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    // Destruir sistema (cleanup)
    destroy() {
        this.stopAutoRefresh();
        
        const system = document.getElementById('notification-system');
        if (system) {
            system.remove();
        }
    }
}

// Instância global do sistema de notificações
let notificationSystem = null;

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que outros scripts carregaram
    setTimeout(() => {
        if (!notificationSystem) {
            notificationSystem = new NotificationSystem();
        }
    }, 1000);
});

// Reinicializar se necessário (para páginas que fazem reload dinâmico)
function initNotificationSystem() {
    if (!notificationSystem) {
        notificationSystem = new NotificationSystem();
    }
}

// Exportar para uso global
window.notificationSystem = notificationSystem;
window.initNotificationSystem = initNotificationSystem;