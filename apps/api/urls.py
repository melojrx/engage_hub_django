from django.urls import path
from .views import (
    EventoListCreateAPIView,
    CategoriaListAPIView,
    FileUploadView,
    SubcategoriaListAPIView,
    EventoRetrieveAPIView,
    UploadURLView
)

urlpatterns = [
    path('eventos/', EventoListCreateAPIView.as_view(), name='evento-list-create'),
    path('eventos/<int:pk>/', EventoRetrieveAPIView.as_view(), name='evento-detail'),
    path('categorias/', CategoriaListAPIView.as_view(), name='categoria-list'),
    path('subcategorias/', SubcategoriaListAPIView.as_view(), name='subcategoria-list'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),          
    path('upload_url/', UploadURLView.as_view(), name='upload-url'),
   
]