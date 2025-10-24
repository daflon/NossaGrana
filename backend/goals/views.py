from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Goal, GoalContribution
from .serializers import (
    GoalSerializer, GoalContributionSerializer, GoalSummarySerializer,
    ContributeToGoalSerializer
)


class GoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar metas de poupança
    """
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retornar apenas metas do usuário autenticado"""
        return Goal.objects.filter(user=self.request.user).prefetch_related('contributions')

    def perform_create(self, serializer):
        """Associar meta ao usuário autenticado"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
        """
        Adicionar contribuição a uma meta
        """
        goal = self.get_object()
        
        if goal.achieved:
            return Response(
                {'error': 'Não é possível contribuir para uma meta já atingida.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ContributeToGoalSerializer(
            data=request.data,
            context={'goal': goal}
        )
        
        if serializer.is_valid():
            result = serializer.save(goal=goal)
            
            response_data = {
                'message': 'Contribuição adicionada com sucesso!',
                'contribution': GoalContributionSerializer(result['contribution']).data,
                'goal': GoalSerializer(result['goal']).data,
                'goal_achieved': result['was_achieved']
            }
            
            if result['was_achieved']:
                response_data['message'] = '🎉 Parabéns! Você atingiu sua meta!'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def contributions(self, request, pk=None):
        """
        Listar contribuições de uma meta
        """
        goal = self.get_object()
        contributions = goal.contributions.all().order_by('-date', '-created_at')
        
        # Paginação
        page = self.paginate_queryset(contributions)
        if page is not None:
            serializer = GoalContributionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = GoalContributionSerializer(contributions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        """
        Resetar uma meta (zerar progresso)
        """
        goal = self.get_object()
        
        # Confirmar ação
        confirm = request.data.get('confirm', False)
        if not confirm:
            return Response(
                {'error': 'Para resetar a meta, envie "confirm": true'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Resetar meta
        goal.current_amount = Decimal('0.00')
        goal.achieved = False
        goal.achieved_date = None
        goal.save()
        
        # Opcional: remover contribuições
        remove_contributions = request.data.get('remove_contributions', False)
        if remove_contributions:
            goal.contributions.all().delete()
        
        return Response({
            'message': 'Meta resetada com sucesso!',
            'goal': GoalSerializer(goal).data
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Resumo geral das metas do usuário
        """
        goals = self.get_queryset()
        
        # Calcular estatísticas
        total_goals = goals.count()
        achieved_goals = goals.filter(achieved=True).count()
        active_goals = goals.filter(achieved=False).count()
        overdue_goals = goals.filter(
            achieved=False,
            target_date__lt=timezone.now().date()
        ).count()
        
        # Valores totais
        totals = goals.aggregate(
            total_target=Sum('target_amount'),
            total_current=Sum('current_amount')
        )
        
        total_target_amount = totals['total_target'] or Decimal('0.00')
        total_current_amount = totals['total_current'] or Decimal('0.00')
        total_remaining_amount = total_target_amount - total_current_amount
        
        # Porcentagem média de conclusão
        if total_goals > 0:
            avg_completion = sum(goal.percentage_completed for goal in goals) / total_goals
        else:
            avg_completion = 0
        
        # Metas próximas do prazo (próximos 30 dias)
        deadline_threshold = timezone.now().date() + timedelta(days=30)
        goals_near_deadline = goals.filter(
            achieved=False,
            target_date__lte=deadline_threshold,
            target_date__gte=timezone.now().date()
        ).count()
        
        summary_data = {
            'total_goals': total_goals,
            'achieved_goals': achieved_goals,
            'active_goals': active_goals,
            'overdue_goals': overdue_goals,
            'total_target_amount': total_target_amount,
            'total_current_amount': total_current_amount,
            'total_remaining_amount': total_remaining_amount,
            'average_completion_percentage': round(avg_completion, 1),
            'goals_near_deadline': goals_near_deadline
        }
        
        serializer = GoalSummarySerializer(summary_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def achieved(self, request):
        """
        Listar metas atingidas
        """
        achieved_goals = self.get_queryset().filter(achieved=True)
        
        page = self.paginate_queryset(achieved_goals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(achieved_goals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Listar metas ativas (não atingidas)
        """
        active_goals = self.get_queryset().filter(achieved=False)
        
        page = self.paginate_queryset(active_goals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(active_goals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Listar metas atrasadas
        """
        overdue_goals = self.get_queryset().filter(
            achieved=False,
            target_date__lt=timezone.now().date()
        )
        
        page = self.paginate_queryset(overdue_goals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(overdue_goals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def near_deadline(self, request):
        """
        Listar metas próximas do prazo
        """
        days = int(request.query_params.get('days', 30))
        deadline_threshold = timezone.now().date() + timedelta(days=days)
        
        near_deadline_goals = self.get_queryset().filter(
            achieved=False,
            target_date__lte=deadline_threshold,
            target_date__gte=timezone.now().date()
        )
        
        page = self.paginate_queryset(near_deadline_goals)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(near_deadline_goals, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Estatísticas detalhadas das metas
        """
        goals = self.get_queryset()
        
        # Estatísticas por mês de criação
        monthly_stats = {}
        for goal in goals:
            month_key = goal.created_at.strftime('%Y-%m')
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {
                    'created': 0,
                    'achieved': 0,
                    'total_target': Decimal('0.00'),
                    'total_current': Decimal('0.00')
                }
            
            monthly_stats[month_key]['created'] += 1
            monthly_stats[month_key]['total_target'] += goal.target_amount
            monthly_stats[month_key]['total_current'] += goal.current_amount
            
            if goal.achieved:
                monthly_stats[month_key]['achieved'] += 1
        
        # Distribuição por faixas de valor
        value_ranges = {
            'até_1000': goals.filter(target_amount__lte=1000).count(),
            '1001_5000': goals.filter(target_amount__gt=1000, target_amount__lte=5000).count(),
            '5001_10000': goals.filter(target_amount__gt=5000, target_amount__lte=10000).count(),
            'acima_10000': goals.filter(target_amount__gt=10000).count()
        }
        
        # Tempo médio para atingir metas
        achieved_goals = goals.filter(achieved=True, achieved_date__isnull=False)
        avg_days_to_achieve = None
        
        if achieved_goals.exists():
            total_days = sum(
                (goal.achieved_date.date() - goal.created_at.date()).days
                for goal in achieved_goals
            )
            avg_days_to_achieve = total_days / achieved_goals.count()
        
        return Response({
            'monthly_statistics': monthly_stats,
            'value_distribution': value_ranges,
            'average_days_to_achieve': avg_days_to_achieve,
            'total_contributions': GoalContribution.objects.filter(goal__user=request.user).count(),
            'total_contributed_amount': GoalContribution.objects.filter(
                goal__user=request.user
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        })

    @action(detail=True, methods=['get'])
    def progress_analysis(self, request, pk=None):
        """
        Análise detalhada de progresso de uma meta específica
        """
        goal = self.get_object()
        
        # Análise de ritmo
        pace_analysis = goal.current_pace_analysis
        
        # Tendência de contribuições
        trend_30_days = goal.get_contribution_trend(30)
        trend_90_days = goal.get_contribution_trend(90)
        
        # Projeções
        projections = {
            'daily_needed': float(goal.daily_target_amount),
            'weekly_needed': float(goal.weekly_target_amount),
            'monthly_needed': float(goal.monthly_target_amount),
        }
        
        # Histórico mensal de contribuições
        monthly_history = {}
        contributions = goal.contributions.all().order_by('date')
        
        for contrib in contributions:
            month_key = contrib.date.strftime('%Y-%m')
            if month_key not in monthly_history:
                monthly_history[month_key] = {
                    'total': Decimal('0.00'),
                    'count': 0,
                    'average': Decimal('0.00')
                }
            
            monthly_history[month_key]['total'] += contrib.amount
            monthly_history[month_key]['count'] += 1
            monthly_history[month_key]['average'] = (
                monthly_history[month_key]['total'] / 
                monthly_history[month_key]['count']
            )
        
        return Response({
            'goal_id': goal.id,
            'goal_name': goal.name,
            'pace_analysis': pace_analysis,
            'trend_analysis': {
                '30_days': trend_30_days,
                '90_days': trend_90_days
            },
            'projections': projections,
            'monthly_contribution_history': monthly_history,
            'estimated_completion': goal.estimated_completion_date,
            'days_remaining': goal.days_remaining,
            'is_on_track': pace_analysis.get('pace_ratio', 0) >= 0.8
        })

    @action(detail=False, methods=['get'])
    def performance_dashboard(self, request):
        """
        Dashboard de performance geral das metas
        """
        goals = self.get_queryset()
        active_goals = goals.filter(achieved=False)
        
        # Análise de performance por meta
        performance_data = []
        for goal in active_goals:
            pace = goal.current_pace_analysis
            performance_data.append({
                'id': goal.id,
                'name': goal.name,
                'percentage_completed': goal.percentage_completed,
                'pace_status': pace.get('status'),
                'pace_ratio': pace.get('pace_ratio', 0),
                'days_remaining': goal.days_remaining,
                'is_overdue': goal.is_overdue,
                'estimated_completion': goal.estimated_completion_date
            })
        
        # Estatísticas gerais de performance
        on_track_count = sum(1 for p in performance_data if p['pace_ratio'] >= 0.8)
        behind_count = sum(1 for p in performance_data if 0.5 <= p['pace_ratio'] < 0.8)
        far_behind_count = sum(1 for p in performance_data if p['pace_ratio'] < 0.5)
        
        return Response({
            'total_active_goals': len(performance_data),
            'performance_summary': {
                'on_track': on_track_count,
                'behind': behind_count,
                'far_behind': far_behind_count,
                'overdue': sum(1 for p in performance_data if p['is_overdue'])
            },
            'goals_performance': performance_data,
            'average_completion_rate': sum(p['percentage_completed'] for p in performance_data) / len(performance_data) if performance_data else 0
        })

    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        """
        Gerar recomendações personalizadas para uma meta
        """
        goal = self.get_object()
        pace_analysis = goal.current_pace_analysis
        
        recommendations = []
        
        # Recomendações baseadas no ritmo atual
        if pace_analysis['status'] == 'far_behind':
            recommendations.append({
                'type': 'urgent',
                'title': 'Ação Urgente Necessária',
                'message': f'Você precisa economizar R$ {goal.daily_target_amount:.2f} por dia para atingir sua meta no prazo.',
                'action': 'Considere revisar seu orçamento ou ajustar a data da meta.'
            })
        elif pace_analysis['status'] == 'behind':
            recommendations.append({
                'type': 'warning',
                'title': 'Acelere o Ritmo',
                'message': f'Aumente suas contribuições para R$ {goal.weekly_target_amount:.2f} por semana.',
                'action': 'Procure fontes de renda extra ou reduza gastos desnecessários.'
            })
        elif pace_analysis['status'] == 'on_track':
            recommendations.append({
                'type': 'success',
                'title': 'Parabéns! Você está no caminho certo',
                'message': 'Continue com o ritmo atual de contribuições.',
                'action': 'Mantenha a disciplina e considere automatizar suas contribuições.'
            })
        
        # Recomendações baseadas no tempo restante
        if goal.days_remaining <= 30 and not goal.achieved:
            recommendations.append({
                'type': 'urgent',
                'title': 'Meta Próxima do Vencimento',
                'message': f'Restam apenas {goal.days_remaining} dias para sua meta.',
                'action': 'Considere fazer um esforço extra ou ajustar o valor alvo.'
            })
        elif goal.days_remaining <= 90 and not goal.achieved:
            recommendations.append({
                'type': 'info',
                'title': 'Reta Final',
                'message': f'Sua meta vence em {goal.days_remaining} dias.',
                'action': 'Mantenha o foco e evite gastos desnecessários.'
            })
        
        # Recomendações baseadas na tendência
        trend = goal.get_contribution_trend(30)
        if trend['trend'] == 'decreasing':
            recommendations.append({
                'type': 'warning',
                'title': 'Contribuições em Declínio',
                'message': 'Suas contribuições têm diminuído no último mês.',
                'action': 'Revise seu orçamento e tente manter contribuições regulares.'
            })
        elif trend['trend'] == 'increasing':
            recommendations.append({
                'type': 'success',
                'title': 'Excelente Progresso!',
                'message': 'Suas contribuições têm aumentado consistentemente.',
                'action': 'Continue assim! Considere aumentar ainda mais se possível.'
            })
        
        # Recomendações baseadas no progresso
        if goal.percentage_completed >= 80:
            recommendations.append({
                'type': 'success',
                'title': 'Quase Lá!',
                'message': f'Você já completou {goal.percentage_completed:.1f}% da sua meta.',
                'action': f'Faltam apenas R$ {goal.remaining_amount:.2f} para atingir seu objetivo!'
            })
        elif goal.percentage_completed >= 50:
            recommendations.append({
                'type': 'info',
                'title': 'Meio Caminho Andado',
                'message': 'Você já passou da metade da sua meta.',
                'action': 'Mantenha o ritmo e você chegará lá!'
            })
        
        # Recomendação de automação
        if goal.contributions.count() >= 3:
            avg_contribution = goal.current_amount / goal.contributions.count()
            recommendations.append({
                'type': 'tip',
                'title': 'Dica: Automatize suas Contribuições',
                'message': f'Sua contribuição média é R$ {avg_contribution:.2f}.',
                'action': 'Configure uma transferência automática mensal para facilitar o processo.'
            })
        
        return Response({
            'goal_id': goal.id,
            'goal_name': goal.name,
            'current_status': pace_analysis['status'],
            'recommendations': recommendations,
            'quick_stats': {
                'percentage_completed': goal.percentage_completed,
                'days_remaining': goal.days_remaining,
                'daily_target': float(goal.daily_target_amount),
                'estimated_completion': goal.estimated_completion_date
            }
        })


class GoalContributionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualizar contribuições (somente leitura)
    """
    serializer_class = GoalContributionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retornar apenas contribuições do usuário autenticado"""
        return GoalContribution.objects.filter(
            goal__user=self.request.user
        ).select_related('goal').order_by('-date', '-created_at')

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Contribuições recentes (últimos 30 dias)
        """
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_contributions = self.get_queryset().filter(date__gte=thirty_days_ago)
        
        page = self.paginate_queryset(recent_contributions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(recent_contributions, many=True)
        return Response(serializer.data)