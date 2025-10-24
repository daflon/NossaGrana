from rest_framework import serializers
from .models import Account, CreditCard, CreditCardBill
from django.contrib.auth.models import User


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer para contas bancárias
    """
    balance_formatted = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'type', 'type_display', 'bank', 
            'initial_balance', 'current_balance', 'balance_formatted',
            'is_active', 'user', 'user_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['current_balance', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Definir o usuário automaticamente
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_initial_balance(self, value):
        """
        Validar saldo inicial
        """
        if value < 0:
            raise serializers.ValidationError("O saldo inicial não pode ser negativo.")
        return value


class AccountSummarySerializer(serializers.ModelSerializer):
    """
    Serializer resumido para contas (para uso em listas)
    """
    balance_formatted = serializers.ReadOnlyField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Account
        fields = ['id', 'name', 'type', 'type_display', 'current_balance', 'balance_formatted', 'is_active']


class CreditCardSerializer(serializers.ModelSerializer):
    """
    Serializer para cartões de crédito
    """
    limit_formatted = serializers.ReadOnlyField()
    available_limit_formatted = serializers.ReadOnlyField()
    usage_percentage = serializers.ReadOnlyField()
    used_limit = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = CreditCard
        fields = [
            'id', 'name', 'bank', 'credit_limit', 'limit_formatted',
            'available_limit', 'available_limit_formatted', 'used_limit',
            'usage_percentage', 'closing_day', 'due_day', 'is_active',
            'user', 'user_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['available_limit', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Definir o usuário automaticamente
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_credit_limit(self, value):
        """
        Validar limite de crédito
        """
        if value <= 0:
            raise serializers.ValidationError("O limite de crédito deve ser maior que zero.")
        return value

    def validate(self, data):
        """
        Validações customizadas
        """
        closing_day = data.get('closing_day')
        due_day = data.get('due_day')
        
        if closing_day and due_day:
            if due_day <= closing_day:
                if due_day - closing_day < 5:
                    raise serializers.ValidationError({
                        'due_day': 'O dia de vencimento deve ser pelo menos 5 dias após o fechamento.'
                    })
        
        return data


class CreditCardSummarySerializer(serializers.ModelSerializer):
    """
    Serializer resumido para cartões (para uso em listas)
    """
    available_limit_formatted = serializers.ReadOnlyField()
    usage_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = CreditCard
        fields = [
            'id', 'name', 'bank', 'credit_limit', 'available_limit', 
            'available_limit_formatted', 'usage_percentage', 'is_active'
        ]


class CreditCardBillSerializer(serializers.ModelSerializer):
    """
    Serializer para faturas de cartão de crédito
    """
    credit_card_name = serializers.CharField(source='credit_card.name', read_only=True)
    credit_card_bank = serializers.CharField(source='credit_card.bank', read_only=True)
    total_formatted = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    remaining_amount_formatted = serializers.CharField(
        source='remaining_amount', 
        read_only=True
    )
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CreditCardBill
        fields = [
            'id', 'credit_card', 'credit_card_name', 'credit_card_bank',
            'reference_month', 'closing_date', 'due_date', 'total_amount',
            'total_formatted', 'paid_amount', 'remaining_amount', 
            'remaining_amount_formatted', 'status', 'status_display',
            'is_overdue', 'days_until_due', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_amount', 'created_at', 'updated_at']

    def validate_paid_amount(self, value):
        """
        Validar valor pago
        """
        if value < 0:
            raise serializers.ValidationError("O valor pago não pode ser negativo.")
        
        # Se está atualizando, verificar se não excede o total
        if self.instance and value > self.instance.total_amount:
            raise serializers.ValidationError("O valor pago não pode exceder o total da fatura.")
        
        return value


class PayBillSerializer(serializers.Serializer):
    """
    Serializer para pagamento de fatura
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    payment_account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.none(),
        required=False,
        allow_null=True
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar contas do usuário logado
        if 'context' in kwargs and 'request' in kwargs['context']:
            user = kwargs['context']['request'].user
            self.fields['payment_account'].queryset = Account.objects.filter(
                user=user, 
                is_active=True
            )

    def validate_amount(self, value):
        """
        Validar valor do pagamento
        """
        if hasattr(self, 'instance') and self.instance:
            bill = self.instance
            if value > bill.remaining_amount:
                raise serializers.ValidationError(
                    f"O valor não pode exceder o restante da fatura (R$ {bill.remaining_amount:.2f})"
                )
        return value

    def validate(self, data):
        """
        Validações adicionais
        """
        payment_account = data.get('payment_account')
        amount = data.get('amount')
        
        # Se foi informada uma conta, verificar se tem saldo
        if payment_account and amount:
            if not payment_account.can_debit(amount):
                raise serializers.ValidationError({
                    'payment_account': f'Saldo insuficiente. Saldo atual: R$ {payment_account.current_balance:.2f}'
                })
        
        return data


class TransferSerializer(serializers.Serializer):
    """
    Serializer para transferências entre contas
    """
    from_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.none())
    to_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.none())
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=200, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar contas do usuário logado
        if 'context' in kwargs and 'request' in kwargs['context']:
            user = kwargs['context']['request'].user
            active_accounts = Account.objects.filter(user=user, is_active=True)
            self.fields['from_account'].queryset = active_accounts
            self.fields['to_account'].queryset = active_accounts

    def validate(self, data):
        """
        Validações da transferência
        """
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        amount = data.get('amount')
        
        # Verificar se as contas são diferentes
        if from_account == to_account:
            raise serializers.ValidationError("As contas de origem e destino devem ser diferentes.")
        
        # Verificar saldo da conta origem
        if from_account and amount:
            if not from_account.can_debit(amount):
                raise serializers.ValidationError({
                    'from_account': f'Saldo insuficiente. Saldo atual: R$ {from_account.current_balance:.2f}'
                })
        
        return data