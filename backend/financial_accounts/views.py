from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction, models
from django.shortcuts import get_object_or_404
from .models import Account, CreditCard, CreditCardBill
from .serializers import (
    AccountSerializer, AccountSummarySerializer,
    CreditCardSerializer, CreditCardSummarySerializer,
    CreditCardBillSerializer, PayBillSerializer, TransferSerializer
)


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar contas bancárias
    """
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by('name')

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountSummarySerializer
        return AccountSerializer

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """
        Retorna o saldo atual da conta
        """
        account = self.get_object()
        account.update_balance()  # Atualizar saldo antes de retornar
        
        return Response({
            'account_id': account.id,
            'account_name': account.name,
            'current_balance': account.current_balance,
            'balance_formatted': account.balance_formatted,
            'last_updated': account.updated_at
        })

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Retorna as transações da conta
        """
        from transactions.serializers import TransactionSerializer
        
        account = self.get_object()
        transactions = account.transaction_set.all().order_by('-date', '-created_at')
        
        # Paginação
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retorna resumo de todas as contas
        """
        accounts = self.get_queryset().filter(is_active=True)
        
        total_balance = sum(account.current_balance for account in accounts)
        
        summary_data = {
            'total_accounts': accounts.count(),
            'total_balance': total_balance,
            'total_balance_formatted': f'R$ {total_balance:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            'accounts_by_type': {}
        }
        
        # Agrupar por tipo
        for account in accounts:
            account_type = account.get_type_display()
            if account_type not in summary_data['accounts_by_type']:
                summary_data['accounts_by_type'][account_type] = {
                    'count': 0,
                    'total_balance': 0
                }
            
            summary_data['accounts_by_type'][account_type]['count'] += 1
            summary_data['accounts_by_type'][account_type]['total_balance'] += float(account.current_balance)
        
        return Response(summary_data)

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """
        Relatório detalhado de uma conta específica
        """
        from transactions.models import Transaction
        from django.db.models import Sum, Count, Q, F
        from django.db.models.functions import TruncMonth
        from datetime import datetime, timedelta
        
        account = self.get_object()
        
        # Filtros de data
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Query base para transações da conta
        transactions_query = Transaction.objects.filter(
            Q(account=account) |
            Q(transfer_from_account=account) |
            Q(transfer_to_account=account)
        )
        
        if date_from:
            transactions_query = transactions_query.filter(date__gte=date_from)
        if date_to:
            transactions_query = transactions_query.filter(date__lte=date_to)
        
        # Calcular totais por tipo
        income_total = transactions_query.filter(
            account=account, type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense_total = transactions_query.filter(
            account=account, type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        transfers_in = transactions_query.filter(
            transfer_to_account=account, type='transfer'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        transfers_out = transactions_query.filter(
            transfer_from_account=account, type='transfer'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Evolução mensal
        monthly_data = transactions_query.annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            income=Sum('amount', filter=Q(account=account, type='income')),
            expense=Sum('amount', filter=Q(account=account, type='expense')),
            transfers_in=Sum('amount', filter=Q(transfer_to_account=account, type='transfer')),
            transfers_out=Sum('amount', filter=Q(transfer_from_account=account, type='transfer')),
            transaction_count=Count('id')
        ).order_by('month')
        
        # Gastos por categoria
        category_breakdown = transactions_query.filter(
            account=account, type='expense'
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Transações recentes
        recent_transactions = transactions_query.order_by('-date', '-created_at')[:10]
        from transactions.serializers import TransactionSerializer
        recent_serializer = TransactionSerializer(recent_transactions, many=True)
        
        report_data = {
            'account': AccountSerializer(account).data,
            'period': {
                'date_from': date_from,
                'date_to': date_to
            },
            'totals': {
                'income': income_total,
                'expense': expense_total,
                'transfers_in': transfers_in,
                'transfers_out': transfers_out,
                'net_flow': income_total - expense_total + transfers_in - transfers_out,
                'transaction_count': transactions_query.count()
            },
            'monthly_evolution': list(monthly_data),
            'category_breakdown': list(category_breakdown),
            'recent_transactions': recent_serializer.data
        }
        
        return Response(report_data)


class CreditCardViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar cartões de crédito
    """
    serializer_class = CreditCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CreditCard.objects.filter(user=self.request.user).order_by('name')

    def get_serializer_class(self):
        if self.action == 'list':
            return CreditCardSummarySerializer
        return CreditCardSerializer

    @action(detail=True, methods=['get'])
    def limit(self, request, pk=None):
        """
        Retorna informações sobre o limite do cartão
        """
        card = self.get_object()
        card.update_available_limit()  # Atualizar limite antes de retornar
        
        return Response({
            'card_id': card.id,
            'card_name': card.name,
            'credit_limit': card.credit_limit,
            'available_limit': card.available_limit,
            'used_limit': card.used_limit,
            'usage_percentage': card.usage_percentage,
            'limit_formatted': card.limit_formatted,
            'available_limit_formatted': card.available_limit_formatted,
            'last_updated': card.updated_at
        })

    @action(detail=True, methods=['get'])
    def bills(self, request, pk=None):
        """
        Retorna as faturas do cartão
        """
        card = self.get_object()
        bills = card.bills.all().order_by('-reference_month')
        
        # Paginação
        page = self.paginate_queryset(bills)
        if page is not None:
            serializer = CreditCardBillSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = CreditCardBillSerializer(bills, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Retorna as transações do cartão
        """
        from transactions.serializers import TransactionSerializer
        
        card = self.get_object()
        transactions = card.transaction_set.all().order_by('-date', '-created_at')
        
        # Paginação
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Retorna resumo de todos os cartões
        """
        cards = self.get_queryset().filter(is_active=True)
        
        total_limit = sum(card.credit_limit for card in cards)
        total_available = sum(card.available_limit for card in cards)
        total_used = total_limit - total_available
        
        summary_data = {
            'total_cards': cards.count(),
            'total_limit': total_limit,
            'total_available': total_available,
            'total_used': total_used,
            'average_usage': (total_used / total_limit * 100) if total_limit > 0 else 0,
            'cards_near_limit': cards.filter(available_limit__lt=models.F('credit_limit') * 0.2).count()
        }
        
        return Response(summary_data)

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """
        Relatório detalhado de um cartão específico
        """
        from transactions.models import Transaction
        from django.db.models import Sum, Count, Q
        from django.db.models.functions import TruncMonth
        from datetime import datetime, timedelta
        
        card = self.get_object()
        
        # Filtros de data
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        # Query base para transações do cartão
        transactions_query = Transaction.objects.filter(credit_card=card)
        
        if date_from:
            transactions_query = transactions_query.filter(date__gte=date_from)
        if date_to:
            transactions_query = transactions_query.filter(date__lte=date_to)
        
        # Calcular totais
        total_spent = transactions_query.filter(
            type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Evolução mensal de gastos
        monthly_data = transactions_query.filter(
            type='expense'
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total_spent=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('month')
        
        # Gastos por categoria
        category_breakdown = transactions_query.filter(
            type='expense'
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Transações recentes
        recent_transactions = transactions_query.order_by('-date', '-created_at')[:10]
        from transactions.serializers import TransactionSerializer
        recent_serializer = TransactionSerializer(recent_transactions, many=True)
        
        # Informações do limite
        card.update_available_limit()
        
        report_data = {
            'card': CreditCardSerializer(card).data,
            'period': {
                'date_from': date_from,
                'date_to': date_to
            },
            'totals': {
                'total_spent': total_spent,
                'transaction_count': transactions_query.count(),
                'average_transaction': total_spent / transactions_query.count() if transactions_query.count() > 0 else 0
            },
            'limit_info': {
                'credit_limit': card.credit_limit,
                'available_limit': card.available_limit,
                'used_limit': card.used_limit,
                'usage_percentage': card.usage_percentage
            },
            'monthly_evolution': list(monthly_data),
            'category_breakdown': list(category_breakdown),
            'recent_transactions': recent_serializer.data
        }
        
        return Response(report_data)


class CreditCardBillViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar faturas de cartão de crédito
    """
    serializer_class = CreditCardBillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CreditCardBill.objects.filter(
            credit_card__user=self.request.user
        ).select_related('credit_card').order_by('-reference_month')

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """
        Registra pagamento de uma fatura
        """
        bill = self.get_object()
        serializer = PayBillSerializer(
            data=request.data, 
            context={'request': request},
            instance=bill
        )
        
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            payment_account = serializer.validated_data.get('payment_account')
            
            try:
                with transaction.atomic():
                    # Registrar pagamento
                    bill.pay(amount, payment_account)
                    
                    # Se foi usada uma conta, atualizar saldo
                    if payment_account:
                        payment_account.update_balance()
                    
                    # Atualizar limite disponível do cartão
                    bill.credit_card.update_available_limit()
                
                return Response({
                    'message': 'Pagamento registrado com sucesso',
                    'bill_id': bill.id,
                    'paid_amount': amount,
                    'remaining_amount': bill.remaining_amount,
                    'status': bill.status
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def calculate_total(self, request, pk=None):
        """
        Recalcula o total da fatura baseado nas transações
        """
        bill = self.get_object()
        bill.calculate_total()
        
        return Response({
            'message': 'Total da fatura recalculado',
            'bill_id': bill.id,
            'total_amount': bill.total_amount,
            'total_formatted': bill.total_formatted
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Retorna faturas próximas do vencimento
        """
        from datetime import date, timedelta
        
        upcoming_date = date.today() + timedelta(days=7)
        upcoming_bills = self.get_queryset().filter(
            due_date__lte=upcoming_date,
            status__in=['open', 'closed']
        ).order_by('due_date')
        
        serializer = self.get_serializer(upcoming_bills, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Retorna faturas vencidas
        """
        from datetime import date
        
        overdue_bills = self.get_queryset().filter(
            due_date__lt=date.today(),
            status__in=['open', 'closed']
        ).order_by('due_date')
        
        serializer = self.get_serializer(overdue_bills, many=True)
        return Response(serializer.data)


class TransferViewSet(viewsets.ViewSet):
    """
    ViewSet para gerenciar transferências entre contas
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        """
        Cria uma nova transferência entre contas
        """
        serializer = TransferSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            from_account = serializer.validated_data['from_account']
            to_account = serializer.validated_data['to_account']
            amount = serializer.validated_data['amount']
            description = serializer.validated_data.get('description', 
                f'Transferência de {from_account.name} para {to_account.name}')
            
            try:
                with transaction.atomic():
                    # Criar transação de saída
                    from transactions.models import Transaction, Category
                    
                    # Buscar ou criar categoria de transferência
                    transfer_category, created = Category.objects.get_or_create(
                        name='Transferência',
                        defaults={'color': '#6c757d', 'icon': 'transfer'}
                    )
                    
                    # Transação de débito na conta origem
                    debit_transaction = Transaction.objects.create(
                        user=request.user,
                        type='transfer',
                        amount=amount,
                        description=f'{description} (Saída)',
                        category=transfer_category,
                        date=request.data.get('date', date.today()),
                        transfer_from_account=from_account,
                        transfer_to_account=to_account
                    )
                    
                    # Transação de crédito na conta destino
                    credit_transaction = Transaction.objects.create(
                        user=request.user,
                        type='transfer',
                        amount=amount,
                        description=f'{description} (Entrada)',
                        category=transfer_category,
                        date=request.data.get('date', date.today()),
                        transfer_from_account=from_account,
                        transfer_to_account=to_account
                    )
                    
                    # Atualizar saldos das contas
                    from_account.update_balance()
                    to_account.update_balance()
                
                return Response({
                    'message': 'Transferência realizada com sucesso',
                    'transfer_id': debit_transaction.id,
                    'from_account': from_account.name,
                    'to_account': to_account.name,
                    'amount': amount,
                    'description': description
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Erro ao processar transferência: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        """
        Lista transferências do usuário
        """
        from transactions.models import Transaction
        from transactions.serializers import TransactionSerializer
        
        transfers = Transaction.objects.filter(
            user=request.user,
            type='transfer'
        ).order_by('-date', '-created_at')
        
        # Paginação
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(transfers, request)
        
        if page is not None:
            serializer = TransactionSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = TransactionSerializer(transfers, many=True)
        return Response(serializer.data)