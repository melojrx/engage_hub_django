from django.urls import path
from . import views

urlpatterns = [
     path('',  views.estatisticas, name='estatisticas'),
     
]