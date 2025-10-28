"""
URL configuration for nossa_grana project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from .health_views import health_check, health_detailed, readiness_check, liveness_check

def api_root(request):
    return JsonResponse({
        'message': 'Nossa Grana API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'transactions': '/api/transactions/',
            'budgets': '/api/budgets/',
            'goals': '/api/goals/',
            'reports': '/api/reports/',
            'financial': '/api/financial/'
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    
    # Health Check Endpoints
    path('api/health/', health_check, name='health_check'),
    path('api/health/detailed/', health_detailed, name='health_detailed'),
    path('api/health/ready/', readiness_check, name='readiness_check'),
    path('api/health/live/', liveness_check, name='liveness_check'),
    
    # API Endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/budgets/', include('budgets.urls')),
    path('api/goals/', include('goals.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/financial/', include('financial_accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)