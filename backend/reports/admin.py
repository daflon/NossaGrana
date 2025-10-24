from django.contrib import admin
from .models import Alert, Reminder


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'priority', 'is_read', 'created_at']
    list_filter = ['type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at', 'read_at']
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        for alert in queryset:
            alert.mark_as_read()
        self.message_user(request, f'{queryset.count()} alertas marcados como lidos.')
    mark_as_read.short_description = 'Marcar como lido'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'reminder_date', 'frequency', 'is_active', 'last_sent']
    list_filter = ['frequency', 'is_active', 'reminder_date', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'last_sent']
    date_hierarchy = 'reminder_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')