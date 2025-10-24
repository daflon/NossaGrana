from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'alerts', views.BudgetAlertViewSet, basename='budget-alert')

urlpatterns = [
    path('', include(router.urls)),
    path('status/', views.BudgetStatusView.as_view(), name='budget-status'),
]