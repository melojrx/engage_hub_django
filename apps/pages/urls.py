from django.urls import path 
from pages import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('home/', views.home, name='home'),
    path('homeUsuario/', views.homeUsuario, name='homeUsuario'),
    path('homeGoverno/', views.homeGoverno, name='homeGoverno'),
    path('iniciar/', views.iniciar, name='iniciar'),
    path('cadastrar/', views.cadastro_evento, name='cadastro_evento'),
    path('loadSubcategoria/', views.load_subcategorias, name='load_subcategorias'),
    path('ocorrencia/<int:num_ocorrencia>/', views.selecionarEvento, name='selecionarEvento'),
    path('ocorrencia/<int:num_ocorrencia>/cadastrarObservacao/<int:evento_historico_id>/', views.cadastrarObservacao, name='cadastrarObservacao'),
    path('ocorrencia/<int:num_ocorrencia>/atender/', views.atender, name='atender'),
    path('ocorrencia/<int:num_ocorrencia>/finalizar/', views.finalizar, name='finalizar'),
    path('search/', views.search, name='search'),
    path('prepare_search/', views.prepare_search, name='prepare_search'),
    path('evento_search/', views.evento_search, name='evento_search'),
    path('user_autocomplete/', views.user_autocomplete, name='user_autocomplete'),
]