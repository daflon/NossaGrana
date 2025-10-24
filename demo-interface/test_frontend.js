/**
 * Testes de Interface - Nossa Grana
 * Testes automatizados para validar funcionalidades do frontend
 */

class FrontendTestSuite {
    constructor() {
        this.testResults = [];
        this.passedTests = 0;
        this.failedTests = 0;
    }

    // Utilitário para executar testes
    async runTest(testName, testFunction) {
        console.log(`🧪 Executando: ${testName}`);
        try {
            await testFunction();
            this.testResults.push({ name: testName, status: 'PASS' });
            this.passedTests++;
            console.log(`✅ ${testName} - PASSOU`);
        } catch (error) {
            this.testResults.push({ name: testName, status: 'FAIL', error: error.message });
            this.failedTests++;
            console.error(`❌ ${testName} - FALHOU: ${error.message}`);
        }
    }

    // Utilitário para aguardar elemento
    waitForElement(selector, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
                return;
            }

            const observer = new MutationObserver(() => {
                const element = document.querySelector(selector);
                if (element) {
                    observer.disconnect();
                    resolve(element);
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });

            setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Elemento ${selector} não encontrado em ${timeout}ms`));
            }, timeout);
        });
    }

    // Simular clique
    simulateClick(element) {
        const event = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: true
        });
        element.dispatchEvent(event);
    }

    // Simular preenchimento de campo
    simulateInput(element, value) {
        element.value = value;
        const event = new Event('input', {
            bubbles: true,
            cancelable: true
        });
        element.dispatchEvent(event);
    }

    // Teste 1: Verificar carregamento da página
    async testPageLoad() {
        if (!document.querySelector('.sidebar')) {
            throw new Error('Sidebar não encontrada');
        }
        if (!document.querySelector('.main-content')) {
            throw new Error('Conteúdo principal não encontrado');
        }
        if (!document.querySelector('.page-title')) {
            throw new Error('Título da página não encontrado');
        }
    }

    // Teste 2: Verificar navegação
    async testNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        if (navLinks.length < 5) {
            throw new Error('Links de navegação insuficientes');
        }

        // Verificar se todos os links têm href
        navLinks.forEach((link, index) => {
            if (!link.getAttribute('href')) {
                throw new Error(`Link de navegação ${index} sem href`);
            }
        });
    }

    // Teste 3: Verificar tema
    async testThemeToggle() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (!themeToggle) {
            throw new Error('Botão de tema não encontrado');
        }

        // Simular clique no tema
        const initialTheme = document.documentElement.getAttribute('data-theme');
        this.simulateClick(themeToggle);
        
        // Aguardar mudança (simular)
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Verificar se função existe
        if (typeof toggleTheme !== 'function') {
            throw new Error('Função toggleTheme não encontrada');
        }
    }

    // Teste 4: Verificar formulários (se existirem)
    async testForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach((form, index) => {
            const requiredFields = form.querySelectorAll('[required]');
            if (requiredFields.length === 0) {
                console.warn(`Formulário ${index} sem campos obrigatórios`);
            }

            // Verificar se tem botão de submit
            const submitBtn = form.querySelector('[type="submit"], .btn-primary');
            if (!submitBtn) {
                throw new Error(`Formulário ${index} sem botão de submit`);
            }
        });
    }

    // Teste 5: Verificar modais (se existirem)
    async testModals() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach((modal, index) => {
            // Verificar estrutura básica do modal
            if (!modal.querySelector('.modal-content')) {
                throw new Error(`Modal ${index} sem conteúdo`);
            }
            if (!modal.querySelector('.modal-header')) {
                throw new Error(`Modal ${index} sem cabeçalho`);
            }
            if (!modal.querySelector('.modal-close')) {
                throw new Error(`Modal ${index} sem botão de fechar`);
            }
        });
    }

    // Teste 6: Verificar API client
    async testApiClient() {
        if (typeof api === 'undefined') {
            throw new Error('Cliente API não encontrado');
        }

        // Verificar métodos essenciais
        const requiredMethods = ['request', 'formatCurrency', 'formatDate'];
        requiredMethods.forEach(method => {
            if (typeof api[method] !== 'function') {
                throw new Error(`Método api.${method} não encontrado`);
            }
        });
    }

    // Teste 7: Verificar formatação de moeda
    async testCurrencyFormatting() {
        if (typeof formatCurrency !== 'function') {
            throw new Error('Função formatCurrency não encontrada');
        }

        const testValue = 1234.56;
        const formatted = formatCurrency(testValue);
        
        if (!formatted.includes('R$')) {
            throw new Error('Formatação de moeda não inclui R$');
        }
        if (!formatted.includes('1.234,56')) {
            throw new Error('Formatação de moeda incorreta');
        }
    }

    // Teste 8: Verificar responsividade básica
    async testResponsiveness() {
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (!sidebar || !mainContent) {
            throw new Error('Elementos principais não encontrados');
        }

        // Verificar se tem classes CSS responsivas
        const hasResponsiveClasses = document.querySelector('[class*="mobile"], [class*="tablet"], [class*="desktop"]');
        if (!hasResponsiveClasses) {
            console.warn('Nenhuma classe responsiva detectada');
        }
    }

    // Teste 9: Verificar acessibilidade básica
    async testAccessibility() {
        // Verificar se botões têm texto ou aria-label
        const buttons = document.querySelectorAll('button');
        buttons.forEach((button, index) => {
            const hasText = button.textContent.trim().length > 0;
            const hasAriaLabel = button.getAttribute('aria-label');
            const hasTitle = button.getAttribute('title');
            
            if (!hasText && !hasAriaLabel && !hasTitle) {
                throw new Error(`Botão ${index} sem texto ou aria-label`);
            }
        });

        // Verificar se inputs têm labels
        const inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="number"]');
        inputs.forEach((input, index) => {
            const id = input.getAttribute('id');
            if (id) {
                const label = document.querySelector(`label[for="${id}"]`);
                if (!label) {
                    console.warn(`Input ${index} sem label associado`);
                }
            }
        });
    }

    // Teste 10: Verificar performance básica
    async testPerformance() {
        // Verificar se não há muitos elementos DOM
        const elementCount = document.querySelectorAll('*').length;
        if (elementCount > 5000) {
            console.warn(`Muitos elementos DOM: ${elementCount}`);
        }

        // Verificar se não há muitas imagens sem lazy loading
        const images = document.querySelectorAll('img');
        let imagesWithoutLazy = 0;
        images.forEach(img => {
            if (!img.getAttribute('loading')) {
                imagesWithoutLazy++;
            }
        });
        
        if (imagesWithoutLazy > 10) {
            console.warn(`${imagesWithoutLazy} imagens sem lazy loading`);
        }
    }

    // Executar todos os testes
    async runAllTests() {
        console.log('🚀 INICIANDO TESTES DE INTERFACE - NOSSA GRANA');
        console.log('=' * 60);

        const tests = [
            ['Carregamento da Página', () => this.testPageLoad()],
            ['Navegação', () => this.testNavigation()],
            ['Toggle de Tema', () => this.testThemeToggle()],
            ['Formulários', () => this.testForms()],
            ['Modais', () => this.testModals()],
            ['Cliente API', () => this.testApiClient()],
            ['Formatação de Moeda', () => this.testCurrencyFormatting()],
            ['Responsividade', () => this.testResponsiveness()],
            ['Acessibilidade', () => this.testAccessibility()],
            ['Performance', () => this.testPerformance()]
        ];

        for (const [testName, testFunction] of tests) {
            await this.runTest(testName, testFunction);
        }

        this.showResults();
    }

    // Mostrar resultados
    showResults() {
        console.log('\n' + '=' * 60);
        console.log('📊 RESULTADOS DOS TESTES DE INTERFACE');
        console.log('=' * 60);
        
        console.log(`✅ Testes Aprovados: ${this.passedTests}`);
        console.log(`❌ Testes Falharam: ${this.failedTests}`);
        console.log(`📈 Taxa de Sucesso: ${((this.passedTests / (this.passedTests + this.failedTests)) * 100).toFixed(1)}%`);

        if (this.failedTests > 0) {
            console.log('\n❌ TESTES QUE FALHARAM:');
            this.testResults
                .filter(result => result.status === 'FAIL')
                .forEach(result => {
                    console.log(`   • ${result.name}: ${result.error}`);
                });
        }

        console.log('\n' + '=' * 60);
        
        if (this.failedTests === 0) {
            console.log('🎉 TODOS OS TESTES DE INTERFACE PASSARAM!');
            console.log('✅ Interface totalmente funcional');
        } else {
            console.log('⚠️ Alguns testes falharam. Verifique os problemas acima.');
        }
        
        console.log('=' * 60);
    }
}

// Função para executar testes quando a página carregar
function runFrontendTests() {
    const testSuite = new FrontendTestSuite();
    testSuite.runAllTests();
}

// Executar automaticamente se estiver em modo de teste
if (window.location.search.includes('test=true')) {
    document.addEventListener('DOMContentLoaded', runFrontendTests);
}

// Exportar para uso manual
window.frontendTests = {
    run: runFrontendTests,
    FrontendTestSuite
};

console.log('🧪 Testes de interface carregados. Execute window.frontendTests.run() para testar.');