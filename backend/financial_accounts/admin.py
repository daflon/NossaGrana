from django.contrib import admin
from .models import Account, CreditCard, CreditCardBill


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'bank', 'current_balance', 'is_active', 'user']
    list_filter = ['type', 'is_active', 'bank']
    search_fields = ['name', 'bank', 'user__username']
    readonly_fields = ['current_balance', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'name', 'type', 'bank')
        }),
        ('Saldos', {
            'fields': ('initial_balance', 'current_balance')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'bank', 'credit_limit', 'available_limit', 'usage_percentage_display', 'is_active', 'user']
    list_filter = ['is_active', 'bank']
    search_fields = ['name', 'bank', 'user__username']
    readonly_fields = ['available_limit', 'usage_percentage_display', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'name', 'bank')
        }),
        ('Limites', {
            'fields': ('credit_limit', 'available_limit')
        }),
        ('Ciclo do Cartão', {
            'fields': ('closing_day', 'due_day')
        }),
        ('Status', {
            'fields': ('is_active', 'usage_percentage_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def usage_percentage_display(self, obj):
        return f'{obj.usage_percentage:.1f}%'
    usage_percentage_display.short_description = 'Uso do Limite'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(CreditCardBill)
class CreditCardBillAdmin(admin.ModelAdmin):
    list_display = ['credit_card', 'reference_month', 'total_amount', 'paid_amount', 'remaining_amount_display', 'status', 'due_date']
    list_filter = ['status', 'credit_card__bank', 'due_date']
    search_fields = ['credit_card__name', 'credit_card__user__username']
    readonly_fields = ['remaining_amount_display', 'days_until_due_display', 'created_at', 'updated_at']
    date_hierarchy = 'reference_month'
    
    fieldsets = (
        ('Informações da Fatura', {
            'fields': ('credit_card', 'reference_month', 'status')
        }),
        ('Datas', {
            'fields': ('closing_date', 'due_date', 'days_until_due_display')
        }),
        ('Valores', {
            'fields': ('total_amount', 'paid_amount', 'remaining_amount_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def remaining_amount_display(self, obj):
        return f'R$ {obj.remaining_amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    remaining_amount_display.short_description = 'Valor Restante'

    def days_until_due_display(self, obj):
        days = obj.days_until_due
        if days < 0:
            return f'{abs(days)} dias em atraso'
        elif days == 0:
            return 'Vence hoje'
        else:
            return f'{days} dias para vencer'
    days_until_due_display.short_description = 'Vencimento'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('credit_card', 'credit_card__user')

    actions = ['calculate_totals', 'mark_as_paid']

    def calculate_totals(self, request, queryset):
        for bill in queryset:
            bill.calculate_total()
        self.message_user(request, f'{queryset.count()} faturas tiveram seus totais recalculados.')
    calculate_totals.short_description = 'Recalcular totais das faturas selecionadas'

    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status__in=['open', 'closed']).update(
            status='paid',
            paid_amount=models.F('total_amount')
        )
        self.message_user(request, f'{updated} faturas foram marcadas como pagas.')
    mark_as_paid.short_description = 'Marcar faturas selecionadas como pagas'