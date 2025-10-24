from django.contrib import admin
from .models import Budget, BudgetAlert


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'user', 'amount', 'month', 'spent_amount', 'percentage_used', 'alert_level', 'created_at']
    list_filter = ['category', 'month', 'created_at']
    search_fields = ['user__username', 'category__name']
    readonly_fields = [
        'created_at', 'updated_at', 'spent_amount', 'remaining_amount', 'percentage_used',
        'daily_average_spent', 'projected_monthly_spending', 'projected_overspend',
        'days_until_limit', 'spending_trend', 'alert_level'
    ]
    date_hierarchy = 'month'
    
    def spent_amount(self, obj):
        return f'R$ {obj.spent_amount:.2f}'
    spent_amount.short_description = 'Valor Gasto'
    
    def percentage_used(self, obj):
        return f'{obj.percentage_used:.1f}%'
    percentage_used.short_description = 'Percentual Usado'
    
    def alert_level(self, obj):
        level = obj.alert_level
        colors = {
            'low': 'green',
            'medium': 'orange', 
            'high': 'red',
            'critical': 'darkred'
        }
        color = colors.get(level, 'black')
        return f'<span style="color: {color}; font-weight: bold;">{level.upper()}</span>'
    alert_level.short_description = 'Nível de Alerta'
    alert_level.allow_tags = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'category', 'amount', 'month')
        }),
        ('Cálculos Automáticos', {
            'fields': (
                'spent_amount', 'remaining_amount', 'percentage_used',
                'daily_average_spent', 'projected_monthly_spending', 'projected_overspend'
            ),
            'classes': ('collapse',)
        }),
        ('Análise de Tendência', {
            'fields': ('days_until_limit', 'spending_trend', 'alert_level'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BudgetAlert)
class BudgetAlertAdmin(admin.ModelAdmin):
    list_display = ['budget', 'alert_type', 'alert_level', 'is_active', 'created_at']
    list_filter = ['alert_type', 'alert_level', 'is_active', 'created_at']
    search_fields = ['budget__category__name', 'budget__user__username', 'message']
    readonly_fields = ['created_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('budget', 'budget__category', 'budget__user')
    
    fieldsets = (
        ('Informações do Alerta', {
            'fields': ('budget', 'alert_type', 'alert_level', 'message')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'resolved_at')
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_active']
    
    def mark_as_resolved(self, request, queryset):
        """
        Marca alertas selecionados como resolvidos
        """
        from datetime import datetime
        updated = queryset.update(is_active=False, resolved_at=datetime.now())
        self.message_user(request, f'{updated} alertas marcados como resolvidos.')
    mark_as_resolved.short_description = 'Marcar como resolvidos'
    
    def mark_as_active(self, request, queryset):
        """
        Marca alertas selecionados como ativos
        """
        updated = queryset.update(is_active=True, resolved_at=None)
        self.message_user(request, f'{updated} alertas marcados como ativos.')
    mark_as_active.short_description = 'Marcar como ativos'