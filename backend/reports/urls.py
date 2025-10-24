from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.SummaryReportView.as_view(), name='summary-report'),
    path('category-breakdown/', views.CategoryBreakdownView.as_view(), name='category-breakdown'),
    path('monthly-trend/', views.MonthlyTrendView.as_view(), name='monthly-trend'),
    path('spending-patterns/', views.SpendingPatternsView.as_view(), name='spending-patterns'),
    path('export/', views.ExportReportView.as_view(), name='export-report'),
]