from rest_framework import serializers
from django.db import models
from .models import Goal, GoalContribution
from financial_accounts.models import Account
from django.contrib.auth.models import User
from datetime import datetime, date
from decimal import Decimal


class GoalContributionSerializer(serializers.ModelSerializer):
    """
    Serializer para contribuições de metas
    """
    source_account_name = serializers.CharField(source='source_account.name', read_only=True)
    is_withdrawal = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = GoalContribution
        fields = [
            'id', 'amount', 'description', 'date', 'source_account', 
            'source_account_name', 'is_withdrawal', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("O valor não pode ser zero.")
        return value


class GoalSerializer(serializers.ModelSerializer):
    """
    Serializer completo para metas
    """
    # Campos calculados
    progress_percentage = serializers.FloatField(read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    months_remaining = serializers.FloatField(read_only=True)
    required_monthly_contribution = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_track = serializers.BooleanField(read_only=True)
    performance_status = serializers.CharField(read_only=True)
    
    # Campos de relacionamento
    linked_account_name = serializers.CharField(source='linked_account.name', read_only=True)
    goal_type_display = serializers.CharField(source='get_goal_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Contribuições recentes
    recent_contributions = GoalContributionSerializer(source='contributions', many=True, read_only=True)
    contributions_count = serializers.SerializerMethodField()
    total_contributed = serializers.SerializerMethodField()
    

    
    # Recomendações
    recommendations = serializers.SerializerMethodField()
    
    # Formatação de datas
    start_date_display = serializers.SerializerMethodField()
    target_date_display = serializers.SerializerMethodField()
    completed_date_display = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'description', 'goal_type', 'goal_type_display',
            'priority', 'priority_display', 'target_amount', 'current_amount',
            'start_date', 'start_date_display', 'target_date', 'target_date_display',
            'completed_date', 'completed_date_display', 'monthly_contribution',
            'auto_contribution', 'linked_account', 'linked_account_name',
            'status', 'status_display', 'notify_milestones', 'notify_deadline',
            'progress_percentage', 'remaining_amount', 'is_completed',
            'days_remaining', 'months_remaining', 'required_monthly_contribution',
            'is_on_track', 'performance_status', 'recent_contributions',
            'contributions_count', 'total_contributed',
            'recommendations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_date']

    def get_contributions_count(self, obj):
        """Retorna o número total de contribuições"""
        return obj.contributions.count()

    def get_total_contributed(self, obj):
        """Retorna o total contribuído (soma de todas as contribuições positivas)"""
        total = obj.contributions.filter(amount__gt=0).aggregate(
            total=models.Sum('amount')
        )['total']
        return total or Decimal('0.00')



    def get_recommendations(self, obj):
        """Retorna recomendações para a meta"""
        return obj.get_recommendations()

    def get_start_date_display(self, obj):
        """Retorna data de início formatada"""
        return obj.start_date.strftime('%d/%m/%Y') if obj.start_date else None

    def get_target_date_display(self, obj):
        """Retorna data meta formatada"""
        return obj.target_date.strftime('%d/%m/%Y') if obj.target_date else None

    def get_completed_date_display(self, obj):
        """Retorna data de conclusão formatada"""
        return obj.completed_date.strftime('%d/%m/%Y') if obj.completed_date else None

    def validate_target_amount(self, value):
        """Valida o valor da meta"""
        if value <= 0:
            raise serializers.ValidationError("O valor da meta deve ser positivo.")
        return value

    def validate_monthly_contribution(self, value):
        """Valida a contribuição mensal"""
        if value < 0:
            raise serializers.ValidationError("A contribuição mensal não pode ser negativa.")
        return value

    def validate_target_date(self, value):
        """Valida a data meta"""
        if value <= date.today():
            raise serializers.ValidationError("A data meta deve ser futura.")
        return value

    def validate(self, data):
        """Validações gerais"""
        start_date = data.get('start_date', getattr(self.instance, 'start_date', None))
        target_date = data.get('target_date')
        
        if start_date and target_date and start_date >= target_date:
            raise serializers.ValidationError({
                'target_date': 'A data meta deve ser posterior à data de início.'
            })
        
        # Validar conta vinculada pertence ao usuário
        linked_account = data.get('linked_account')
        if linked_account:
            user = self.context['request'].user
            if linked_account.user != user:
                raise serializers.ValidationError({
                    'linked_account': 'A conta selecionada não pertence ao usuário.'
                })
        
        return data

    def create(self, validated_data):
        """Criar meta associada ao usuário logado"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def to_representation(self, instance):
        """Customizar representação dos dados"""
        data = super().to_representation(instance)
        
        # Limitar contribuições recentes a 5
        if 'recent_contributions' in data:
            data['recent_contributions'] = data['recent_contributions'][:5]
        
        return data


class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para criação de metas
    """
    class Meta:
        model = Goal
        fields = [
            'title', 'description', 'goal_type', 'priority', 'target_amount',
            'target_date', 'monthly_contribution', 'linked_account',
            'notify_milestones', 'notify_deadline'
        ]

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor da meta deve ser positivo.")
        return value

    def validate_target_date(self, value):
        if value <= date.today():
            raise serializers.ValidationError("A data meta deve ser futura.")
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class GoalSummarySerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listagens
    """
    progress_percentage = serializers.FloatField(read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    performance_status = serializers.CharField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    goal_type_display = serializers.CharField(source='get_goal_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'goal_type', 'goal_type_display', 'target_amount',
            'current_amount', 'target_date', 'status', 'status_display',
            'progress_percentage', 'remaining_amount', 'performance_status',
            'days_remaining'
        ]


class GoalContributionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criar contribuições
    """
    class Meta:
        model = GoalContribution
        fields = ['amount', 'description', 'date', 'source_account']

    def validate_amount(self, value):
        if value == 0:
            raise serializers.ValidationError("O valor não pode ser zero.")
        return value

    def validate(self, data):
        # Validar conta de origem pertence ao usuário
        source_account = data.get('source_account')
        if source_account:
            user = self.context['request'].user
            if source_account.user != user:
                raise serializers.ValidationError({
                    'source_account': 'A conta selecionada não pertence ao usuário.'
                })
        
        return data


class GoalAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer para análise detalhada de metas
    """
    # Todos os campos calculados
    progress_percentage = serializers.FloatField(read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    months_remaining = serializers.FloatField(read_only=True)
    required_monthly_contribution = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_track = serializers.BooleanField(read_only=True)
    performance_status = serializers.CharField(read_only=True)
    
    # Análises avançadas
    projection = serializers.SerializerMethodField()
    milestone_progress = serializers.SerializerMethodField()
    contribution_analysis = serializers.SerializerMethodField()
    recommendations = serializers.SerializerMethodField()
    
    # Estatísticas
    total_contributed = serializers.SerializerMethodField()
    average_monthly_contribution = serializers.SerializerMethodField()
    contributions_count = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'goal_type', 'priority', 'target_amount', 'current_amount',
            'start_date', 'target_date', 'status', 'progress_percentage',
            'remaining_amount', 'is_completed', 'days_remaining', 'months_remaining',
            'required_monthly_contribution', 'is_on_track', 'performance_status',
            'projection', 'milestone_progress', 'contribution_analysis',
            'recommendations', 'total_contributed', 'average_monthly_contribution',
            'contributions_count'
        ]

    def get_projection(self, obj):
        """Retorna projeção de conclusão da meta"""
        return obj.calculate_projection()

    def get_milestone_progress(self, obj):
        """Retorna progresso dos marcos"""
        current = obj.progress_percentage
        milestones = [25, 50, 75, 100]
        
        progress = []
        for milestone in milestones:
            progress.append({
                'percentage': milestone,
                'achieved': current >= milestone,
                'amount_needed': float(obj.target_amount * Decimal(str(milestone / 100))),
                'remaining_to_milestone': max(0, float(obj.target_amount * Decimal(str(milestone / 100)) - obj.current_amount))
            })
        
        return progress

    def get_contribution_analysis(self, obj):
        """Retorna análise das contribuições"""
        from django.db.models import Sum, Avg, Count
        from datetime import datetime, timedelta
        
        contributions = obj.contributions.filter(amount__gt=0)
        
        # Últimos 6 meses
        six_months_ago = datetime.now().date() - timedelta(days=180)
        recent_contributions = contributions.filter(date__gte=six_months_ago)
        
        return {
            'total_contributions': contributions.count(),
            'total_amount': contributions.aggregate(Sum('amount'))['amount__sum'] or 0,
            'average_amount': contributions.aggregate(Avg('amount'))['amount__avg'] or 0,
            'recent_contributions_count': recent_contributions.count(),
            'recent_total_amount': recent_contributions.aggregate(Sum('amount'))['amount__sum'] or 0,
            'largest_contribution': contributions.aggregate(models.Max('amount'))['amount__max'] or 0,
            'smallest_contribution': contributions.aggregate(models.Min('amount'))['amount__min'] or 0,
        }

    def get_recommendations(self, obj):
        """Retorna recomendações detalhadas"""
        return obj.get_recommendations()

    def get_total_contributed(self, obj):
        """Total contribuído"""
        return obj.contributions.filter(amount__gt=0).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')

    def get_average_monthly_contribution(self, obj):
        """Média mensal de contribuições"""
        from django.db.models import Sum
        from datetime import datetime
        
        # Calcular meses desde o início
        start_date = obj.start_date
        current_date = datetime.now().date()
        months_elapsed = max(1, (current_date.year - start_date.year) * 12 + current_date.month - start_date.month)
        
        total_contributed = obj.contributions.filter(amount__gt=0).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        return total_contributed / months_elapsed

    def get_contributions_count(self, obj):
        """Número total de contribuições"""
        return obj.contributions.count()


class ContributeToGoalSerializer(serializers.Serializer):
    """
    Serializer para contribuir para uma meta
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    description = serializers.CharField(max_length=200, required=False, allow_blank=True)
    date = serializers.DateField(required=False)
    source_account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.none(),
        required=False,
        allow_null=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'context' in kwargs and 'request' in kwargs['context']:
            user = kwargs['context']['request'].user
            self.fields['source_account'].queryset = Account.objects.filter(user=user)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor deve ser positivo.")
        return value

    def validate_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data não pode ser futura.")
        return value or date.today()

    def validate(self, data):
        goal = self.context.get('goal')
        if goal and goal.status == 'completed':
            raise serializers.ValidationError("Não é possível contribuir para uma meta já concluída.")
        return data

    def save(self, goal):
        amount = self.validated_data['amount']
        description = self.validated_data.get('description', 'Contribuição para meta')
        contribution_date = self.validated_data.get('date', date.today())
        source_account = self.validated_data.get('source_account')
        
        # Usar o método add_contribution do modelo
        contribution = goal.add_contribution(
            amount=amount,
            description=description,
            source_account=source_account
        )
        
        # Atualizar a data se fornecida
        if contribution_date != date.today():
            contribution.date = contribution_date
            contribution.save()
        
        return {
            'contribution': contribution,
            'goal': goal,
            'was_completed': goal.is_completed
        }