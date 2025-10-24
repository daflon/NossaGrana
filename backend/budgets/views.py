from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import datetime, date
from .models import Budget, BudgetAlert
from .serializers import (
    BudgetSerializer, BudgetCreateSerializer, BudgetStatusSerializer,
    BudgetAlertSerializer, BudgetProgressAnalysisSerializer
)
from transactions.models import Category


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para CRUD de orçamentos
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna orçamentos do usuário logado com filtros opcionais
        """
        queryset = Budget.objects.filter(user=self.request.user).select_related('category')
        
        # Filtro por mês
        month = self.request.query_params.get('month')
        if month:
            try:
                month_date = parse_date(f"{month}-01")
                if month_date:
                    queryset = queryset.filter(month=month_date)
            except ValueError:
                pass
        
        # Filtro por categoria
        category_id = self.request.query_params.get('category')
        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass
        
        # Filtro por status (exceeded, warning, ok)
        status_filter = self.request.query_params.get('status')
        if status_filter == 'exceeded':
            # Filtrar orçamentos excedidos (será calculado no serializer)
            pass
        elif status_filter == 'warning':
            # Filtrar orçamentos próximos do limite (será calculado no serializer)
            pass
        
        return queryset.order_by('-month', 'category__name')
    
    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na ação
        """
        if self.action == 'create':
            return BudgetCreateSerializer
        return BudgetSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Criar novo orçamento
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            budget = serializer.save()
            response_serializer = BudgetSerializer(budget, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': 'Erro ao criar orçamento', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Atualizar orçamento existente
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            budget = serializer.save()
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Erro ao atualizar orçamento', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Deletar orçamento
        """
        instance = self.get_object()
        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': 'Erro ao deletar orçamento', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def current_month(self, request):
        """
        Retorna orçamentos do mês atual
        """
        current_month = date.today().replace(day=1)
        budgets = self.get_queryset().filter(month=current_month)
        serializer = self.get_serializer(budgets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories_without_budget(self, request):
        """
        Retorna categorias que não possuem orçamento no mês especificado
        """
        month = request.query_params.get('month')
        if not month:
            month = date.today().strftime('%Y-%m')
        
        try:
            month_date = parse_date(f"{month}-01")
            if not month_date:
                return Response(
                    {'error': 'Formato de mês inválido. Use YYYY-MM'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Formato de mês inválido. Use YYYY-MM'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Categorias que já possuem orçamento neste mês
        budgeted_categories = Budget.objects.filter(
            user=request.user,
            month=month_date
        ).values_list('category_id', flat=True)
        
        # Categorias disponíveis sem orçamento
        available_categories = Category.objects.exclude(
            id__in=budgeted_categories
        ).values('id', 'name', 'color', 'icon')
        
        return Response(list(available_categories))

    @action(detail=False, methods=['get'])
    def progress_analysis(self, request):
        """
        Retorna análise detalhada de progresso dos orçamentos
        """
        month = request.query_params.get('month')
        if not month:
            month_date = date.today().replace(day=1)
        else:
            try:
                month_date = parse_date(f"{month}-01")
                if not month_date:
                    return Response(
                        {'error': 'Formato de mês inválido. Use YYYY-MM'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Formato de mês inválido. Use YYYY-MM'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        budgets = Budget.objects.filter(
            user=request.user,
            month=month_date
        ).select_related('category').prefetch_related('alerts')
        
        # Gerar alertas automáticos para todos os orçamentos
        for budget in budgets:
            BudgetAlert.check_and_create_alerts(budget)
        
        serializer = BudgetProgressAnalysisSerializer(budgets, many=True)
        
        return Response({
            'month': month_date.strftime('%Y-%m'),
            'month_display': month_date.strftime('%m/%Y'),
            'budgets': serializer.data,
            'analysis_timestamp': datetime.now().isoformat()
        })

    @action(detail=True, methods=['post'])
    def generate_alerts(self, request, pk=None):
        """
        Gera alertas automáticos para um orçamento específico
        """
        budget = self.get_object()
        alerts = BudgetAlert.check_and_create_alerts(budget)
        
        serializer = BudgetAlertSerializer(alerts, many=True)
        
        return Response({
            'budget_id': budget.id,
            'alerts_generated': len(alerts),
            'alerts': serializer.data
        })

    @action(detail=False, methods=['post'])
    def generate_all_alerts(self, request):
        """
        Gera alertas automáticos para todos os orçamentos do usuário
        """
        month = request.data.get('month')
        if month:
            try:
                month_date = parse_date(f"{month}-01")
                budgets = Budget.objects.filter(user=request.user, month=month_date)
            except ValueError:
                return Response(
                    {'error': 'Formato de mês inválido. Use YYYY-MM'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Gerar para orçamentos do mês atual
            current_month = date.today().replace(day=1)
            budgets = Budget.objects.filter(user=request.user, month=current_month)
        
        all_alerts = []
        for budget in budgets:
            alerts = BudgetAlert.check_and_create_alerts(budget)
            all_alerts.extend(alerts)
        
        serializer = BudgetAlertSerializer(all_alerts, many=True)
        
        return Response({
            'budgets_processed': len(budgets),
            'total_alerts_generated': len(all_alerts),
            'alerts': serializer.data
        })


class BudgetStatusView(APIView):
    """
    View para obter status consolidado dos orçamentos
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna status dos orçamentos do mês atual ou especificado
        """
        month = request.query_params.get('month')
        if not month:
            month_date = date.today().replace(day=1)
        else:
            try:
                month_date = parse_date(f"{month}-01")
                if not month_date:
                    return Response(
                        {'error': 'Formato de mês inválido. Use YYYY-MM'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {'error': 'Formato de mês inválido. Use YYYY-MM'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        budgets = Budget.objects.filter(
            user=request.user,
            month=month_date
        ).select_related('category')
        
        serializer = BudgetStatusSerializer(budgets, many=True)
        
        # Calcular estatísticas gerais
        total_budgeted = sum(budget.amount for budget in budgets)
        total_spent = sum(budget.spent_amount for budget in budgets)
        budgets_exceeded = sum(1 for budget in budgets if budget.is_over_budget)
        budgets_warning = sum(1 for budget in budgets if budget.is_near_limit and not budget.is_over_budget)
        
        response_data = {
            'month': month_date.strftime('%Y-%m'),
            'month_display': month_date.strftime('%m/%Y'),
            'summary': {
                'total_budgets': len(budgets),
                'total_budgeted': total_budgeted,
                'total_spent': total_spent,
                'total_remaining': total_budgeted - total_spent,
                'budgets_exceeded': budgets_exceeded,
                'budgets_warning': budgets_warning,
                'budgets_ok': len(budgets) - budgets_exceeded - budgets_warning,
            },
            'budgets': serializer.data
        }
        
        return Response(response_data)


class BudgetAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualizar alertas de orçamento
    """
    serializer_class = BudgetAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna alertas dos orçamentos do usuário logado
        """
        queryset = BudgetAlert.objects.filter(
            budget__user=self.request.user
        ).select_related('budget', 'budget__category')

        # Filtro por status ativo/inativo
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active_bool)

        # Filtro por tipo de alerta
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)

        # Filtro por nível de alerta
        alert_level = self.request.query_params.get('alert_level')
        if alert_level:
            queryset = queryset.filter(alert_level=alert_level)

        # Filtro por mês do orçamento
        month = self.request.query_params.get('month')
        if month:
            try:
                month_date = parse_date(f"{month}-01")
                if month_date:
                    queryset = queryset.filter(budget__month=month_date)
            except ValueError:
                pass

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Marca um alerta como resolvido
        """
        alert = self.get_object()
        alert.resolve()
        
        serializer = self.get_serializer(alert)
        return Response({
            'message': 'Alerta marcado como resolvido',
            'alert': serializer.data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retorna resumo dos alertas do usuário
        """
        queryset = self.get_queryset()
        
        # Contar alertas por nível
        alert_counts = {
            'critical': queryset.filter(alert_level='critical', is_active=True).count(),
            'high': queryset.filter(alert_level='high', is_active=True).count(),
            'medium': queryset.filter(alert_level='medium', is_active=True).count(),
            'low': queryset.filter(alert_level='low', is_active=True).count(),
        }
        
        # Contar alertas por tipo
        alert_types = {
            'over_budget': queryset.filter(alert_type='over_budget', is_active=True).count(),
            'near_limit': queryset.filter(alert_type='near_limit', is_active=True).count(),
            'projection_warning': queryset.filter(alert_type='projection_warning', is_active=True).count(),
            'trend_warning': queryset.filter(alert_type='trend_warning', is_active=True).count(),
        }
        
        total_active = queryset.filter(is_active=True).count()
        total_resolved = queryset.filter(is_active=False).count()
        
        return Response({
            'total_active_alerts': total_active,
            'total_resolved_alerts': total_resolved,
            'alerts_by_level': alert_counts,
            'alerts_by_type': alert_types,
            'most_recent_alerts': BudgetAlertSerializer(
                queryset.filter(is_active=True)[:5], many=True
            ).data
        })