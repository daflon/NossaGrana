from rest_framework import serializers
from .models import Budget, BudgetAlert
from transactions.models import Category
from django.contrib.auth.models import User
from datetime import datetime
from decimal import Decimal


class BudgetSerializer(serializers.ModelSerializer):
    """
    Serializer para orçamentos com campos calculados
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    spent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percentage_used = serializers.FloatField(read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)
    is_near_limit = serializers.BooleanField(read_only=True)
    month_display = serializers.SerializerMethodField()
    
    # Novos campos calculados
    daily_average_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    projected_monthly_spending = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    projected_overspend = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    days_until_limit = serializers.IntegerField(read_only=True)
    spending_trend = serializers.CharField(read_only=True)
    alert_level = serializers.CharField(read_only=True)
    alert_message = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'category', 'category_name', 'category_color', 'category_icon',
            'amount', 'month', 'month_display', 'spent_amount', 'remaining_amount',
            'percentage_used', 'is_over_budget', 'is_near_limit',
            'daily_average_spent', 'projected_monthly_spending', 'projected_overspend',
            'days_until_limit', 'spending_trend', 'alert_level', 'alert_message',
            'recommendations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_month_display(self, obj):
        """
        Retorna o mês em formato brasileiro (MM/YYYY)
        """
        return obj.month.strftime('%m/%Y')

    def get_alert_message(self, obj):
        """
        Retorna mensagem de alerta personalizada
        """
        return obj.get_alert_message()

    def get_recommendations(self, obj):
        """
        Retorna recomendações baseadas na análise do orçamento
        """
        return obj.get_recommendations()

    def validate_amount(self, value):
        """
        Valida se o valor é positivo
        """
        if value <= 0:
            raise serializers.ValidationError("O valor do orçamento deve ser positivo.")
        return value

    def validate_month(self, value):
        """
        Valida se o mês é o primeiro dia do mês e não é passado
        """
        if value.day != 1:
            raise serializers.ValidationError("A data deve ser o primeiro dia do mês.")
        
        # Permitir mês atual e futuros
        current_month = datetime.now().date().replace(day=1)
        if value < current_month:
            raise serializers.ValidationError("Não é possível criar orçamentos para meses passados.")
        
        return value

    def validate(self, data):
        """
        Validação de unicidade por usuário/categoria/mês
        """
        user = self.context['request'].user
        category = data.get('category')
        month = data.get('month')

        # Verificar se já existe orçamento para esta categoria/mês
        existing_budget = Budget.objects.filter(
            user=user,
            category=category,
            month=month
        )

        # Se estamos editando, excluir o próprio orçamento da verificação
        if self.instance:
            existing_budget = existing_budget.exclude(pk=self.instance.pk)

        if existing_budget.exists():
            raise serializers.ValidationError(
                "Já existe um orçamento para esta categoria neste mês."
            )

        return data

    def create(self, validated_data):
        """
        Criar orçamento associado ao usuário logado
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BudgetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para criação de orçamentos
    """
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor do orçamento deve ser positivo.")
        return value

    def validate_month(self, value):
        if value.day != 1:
            raise serializers.ValidationError("A data deve ser o primeiro dia do mês.")
        
        current_month = datetime.now().date().replace(day=1)
        if value < current_month:
            raise serializers.ValidationError("Não é possível criar orçamentos para meses passados.")
        
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BudgetStatusSerializer(serializers.ModelSerializer):
    """
    Serializer para status dos orçamentos (usado no endpoint de status)
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    spent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percentage_used = serializers.FloatField(read_only=True)
    is_over_budget = serializers.BooleanField(read_only=True)
    is_near_limit = serializers.BooleanField(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'category_name', 'category_color', 'amount',
            'spent_amount', 'remaining_amount', 'percentage_used',
            'is_over_budget', 'is_near_limit', 'status'
        ]

    def get_status(self, obj):
        """
        Retorna o status do orçamento
        """
        if obj.is_over_budget:
            return 'exceeded'
        elif obj.is_near_limit:
            return 'warning'
        else:
            return 'ok'


class BudgetAlertSerializer(serializers.ModelSerializer):
    """
    Serializer para alertas de orçamento
    """
    budget_category = serializers.CharField(source='budget.category.name', read_only=True)
    budget_month = serializers.CharField(source='budget.month_display', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    alert_level_display = serializers.CharField(source='get_alert_level_display', read_only=True)

    class Meta:
        model = BudgetAlert
        fields = [
            'id', 'budget', 'budget_category', 'budget_month',
            'alert_type', 'alert_type_display', 'alert_level', 'alert_level_display',
            'message', 'is_active', 'created_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'created_at', 'resolved_at']


class BudgetProgressAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer detalhado para análise de progresso de orçamentos
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    
    # Campos básicos
    spent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percentage_used = serializers.FloatField(read_only=True)
    
    # Análise avançada
    daily_average_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    projected_monthly_spending = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    projected_overspend = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    days_until_limit = serializers.IntegerField(read_only=True)
    spending_trend = serializers.CharField(read_only=True)
    alert_level = serializers.CharField(read_only=True)
    
    # Alertas ativos
    active_alerts = BudgetAlertSerializer(source='alerts', many=True, read_only=True)
    alert_count = serializers.SerializerMethodField()
    
    # Análise textual
    alert_message = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()
    trend_analysis = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'category_name', 'category_color', 'amount', 'month',
            'spent_amount', 'remaining_amount', 'percentage_used',
            'daily_average_spent', 'projected_monthly_spending', 'projected_overspend',
            'days_until_limit', 'spending_trend', 'alert_level',
            'active_alerts', 'alert_count', 'alert_message', 'recommendations',
            'trend_analysis'
        ]

    def get_alert_count(self, obj):
        """
        Retorna o número de alertas ativos
        """
        return obj.alerts.filter(is_active=True).count()

    def get_alert_message(self, obj):
        """
        Retorna mensagem de alerta personalizada
        """
        return obj.get_alert_message()

    def get_recommendations(self, obj):
        """
        Retorna recomendações baseadas na análise do orçamento
        """
        return obj.get_recommendations()

    def get_trend_analysis(self, obj):
        """
        Retorna análise textual da tendência
        """
        trend = obj.spending_trend
        
        trend_messages = {
            'accelerating': 'Gastos estão acelerando - atenção redobrada necessária',
            'stable': 'Gastos mantêm ritmo constante',
            'decelerating': 'Gastos estão desacelerando - bom controle',
            'completed': 'Período do orçamento finalizado',
            'insufficient_data': 'Dados insuficientes para análise de tendência'
        }
        
        return trend_messages.get(trend, 'Tendência não identificada')