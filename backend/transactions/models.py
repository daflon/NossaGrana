from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


class Category(models.Model):
    """
    Categorias para classificação de transações
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='Nome')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='Cor (Hex)')
    icon = models.CharField(max_length=50, default='category', verbose_name='Ícone')
    is_default = models.BooleanField(default=False, verbose_name='Categoria Padrão')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Tags personalizadas para transações
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    name = models.CharField(max_length=30, verbose_name='Nome')
    color = models.CharField(max_length=7, default='#6c757d', verbose_name='Cor (Hex)')
    description = models.CharField(max_length=100, blank=True, verbose_name='Descrição')
    is_default = models.BooleanField(default=False, verbose_name='Tag Padrão')
    usage_count = models.IntegerField(default=0, verbose_name='Contador de Uso')
    is_active = models.BooleanField(default=True, verbose_name='Ativa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['-usage_count', 'name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f'{self.name} ({self.user.username})'

    def clean(self):
        """
        Validações customizadas
        """
        from django.core.exceptions import ValidationError
        import re
        
        # Validar nome da tag
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'O nome da tag é obrigatório.'})
        
        # Normalizar nome (manter case original, apenas remover espaços extras)
        self.name = self.name.strip()
        
        if len(self.name) < 2:
            raise ValidationError({'name': 'O nome deve ter pelo menos 2 caracteres.'})
        
        if len(self.name) > 30:
            raise ValidationError({'name': 'O nome deve ter no máximo 30 caracteres.'})
        
        # Validar caracteres permitidos (incluindo acentos e caracteres especiais)
        if not re.match(r'^[\w\s\-À-ÿ]+$', self.name, re.UNICODE):
            raise ValidationError({
                'name': 'O nome pode conter apenas letras, números, hífen, underscore e espaços.'
            })
        
        # Validar cor hexadecimal
        if self.color and not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
            raise ValidationError({'color': 'A cor deve estar no formato hexadecimal (#RRGGBB).'})
        
        # Verificar unicidade por usuário (case-insensitive)
        if Tag.objects.filter(user=self.user, name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'Você já possui uma tag com este nome.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def increment_usage(self):
        """
        Incrementa o contador de uso da tag
        """
        self.usage_count += 1
        self.save(update_fields=['usage_count', 'updated_at'])

    def decrement_usage(self):
        """
        Decrementa o contador de uso da tag
        """
        if self.usage_count > 0:
            self.usage_count -= 1
            self.save(update_fields=['usage_count', 'updated_at'])

    def get_transactions_count(self):
        """
        Retorna o número de transações que usam esta tag
        """
        return self.transaction_set.count()

    def get_total_amount(self):
        """
        Retorna o valor total das transações com esta tag
        """
        from django.db.models import Sum
        result = self.transaction_set.aggregate(total=Sum('amount'))
        return result['total'] or Decimal('0.00')

    def get_recent_transactions(self, limit=5):
        """
        Retorna as transações mais recentes com esta tag
        """
        return self.transaction_set.order_by('-date', '-created_at')[:limit]

    @property
    def formatted_name(self):
        """
        Retorna o nome formatado da tag
        """
        return self.name.title()

    @classmethod
    def get_popular_tags(cls, user, limit=10):
        """
        Retorna as tags mais usadas do usuário
        """
        return cls.objects.filter(
            user=user, 
            is_active=True
        ).order_by('-usage_count', 'name')[:limit]

    @classmethod
    def create_default_tags(cls, user):
        """
        Cria tags padrão para um novo usuário
        """
        default_tags = [
            {'name': 'Essencial', 'color': '#dc3545', 'description': 'Gastos essenciais'},
            {'name': 'Lazer', 'color': '#28a745', 'description': 'Entretenimento e diversão'},
            {'name': 'Trabalho', 'color': '#007bff', 'description': 'Relacionado ao trabalho'},
            {'name': 'Saúde', 'color': '#fd7e14', 'description': 'Gastos com saúde'},
            {'name': 'Educação', 'color': '#6f42c1', 'description': 'Investimento em educação'},
            {'name': 'Casa', 'color': '#20c997', 'description': 'Gastos domésticos'},
            {'name': 'Transporte', 'color': '#ffc107', 'description': 'Locomoção e transporte'},
            {'name': 'Investimento', 'color': '#6c757d', 'description': 'Aplicações financeiras'},
        ]
        
        created_tags = []
        for tag_data in default_tags:
            tag, created = cls.objects.get_or_create(
                user=user,
                name=tag_data['name'],
                defaults={
                    'color': tag_data['color'],
                    'description': tag_data['description'],
                    'is_default': True
                }
            )
            if created:
                created_tags.append(tag)
        
        return created_tags


class Transaction(models.Model):
    """
    Transações financeiras (receitas e despesas)
    """
    TRANSACTION_TYPES = [
        ('income', 'Receita'),
        ('expense', 'Despesa'),
        ('transfer', 'Transferência'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuário')
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name='Tipo')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Valor'
    )
    description = models.CharField(max_length=200, verbose_name='Descrição')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoria')
    date = models.DateField(verbose_name='Data')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Tags')
    
    # Meio de pagamento (conta ou cartão)
    account = models.ForeignKey(
        'financial_accounts.Account', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Conta Bancária'
    )
    credit_card = models.ForeignKey(
        'financial_accounts.CreditCard', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name='Cartão de Crédito'
    )
    
    # Para transferências entre contas
    transfer_to_account = models.ForeignKey(
        'financial_accounts.Account', 
        on_delete=models.CASCADE, 
        related_name='transfers_received', 
        null=True, 
        blank=True,
        verbose_name='Conta Destino'
    )
    transfer_from_account = models.ForeignKey(
        'financial_accounts.Account', 
        on_delete=models.CASCADE, 
        related_name='transfers_sent', 
        null=True, 
        blank=True,
        verbose_name='Conta Origem'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.get_type_display()}: {self.description} - R$ {self.amount}'

    def clean(self):
        """
        Validações customizadas
        """
        from django.core.exceptions import ValidationError
        
        # Data não pode ser futura
        if self.date and self.date > timezone.now().date():
            raise ValidationError({'date': 'A data não pode ser futura.'})
        
        # Descrição deve ter pelo menos 3 caracteres
        if self.description and len(self.description.strip()) < 3:
            raise ValidationError({'description': 'A descrição deve ter pelo menos 3 caracteres.'})
        
        # Validações de meio de pagamento
        if self.type == 'transfer':
            # Para transferências, deve ter conta origem e destino
            if not self.transfer_from_account or not self.transfer_to_account:
                raise ValidationError('Transferências devem ter conta origem e destino.')
            if self.transfer_from_account == self.transfer_to_account:
                raise ValidationError('Conta origem e destino devem ser diferentes.')
            # Transferências não devem ter account ou credit_card
            if self.account or self.credit_card:
                raise ValidationError('Transferências não devem ter conta ou cartão associado.')
        else:
            # Para receitas e despesas, deve ter conta OU cartão (não ambos)
            if self.account and self.credit_card:
                raise ValidationError('Transação deve ter conta OU cartão, não ambos.')
            if not self.account and not self.credit_card:
                raise ValidationError('Transação deve ter uma conta ou cartão associado.')
            # Receitas e despesas não devem ter contas de transferência
            if self.transfer_from_account or self.transfer_to_account:
                raise ValidationError('Apenas transferências podem ter contas de origem/destino.')
        
        # Verificar se a conta/cartão pertence ao mesmo usuário
        if self.account and self.account.user != self.user:
            raise ValidationError('A conta selecionada não pertence ao usuário.')
        if self.credit_card and self.credit_card.user != self.user:
            raise ValidationError('O cartão selecionado não pertence ao usuário.')
        if self.transfer_from_account and self.transfer_from_account.user != self.user:
            raise ValidationError('A conta origem não pertence ao usuário.')
        if self.transfer_to_account and self.transfer_to_account.user != self.user:
            raise ValidationError('A conta destino não pertence ao usuário.')

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.full_clean()
        
        # Verificar se é uma nova transação
        is_new = self.pk is None
        
        # Salvar a transação
        super().save(*args, **kwargs)
        
        # Atualizar saldos após salvar (tanto para nova quanto para atualização)
        self.update_account_balances()

    def add_tags(self, tag_names):
        """
        Adiciona tags à transação por nome
        """
        if not tag_names:
            return []
        
        added_tags = []
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            if tag_name:
                # Tentar encontrar tag existente (case-insensitive)
                try:
                    tag = Tag.objects.get(user=self.user, name__iexact=tag_name)
                except Tag.DoesNotExist:
                    tag = Tag.objects.create(
                        user=self.user,
                        name=tag_name,
                        color='#6c757d'
                    )
                
                if self.tags.filter(id=tag.id).exists():
                    continue  # Tag já associada
                
                self.tags.add(tag)
                tag.increment_usage()
                added_tags.append(tag)
        
        return added_tags

    def remove_tags(self, tag_names):
        """
        Remove tags da transação por nome
        """
        if not tag_names:
            return []
        
        removed_tags = []
        for tag_name in tag_names:
            tag_name = tag_name.strip().lower()
            try:
                tag = Tag.objects.get(user=self.user, name__iexact=tag_name)
                if self.tags.filter(id=tag.id).exists():
                    self.tags.remove(tag)
                    tag.decrement_usage()
                    removed_tags.append(tag)
            except Tag.DoesNotExist:
                continue
        
        return removed_tags

    def sync_tags(self, tag_names):
        """
        Sincroniza as tags da transação com a lista fornecida
        """
        if tag_names is None:
            return
        
        # Normalizar nomes das tags (manter case original)
        normalized_names = [name.strip() for name in tag_names if name.strip()]
        
        # Tags atuais
        current_tags = list(self.tags.all())
        current_names_lower = [tag.name.lower() for tag in current_tags]
        
        # Tags para adicionar (case-insensitive check)
        to_add = [name for name in normalized_names if name.lower() not in current_names_lower]
        
        # Tags para remover (case-insensitive check)
        normalized_names_lower = [name.lower() for name in normalized_names]
        to_remove = [tag for tag in current_tags if tag.name.lower() not in normalized_names_lower]
        
        # Remover tags
        for tag in to_remove:
            self.tags.remove(tag)
            tag.decrement_usage()
        
        # Adicionar novas tags
        for tag_name in to_add:
            # Tentar encontrar tag existente (case-insensitive)
            try:
                tag = Tag.objects.get(user=self.user, name__iexact=tag_name)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(
                    user=self.user,
                    name=tag_name,
                    color='#6c757d'
                )
            
            self.tags.add(tag)
            tag.increment_usage()

    @property
    def tags_display(self):
        """
        Retorna as tags formatadas para exibição
        """
        return ', '.join([tag.formatted_name for tag in self.tags.all()])

    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Salvar referências antes de deletar
        account = self.account
        credit_card = self.credit_card
        transfer_from = self.transfer_from_account
        transfer_to = self.transfer_to_account
        
        # Deletar a transação
        super().delete(*args, **kwargs)
        
        # Atualizar saldos após deletar
        if account:
            account.update_balance()
        if credit_card:
            credit_card.update_available_limit()
        if transfer_from:
            transfer_from.update_balance()
        if transfer_to:
            transfer_to.update_balance()

    def update_account_balances(self):
        """
        Atualiza os saldos das contas relacionadas
        """
        if self.account:
            self.account.update_balance()
        if self.credit_card:
            self.credit_card.update_available_limit()
        if self.transfer_from_account:
            self.transfer_from_account.update_balance()
        if self.transfer_to_account:
            self.transfer_to_account.update_balance()

    @property
    def payment_method_display(self):
        """
        Retorna o meio de pagamento formatado
        """
        if self.account:
            return f"Conta: {self.account.name}"
        elif self.credit_card:
            return f"Cartão: {self.credit_card.name}"
        elif self.type == 'transfer':
            return f"Transferência: {self.transfer_from_account.name} → {self.transfer_to_account.name}"
        return "Não informado"