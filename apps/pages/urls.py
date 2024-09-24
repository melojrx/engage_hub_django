from django.urls import path 
from pages import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('home/', views.home, name='home'),
    path('homeGoverno/', views.homeGoverno, name='homeGoverno'),
    path('iniciar/', views.iniciar, name='iniciar'),
    path('cadastrar/', views.cadastro_evento, name='cadastro_evento'),
    path('loadSubcategoria/', views.load_subcategorias, name='load_subcategorias'),
]