/**
 * Gerenciador Global de Modais - Nossa Grana
 * Suporte à tecla ESC e padronização de comportamento
 */

class ModalManager {
    constructor() {
        this.openModals = [];
        this.setupGlobalListeners();
    }

    setupGlobalListeners() {
        // Listener global para tecla ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.openModals.length > 0) {
                this.closeTopModal();
            }
        });

        // Listener para cliques fora do modal
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target.id);
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            this.openModals.push(modalId);
            
            // Focar no primeiro input do modal
            setTimeout(() => {
                const firstInput = modal.querySelector('input, select, textarea');
                if (firstInput) {
                    firstInput.focus();
                }
            }, 100);
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            this.openModals = this.openModals.filter(id => id !== modalId);
        }
    }

    closeTopModal() {
        if (this.openModals.length > 0) {
            const topModalId = this.openModals[this.openModals.length - 1];
            this.closeModal(topModalId);
        }
    }

    closeAllModals() {
        this.openModals.forEach(modalId => {
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'none';
            }
        });
        this.openModals = [];
    }
}

// Instância global do gerenciador de modais
const modalManager = new ModalManager();

// Funções globais para compatibilidade
window.openModal = (modalId) => modalManager.openModal(modalId);
window.closeModal = (modalId) => modalManager.closeModal(modalId);