from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet, CreditCardViewSet, CreditCardBillViewSet, TransferViewSet

# Criar router para as ViewSets
router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'credit-cards', CreditCardViewSet, basename='creditcard')
router.register(r'credit-card-bills', CreditCardBillViewSet, basename='creditcardbill')
router.register(r'transfers', TransferViewSet, basename='transfer')

urlpatterns = [
    path('', include(router.urls)),
]