from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'goals', views.GoalViewSet, basename='goal')
router.register(r'contributions', views.GoalContributionViewSet, basename='goalcontribution')

urlpatterns = [
    path('', include(router.urls)),
]