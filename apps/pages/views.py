from base64 import b64encode
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.enum import statusEventoEnum
from contas.permissions import grupo_administrador_required
from .forms import EventoForm
from .models import Evento, EventoHistorico, Categoria, Subcategoria, StatusEvento
from geopy.geocoders import Nominatim
from core.enum import statusEventoEnum

import folium
import datetime

def index(request):
        messages.debug(request, 'Mensagem de debug')
        return render(request, 'index.html')

@login_required()
def home(request):
    if request.user.groups.filter(name__in=['Administrador', 'Governo']).exists():
        return redirect('homeGoverno')
    else:
        return redirect('homeUsuario')

@login_required
def homeUsuario(request):
    # Define o número de linhas por página
    ROWS_PER_PAGE = 3
    page = request.GET.get('page', 1)

    # Filtra os eventos do usuário logado e que não estão finalizados
    listHistoricoEvento = EventoHistorico.objects.filter(
        Q(dataFim__isnull=True) &
        Q(idEvento__idUsuario=request.user)
    ).order_by('-dataInicio')

    # Paginação
    paginator = Paginator(listHistoricoEvento, ROWS_PER_PAGE)
    listHistoricoEvento_paginated = paginator.get_page(page)

    # Codifica o arquivo para base64 para exibir a imagem
    for evento in listHistoricoEvento_paginated:
        if evento.idEvento.file:  # Verifica se há um arquivo de imagem
            # Lê e converte o arquivo de imagem para base64
            with evento.idEvento.file.open('rb') as f:
                evento.idEvento.fileBase64 = b64encode(f.read()).decode()

    return render(request, 'home.html', {'listHistoricoEvento': listHistoricoEvento_paginated})

@login_required()
@grupo_administrador_required(['Administrador', 'Governo'])
def homeGoverno(request):
    is_admin = request.user.groups.filter(name__in=['Administrador', 'Governo']).exists()

    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=2)

    # Obter os IDs dos status
    status_finalizado = StatusEvento.objects.get(txtStatusEvento='Finalizado')
    status_aguardando = StatusEvento.objects.get(txtStatusEvento='Aguardando Atendimento')
    status_em_andamento = StatusEvento.objects.get(txtStatusEvento='Em Andamento')

    # Subconsulta para eventos finalizados após amanhã
    subquery = EventoHistorico.objects.filter(
        idStatusEvento__id=status_finalizado.id,
        dataInicio__gt=tomorrow
    ).values_list('id', flat=True)

    # Lista de eventos históricos que não estão finalizados e não estão na subconsulta
    listHistoricoEvento = EventoHistorico.objects.filter(
        dataFim__isnull=True
    ).exclude(id__in=subquery)

    # Contagens
    contTotal = Evento.objects.aggregate(total=Count('id', distinct=True))['total']
    contFinalizada = EventoHistorico.objects.filter(
        dataFim__isnull=True,
        idStatusEvento__id=status_finalizado.id
    ).values('idEvento').distinct().count()
    contAguardando = EventoHistorico.objects.filter(
        dataFim__isnull=True,
        idStatusEvento__id=status_aguardando.id
    ).values('idEvento').distinct().count()
    contEmAndamento = EventoHistorico.objects.filter(
        dataFim__isnull=True,
        idStatusEvento__id=status_em_andamento.id
    ).values('idEvento').distinct().count()

    # Preparação de dados para o mapa
    listLat = [float(row.idEvento.txtLat) for row in listHistoricoEvento if row.idEvento.txtLat]
    listLong = [float(row.idEvento.txtLong) for row in listHistoricoEvento if row.idEvento.txtLong]
    listOcorrencia = [
        f"<b>Ocorrência:</b> {row.idEvento.numOcorrencia}<br><b>Status:</b> {row.idStatusEvento.txtStatusEvento}<br><b>Problema:</b> {row.idEvento.txtProblema}"
        for row in listHistoricoEvento
    ]
    listStatus = [row.idStatusEvento.id for row in listHistoricoEvento]

    # Criação do mapa com Folium
    map = folium.Map(location=[-22.2312106, -54.8358869], zoom_start=15)

    for lat, lon, ocorrencia, status in zip(listLat, listLong, listOcorrencia, listStatus):
        if status == status_aguardando.id:
            icon_color = "red"
        elif status == status_em_andamento.id:
            icon_color = "blue"
        elif status == status_finalizado.id:
            icon_color = "green"
        else:
            icon_color = "gray"

        folium.Marker(
            location=[lat, lon],
            popup=ocorrencia,
            icon=folium.Icon(color=icon_color, icon="glyphicon glyphicon-exclamation-sign")
        ).add_to(map)

    # Lista de eventos para a div da direita (limite de 10)
    listHistoricoEventoDireita = EventoHistorico.objects.filter(
        ~Q(idStatusEvento__id=status_finalizado.id),
        dataFim__isnull=True
    ).order_by('-dataInicio')[:10]

    # Codificação das imagens em base64
    for t in listHistoricoEventoDireita:
        if t.idEvento.file:
            with t.idEvento.file.open('rb') as f:
                t.idEvento.fileBase64 = b64encode(f.read()).decode()

    # Renderização do mapa
    mapHtml = map._repr_html_()

    context = {
        'is_admin': is_admin,
        'listHistoricoEvento': listHistoricoEvento,
        'listHistoricoEventoDireita': listHistoricoEventoDireita,
        'mapHtml': mapHtml,
        'contTotal': contTotal,
        'contFinalizada': contFinalizada,
        'contAguardando': contAguardando,
        'contEmAndamento': contEmAndamento,
    }

    return render(request, 'homeGoverno.html', context)

@login_required
def iniciar(request):
    if request.method == 'GET':
        form = EventoForm()
        
        # Obtendo a lista de categorias com dataFim como None
        listCategoria = Categoria.objects.filter(dataFim__isnull=True)
        
        # Adicionando as opções de categoria ao formulário
        form.fields['categoria'].choices = [(0, "Selecione...")] + [(cat.id, cat.txtCategoria) for cat in listCategoria]

        return render(request, 'cadastro_evento.html', {'listCategoria': listCategoria, 'form': form})

@login_required
def cadastro_evento(request):
    listCategoria = Categoria.objects.filter(dataFim__isnull=True)

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)

        if form.is_valid():
            subcategoriaSelect = form.cleaned_data.get('subcategoria')
            txtProblema = form.cleaned_data.get('problema')
            txtEndereco = form.cleaned_data.get('endereco')
            txtLat = form.cleaned_data.get('latitude')
            txtLong = form.cleaned_data.get('longitude')
            file = request.FILES.get('file')
            dataInicio = timezone.now()

            # Geocoding: validando latitude e longitude se não foram informados
            if not txtLat and not txtLong:
                geolocator = Nominatim(user_agent="evento_app")
                location = geolocator.geocode(txtEndereco)

                if not location:
                    messages.error(request, 'Endereço não encontrado.')
                    form.fields['categoria'].choices = [(0, "Selecione...")] + [(cat.id, cat.txtCategoria) for cat in listCategoria]
                    return render(request, 'cadastro_evento.html', {'form': form, 'listCategoria': listCategoria})

                txtLat = location.latitude
                txtLong = location.longitude

            # Gerando o número de ocorrência
            numOcorrencia = f"{dataInicio.year}{request.user.id}{dataInicio.day}{dataInicio.month}{dataInicio.hour}{dataInicio.minute}{dataInicio.second}"

            # Criando o evento
            evento = Evento.objects.create(
                idSubcategoria=subcategoriaSelect,
                idUsuario=request.user,
                numOcorrencia=numOcorrencia,
                txtProblema=txtProblema,
                txtEndereco=txtEndereco,
                txtLat=txtLat,
                txtLong=txtLong,
                file=file,
                dataInicio=dataInicio
            )

            # Buscando o status correto no banco de dados
            status_aguardando_atendimento = StatusEvento.objects.get(txtStatusEvento=statusEventoEnum.StatusEventoEnum.AGUARDANDO_ATENDIMENTO.value)

            # Criando o histórico do evento com o status recuperado
            eventoHistorico = EventoHistorico.objects.create(
                idEvento=evento,
                idStatusEvento=status_aguardando_atendimento,  
                idUsuario=request.user,
                dataInicio=dataInicio
            )

            messages.success(request, 'Evento cadastrado com sucesso.')
            return redirect('home')

        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            form.fields['categoria'].choices = [(0, "Selecione...")] + [(cat.id, cat.txtCategoria) for cat in listCategoria]
            return render(request, 'cadastro_evento.html', {'form': form, 'listCategoria': listCategoria})

    else:
        form = EventoForm()
        form.fields['categoria'].choices = [(0, "Selecione...")] + [(cat.id, cat.txtCategoria) for cat in listCategoria]

    return render(request, 'cadastro_evento.html', {'form': form, 'listCategoria': listCategoria})

@login_required
def load_subcategorias(request):
    categoria_id = request.POST.get('id_categoria')
    
    if categoria_id:
        # Filtrar subcategorias com base na categoria selecionada
        subcategorias = Subcategoria.objects.filter(idCategoria_id=categoria_id)
        
        # Renderizar o HTML com as opções de subcategoria
        html = render_to_string('subcategoriaAjax.html', {'subcategorias': subcategorias})
        
        return JsonResponse({'htmlresponse': html})
    else:
        return JsonResponse({'htmlresponse': ''})

@login_required
def selecionarEvento(request, num_ocorrencia):
    eventoHistorico = get_object_or_404(EventoHistorico, idEvento__numOcorrencia=num_ocorrencia, dataFim__isnull=True)

    listEventoHistorico = EventoHistorico.objects.filter(
        idEvento=eventoHistorico.idEvento
    ).select_related('idEvento', 'idStatusEvento', 'idUsuario')

    # Codificar a imagem em base64 para o evento principal
    if eventoHistorico.idEvento.file:
        with eventoHistorico.idEvento.file.open('rb') as f:
            eventoHistorico.idEvento.fileBase64 = b64encode(f.read()).decode()

    # Codificar a imagem em base64 para os eventos históricos
    for t in listEventoHistorico:
        if t.idEvento.file:
            with t.idEvento.file.open('rb') as f:
                t.idEvento.fileBase64 = b64encode(f.read()).decode()

    # Verificar as permissões do usuário
    if request.user.groups.filter(name__in=['Governo', 'Administrador']).exists():
        template_name = 'visualizarEventoGoverno.html'
    else:
        template_name = 'visualizarEvento.html'

    return render(request, template_name, {
        'eventoHistorico': eventoHistorico,
        'listEventoHistorico': listEventoHistorico
    })