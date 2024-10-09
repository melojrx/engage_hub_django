from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from contas.permissions import grupo_administrador_required
from django.contrib import messages


@login_required()
@grupo_administrador_required(['Administrador', 'Governo'])
def estatisticas(request):
    messages.info(request, 'A funcionalidade "Estatísticas" está em desenvolvimento.')
    return render(request, 'estatisticas.html')

