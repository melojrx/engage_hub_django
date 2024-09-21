from multiprocessing import context
from urllib import request
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from contas.permissions import grupo_administrador_required

# Create your views here.
def index(request):
        messages.debug(request, 'Mensagem de debug')
        return render(request, 'index.html')

@login_required()
def home(request):
    return render(request, 'home.html')

@login_required()
@grupo_administrador_required(['Administrador', 'Governo'])
def homeGoverno(request):
        is_admin = request.user.groups.filter(name='Administrador').exists()
        context = {
        'is_admin': is_admin}
        return render(request, 'homeGoverno.html', context)