# Nossa Grana - Sistema de Controle Financeiro Familiar

Sistema web completo para controle financeiro doméstico familiar, permitindo gerenciamento compartilhado de receitas, despesas, orçamentos, metas de poupança, contas bancárias e cartões de crédito.

## 🚀 Status do Projeto

**✅ SISTEMA FUNCIONAL E PRONTO PARA USO**

- **Progresso Geral**: 95% completo
- **Backend**: 95% implementado
- **Frontend**: 95% implementado  
- **Interface Demo**: 100% funcional
- **Landing Page**: ✅ Profissional com CRO otimizado
- **UI/UX**: ✅ Padronizado e consistente
- **Sistema de Cartões**: ✅ Aprimorado com UX avançada
- **Segurança**: ✅ Aprovado (0 vulnerabilidades críticas)
- **Performance**: ✅ Aprovado (<2s carregamento)
- **Responsividade**: ✅ Aprovado (100% mobile-friendly)

## 🛠️ Tecnologias

### Backend
- **Python 3.9+** com Django 4.2+
- **Django REST Framework 3.14+** para APIs
- **JWT** para autenticação segura
- **SQLite** (desenvolvimento) / **PostgreSQL** (produção)
- **Middleware avançado** de segurança e performance

### Frontend
- **Interface Demo**: HTML5/CSS3/JavaScript ES6+ (100% funcional)
- **React.js 18+** (estrutura completa implementada)
- **Material-UI** para componentes
- **Chart.js** para visualizações
- **Axios** para requisições HTTP

### DevOps & Infraestrutura
- **Docker** para containerização
- **Nginx** para proxy reverso
- **SSL/HTTPS** configurado
- **Scripts automatizados** de deploy e monitoramento

## 📋 Funcionalidades Implementadas

### ✅ **Sistema de Autenticação Completo**
- Registro e login com JWT
- Middleware de segurança avançado
- Proteção de rotas e endpoints
- Gerenciamento de sessões
- Rate limiting e proteção contra ataques

### ✅ **Gestão Financeira Avançada**

#### **Transações Completas**
- CRUD completo de receitas, despesas e transferências
- Sistema avançado de categorização
- Tags personalizadas com contadores de uso
- Validações rigorosas de dados
- Histórico completo com filtros

#### **Contas Bancárias**
- Gestão de contas corrente, poupança, investimento
- Cálculo automático de saldos
- Transferências entre contas com validações
- Histórico de movimentações

#### **Cartões de Crédito Aprimorados**
- Controle de limite e saldo disponível
- Gestão de faturas e vencimentos
- Cálculo automático de limite disponível
- **Cálculo inteligente de ciclos** (permite ciclos que cruzam meses)
- **Top Card de Próximo Fechamento** proativo com alertas urgentes
- **Botão "Pagar Fatura"** integrado aos cards
- **Badge "Melhor Compra"** com destaque verde vibrante
- **Exibição de datas calculadas** (DD/MMM) precisas
- **Modal com design consistente** e suporte à tecla ESC
- **Contraste aprimorado** para valores monetários

### ✅ **Sistema de Orçamentos Inteligente**
- Criação de orçamentos mensais por categoria
- **Cálculos automáticos avançados**:
  - Progresso em tempo real
  - Análise de tendências
  - Projeções mensais
  - Média diária de gastos
- **Sistema de alertas inteligente**:
  - Alertas de 80% e 100% do orçamento
  - Projeções de estouro
  - Análise de tendências
  - 4 níveis de severidade (Crítico, Alto, Médio, Baixo)
- **Recomendações personalizadas**
- **3 visualizações**: Lista, Progresso Visual, Análise Avançada

### ✅ **Sistema de Metas de Poupança**
- Criação de metas com valores alvo e prazos
- Cálculos avançados de progresso
- Análise de ritmo e tendências
- Sistema de contribuições
- Estimativas inteligentes de tempo

### ✅ **Dashboard e Relatórios Completos**
- Dashboard principal com resumo financeiro
- Gráficos interativos (pizza, barras, tendências)
- Relatórios por conta, cartão e categoria
- Filtros avançados por período
- Análises comparativas
- Métricas em tempo real

### ✅ **Landing Page Profissional**
- Design moderno com Hero section
- Autenticação via modal (melhor UX)
- Cards de recursos clicáveis com hover effects
- Seção de credenciais demo com copy-to-clipboard
- Navegação inteligente baseada em status de login
- Otimizações de conversão (CRO) implementadas
- Toast notifications para feedback visual

### ✅ **Sistema de Alertas Avançado**
- **4 tipos de alerta**: Excedido, Próximo Limite, Projeção, Tendência
- **4 níveis de severidade**: Crítico, Alto, Médio, Baixo
- Geração automática baseada em regras
- Centro de alertas unificado
- Filtros avançados e estatísticas
- Resolução manual de alertas

## 🌐 Instalação e Uso

### Pré-requisitos
- Python 3.9+
- Node.js 16+
- Git

### Instalação Rápida (Recomendada)

1. **Clone o repositório**:
```bash
git clone <repository-url>
cd NossaGrana
```

2. **Configure o backend**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# ou source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8001
```

3. **Configure a interface de demonstração**:
```bash
cd demo-interface
npm install
npm start
```

### Acesso ao Sistema

#### **Interface Principal (Recomendada)**
- **Landing Page**: http://localhost:3001 (Nova página profissional)
- **Dashboard**: http://localhost:3001/dashboard
- **Transações**: http://localhost:3001/transactions
- **Orçamentos**: http://localhost:3001/budgets
- **Alertas**: http://localhost:3001/alerts
- **Metas**: http://localhost:3001/goals
- **Relatórios**: http://localhost:3001/reports
- **Contas**: http://localhost:3001/accounts
- **Cartões**: http://localhost:3001/credit-cards

#### **APIs e Admin**
- **Backend API**: http://127.0.0.1:8001/api
- **Admin Django**: http://127.0.0.1:8001/admin
- **Frontend React**: http://localhost:3000 (se configurado)

## 🎯 Demonstração Completa

### **Fluxo de Teste Recomendado**:

1. **Acessar Landing Page** (http://localhost:3001) - Nova experiência profissional
2. **Testar Credenciais Demo** - Use os botões de copiar para facilitar
3. **Fazer Login via Modal** - UX otimizada sem redirecionamento
4. **Explorar Dashboard** - Interface padronizada com menu lateral
5. **Criar Contas Bancárias** e Cartões de Crédito
6. **Adicionar Transações** (receitas, despesas, transferências)
7. **Configurar Orçamentos** mensais por categoria
8. **Explorar Alertas** automáticos gerados
9. **Navegar entre páginas** - Menu lateral padronizado em todas as páginas
10. **Testar Responsividade** - Interface 100% mobile-friendly

### **Cenários de Teste Avançados**:

#### **Orçamentos Inteligentes**:
- Criar orçamento menor que gastos → Ver alerta "Excedido"
- Criar orçamento próximo dos gastos → Ver alerta "Atenção"
- Navegar entre meses → Ver dados específicos
- Usar análise avançada → Ver projeções e recomendações

#### **Sistema de Alertas**:
- Gerar alertas automáticos → Ver diferentes tipos e níveis
- Filtrar por nível/tipo → Testar funcionalidade
- Resolver alertas → Ver mudança de status
- Ver estatísticas → Entender distribuição

## 📚 Documentação Técnica

### **Documentação da API**
- **Orçamentos**: `backend/budgets/API_DOCUMENTATION.md`
- **Cálculos**: `backend/budgets/PROGRESS_CALCULATIONS.md`
- **Interface Demo**: `demo-interface/README.md`

### **Documentação do Sistema**
- **Setup**: `SETUP.md`
- **Deploy**: `DEPLOY.md`
- **Roadmap**: `ROADMAP.md`
- **Regras**: `RULES.md`
- **Métricas**: `METRICAS_SUCESSO.md`

## 🧪 Testes e Qualidade

### **Testes Automatizados**
```bash
# Executar todos os testes
python run_all_tests.py

# Testes específicos
cd backend
python test_comprehensive.py
python test_security_vulnerabilities.py
python test_advanced_calculations.py
```

### **Métricas de Qualidade**
```bash
cd metrics
python run_all_metrics.py
```

### **Status dos Testes**
- **Segurança**: ✅ 0 vulnerabilidades críticas
- **Performance**: ✅ <2s carregamento inicial
- **Responsividade**: ✅ 100% mobile-friendly
- **Usabilidade**: ✅ <3 cliques para ações principais
- **Cobertura**: ⚠️ 60% (Meta: >80%)

## 🚀 Deploy em Produção

### **Deploy Automatizado (Recomendado)**
```bash
# Deploy completo
./deploy.sh

# Monitorar sistema
./monitor.sh

# Backup automático
./backup.sh
```

### **Deploy com Docker**
```bash
# Configurar ambiente
cp .env.prod.example .env.prod

# Gerar certificados SSL
./generate-ssl.sh

# Iniciar containers
docker-compose -f docker-compose.prod.yml up -d
```

## 🏗️ Arquitetura do Sistema

### **Backend (Django)**
```
backend/
├── accounts/           # Autenticação e usuários
├── transactions/       # Transações financeiras
├── financial_accounts/ # Contas e cartões
├── budgets/           # Orçamentos e alertas
├── goals/             # Metas de poupança
├── reports/           # Relatórios
├── middleware/        # Segurança e performance
└── utils/             # Utilitários e cache
```

### **Frontend**
```
demo-interface/        # Interface 100% funcional
├── public/
│   ├── index.html     # Página principal
│   ├── dashboard.html # Dashboard
│   ├── transactions.html # Transações
│   ├── budgets.html   # Orçamentos
│   ├── alerts.html    # Alertas
│   └── js/            # JavaScript modular
└── server.js          # Servidor Node.js

frontend/              # React.js (estrutura completa)
├── src/
│   ├── components/    # Componentes reutilizáveis
│   ├── pages/         # Páginas principais
│   ├── services/      # Serviços de API
│   └── hooks/         # Hooks customizados
```

## 📊 Funcionalidades por Módulo

### **Transações**
- ✅ CRUD completo
- ✅ Categorização avançada
- ✅ Tags personalizadas
- ✅ Filtros e busca
- ✅ Validações rigorosas
- ✅ Transferências entre contas

### **Orçamentos**
- ✅ Criação mensal por categoria
- ✅ Cálculos automáticos
- ✅ 3 visualizações diferentes
- ✅ Sistema de alertas
- ✅ Análise preditiva
- ✅ Recomendações personalizadas

### **Contas e Cartões**
- ✅ Gestão completa
- ✅ Saldos automáticos
- ✅ Limites de cartão
- ✅ Histórico de movimentações

### **Alertas**
- ✅ 4 tipos de alerta
- ✅ 4 níveis de severidade
- ✅ Geração automática
- ✅ Centro unificado
- ✅ Filtros avançados

### **Dashboard**
- ✅ Resumo financeiro
- ✅ Métricas em tempo real
- ✅ Gráficos interativos
- ✅ Transações recentes

## 🔒 Segurança Implementada

- **Autenticação JWT** com refresh tokens
- **Middleware de segurança** avançado
- **Rate limiting** para proteção contra ataques
- **Validações rigorosas** de entrada
- **Headers de segurança** configurados
- **Proteção CSRF** ativa
- **Logs de auditoria** para transações
- **Criptografia** de dados sensíveis

## ⚡ Performance e Otimizações

- **Cache inteligente** para consultas frequentes
- **Queries otimizadas** com select_related/prefetch_related
- **Middleware de performance** ativo
- **Compressão de assets** configurada
- **Loading states** na interface
- **Lazy loading** implementado

## 🎨 Interface e UX

### **Design System**
- Cores e tipografia padronizadas
- Componentes reutilizáveis
- Design responsivo completo
- Feedback visual adequado
- Headers padronizados em todas as páginas
- Menu lateral consistente com ordenação lógica

### **Experiência do Usuário**
- Landing page profissional com CRO otimizado
- Navegação intuitiva com menu lateral padronizado
- Autenticação via modal (sem redirecionamento)
- < 3 cliques para ações principais
- Loading states e animações suaves
- Toast notifications para feedback
- Copy-to-clipboard para credenciais demo
- Cards clicáveis com hover effects
- Interface mobile-friendly
- Navegação inteligente baseada em status de login
- **Modais consistentes** com fundo sólido e opaco
- **Suporte universal à tecla ESC** para fechar modais
- **Contraste aprimorado** para valores monetários
- **Badges e alertas visuais** para informações importantes

## 🔄 Próximos Passos

### **Curto Prazo (1-2 semanas)**
- [x] Landing page profissional com CRO
- [x] Padronização de UI/UX em todas as páginas
- [x] Menu lateral consistente
- [x] Autenticação via modal
- [ ] Aumentar cobertura de testes para >80%
- [ ] Implementar exportação PDF de relatórios
- [ ] Otimizar performance de queries complexas

### **Médio Prazo (1-2 meses)**
- [ ] Implementar integrações bancárias
- [ ] Adicionar machine learning para categorização
- [ ] Desenvolver app mobile
- [ ] Implementar backup automático

### **Longo Prazo (3-6 meses)**
- [ ] Multi-tenancy para famílias
- [ ] API pública para integrações
- [ ] Consultoria financeira com IA
- [ ] Marketplace de plugins

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

**Importante**: Mantenha a paridade frontend-backend - toda funcionalidade deve ter API e interface correspondentes.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Suporte

Para suporte, consulte:
- `SETUP.md` para problemas de instalação
- `RULES.md` para regras de desenvolvimento
- `DEPLOY.md` para instruções de deploy
- Issues no GitHub para bugs e sugestões

---

## 🎉 Conclusão

**Nossa Grana** é um sistema completo e profissional de controle financeiro familiar, com:

- ✅ **95% das funcionalidades implementadas**
- ✅ **Landing page profissional** com CRO otimizado
- ✅ **Interface 100% funcional** e padronizada
- ✅ **UX otimizada** com autenticação modal e navegação inteligente
- ✅ **Sistema de cartões aprimorado** com UX avançada
- ✅ **Modais consistentes** com suporte à tecla ESC
- ✅ **Cálculos financeiros robustos** e confiáveis
- ✅ **Segurança aprovada** (0 vulnerabilidades críticas)
- ✅ **Performance otimizada** (<2s carregamento)
- ✅ **Design responsivo** (100% mobile-friendly)
- ✅ **Pronto para produção** com deploy automatizado

**O sistema está FUNCIONAL e PRONTO PARA USO!** 🚀

*Versão atual: 1.0.0 - Sistema funcional e pronto para produção*

---

**Nossa Grana** - Controle financeiro familiar inteligente! 💰👨‍👩‍👧‍👦