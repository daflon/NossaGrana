# API de Orçamentos - Documentação

## Endpoints Disponíveis

### 1. Listar Orçamentos
**GET** `/api/budgets/budgets/`

Lista todos os orçamentos do usuário autenticado.

**Parâmetros de Query (opcionais):**
- `month`: Filtrar por mês (formato: YYYY-MM)
- `category`: Filtrar por ID da categoria
- `status`: Filtrar por status (exceeded, warning, ok)

**Exemplo de Resposta:**
```json
[
    {
        "id": 1,
        "category": 1,
        "category_name": "Alimentação",
        "category_color": "#28a745",
        "category_icon": "restaurant",
        "amount": "500.00",
        "month": "2024-11-01",
        "month_display": "11/2024",
        "spent_amount": "320.50",
        "remaining_amount": "179.50",
        "percentage_used": 64.1,
        "is_over_budget": false,
        "is_near_limit": false,
        "created_at": "2024-11-01T10:00:00Z",
        "updated_at": "2024-11-01T10:00:00Z"
    }
]
```

### 2. Criar Orçamento
**POST** `/api/budgets/budgets/`

Cria um novo orçamento para o usuário autenticado.

**Corpo da Requisição:**
```json
{
    "category": 1,
    "amount": "500.00",
    "month": "2024-11-01"
}
```

**Validações:**
- `amount`: Deve ser positivo
- `month`: Deve ser o primeiro dia do mês e não pode ser passado
- Não pode existir outro orçamento para a mesma categoria/mês

### 3. Obter Orçamento Específico
**GET** `/api/budgets/budgets/{id}/`

Retorna detalhes de um orçamento específico.

### 4. Atualizar Orçamento
**PUT** `/api/budgets/budgets/{id}/` ou **PATCH** `/api/budgets/budgets/{id}/`

Atualiza um orçamento existente.

### 5. Deletar Orçamento
**DELETE** `/api/budgets/budgets/{id}/`

Remove um orçamento.

### 6. Orçamentos do Mês Atual
**GET** `/api/budgets/budgets/current_month/`

Retorna todos os orçamentos do mês atual.

### 7. Categorias Sem Orçamento
**GET** `/api/budgets/budgets/categories_without_budget/`

Lista categorias que não possuem orçamento no mês especificado.

**Parâmetros de Query:**
- `month`: Mês para verificar (formato: YYYY-MM, padrão: mês atual)

### 8. Status dos Orçamentos
**GET** `/api/budgets/status/`

Retorna status consolidado dos orçamentos.

**Parâmetros de Query:**
- `month`: Mês para análise (formato: YYYY-MM, padrão: mês atual)

**Exemplo de Resposta:**
```json
{
    "month": "2024-11",
    "month_display": "11/2024",
    "summary": {
        "total_budgets": 5,
        "total_budgeted": "2500.00",
        "total_spent": "1800.50",
        "total_remaining": "699.50",
        "budgets_exceeded": 1,
        "budgets_warning": 2,
        "budgets_ok": 2
    },
    "budgets": [
        {
            "id": 1,
            "category_name": "Alimentação",
            "category_color": "#28a745",
            "amount": "500.00",
            "spent_amount": "520.00",
            "remaining_amount": "-20.00",
            "percentage_used": 104.0,
            "is_over_budget": true,
            "is_near_limit": true,
            "status": "exceeded"
        }
    ]
}
```

## Status dos Orçamentos

- **ok**: Orçamento normal (< 80% usado)
- **warning**: Próximo do limite (80-100% usado)
- **exceeded**: Orçamento excedido (> 100% usado)

## Campos Calculados

- `spent_amount`: Valor gasto na categoria no mês
- `remaining_amount`: Valor restante do orçamento
- `percentage_used`: Porcentagem utilizada do orçamento
- `is_over_budget`: Se o orçamento foi excedido
- `is_near_limit`: Se está próximo do limite (>= 80%)

## Autenticação

Todos os endpoints requerem autenticação JWT. Inclua o token no header:
```
Authorization: Bearer <seu_token_jwt>
```