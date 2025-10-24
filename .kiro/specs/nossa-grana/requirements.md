# Requisitos - Nossa Grana

## Introdução

O Nossa Grana é um sistema de controle financeiro doméstico familiar que permite o gerenciamento compartilhado de receitas, despesas, orçamentos e metas de poupança. O sistema é projetado para uso pessoal/familiar, oferecendo uma interface simples e funcional para controle financeiro eficiente.

## Glossário

- **Sistema_Nossa_Grana**: O sistema completo de controle financeiro doméstico
- **Usuario_Familiar**: Membro da família com acesso autenticado ao sistema
- **Transacao**: Registro de entrada (receita) ou saída (despesa) financeira
- **Categoria**: Classificação pré-definida para transações (ex.: Alimentação, Transporte)
- **Tag**: Etiqueta personalizada aplicável a transações
- **Orcamento**: Limite financeiro definido para uma categoria em um período
- **Meta_Poupanca**: Objetivo de economia com valor alvo e prazo
- **Relatorio**: Documento com análise visual dos dados financeiros
- **Alerta**: Notificação automática sobre eventos financeiros relevantes
- **Conta_Bancaria**: Conta financeira (corrente, poupança, investimento) com saldo
- **Cartao_Credito**: Cartão de crédito com limite, fatura e data de vencimento
- **Meio_Pagamento**: Conta bancária ou cartão usado para realizar uma transação
- **Transferencia**: Movimentação de valor entre duas contas do usuário
- **Fatura_Cartao**: Conjunto de transações de um cartão em um período específico

## Requisitos

### Requisito 1

**User Story:** Como um usuário familiar, eu quero registrar minhas receitas e despesas manualmente, para que eu possa acompanhar meu fluxo de caixa.

#### Acceptance Criteria

1. WHEN um Usuario_Familiar acessa o formulário de transação, THE Sistema_Nossa_Grana SHALL exibir campos para data, valor, descrição e tipo (receita/despesa)
2. WHEN um Usuario_Familiar submete uma transação válida, THE Sistema_Nossa_Grana SHALL salvar os dados no banco de dados
3. IF um Usuario_Familiar submete dados inválidos, THEN THE Sistema_Nossa_Grana SHALL exibir mensagens de erro específicas
4. THE Sistema_Nossa_Grana SHALL permitir edição e exclusão de transações existentes
5. THE Sistema_Nossa_Grana SHALL exibir lista de todas as transações ordenadas por data

### Requisito 2

**User Story:** Como um usuário familiar, eu quero categorizar e etiquetar minhas transações, para que eu possa organizar melhor meus gastos.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL fornecer categorias pré-definidas (Alimentação, Transporte, Lazer, Saúde, Educação, Casa, Outros)
2. WHEN um Usuario_Familiar registra uma transação, THE Sistema_Nossa_Grana SHALL permitir seleção de categoria
3. THE Sistema_Nossa_Grana SHALL permitir criação de tags personalizadas
4. WHEN um Usuario_Familiar aplica tags, THE Sistema_Nossa_Grana SHALL associar múltiplas tags a uma transação
5. THE Sistema_Nossa_Grana SHALL permitir filtrar transações por categoria e tags

### Requisito 3

**User Story:** Como um usuário familiar, eu quero criar orçamentos mensais por categoria, para que eu possa controlar meus gastos.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL permitir definição de limite mensal por categoria
2. WHEN gastos de uma categoria atingem 80% do limite, THE Sistema_Nossa_Grana SHALL exibir alerta de aproximação
3. WHEN gastos de uma categoria excedem o limite, THE Sistema_Nossa_Grana SHALL exibir alerta de estouro
4. THE Sistema_Nossa_Grana SHALL calcular progresso do orçamento em tempo real
5. THE Sistema_Nossa_Grana SHALL exibir comparativo entre orçado e realizado

### Requisito 4

**User Story:** Como um usuário familiar, eu quero criar metas de poupança, para que eu possa alcançar objetivos financeiros específicos.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL permitir criação de Meta_Poupanca com nome, valor alvo e data objetivo
2. THE Sistema_Nossa_Grana SHALL calcular progresso percentual da meta baseado em transações de poupança
3. THE Sistema_Nossa_Grana SHALL estimar tempo necessário para atingir a meta baseado na média mensal
4. WHEN uma Meta_Poupanca é atingida, THE Sistema_Nossa_Grana SHALL exibir notificação de sucesso
5. THE Sistema_Nossa_Grana SHALL permitir múltiplas metas simultâneas

### Requisito 5

**User Story:** Como um usuário familiar, eu quero visualizar relatórios e gráficos dos meus dados financeiros, para que eu possa analisar padrões de gastos.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL gerar gráficos de pizza para distribuição de gastos por categoria
2. THE Sistema_Nossa_Grana SHALL gerar gráficos de barras para comparativo mensal de receitas e despesas
3. THE Sistema_Nossa_Grana SHALL permitir filtros por período (mensal, trimestral, anual)
4. THE Sistema_Nossa_Grana SHALL calcular totais, médias e tendências automaticamente
5. THE Sistema_Nossa_Grana SHALL permitir exportação de relatórios em formato PDF

### Requisito 6

**User Story:** Como um usuário familiar, eu quero receber alertas sobre eventos financeiros importantes, para que eu não perca prazos ou limites.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL enviar alertas quando orçamentos atingem 80% do limite
2. THE Sistema_Nossa_Grana SHALL enviar alertas quando orçamentos são excedidos
3. THE Sistema_Nossa_Grana SHALL permitir configuração de lembretes para vencimento de contas
4. WHEN uma Meta_Poupanca é atingida, THE Sistema_Nossa_Grana SHALL enviar notificação
5. THE Sistema_Nossa_Grana SHALL exibir alertas na interface e opcionalmente por email

### Requisito 7

**User Story:** Como um membro da família, eu quero acessar o sistema com minha própria conta, para que eu possa contribuir com o controle financeiro familiar.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL implementar autenticação individual com email e senha
2. THE Sistema_Nossa_Grana SHALL permitir múltiplos Usuario_Familiar acessarem os mesmos dados financeiros
3. THE Sistema_Nossa_Grana SHALL manter log de qual usuário criou cada transação
4. THE Sistema_Nossa_Grana SHALL implementar autorização baseada em JWT
5. THE Sistema_Nossa_Grana SHALL proteger todas as rotas com autenticação obrigatória

### Requisito 8

**User Story:** Como um usuário do sistema, eu quero uma interface responsiva e intuitiva, para que eu possa usar o sistema em qualquer dispositivo.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL funcionar adequadamente em dispositivos desktop, tablet e mobile
2. THE Sistema_Nossa_Grana SHALL implementar design responsivo com breakpoints apropriados
3. THE Sistema_Nossa_Grana SHALL seguir princípios de usabilidade com navegação clara
4. THE Sistema_Nossa_Grana SHALL carregar páginas em menos de 3 segundos
5. THE Sistema_Nossa_Grana SHALL implementar validação de formulários em tempo real

### Requisito 9

**User Story:** Como um usuário do sistema, eu quero que toda funcionalidade disponível na API tenha uma interface correspondente, para que eu possa acessar todas as funcionalidades através da interface web.

#### Acceptance Criteria

1. WHEN uma API é implementada no backend, THE Sistema_Nossa_Grana SHALL implementar interface correspondente no frontend
2. THE Sistema_Nossa_Grana SHALL garantir paridade funcional entre backend e frontend
3. THE Sistema_Nossa_Grana SHALL implementar todas as operações CRUD disponíveis na API através da interface
4. THE Sistema_Nossa_Grana SHALL exibir todos os dados calculados e campos disponíveis na API
5. THE Sistema_Nossa_Grana SHALL implementar todos os filtros e funcionalidades avançadas da API na interface

### Requisito 10

**User Story:** Como um usuário familiar, eu quero cadastrar minhas contas bancárias e cartões de crédito, para que eu possa controlar o saldo real de cada meio de pagamento.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL permitir cadastro de Conta_Bancaria com nome, tipo, banco e saldo inicial
2. THE Sistema_Nossa_Grana SHALL permitir cadastro de Cartao_Credito com nome, limite, dia de vencimento e banco
3. THE Sistema_Nossa_Grana SHALL calcular saldo atual de cada conta baseado nas transações
4. THE Sistema_Nossa_Grana SHALL calcular saldo disponível de cartão baseado no limite e gastos
5. THE Sistema_Nossa_Grana SHALL permitir ativação/desativação de contas e cartões

### Requisito 11

**User Story:** Como um usuário familiar, eu quero vincular cada transação a uma conta ou cartão específico, para que eu possa rastrear o uso de cada meio de pagamento.

#### Acceptance Criteria

1. WHEN um Usuario_Familiar registra uma transação, THE Sistema_Nossa_Grana SHALL exigir seleção de Meio_Pagamento
2. WHEN uma despesa é registrada em Conta_Bancaria, THE Sistema_Nossa_Grana SHALL debitar o valor do saldo
3. WHEN uma receita é registrada em Conta_Bancaria, THE Sistema_Nossa_Grana SHALL creditar o valor ao saldo
4. WHEN uma despesa é registrada em Cartao_Credito, THE Sistema_Nossa_Grana SHALL reduzir o limite disponível
5. THE Sistema_Nossa_Grana SHALL impedir transações que excedam saldo disponível ou limite do cartão

### Requisito 12

**User Story:** Como um usuário familiar, eu quero realizar transferências entre minhas contas, para que eu possa movimentar dinheiro conforme necessário.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL permitir criação de Transferencia entre duas Conta_Bancaria
2. WHEN uma Transferencia é executada, THE Sistema_Nossa_Grana SHALL debitar da conta origem e creditar na conta destino
3. THE Sistema_Nossa_Grana SHALL registrar a transferência como duas transações vinculadas
4. THE Sistema_Nossa_Grana SHALL impedir transferências que excedam o saldo da conta origem
5. THE Sistema_Nossa_Grana SHALL exibir histórico de transferências com identificação clara

### Requisito 13

**User Story:** Como um usuário familiar, eu quero visualizar relatórios específicos por conta e cartão, para que eu possa analisar o uso de cada meio de pagamento.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL gerar relatórios de movimentação por Conta_Bancaria
2. THE Sistema_Nossa_Grana SHALL gerar relatórios de gastos por Cartao_Credito
3. THE Sistema_Nossa_Grana SHALL calcular evolução do saldo de cada conta ao longo do tempo
4. THE Sistema_Nossa_Grana SHALL exibir utilização percentual do limite de cada cartão
5. THE Sistema_Nossa_Grana SHALL permitir comparativo de gastos entre diferentes meios de pagamento

### Requisito 14

**User Story:** Como um usuário familiar, eu quero gerenciar as faturas dos meus cartões de crédito, para que eu possa controlar os vencimentos e valores.

#### Acceptance Criteria

1. THE Sistema_Nossa_Grana SHALL gerar Fatura_Cartao automaticamente baseada no ciclo do cartão
2. THE Sistema_Nossa_Grana SHALL calcular valor total da fatura e data de vencimento
3. WHEN uma fatura vence em 7 dias, THE Sistema_Nossa_Grana SHALL enviar alerta de vencimento
4. THE Sistema_Nossa_Grana SHALL permitir registro de pagamento de fatura
5. THE Sistema_Nossa_Grana SHALL exibir histórico de faturas pagas e pendentes