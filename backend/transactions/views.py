from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum
from decimal import Decimal
from .models import Category, Tag, Transaction
from .serializers import (
    CategorySerializer, TagSerializer, TransactionSerializer,
    TransactionSummarySerializer, TransactionFilterSerializer, TransferSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para categorias com CRUD completo
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        """
        Permite filtrar categorias
        """
        queryset = Category.objects.all()
        
        # Filtrar apenas categorias padrão se solicitado
        is_default = self.request.query_params.get('is_default', None)
        if is_default is not None:
            is_default_bool = is_default.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_default=is_default_bool)
        
        return queryset.order_by('name')

    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """
        Endpoint para obter apenas categorias padrão
        """
        default_categories = Category.objects.filter(is_default=True).order_by('name')
        serializer = self.get_serializer(default_categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def with_stats(self, request):
        """
        Endpoint para categorias com estatísticas de uso
        """
        from django.db.models import Count, Sum
        
        # Obter estatísticas de transações por categoria
        categories = Category.objects.annotate(
            transaction_count=Count('transaction'),
            total_income=Sum('transaction__amount', filter=Q(transaction__type='income')),
            total_expense=Sum('transaction__amount', filter=Q(transaction__type='expense'))
        ).order_by('name')
        
        # Serializar com estatísticas
        data = []
        for category in categories:
            category_data = CategorySerializer(category).data
            category_data.update({
                'transaction_count': category.transaction_count or 0,
                'total_income': category.total_income or Decimal('0.00'),
                'total_expense': category.total_expense or Decimal('0.00'),
                'balance': (category.total_income or Decimal('0.00')) - (category.total_expense or Decimal('0.00'))
            })
            data.append(category_data)
        
        return Response(data)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Endpoint para obter transações de uma categoria específica
        """
        category = self.get_object()
        transactions = Transaction.objects.filter(
            category=category,
            user=request.user
        ).select_related('category', 'user').prefetch_related('tags')
        
        # Aplicar filtros de data se fornecidos
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            transactions = transactions.filter(date__gte=date_from)
        if date_to:
            transactions = transactions.filter(date__lte=date_to)
        
        # Paginação
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Endpoint para resumo financeiro de uma categoria
        """
        category = self.get_object()
        
        # Filtros de data
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        queryset = Transaction.objects.filter(
            category=category,
            user=request.user
        )
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Calcular totais
        income_total = queryset.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        expense_total = queryset.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        balance = income_total - expense_total
        transaction_count = queryset.count()
        
        # Calcular médias mensais
        from django.db.models.functions import TruncMonth
        monthly_data = queryset.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            income=Sum('amount', filter=Q(type='income')),
            expense=Sum('amount', filter=Q(type='expense')),
            count=Count('id')
        ).order_by('month')
        
        summary_data = {
            'category': CategorySerializer(category).data,
            'total_income': income_total,
            'total_expense': expense_total,
            'balance': balance,
            'transaction_count': transaction_count,
            'monthly_data': list(monthly_data)
        }
        
        return Response(summary_data)

    def perform_create(self, serializer):
        """
        Customizar criação de categoria
        """
        # Não permitir criar categorias padrão via API
        serializer.save(is_default=False)

    def perform_update(self, serializer):
        """
        Customizar atualização de categoria
        """
        # Não permitir alterar o status de categoria padrão
        instance = self.get_object()
        if instance.is_default:
            serializer.save(is_default=True)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        """
        Customizar exclusão de categoria
        """
        from django.core.exceptions import ValidationError
        
        # Não permitir excluir categorias padrão
        if instance.is_default:
            raise ValidationError("Não é possível excluir categorias padrão.")
        
        # Verificar se há transações usando esta categoria
        transaction_count = Transaction.objects.filter(category=instance).count()
        if transaction_count > 0:
            raise ValidationError(
                f"Não é possível excluir esta categoria pois ela possui {transaction_count} transação(ões) associada(s)."
            )
        
        instance.delete()


class TagViewSet(viewsets.ModelViewSet):
    """
    ViewSet para tags (CRUD completo)
    """
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'usage_count', 'created_at']
    ordering = ['-usage_count', 'name']

    def get_queryset(self):
        """Retornar apenas tags do usuário autenticado"""
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Associar tag ao usuário autenticado"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Retorna as tags mais populares do usuário
        """
        limit = int(request.query_params.get('limit', 10))
        popular_tags = Tag.get_popular_tags(request.user, limit)
        serializer = self.get_serializer(popular_tags, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def suggestions(self, request):
        """
        Sugestões de tags baseadas no texto fornecido
        """
        query = request.query_params.get('q', '').strip().lower()
        if not query:
            return Response([])
        
        # Buscar tags que começam com o texto
        suggestions = self.get_queryset().filter(
            name__istartswith=query
        ).order_by('-usage_count', 'name')[:5]
        
        serializer = self.get_serializer(suggestions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """
        Criar tags padrão para o usuário
        """
        created_tags = Tag.create_default_tags(request.user)
        
        if created_tags:
            serializer = self.get_serializer(created_tags, many=True)
            return Response({
                'message': f'{len(created_tags)} tags padrão criadas com sucesso!',
                'tags': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Tags padrão já existem para este usuário.',
                'tags': []
            })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Resumo das tags do usuário
        """
        tags = self.get_queryset()
        active_tags = tags.filter(is_active=True)
        
        # Tag mais usada
        most_used_tag = active_tags.order_by('-usage_count').first()
        
        # Total de transações com tags
        total_tagged_transactions = Transaction.objects.filter(
            user=request.user,
            tags__isnull=False
        ).distinct().count()
        
        # Tags por uso (top 5)
        tags_by_usage = active_tags.order_by('-usage_count')[:5]
        
        summary_data = {
            'total_tags': tags.count(),
            'active_tags': active_tags.count(),
            'most_used_tag': TagSerializer(most_used_tag).data if most_used_tag else None,
            'total_tagged_transactions': total_tagged_transactions,
            'tags_by_usage': TagSerializer(tags_by_usage, many=True).data
        }
        
        return Response(summary_data)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Listar transações de uma tag específica
        """
        tag = self.get_object()
        transactions = tag.transaction_set.all().order_by('-date', '-created_at')
        
        # Aplicar filtros de data se fornecidos
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            transactions = transactions.filter(date__gte=date_from)
        if date_to:
            transactions = transactions.filter(date__lte=date_to)
        
        # Paginação
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Ativar/desativar uma tag
        """
        tag = self.get_object()
        tag.is_active = not tag.is_active
        tag.save()
        
        status_text = 'ativada' if tag.is_active else 'desativada'
        return Response({
            'message': f'Tag {status_text} com sucesso!',
            'tag': TagSerializer(tag).data
        })

    @action(detail=False, methods=['get'])
    def unused(self, request):
        """
        Listar tags não utilizadas
        """
        unused_tags = self.get_queryset().filter(usage_count=0)
        serializer = self.get_serializer(unused_tags, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def cleanup_unused(self, request):
        """
        Remover tags não utilizadas (exceto padrão)
        """
        unused_tags = self.get_queryset().filter(
            usage_count=0,
            is_default=False
        )
        count = unused_tags.count()
        unused_tags.delete()
        
        return Response({
            'message': f'{count} tags não utilizadas foram removidas.'
        })

    def perform_destroy(self, instance):
        """
        Customizar exclusão de tag
        """
        from django.core.exceptions import ValidationError
        
        # Não permitir excluir tags padrão
        if instance.is_default:
            raise ValidationError("Não é possível excluir tags padrão.")
        
        # Verificar se há transações usando esta tag
        transaction_count = instance.get_transactions_count()
        if transaction_count > 0:
            raise ValidationError(
                f"Não é possível excluir esta tag pois ela está sendo usada em {transaction_count} transação(ões)."
            )
        
        instance.delete()
        serializer = self.get_serializer(created_tags, many=True)
        return Response({
            'message': f'{len(created_tags)} tags padrão criadas com sucesso!',
            'tags': serializer.data
        }, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """
        Customizar exclusão de tag
        """
        # Verificar se a tag está sendo usada
        transaction_count = instance.transaction_set.count()
        if transaction_count > 0:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(
                f"Não é possível excluir esta tag pois ela está sendo usada em {transaction_count} transação(ões)."
            )
        
        instance.delete() 


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para transações com filtros avançados
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'category', 'date']
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']

    def get_queryset(self):
        """
        Retorna apenas transações do usuário autenticado
        """
        return Transaction.objects.filter(
            user=self.request.user
        ).select_related('category', 'user').prefetch_related('tags')

    def perform_create(self, serializer):
        """
        Associa a transação ao usuário autenticado
        """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Endpoint para resumo financeiro
        """
        queryset = self.get_queryset()
        
        # Aplicar filtros se fornecidos
        filter_serializer = TransactionFilterSerializer(data=request.query_params)
        if filter_serializer.is_valid():
            filters = filter_serializer.validated_data
            queryset = self.apply_filters(queryset, filters)
        
        # Calcular totais
        income_total = queryset.filter(type='income').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        expense_total = queryset.filter(type='expense').aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        balance = income_total - expense_total
        transaction_count = queryset.count()
        
        summary_data = {
            'total_income': income_total,
            'total_expense': expense_total,
            'balance': balance,
            'transaction_count': transaction_count
        }
        
        serializer = TransactionSummarySerializer(summary_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Endpoint para transações agrupadas por categoria
        """
        queryset = self.get_queryset()
        
        # Aplicar filtros se fornecidos
        filter_serializer = TransactionFilterSerializer(data=request.query_params)
        if filter_serializer.is_valid():
            filters = filter_serializer.validated_data
            queryset = self.apply_filters(queryset, filters)
        
        # Agrupar por categoria
        categories_data = []
        for category in Category.objects.all():
            category_transactions = queryset.filter(category=category)
            
            income_total = category_transactions.filter(type='income').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            expense_total = category_transactions.filter(type='expense').aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00')
            
            if income_total > 0 or expense_total > 0:
                categories_data.append({
                    'category': CategorySerializer(category).data,
                    'income_total': income_total,
                    'expense_total': expense_total,
                    'balance': income_total - expense_total,
                    'transaction_count': category_transactions.count()
                })
        
        return Response(categories_data)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Endpoint para criação em lote de transações
        """
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Esperado uma lista de transações'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        transactions = serializer.save()
        
        return Response(
            self.get_serializer(transactions, many=True).data,
            status=status.HTTP_201_CREATED
        )

    def apply_filters(self, queryset, filters):
        """
        Aplica filtros avançados ao queryset
        """
        if filters.get('type'):
            queryset = queryset.filter(type=filters['type'])
        
        if filters.get('category'):
            queryset = queryset.filter(category_id=filters['category'])
        
        if filters.get('tags'):
            queryset = queryset.filter(tags__id__in=filters['tags']).distinct()
        
        if filters.get('date_from'):
            queryset = queryset.filter(date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(date__lte=filters['date_to'])
        
        if filters.get('amount_min'):
            queryset = queryset.filter(amount__gte=filters['amount_min'])
        
        if filters.get('amount_max'):
            queryset = queryset.filter(amount__lte=filters['amount_max'])
        
        if filters.get('search'):
            search_term = filters['search']
            queryset = queryset.filter(
                Q(description__icontains=search_term) |
                Q(category__name__icontains=search_term)
            )
        
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Lista transações com filtros aplicados
        """
        queryset = self.get_queryset()
        
        # Aplicar filtros se fornecidos
        filter_serializer = TransactionFilterSerializer(data=request.query_params)
        if filter_serializer.is_valid():
            filters = filter_serializer.validated_data
            queryset = self.apply_filters(queryset, filters)
        
        # Aplicar filtros do DRF
        queryset = self.filter_queryset(queryset)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """
        Endpoint para criar transferências entre contas
        """
        serializer = TransferSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                transaction = serializer.save()
                response_serializer = TransactionSerializer(transaction)
                return Response(
                    {
                        'message': 'Transferência realizada com sucesso!',
                        'transaction': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    {'error': f'Erro ao processar transferência: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def transfers(self, request):
        """
        Endpoint para listar apenas transferências
        """
        queryset = self.get_queryset().filter(type='transfer')
        
        # Aplicar filtros de data se fornecidos
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        # Paginação
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)