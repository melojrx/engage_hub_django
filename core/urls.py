from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework import permissions

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from apps.api.views import MyTokenObtainPairView  


schema_view = get_schema_view(
    openapi.Info(
        title="Engage Hub API",
        default_version='v1',
        description="API para gerenciamento de eventos do Engage Hub",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contato@engagehub.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],  # Removido se não necessário
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('contas.urls')),
    path('', include('pages.urls')),
    path('estatisticas/', include('estatisticas.urls')), 
    
    path('api/v1/', include('api.urls')),
    
     # Endpoints JWT personalizados
    path('api/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
     # Rotas para a documentação Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)