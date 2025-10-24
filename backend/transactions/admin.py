from django.contrib import admin
from .models import Category, Tag, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'icon', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'type', 'amount', 'category', 'user', 'date', 'created_at']
    list_filter = ['type', 'category', 'date', 'created_at']
    search_fields = ['description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['tags']
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')