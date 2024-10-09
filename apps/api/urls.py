from django.urls import path
from api import views
from .views import (
    EventoListCreateAPIView,
    CategoriaListAPIView,
    SubcategoriaListAPIView,
    LoginAPIView,
    LogoutAPIView,
    EventoRetrieveAPIView
)


urlpatterns = [
    path('eventos/', EventoListCreateAPIView.as_view(), name='evento-list-create'),
    path('eventos/<int:pk>/', EventoRetrieveAPIView.as_view(), name='evento-detail'),
    path('categorias/', CategoriaListAPIView.as_view(), name='categoria-list'),
    path('subcategorias/', SubcategoriaListAPIView.as_view(), name='subcategoria-list'),
    path('login/', LoginAPIView.as_view(), name='api-login'),
    path('logout/', LogoutAPIView.as_view(), name='api-logout'),
]