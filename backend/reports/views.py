from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Sum, Count, Avg, Q, F, Case, When
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import calendar

from transactions.models import Transaction, Category
from budgets.models import Budget
from .serializers import (
    FinancialSummarySerializer, CategoryBreakdownSerializer, 
    MonthlyTrendSerializer, SpendingPatternSerializer,
    FinancialInsightSerializer, BudgetPerformanceSerializer,
    PredictionSerializer, ComparisonReportSerializer
)


class SummaryReportView(APIView):
    """
    View para relatório de resumo financeiro
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Parâmetros de filtro
        period = request.query_params.get('period', 'current_month')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Definir período
        if date_from and date_to:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            period_label = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
        else:
            start_date, end_date, period_label = self._get_period_dates(period)
        
        # Query base
        transactions = Transaction.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calcular métricas principais
        income_total = transactions.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        expense_total = transactions.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        net_balance = income_total - expense_total
        transaction_count = transactions.count()
        
        average_transaction = Decimal('0.00')
        if transaction_count > 0:
            total_amount = income_total + expense_total
            average_transaction = total_amount / transaction_count
        
        # Calcular comparativos com período anterior
        prev_start, prev_end, _ = self._get_previous_period(start_date, end_date)
        prev_transactions = Transaction.objects.filter(
            user=request.user,
            date__gte=prev_start,
            date__lte=prev_end
        )
        
        prev_income = prev_transactions.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        prev_expense = prev_transactions.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        prev_balance = prev_income - prev_expense
        
        # Calcular mudanças percentuais
        income_change = self._calculate_percentage_change(prev_income, income_total)
        expense_change = self._calculate_percentage_change(prev_expense, expense_total)
        balance_change = self._calculate_percentage_change(prev_balance, net_balance)
        
        # Calcular insights
        savings_rate = 0.0
        expense_ratio = 0.0
        
        if income_total > 0:
            savings_rate = float((net_balance / income_total) * 100)
            expense_ratio = float((expense_total / income_total) * 100)
        
        summary_data = {
            'period': period_label,
            'total_income': income_total,
            'total_expense': expense_total,
            'net_balance': net_balance,
            'transaction_count': transaction_count,
            'average_transaction': average_transaction,
            'income_change': income_change,
            'expense_change': expense_change,
            'balance_change': balance_change,
            'savings_rate': savings_rate,
            'expense_ratio': expense_ratio
        }
        
        serializer = FinancialSummarySerializer(summary_data)
        return Response(serializer.data)

    def _get_period_dates(self, period):
        """
        Retorna as datas de início e fim baseado no período
        """
        today = timezone.now().date()
        
        if period == 'current_month':
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            period_label = today.strftime('%B %Y')
            
        elif period == 'last_month':
            if today.month == 1:
                start_date = today.replace(year=today.year - 1, month=12, day=1)
                end_date = today.replace(day=1) - timedelta(days=1)
            else:
                start_date = today.replace(month=today.month - 1, day=1)
                end_date = today.replace(day=1) - timedelta(days=1)
            period_label = start_date.strftime('%B %Y')
            
        elif period == 'current_year':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
            period_label = str(today.year)
            
        elif period == 'last_30_days':
            end_date = today
            start_date = today - timedelta(days=30)
            period_label = 'Últimos 30 dias'
            
        elif period == 'last_90_days':
            end_date = today
            start_date = today - timedelta(days=90)
            period_label = 'Últimos 90 dias'
            
        else:  # current_month como padrão
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
            period_label = today.strftime('%B %Y')
        
        return start_date, end_date, period_label

    def _get_previous_period(self, start_date, end_date):
        """
        Retorna o período anterior para comparação
        """
        period_length = (end_date - start_date).days + 1
        prev_end = start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=period_length - 1)
        period_label = f"{prev_start.strftime('%d/%m/%Y')} - {prev_end.strftime('%d/%m/%Y')}"
        
        return prev_start, prev_end, period_label

    def _calculate_percentage_change(self, old_value, new_value):
        """
        Calcula a mudança percentual
        """
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        
        return float(((new_value - old_value) / old_value) * 100)


class CategoryBreakdownView(APIView):
    """
    View para breakdown de gastos por categoria
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Parâmetros de filtro
        period = request.query_params.get('period', 'current_month')
        transaction_type = request.query_params.get('type', 'expense')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Definir período
        if date_from and date_to:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            start_date, end_date, _ = self._get_period_dates(period)
        
        # Query base
        transactions = Transaction.objects.filter(
            user=request.user,
            type=transaction_type,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Período anterior para comparação
        prev_start, prev_end, _ = self._get_previous_period(start_date, end_date)
        
        # Query otimizada: buscar ambos os períodos em uma única consulta
        category_data = Transaction.objects.filter(
            user=request.user,
            type=transaction_type,
            date__gte=prev_start,
            date__lte=end_date
        ).values(
            'category__id',
            'category__name', 
            'category__color'
        ).annotate(
            # Período atual
            current_total=Sum(
                Case(
                    When(date__gte=start_date, then='amount'),
                    default=0
                )
            ),
            current_count=Count(
                Case(
                    When(date__gte=start_date, then='id'),
                    default=None
                )
            ),
            # Período anterior
            previous_total=Sum(
                Case(
                    When(date__lt=start_date, then='amount'),
                    default=0
                )
            ),
            # Média do período atual
            average_transaction=Avg(
                Case(
                    When(date__gte=start_date, then='amount'),
                    default=None
                )
            )
        ).filter(current_total__gt=0).order_by('-current_total')
        
        # Calcular total geral para percentuais
        total_general = sum(item['current_total'] for item in category_data)
        
        # Processar dados otimizados
        breakdown_data = []
        for item in category_data:
            current_amount = item['current_total']
            prev_amount = item['previous_total'] or Decimal('0.00')
            
            # Calcular mudança
            amount_change = self._calculate_percentage_change(prev_amount, current_amount)
            
            # Determinar tendência
            if amount_change > 10:
                trend = 'up'
            elif amount_change < -10:
                trend = 'down'
            else:
                trend = 'stable'
            
            # Calcular percentual
            percentage = 0.0
            if total_general > 0:
                percentage = float((current_amount / total_general) * 100)
            
            breakdown_data.append({
                'category_id': item['category__id'],
                'category_name': item['category__name'],
                'category_color': item['category__color'],
                'total_amount': current_amount,
                'transaction_count': item['current_count'],
                'percentage': percentage,
                'average_transaction': item['average_transaction'] or Decimal('0.00'),
                'amount_change': amount_change,
                'trend': trend
            })
        
        serializer = CategoryBreakdownSerializer(breakdown_data, many=True)
        return Response(serializer.data)

    def _get_period_dates(self, period):
        """
        Reutiliza a mesma lógica da SummaryReportView
        """
        summary_view = SummaryReportView()
        return summary_view._get_period_dates(period)

    def _get_previous_period(self, start_date, end_date):
        """
        Reutiliza a mesma lógica da SummaryReportView
        """
        summary_view = SummaryReportView()
        return summary_view._get_previous_period(start_date, end_date)

    def _calculate_percentage_change(self, old_value, new_value):
        """
        Reutiliza a mesma lógica da SummaryReportView
        """
        summary_view = SummaryReportView()
        return summary_view._calculate_percentage_change(old_value, new_value)


class MonthlyTrendView(APIView):
    """
    View para análise de tendências mensais
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Parâmetros
        months_back = int(request.query_params.get('months', 12))
        
        # Data de início (X meses atrás)
        today = timezone.now().date()
        start_date = today.replace(day=1) - timedelta(days=30 * months_back)
        start_date = start_date.replace(day=1)
        
        # Query base
        transactions = Transaction.objects.filter(
            user=request.user,
            date__gte=start_date
        )
        
        # Agrupar por mês
        monthly_data = transactions.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total_income=Sum('amount', filter=Q(type='income')),
            total_expense=Sum('amount', filter=Q(type='expense')),
            transaction_count=Count('id')
        ).order_by('month')
        
        # Processar dados
        trend_data = []
        prev_income = Decimal('0.00')
        prev_expense = Decimal('0.00')
        
        for item in monthly_data:
            month_date = item['month']
            total_income = item['total_income'] or Decimal('0.00')
            total_expense = item['total_expense'] or Decimal('0.00')
            net_balance = total_income - total_expense
            
            # Calcular taxa de poupança
            savings_rate = 0.0
            if total_income > 0:
                savings_rate = float((net_balance / total_income) * 100)
            
            # Calcular crescimento
            income_growth = self._calculate_percentage_change(prev_income, total_income)
            expense_growth = self._calculate_percentage_change(prev_expense, total_expense)
            
            trend_data.append({
                'month': month_date.strftime('%Y-%m'),
                'year': month_date.year,
                'month_name': month_date.strftime('%B %Y'),
                'total_income': total_income,
                'total_expense': total_expense,
                'net_balance': net_balance,
                'transaction_count': item['transaction_count'],
                'savings_rate': savings_rate,
                'expense_growth': expense_growth,
                'income_growth': income_growth
            })
            
            prev_income = total_income
            prev_expense = total_expense
        
        serializer = MonthlyTrendSerializer(trend_data, many=True)
        return Response(serializer.data)

    def _calculate_percentage_change(self, old_value, new_value):
        """
        Reutiliza a mesma lógica da SummaryReportView
        """
        summary_view = SummaryReportView()
        return summary_view._calculate_percentage_change(old_value, new_value)


class SpendingPatternsView(APIView):
    """
    View para análise de padrões de gastos
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pattern_type = request.query_params.get('type', 'weekly')
        period = request.query_params.get('period', 'last_90_days')
        
        # Definir período
        today = timezone.now().date()
        if period == 'last_30_days':
            start_date = today - timedelta(days=30)
        elif period == 'last_90_days':
            start_date = today - timedelta(days=90)
        elif period == 'current_year':
            start_date = today.replace(month=1, day=1)
        else:
            start_date = today - timedelta(days=90)
        
        # Query base
        transactions = Transaction.objects.filter(
            user=request.user,
            type='expense',
            date__gte=start_date,
            date__lte=today
        )
        
        if pattern_type == 'daily':
            # Padrão por dia da semana
            pattern_data = self._analyze_daily_patterns(transactions)
        elif pattern_type == 'weekly':
            # Padrão semanal
            pattern_data = self._analyze_weekly_patterns(transactions)
        else:
            # Padrão mensal
            pattern_data = self._analyze_monthly_patterns(transactions)
        
        serializer = SpendingPatternSerializer(pattern_data, many=True)
        return Response(serializer.data)

    def _analyze_daily_patterns(self, transactions):
        """
        Analisa padrões por dia da semana
        """
        from django.db.models.functions import Extract
        
        daily_data = transactions.annotate(
            weekday=Extract('date__week_day')
        ).values('weekday').annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            average_amount=Avg('amount')
        ).order_by('weekday')
        
        weekdays = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        
        patterns = []
        peak_amount = Decimal('0.00')
        peak_day = ''
        
        for item in daily_data:
            weekday_name = weekdays[item['weekday'] - 1]
            if item['total_amount'] > peak_amount:
                peak_amount = item['total_amount']
                peak_day = weekday_name
            
            patterns.append({
                'pattern_type': 'daily',
                'period_label': weekday_name,
                'average_amount': item['average_amount'],
                'transaction_count': item['transaction_count'],
                'peak_day': peak_day,
                'peak_amount': peak_amount
            })
        
        return patterns

    def _analyze_weekly_patterns(self, transactions):
        """
        Analisa padrões semanais
        """
        weekly_data = transactions.annotate(
            week=TruncWeek('date')
        ).values('week').annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            average_amount=Avg('amount')
        ).order_by('week')
        
        patterns = []
        peak_amount = Decimal('0.00')
        peak_week = ''
        
        for item in weekly_data:
            week_label = f"Semana de {item['week'].strftime('%d/%m')}"
            if item['total_amount'] > peak_amount:
                peak_amount = item['total_amount']
                peak_week = week_label
            
            patterns.append({
                'pattern_type': 'weekly',
                'period_label': week_label,
                'average_amount': item['average_amount'],
                'transaction_count': item['transaction_count'],
                'peak_day': peak_week,
                'peak_amount': peak_amount
            })
        
        return patterns

    def _analyze_monthly_patterns(self, transactions):
        """
        Analisa padrões mensais
        """
        monthly_data = transactions.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            average_amount=Avg('amount')
        ).order_by('month')
        
        patterns = []
        peak_amount = Decimal('0.00')
        peak_month = ''
        
        for item in monthly_data:
            month_label = item['month'].strftime('%B %Y')
            if item['total_amount'] > peak_amount:
                peak_amount = item['total_amount']
                peak_month = month_label
            
            patterns.append({
                'pattern_type': 'monthly',
                'period_label': month_label,
                'average_amount': item['average_amount'],
                'transaction_count': item['transaction_count'],
                'peak_day': peak_month,
                'peak_amount': peak_amount
            })
        
        return patterns


class ExportReportView(APIView):
    """
    View para exportação de relatórios (placeholder para implementação futura)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': 'Funcionalidade de exportação será implementada na próxima fase',
            'available_formats': ['pdf', 'excel', 'csv'],
            'available_reports': [
                'summary', 'detailed', 'category_breakdown', 
                'monthly_trend', 'budget_performance', 'comparison'
            ]
        })