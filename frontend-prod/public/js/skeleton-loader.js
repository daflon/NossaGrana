/**
 * Skeleton Loader Components - Nossa Grana
 */

class SkeletonLoader {
    static createCardSkeleton() {
        return `
            <div class="skeleton-card">
                <div class="skeleton-header">
                    <div class="skeleton-icon"></div>
                    <div class="skeleton-info">
                        <div class="skeleton-line skeleton-title"></div>
                        <div class="skeleton-line skeleton-subtitle"></div>
                    </div>
                    <div class="skeleton-actions">
                        <div class="skeleton-btn"></div>
                        <div class="skeleton-btn"></div>
                        <div class="skeleton-btn"></div>
                    </div>
                </div>
                <div class="skeleton-content">
                    <div class="skeleton-line skeleton-balance"></div>
                    <div class="skeleton-line skeleton-text"></div>
                    <div class="skeleton-progress"></div>
                </div>
                <div class="skeleton-footer">
                    <div class="skeleton-line skeleton-status"></div>
                    <div class="skeleton-btn skeleton-btn-large"></div>
                </div>
            </div>
        `;
    }

    static createAccountSkeleton() {
        return `
            <div class="skeleton-account">
                <div class="skeleton-header">
                    <div class="skeleton-icon"></div>
                    <div class="skeleton-info">
                        <div class="skeleton-line skeleton-title"></div>
                        <div class="skeleton-line skeleton-subtitle"></div>
                    </div>
                </div>
                <div class="skeleton-balance-section">
                    <div class="skeleton-line skeleton-balance"></div>
                </div>
                <div class="skeleton-actions-section">
                    <div class="skeleton-btn"></div>
                    <div class="skeleton-btn"></div>
                </div>
            </div>
        `;
    }

    static createReportSkeleton() {
        return `
            <div class="skeleton-report">
                <div class="skeleton-chart"></div>
                <div class="skeleton-legend">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                </div>
            </div>
        `;
    }

    static createCreditCardSkeleton() {
        return `
            <div class="credit-card-item skeleton-card">
                <div class="card-header">
                    <div class="skeleton-icon"></div>
                    <div class="card-info">
                        <div class="skeleton-text skeleton-title"></div>
                        <div class="skeleton-text skeleton-subtitle"></div>
                    </div>
                    <div class="card-actions">
                        <div class="skeleton-button"></div>
                        <div class="skeleton-button"></div>
                        <div class="skeleton-button"></div>
                    </div>
                </div>
                
                <div class="card-limits">
                    <div class="limit-info">
                        <div class="skeleton-text skeleton-small"></div>
                        <div class="skeleton-text skeleton-value"></div>
                    </div>
                    <div class="limit-info">
                        <div class="skeleton-text skeleton-small"></div>
                        <div class="skeleton-text skeleton-value"></div>
                    </div>
                </div>
                
                <div class="usage-section">
                    <div class="usage-header">
                        <div class="skeleton-text skeleton-small"></div>
                        <div class="skeleton-text skeleton-percentage"></div>
                    </div>
                    <div class="skeleton-progress-bar"></div>
                </div>
                
                <div class="card-cycle">
                    <div class="cycle-row">
                        <div class="skeleton-text skeleton-cycle"></div>
                    </div>
                    <div class="cycle-row">
                        <div class="skeleton-text skeleton-cycle"></div>
                    </div>
                    <div class="cycle-row">
                        <div class="skeleton-text skeleton-cycle"></div>
                    </div>
                </div>
                
                <div class="card-footer">
                    <div class="skeleton-text skeleton-status"></div>
                    <div class="skeleton-button skeleton-btn-detail"></div>
                    <div class="skeleton-button skeleton-btn-pay"></div>
                </div>
            </div>
        `;
    }

    static createSummarySkeleton() {
        return `
            <div class="skeleton-text skeleton-summary-value"></div>
        `;
    }

    static injectStyles() {
        const styles = `
            .skeleton-card, .skeleton-account, .skeleton-report {
                background: var(--bg-secondary);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                border: 1px solid var(--border-color);
            }

            .skeleton-header {
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .skeleton-icon {
                width: 48px;
                height: 48px;
                border-radius: 8px;
                background: var(--skeleton-color);
                animation: skeleton-pulse 1.5s ease-in-out infinite;
            }

            .skeleton-info {
                flex: 1;
            }

            .skeleton-actions {
                display: flex;
                gap: 0.5rem;
            }

            .skeleton-line {
                height: 16px;
                background: var(--skeleton-color);
                border-radius: 4px;
                animation: skeleton-pulse 1.5s ease-in-out infinite;
                margin-bottom: 0.5rem;
            }

            .skeleton-title {
                width: 60%;
                height: 20px;
            }

            .skeleton-subtitle {
                width: 40%;
            }

            .skeleton-balance {
                width: 80%;
                height: 24px;
                margin: 1rem 0;
            }

            .skeleton-text {
                width: 50%;
            }

            .skeleton-status {
                width: 30%;
            }

            .skeleton-btn {
                width: 32px;
                height: 32px;
                border-radius: 6px;
                background: var(--skeleton-color);
                animation: skeleton-pulse 1.5s ease-in-out infinite;
            }

            .skeleton-btn-large {
                width: 120px;
                height: 36px;
            }

            .skeleton-progress {
                width: 100%;
                height: 8px;
                border-radius: 4px;
                background: var(--skeleton-color);
                animation: skeleton-pulse 1.5s ease-in-out infinite;
                margin: 1rem 0;
            }

            .skeleton-content {
                margin: 1rem 0;
            }

            .skeleton-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 1rem;
            }

            .skeleton-balance-section {
                text-align: center;
                margin: 1.5rem 0;
            }

            .skeleton-actions-section {
                display: flex;
                gap: 0.5rem;
                justify-content: center;
            }

            .skeleton-chart {
                width: 100%;
                height: 200px;
                border-radius: 8px;
                background: var(--skeleton-color);
                animation: skeleton-pulse 1.5s ease-in-out infinite;
                margin-bottom: 1rem;
            }

            .skeleton-legend {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }

            /* Credit Card Skeleton Styles */
            .skeleton-text,
            .skeleton-icon,
            .skeleton-button,
            .skeleton-progress-bar {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: skeleton-loading 1.5s infinite;
                border-radius: 4px;
            }

            @keyframes skeleton-loading {
                0% { background-position: 200% 0; }
                100% { background-position: -200% 0; }
            }

            .skeleton-title {
                height: 20px;
                width: 70%;
                margin-bottom: 8px;
            }

            .skeleton-subtitle {
                height: 16px;
                width: 50%;
            }

            .skeleton-button {
                width: 32px;
                height: 32px;
                border-radius: 6px;
            }

            .skeleton-small {
                height: 14px;
                width: 60%;
                margin-bottom: 4px;
            }

            .skeleton-value {
                height: 18px;
                width: 80%;
            }

            .skeleton-percentage {
                height: 18px;
                width: 40px;
            }

            .skeleton-progress-bar {
                height: 12px;
                width: 100%;
                border-radius: 6px;
            }

            .skeleton-cycle {
                height: 16px;
                width: 100%;
                margin-bottom: 8px;
            }

            .skeleton-status {
                height: 16px;
                width: 60px;
            }

            .skeleton-btn-detail {
                height: 32px;
                width: 80px;
                border-radius: 4px;
            }

            .skeleton-btn-pay {
                height: 32px;
                width: 100px;
                border-radius: 4px;
            }

            .skeleton-summary-value {
                height: 24px;
                width: 100%;
                border-radius: 4px;
            }

            /* Dark Theme Credit Card Skeleton */
            [data-theme="dark"] .skeleton-text,
            [data-theme="dark"] .skeleton-icon,
            [data-theme="dark"] .skeleton-button,
            [data-theme="dark"] .skeleton-progress-bar {
                background: linear-gradient(90deg, #4a5568 25%, #2d3748 50%, #4a5568 75%);
                background-size: 200% 100%;
            }

            :root {
                --skeleton-color: #e2e8f0;
            }

            [data-theme="dark"] {
                --skeleton-color: #374151;
            }

            @keyframes skeleton-pulse {
                0%, 100% {
                    opacity: 1;
                }
                50% {
                    opacity: 0.6;
                }
            }
        `;

        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }

    static showSkeletons(containerId, type, count = 3) {
        const container = document.getElementById(containerId);
        if (!container) return;

        let skeletonHtml = '';
        for (let i = 0; i < count; i++) {
            switch (type) {
                case 'card':
                    skeletonHtml += this.createCardSkeleton();
                    break;
                case 'account':
                    skeletonHtml += this.createAccountSkeleton();
                    break;
                case 'report':
                    skeletonHtml += this.createReportSkeleton();
                    break;
                case 'credit-card':
                    skeletonHtml += this.createCreditCardSkeleton();
                    break;
                case 'summary':
                    skeletonHtml += this.createSummarySkeleton();
                    break;
            }
        }

        container.innerHTML = skeletonHtml;
    }

    static hide(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }
}

// Injetar estilos automaticamente
document.addEventListener('DOMContentLoaded', () => {
    SkeletonLoader.injectStyles();
});

window.SkeletonLoader = SkeletonLoader;