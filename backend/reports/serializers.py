from rest_framework import serializers
from django.db.models import Sum, Count, Avg, Q
from django.contrib.auth.models import User
from transactions.models import Transaction, Category
from budgets.models import Budget
from datetime import datetime, timedelta
from decimal import Decimal
import calendar


class FinancialSummarySerializer(serializers.Serializer):
    """
    Serializer para resumo financeiro geral
    """
    period = serializers.CharField(read_only=True)
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_expense = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    transaction_count = serializers.IntegerField(read_only=True)
    average_transaction = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Comparativos
    income_change = serializers.FloatField(read_only=True)
    expense_change = serializers.FloatField(read_only=True)
    balance_change = serializers.FloatField(read_only=True)
    
    # Insights
    savings_rate = serializers.FloatField(read_only=True)
    expense_ratio = serializers.FloatField(read_only=True)


class CategoryBreakdownSerializer(serializers.Serializer):
    """
    Serializer para breakdown por categoria
    """
    category_id = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(read_only=True)
    category_color = serializers.CharField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    transaction_count = serializers.IntegerField(read_only=True)
    percentage = serializers.FloatField(read_only=True)
    average_transaction = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Comparativo com período anterior
    amount_change = serializers.FloatField(read_only=True)
    trend = serializers.CharField(read_only=True)  # 'up', 'down', 'stable'


class MonthlyTrendSerializer(serializers.Serializer):
    """
    Serializer para tendências mensais
    """
    month = serializers.CharField(read_only=True)
    year = serializers.IntegerField(read_only=True)
    month_name = serializers.CharField(read_only=True)
    total_income = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_expense = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    transaction_count = serializers.IntegerField(read_only=True)
    
    # Análises
    savings_rate = serializers.FloatField(read_only=True)
    expense_growth = serializers.FloatField(read_only=True)
    income_growth = serializers.FloatField(read_only=True)


class SpendingPatternSerializer(serializers.Serializer):
    """
    Serializer para padrões de gastos
    """
    pattern_type = serializers.CharField(read_only=True)  # 'daily', 'weekly', 'monthly'
    period_label = serializers.CharField(read_only=True)
    average_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    transaction_count = serializers.IntegerField(read_only=True)
    peak_day = serializers.CharField(read_only=True)
    peak_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)


class FinancialInsightSerializer(serializers.Serializer):
    """
    Serializer para insights financeiros automáticos
    """
    insight_type = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    impact_level = serializers.CharField(read_only=True)  # 'low', 'medium', 'high'
    category = serializers.CharField(read_only=True)
    value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percentage = serializers.FloatField(read_only=True)
    recommendation = serializers.CharField(read_only=True)


class BudgetPerformanceSerializer(serializers.Serializer):
    """
    Serializer para performance de orçamentos
    """
    category_name = serializers.CharField(read_only=True)
    category_color = serializers.CharField(read_only=True)
    budgeted_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    spent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percentage_used = serializers.FloatField(read_only=True)
    performance_score = serializers.FloatField(read_only=True)  # 0-100
    status = serializers.CharField(read_only=True)  # 'excellent', 'good', 'warning', 'critical'
    
    # Comparativo
    vs_last_month = serializers.FloatField(read_only=True)
    trend = serializers.CharField(read_only=True)


class PredictionSerializer(serializers.Serializer):
    """
    Serializer para previsões financeiras
    """
    prediction_type = serializers.CharField(read_only=True)  # 'monthly_expense', 'budget_exhaustion', 'savings_goal'
    period = serializers.CharField(read_only=True)
    predicted_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    confidence_level = serializers.FloatField(read_only=True)  # 0-100
    based_on_data = serializers.CharField(read_only=True)
    factors = serializers.ListField(child=serializers.CharField(), read_only=True)
    recommendation = serializers.CharField(read_only=True)


class ComparisonReportSerializer(serializers.Serializer):
    """
    Serializer para relatórios comparativos
    """
    comparison_type = serializers.CharField(read_only=True)  # 'month_over_month', 'year_over_year'
    current_period = serializers.CharField(read_only=True)
    previous_period = serializers.CharField(read_only=True)
    
    current_income = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    previous_income = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    income_change = serializers.FloatField(read_only=True)
    
    current_expense = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    previous_expense = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    expense_change = serializers.FloatField(read_only=True)
    
    current_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    previous_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    balance_change = serializers.FloatField(read_only=True)
    
    # Análise
    overall_trend = serializers.CharField(read_only=True)  # 'improving', 'declining', 'stable'
    key_changes = serializers.ListField(child=serializers.CharField(), read_only=True)


class ExportReportSerializer(serializers.Serializer):
    """
    Serializer para configuração de exportação de relatórios
    """
    report_type = serializers.ChoiceField(choices=[
        ('summary', 'Resumo Financeiro'),
        ('detailed', 'Relatório Detalhado'),
        ('category_breakdown', 'Breakdown por Categoria'),
        ('monthly_trend', 'Tendência Mensal'),
        ('budget_performance', 'Performance de Orçamentos'),
        ('comparison', 'Relatório Comparativo'),
    ])
    format = serializers.ChoiceField(choices=[
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ], default='pdf')
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    include_charts = serializers.BooleanField(default=True)
    include_insights = serializers.BooleanField(default=True)
    categories = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="IDs das categorias a incluir (opcional)"
    )