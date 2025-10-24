from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Sum, Q


class Account(models.Model):
    """
    Modelo para contas bancárias (corrente, poupança, investimento, dinheiro)
    """
    ACCOUNT_TYPES = [
        ('checking', 'Conta Corrente'),
        ('savings', 'Poupança'),
        ('investment', 'Investimento'),
        ('cash', 'Dinheiro'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100, verbose_name='Nome da Conta')
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, verbose_name='Tipo')
    bank = models.CharField(max_length=100, blank=True, verbose_name='Banco')
    initial_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Saldo Inicial'
    )
    current_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Saldo Atual'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Conta Bancária'
        verbose_name_plural = 'Contas Bancárias'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_type_display()})'

    def save(self, *args, **kwargs):
        # Se é uma nova conta, definir saldo atual igual ao inicial
        if not self.pk:
            self.current_balance = self.initial_balance
        super().save(*args, **kwargs)

    @transaction.atomic
    def update_balance(self):
        """
        Atualiza o saldo atual baseado nas transações com lock para evitar race conditions
        """
        from transactions.models import Transaction
        
        # Lock na conta para evitar race conditions
        account = Account.objects.select_for_update().get(id=self.id)
        
        # Uma única query otimizada para todos os cálculos
        totals = Transaction.objects.filter(
            Q(account=account) | Q(transfer_to_account=account) | Q(transfer_from_account=account)
        ).aggregate(
            income=Sum('amount', filter=Q(type='income', account=account)),
            expense=Sum('amount', filter=Q(type='expense', account=account)),
            transfers_in=Sum('amount', filter=Q(type='transfer', transfer_to_account=account)),
            transfers_out=Sum('amount', filter=Q(type='transfer', transfer_from_account=account))
        )
        
        # Calcular saldo atual
        account.current_balance = (
            account.initial_balance + 
            (totals['income'] or Decimal('0.00')) - 
            (totals['expense'] or Decimal('0.00')) + 
            (totals['transfers_in'] or Decimal('0.00')) - 
            (totals['transfers_out'] or Decimal('0.00'))
        )
        account.save(update_fields=['current_balance', 'updated_at'])

    def can_debit(self, amount):
        """
        Verifica se é possível debitar um valor da conta
        """
        return self.current_balance >= amount

    @property
    def balance_formatted(self):
        """
        Retorna o saldo formatado em reais
        """
        return f'R$ {self.current_balance:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


class CreditCard(models.Model):
    """
    Modelo para cartões de crédito
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_cards')
    name = models.CharField(max_length=100, verbose_name='Nome do Cartão')
    bank = models.CharField(max_length=100, verbose_name='Banco')
    credit_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Limite de Crédito'
    )
    available_limit = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='Limite Disponível'
    )
    closing_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name='Dia de Fechamento'
    )
    due_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        verbose_name='Dia de Vencimento'
    )
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cartão de Crédito'
        verbose_name_plural = 'Cartões de Crédito'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} - {self.bank}'

    def save(self, *args, **kwargs):
        # Se é um novo cartão, definir limite disponível igual ao limite total
        if not self.pk:
            self.available_limit = self.credit_limit
        super().save(*args, **kwargs)

    def clean(self):
        """
        Validações customizadas
        """
        if self.due_day <= self.closing_day:
            # Se vencimento é no mesmo mês, deve ser após o fechamento
            if self.due_day - self.closing_day < 5:
                raise ValidationError(
                    'O dia de vencimento deve ser pelo menos 5 dias após o fechamento'
                )

    @transaction.atomic
    def update_available_limit(self):
        """
        Atualiza o limite disponível baseado nas transações não pagas com lock
        """
        from transactions.models import Transaction
        
        # Lock no cartão para evitar race conditions
        card = CreditCard.objects.select_for_update().get(id=self.id)
        
        # Somar gastos não pagos (transações do cartão)
        used_limit = Transaction.objects.filter(
            credit_card=card,
            type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Calcular limite disponível
        card.available_limit = card.credit_limit - used_limit
        card.save(update_fields=['available_limit', 'updated_at'])

    def can_charge(self, amount):
        """
        Verifica se é possível fazer uma cobrança no cartão
        """
        return self.available_limit >= amount

    @property
    def used_limit(self):
        """
        Retorna o valor usado do limite
        """
        return self.credit_limit - self.available_limit

    @property
    def usage_percentage(self):
        """
        Retorna a porcentagem de uso do limite
        """
        if self.credit_limit > 0:
            return (self.used_limit / self.credit_limit) * 100
        return 0

    @property
    def limit_formatted(self):
        """
        Retorna o limite formatado em reais
        """
        return f'R$ {self.credit_limit:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    @property
    def available_limit_formatted(self):
        """
        Retorna o limite disponível formatado em reais
        """
        return f'R$ {self.available_limit:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


class CreditCardBill(models.Model):
    """
    Modelo para faturas de cartão de crédito
    """
    BILL_STATUS = [
        ('open', 'Aberta'),
        ('closed', 'Fechada'),
        ('paid', 'Paga'),
        ('overdue', 'Vencida'),
    ]
    
    credit_card = models.ForeignKey(
        CreditCard, 
        on_delete=models.CASCADE, 
        related_name='bills'
    )
    reference_month = models.DateField(verbose_name='Mês de Referência')
    closing_date = models.DateField(verbose_name='Data de Fechamento')
    due_date = models.DateField(verbose_name='Data de Vencimento')
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Valor Total'
    )
    paid_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name='Valor Pago'
    )
    status = models.CharField(
        max_length=10, 
        choices=BILL_STATUS, 
        default='open',
        verbose_name='Status'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fatura de Cartão'
        verbose_name_plural = 'Faturas de Cartão'
        ordering = ['-reference_month']
        unique_together = ['credit_card', 'reference_month']

    def __str__(self):
        return f'{self.credit_card.name} - {self.reference_month.strftime("%m/%Y")}'

    def calculate_total(self):
        """
        Calcula o total da fatura baseado nas transações do período
        """
        from transactions.models import Transaction
        from datetime import datetime, timedelta
        
        # Definir período da fatura (do fechamento anterior até o fechamento atual)
        start_date = self.reference_month
        end_date = self.closing_date
        
        # Somar transações do cartão no período
        transactions_total = Transaction.objects.filter(
            credit_card=self.credit_card,
            type='expense',
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        self.total_amount = transactions_total
        self.save(update_fields=['total_amount', 'updated_at'])

    def pay(self, amount, payment_account=None):
        """
        Registra um pagamento da fatura
        """
        if amount <= 0:
            raise ValidationError('O valor do pagamento deve ser positivo')
        
        if self.paid_amount + amount > self.total_amount:
            raise ValidationError('O valor pago não pode exceder o total da fatura')
        
        self.paid_amount += amount
        
        # Atualizar status
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
        
        self.save(update_fields=['paid_amount', 'status', 'updated_at'])
        
        # Se foi informada uma conta para débito, criar transação
        if payment_account:
            from transactions.models import Transaction
            Transaction.objects.create(
                user=self.credit_card.user,
                type='expense',
                amount=amount,
                description=f'Pagamento fatura {self.credit_card.name} - {self.reference_month.strftime("%m/%Y")}',
                account=payment_account,
                date=datetime.now().date(),
                category_id=1  # Assumindo categoria padrão, ajustar conforme necessário
            )

    @property
    def remaining_amount(self):
        """
        Retorna o valor restante a pagar
        """
        return self.total_amount - self.paid_amount

    @property
    def is_overdue(self):
        """
        Verifica se a fatura está vencida
        """
        from datetime import date
        return date.today() > self.due_date and self.status != 'paid'

    @property
    def days_until_due(self):
        """
        Retorna quantos dias faltam para o vencimento
        """
        from datetime import date
        return (self.due_date - date.today()).days

    @property
    def total_formatted(self):
        """
        Retorna o total formatado em reais
        """
        return f'R$ {self.total_amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')