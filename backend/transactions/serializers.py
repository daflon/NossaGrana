from rest_framework import serializers
from django.utils import timezone
from django.db import transaction as db_transaction
from .models import Category, Tag, Transaction


class CategorySerializer(serializers.ModelSerializer):
    transaction_count = serializers.IntegerField(read_only=True)
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_expense = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'color', 'icon', 'is_default', 'created_at',
            'transaction_count', 'total_income', 'total_expense', 'balance'
        ]
        read_only_fields = ['is_default', 'created_at', 'transaction_count', 
                           'total_income', 'total_expense', 'balance']

    def validate_name(self, value):
        """
        Valida se o nome da categoria é único (case-insensitive)
        """
        if not value or not value.strip():
            raise serializers.ValidationError("O nome da categoria é obrigatório.")
        
        name = value.strip()
        if len(name) < 2:
            raise serializers.ValidationError("O nome deve ter pelo menos 2 caracteres.")
        
        if len(name) > 50:
            raise serializers.ValidationError("O nome deve ter no máximo 50 caracteres.")
        
        # Verificar unicidade (case-insensitive)
        queryset = Category.objects.filter(name__iexact=name)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Já existe uma categoria com este nome.")
        
        return name

    def validate_color(self, value):
        """
        Valida se a cor está no formato hexadecimal
        """
        import re
        
        if not value:
            return '#007bff'  # Cor padrão
        
        # Verificar formato hexadecimal
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError("A cor deve estar no formato hexadecimal (#RRGGBB).")
        
        return value

    def validate_icon(self, value):
        """
        Valida o ícone da categoria
        """
        if not value:
            return 'category'  # Ícone padrão
        
        if len(value) > 50:
            raise serializers.ValidationError("O ícone deve ter no máximo 50 caracteres.")
        
        return value

    def create(self, validated_data):
        """
        Cria uma nova categoria
        """
        # Garantir que não seja marcada como padrão
        validated_data['is_default'] = False
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Atualiza uma categoria existente
        """
        # Não permitir alterar o status de categoria padrão
        if instance.is_default:
            validated_data.pop('is_default', None)
        
        return super().update(instance, validated_data)


class TagSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    formatted_name = serializers.ReadOnlyField()
    usage_count = serializers.ReadOnlyField()
    transaction_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = [
            'id', 'user', 'name', 'formatted_name', 'color', 'description', 
            'is_default', 'usage_count', 'transaction_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'is_default', 'usage_count', 'created_at', 'updated_at']

    def get_transaction_count(self, obj):
        """Contar transações que usam esta tag"""
        return obj.get_transactions_count()

    def validate_name(self, value):
        """Validar nome da tag"""
        if not value or not value.strip():
            raise serializers.ValidationError("O nome da tag é obrigatório.")
        
        name = value.strip().lower()
        if len(name) < 2:
            raise serializers.ValidationError("O nome deve ter pelo menos 2 caracteres.")
        
        if len(name) > 30:
            raise serializers.ValidationError("O nome deve ter no máximo 30 caracteres.")
        
        import re
        if not re.match(r'^[\w\s\-À-ÿ]+$', name, re.UNICODE):
            raise serializers.ValidationError(
                "O nome pode conter apenas letras, números, hífen, underscore e espaços."
            )
        
        return name

    def validate_color(self, value):
        """Validar cor hexadecimal"""
        if not value:
            return '#6c757d'  # Cor padrão
        
        import re
        if not re.match(r'^#[0-9A-Fa-f]{6}$', value):
            raise serializers.ValidationError("A cor deve estar no formato hexadecimal (#RRGGBB).")
        
        return value

    def validate(self, data):
        """Validações cruzadas"""
        user = self.context['request'].user
        name = data.get('name', '').strip().lower()
        
        if name:
            queryset = Tag.objects.filter(user=user, name__iexact=name)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'name': 'Você já possui uma tag com este nome.'
                })
        
        return data

    def create(self, validated_data):
        """Criar nova tag"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    tags_list = TagSerializer(source='tags', many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=30),
        write_only=True,
        required=False,
        allow_empty=True,
        help_text="Lista de nomes de tags (serão criadas automaticamente se não existirem)"
    )
    tags_display = serializers.ReadOnlyField()
    
    # Campos de meio de pagamento
    account_name = serializers.CharField(source='account.name', read_only=True)
    credit_card_name = serializers.CharField(source='credit_card.name', read_only=True)
    payment_method_display = serializers.ReadOnlyField()
    
    # Campos de transferência
    transfer_from_account_name = serializers.CharField(source='transfer_from_account.name', read_only=True)
    transfer_to_account_name = serializers.CharField(source='transfer_to_account.name', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'type', 'amount', 'description', 'category', 'category_name', 
            'category_color', 'date', 'tags_list', 'tag_ids', 'tag_names', 'tags_display', 'user',
            'account', 'account_name', 'credit_card', 'credit_card_name',
            'transfer_from_account', 'transfer_from_account_name',
            'transfer_to_account', 'transfer_to_account_name',
            'payment_method_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_date(self, value):
        """
        Valida se a data não é futura
        """
        if value > timezone.now().date():
            raise serializers.ValidationError("A data não pode ser futura.")
        return value

    def validate_description(self, value):
        """
        Valida se a descrição tem pelo menos 3 caracteres
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError("A descrição deve ter pelo menos 3 caracteres.")
        return value.strip()

    def validate_amount(self, value):
        """
        Valida se o valor é positivo
        """
        if value <= 0:
            raise serializers.ValidationError("O valor deve ser positivo.")
        return value

    def validate_tag_ids(self, value):
        """
        Valida se todas as tags existem
        """
        if value:
            existing_tags = Tag.objects.filter(id__in=value).count()
            if existing_tags != len(value):
                raise serializers.ValidationError("Uma ou mais tags não existem.")
        return value

    def validate(self, data):
        """
        Validações cruzadas para meio de pagamento
        """
        transaction_type = data.get('type')
        account = data.get('account')
        credit_card = data.get('credit_card')
        transfer_from = data.get('transfer_from_account')
        transfer_to = data.get('transfer_to_account')
        amount = data.get('amount')
        user = self.context['request'].user
        
        if transaction_type == 'transfer':
            # Para transferências, deve ter conta origem e destino
            if not transfer_from or not transfer_to:
                raise serializers.ValidationError(
                    "Transferências devem ter conta origem e destino."
                )
            if transfer_from == transfer_to:
                raise serializers.ValidationError(
                    "Conta origem e destino devem ser diferentes."
                )
            # Verificar se as contas pertencem ao usuário
            if transfer_from.user != user:
                raise serializers.ValidationError(
                    "A conta origem não pertence ao usuário."
                )
            if transfer_to.user != user:
                raise serializers.ValidationError(
                    "A conta destino não pertence ao usuário."
                )
            # Transferências não devem ter account ou credit_card
            if account or credit_card:
                raise serializers.ValidationError(
                    "Transferências não devem ter conta ou cartão associado."
                )
        else:
            # Para receitas e despesas, deve ter conta OU cartão (não ambos)
            if account and credit_card:
                raise serializers.ValidationError(
                    "Transação deve ter conta OU cartão, não ambos."
                )
            if not account and not credit_card:
                raise serializers.ValidationError(
                    "Transação deve ter uma conta ou cartão associado."
                )
            # Verificar se a conta/cartão pertence ao usuário
            if account and account.user != user:
                raise serializers.ValidationError(
                    "A conta selecionada não pertence ao usuário."
                )
            if credit_card and credit_card.user != user:
                raise serializers.ValidationError(
                    "O cartão selecionado não pertence ao usuário."
                )
            
            # Validações de saldo/limite para despesas
            if transaction_type == 'expense' and amount:
                if account and not account.can_debit(amount):
                    raise serializers.ValidationError(
                        f"Saldo insuficiente na conta {account.name}. "
                        f"Saldo atual: R$ {account.current_balance:.2f}"
                    )
                if credit_card and not credit_card.can_charge(amount):
                    raise serializers.ValidationError(
                        f"Limite insuficiente no cartão {credit_card.name}. "
                        f"Limite disponível: R$ {credit_card.available_limit:.2f}"
                    )
            
            # Receitas e despesas não devem ter contas de transferência
            if transfer_from or transfer_to:
                raise serializers.ValidationError(
                    "Apenas transferências podem ter contas de origem/destino."
                )
        
        return data

    def create(self, validated_data):
        """
        Cria uma nova transação
        """
        tag_ids = validated_data.pop('tag_ids', [])
        tag_names = validated_data.pop('tag_names', [])
        validated_data['user'] = self.context['request'].user
        
        transaction = Transaction.objects.create(**validated_data)
        
        # Processar tags por ID
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids, user=transaction.user)
            transaction.tags.set(tags)
            # Incrementar contador de uso
            for tag in tags:
                tag.increment_usage()
        
        # Processar tags por nome (criar se não existir)
        if tag_names:
            transaction.add_tags(tag_names)
        
        return transaction

    def update(self, instance, validated_data):
        """
        Atualiza uma transação existente
        """
        tag_ids = validated_data.pop('tag_ids', None)
        tag_names = validated_data.pop('tag_names', None)
        
        # Atualiza campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Atualiza tags por ID se fornecidas
        if tag_ids is not None:
            # Decrementar uso das tags antigas
            for tag in instance.tags.all():
                tag.decrement_usage()
            
            if tag_ids:
                tags = Tag.objects.filter(id__in=tag_ids, user=instance.user)
                instance.tags.set(tags)
                # Incrementar uso das novas tags
                for tag in tags:
                    tag.increment_usage()
            else:
                instance.tags.clear()
        
        # Atualiza tags por nome se fornecidas
        if tag_names is not None:
            instance.sync_tags(tag_names)
        
        return instance


class TransactionSummarySerializer(serializers.Serializer):
    """
    Serializer para resumo de transações
    """
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    transaction_count = serializers.IntegerField()


class TransferSerializer(serializers.Serializer):
    """
    Serializer específico para transferências entre contas
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=200)
    from_account = serializers.IntegerField()
    to_account = serializers.IntegerField()
    date = serializers.DateField()
    category = serializers.IntegerField(required=False)

    def validate_amount(self, value):
        """
        Valida se o valor é positivo
        """
        if value <= 0:
            raise serializers.ValidationError("O valor deve ser positivo.")
        return value

    def validate_description(self, value):
        """
        Valida se a descrição tem pelo menos 3 caracteres
        """
        if len(value.strip()) < 3:
            raise serializers.ValidationError("A descrição deve ter pelo menos 3 caracteres.")
        return value.strip()

    def validate_date(self, value):
        """
        Valida se a data não é futura
        """
        if value > timezone.now().date():
            raise serializers.ValidationError("A data não pode ser futura.")
        return value

    def validate(self, data):
        """
        Validações cruzadas para transferência
        """
        from financial_accounts.models import Account
        from .models import Category
        
        user = self.context['request'].user
        from_account_id = data.get('from_account')
        to_account_id = data.get('to_account')
        amount = data.get('amount')
        
        # Verificar se as contas são diferentes
        if from_account_id == to_account_id:
            raise serializers.ValidationError("Conta origem e destino devem ser diferentes.")
        
        # Verificar se as contas existem e pertencem ao usuário
        try:
            from_account = Account.objects.get(id=from_account_id, user=user)
            to_account = Account.objects.get(id=to_account_id, user=user)
        except Account.DoesNotExist:
            raise serializers.ValidationError("Uma ou ambas as contas não existem ou não pertencem ao usuário.")
        
        # Verificar se a conta origem tem saldo suficiente
        if not from_account.can_debit(amount):
            raise serializers.ValidationError(
                f"Saldo insuficiente na conta {from_account.name}. "
                f"Saldo atual: R$ {from_account.current_balance:.2f}"
            )
        
        # Verificar se as contas estão ativas
        if not from_account.is_active:
            raise serializers.ValidationError("A conta origem não está ativa.")
        if not to_account.is_active:
            raise serializers.ValidationError("A conta destino não está ativa.")
        
        # Verificar categoria se fornecida
        category_id = data.get('category')
        if category_id:
            try:
                Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise serializers.ValidationError("Categoria não encontrada.")
        
        # Adicionar objetos ao contexto para uso no create
        data['from_account_obj'] = from_account
        data['to_account_obj'] = to_account
        
        return data

    @db_transaction.atomic
    def create(self, validated_data):
        """
        Cria uma transferência entre contas com validação de saldo
        """
        from .models import Category
        from financial_accounts.models import Account
        
        user = self.context['request'].user
        amount = validated_data['amount']
        description = validated_data['description']
        date = validated_data['date']
        from_account = validated_data['from_account_obj']
        to_account = validated_data['to_account_obj']
        
        # Lock nas contas para verificar saldo
        from_account = Account.objects.select_for_update().get(id=from_account.id)
        to_account = Account.objects.select_for_update().get(id=to_account.id)
        
        # Verificar saldo suficiente novamente (double-check com lock)
        if not from_account.can_debit(amount):
            raise serializers.ValidationError(
                f"Saldo insuficiente. Saldo atual: R$ {from_account.current_balance:.2f}"
            )
        
        # Obter categoria padrão para transferências ou usar a fornecida
        category_id = validated_data.get('category')
        if category_id:
            category = Category.objects.get(id=category_id)
        else:
            # Criar ou obter categoria padrão para transferências
            category, created = Category.objects.get_or_create(
                name='Transferência',
                defaults={
                    'color': '#6c757d',
                    'icon': 'transfer',
                    'is_default': True
                }
            )
        
        # Criar a transação de transferência
        transaction_obj = Transaction.objects.create(
            user=user,
            type='transfer',
            amount=amount,
            description=description,
            category=category,
            date=date,
            transfer_from_account=from_account,
            transfer_to_account=to_account
        )
        
        return transaction_obj


class TransactionFilterSerializer(serializers.Serializer):
    """
    Serializer para filtros de transações
    """
    type = serializers.ChoiceField(choices=Transaction.TRANSACTION_TYPES, required=False)
    category = serializers.IntegerField(required=False)
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    amount_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    amount_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    search = serializers.CharField(max_length=200, required=False)

    def validate(self, data):
        """
        Validações cruzadas
        """
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise serializers.ValidationError("A data inicial deve ser anterior à data final.")
        
        amount_min = data.get('amount_min')
        amount_max = data.get('amount_max')
        
        if amount_min and amount_max and amount_min > amount_max:
            raise serializers.ValidationError("O valor mínimo deve ser menor que o valor máximo.")
        
        return data