from django.contrib import admin
from .models import Goal, GoalContribution


class GoalContributionInline(admin.TabularInline):
    model = GoalContribution
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'current_amount', 'target_amount', 'progress_display', 'target_date', 'achieved']
    list_filter = ['achieved', 'target_date', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'achieved_date', 'progress_display', 'remaining_amount']
    inlines = [GoalContributionInline]
    date_hierarchy = 'target_date'
    
    def progress_display(self, obj):
        return f'{obj.percentage_completed:.1f}%'
    progress_display.short_description = 'Progresso'
    
    def remaining_amount(self, obj):
        return f'R$ {obj.remaining_amount}'
    remaining_amount.short_description = 'Valor Restante'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(GoalContribution)
class GoalContributionAdmin(admin.ModelAdmin):
    list_display = ['goal', 'amount', 'date', 'description', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['goal__name', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('goal', 'goal__user')