from base64 import b64encode
from django.db.models.functions import Concat
from django.db.models import Q, Count, Max, Value, CharField, F
from django.forms import CharField
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.enum import statusEventoEnum
from contas.permissions import grupo_administrador_required, grupo_usuario_required
from .forms import EventoForm
from .models import MyUser, Evento, EventoHistorico, Categoria, EventoObservacao, Subcategoria, StatusEvento
from geopy.geocoders import Nominatim
from core.enum import statusEventoEnum
from django.contrib.auth import get_user_model

User = get_user_model()

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
@grupo_usuario_required(['Usuario'])
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

    # Obter os status e adicioná-los ao contexto
    status_aguardando = StatusEvento.objects.get(txtStatusEvento='Aguardando Atendimento')
    status_em_andamento = StatusEvento.objects.get(txtStatusEvento='Em Andamento')
    status_finalizado = StatusEvento.objects.get(txtStatusEvento='Finalizado')

    # Verificar as permissões do usuário
    if request.user.groups.filter(name__in=['Governo', 'Administrador']).exists():
        template_name = 'visualizarEventoGoverno.html'
    else:
        template_name = 'visualizarEvento.html'

    return render(request, template_name, {
        'eventoHistorico': eventoHistorico,
        'listEventoHistorico': listEventoHistorico,
        'status_aguardando': status_aguardando,
        'status_em_andamento': status_em_andamento,
        'status_finalizado': status_finalizado,
    })

@login_required
def cadastrarObservacao(request, evento_historico_id, num_ocorrencia):
    if request.method == 'POST':
        txtObservacao = request.POST.get('observacao', '').strip()
        dataInicio = timezone.now()

        try:
            eventoHistorico = get_object_or_404(EventoHistorico, id=evento_historico_id)
            eventoObservacao = EventoObservacao(
                idEventoHistorico=eventoHistorico,
                idUsuario=request.user,
                txtObservacao=txtObservacao,
                dataInicio=dataInicio
            )
            eventoObservacao.save()
            messages.success(request, 'Observação cadastrada com sucesso.')
        except Exception as e:
            messages.error(request, f'Erro: {e}')
        
        return redirect('selecionarEvento', num_ocorrencia=num_ocorrencia)
    else:
        return redirect('selecionarEvento', num_ocorrencia=num_ocorrencia)

@login_required
def atender(request, num_ocorrencia):
    try:
        data = timezone.now()

        evento = get_object_or_404(Evento, numOcorrencia=num_ocorrencia)
        # Fecha o EventoHistorico atual
        eventoHistorico_atual = EventoHistorico.objects.filter(idEvento=evento, dataFim__isnull=True).first()
        if eventoHistorico_atual:
            eventoHistorico_atual.dataFim = data
            eventoHistorico_atual.save()
        
        # Obter o StatusEvento correspondente a "Em Andamento"
        status_em_andamento = get_object_or_404(StatusEvento, txtStatusEvento='Em Andamento')

        # Criar um novo EventoHistorico com o status "Em Andamento"
        newEventoHistorico = EventoHistorico(
            idEvento=evento,
            idStatusEvento=status_em_andamento,
            idUsuario=request.user,
            dataInicio=data
        )
        newEventoHistorico.save()

        messages.success(request, f'Evento alterado para: {status_em_andamento.txtStatusEvento}.')
    except Exception as e:
        messages.error(request, f'Erro: {e}')

    return redirect('selecionarEvento', num_ocorrencia=num_ocorrencia)

@login_required
def finalizar(request, num_ocorrencia):
    try:
        data = timezone.now()

        evento = get_object_or_404(Evento, numOcorrencia=num_ocorrencia)
        # Fecha o EventoHistorico atual
        eventoHistorico_atual = EventoHistorico.objects.filter(idEvento=evento, dataFim__isnull=True).first()
        if eventoHistorico_atual:
            eventoHistorico_atual.dataFim = data
            eventoHistorico_atual.save()
        
        # Obter o StatusEvento correspondente a "Finalizado"
        status_finalizado = get_object_or_404(StatusEvento, txtStatusEvento='Finalizado')

        # Criar um novo EventoHistorico com o status "Finalizado"
        newEventoHistorico = EventoHistorico(
            idEvento=evento,
            idStatusEvento=status_finalizado,
            idUsuario=request.user,
            dataInicio=data
        )
        newEventoHistorico.save()

        messages.success(request, f'Evento alterado para: {status_finalizado.txtStatusEvento}.')
    except Exception as e:
        messages.error(request, f'Erro: {e}')

    return redirect('selecionarEvento', num_ocorrencia=num_ocorrencia)

@login_required
def search(request):
    numOcorrencia = request.GET.get('numOcorrencia', '').strip()
    if not numOcorrencia:
        messages.error(request, 'Por favor, insira um número de ocorrência para pesquisar.')
        return redirect('homeGoverno')

    eventoHistorico = EventoHistorico.objects.filter(
        dataFim__isnull=True,
        idEvento__numOcorrencia=numOcorrencia
    ).first()

    if eventoHistorico is None:
        messages.error(request, f'Ocorrência {numOcorrencia} não encontrada.')
        return redirect('homeGoverno')

    return redirect('selecionarEvento', num_ocorrencia=eventoHistorico.idEvento.numOcorrencia)

@login_required
def prepare_search(request):
    list_categoria = Categoria.objects.filter(dataFim__isnull=True)
    list_status = StatusEvento.objects.filter(dataFim__isnull=True)
    list_usuario = MyUser.objects.all()

    context = {
        'listCategoria': list_categoria,
        'listStatus': list_status,
        'listUsuario': list_usuario,
    }
    return render(request, 'filtraEventos.html', context)

@login_required
def evento_search(request):
    list_categoria = Categoria.objects.filter(dataFim__isnull=True)
    list_status = StatusEvento.objects.filter(dataFim__isnull=True)
    list_usuario = User.objects.all()

    # Obtendo os parâmetros de busca
    numOcorrenciaSearch = request.GET.get('numOcorrenciaSearch', '').strip()
    statusSearch = request.GET.get('statusSearch', '').strip()
    categoriaSearch = request.GET.get('categoriaSearch', '').strip()
    dataInicioSearch = request.GET.get('dataInicioSearch', '').strip()
    dataFimSearch = request.GET.get('dataFimSearch', '').strip()
    userSearch = request.GET.get('userSearch', '').strip()

    if not any([numOcorrenciaSearch, statusSearch, categoriaSearch, dataInicioSearch, dataFimSearch, userSearch]):
        messages.error(request, 'Informe pelo menos um critério de pesquisa.')
        context = {
            'listCategoria': list_categoria,
            'listStatus': list_status,
            'listUsuario': list_usuario,
        }
        return render(request, 'filtraEventos.html', context)

    query_search = EventoHistorico.objects.filter(dataFim__isnull=True)

    if numOcorrenciaSearch:
        query_search = query_search.filter(idEvento__numOcorrencia=numOcorrenciaSearch)

    if statusSearch:
        query_search = query_search.filter(idStatusEvento__id=statusSearch)

    if categoriaSearch:
        query_search = query_search.filter(idEvento__idSubcategoria__idCategoria__id=categoriaSearch)

    if userSearch:
        query_search = query_search.filter(idEvento__idUsuario__email__icontains=userSearch)

    if dataInicioSearch and dataFimSearch:
        query_search = query_search.filter(idEvento__dataInicio__range=[dataInicioSearch, dataFimSearch])
    elif dataInicioSearch:
        query_search = query_search.filter(idEvento__dataInicio__gte=dataInicioSearch)
    elif dataFimSearch:
        query_search = query_search.filter(idEvento__dataInicio__lte=dataFimSearch)

    query_search = query_search.order_by('-dataInicio')

    # Paginação
    ROWS_PER_PAGE = 5
    page = request.GET.get('page', 1)
    paginator = Paginator(query_search, ROWS_PER_PAGE)

    try:
        list_evento_historico_search = paginator.page(page)
    except PageNotAnInteger:
        list_evento_historico_search = paginator.page(1)
    except EmptyPage:
        list_evento_historico_search = paginator.page(paginator.num_pages)

    if not list_evento_historico_search:
        messages.error(request, 'A pesquisa não encontrou nenhum resultado.')
        context = {
            'listCategoria': list_categoria,
            'listStatus': list_status,
            'listUsuario': list_usuario,
        }
        return render(request, 'filtraEventos.html', context)

    context = {
        'listCategoria': list_categoria,
        'listStatus': list_status,
        'listUsuario': list_usuario,
        'listEventoHistoricoSearch': list_evento_historico_search,
        'numOcorrenciaSearch': numOcorrenciaSearch,
        'statusSearch': statusSearch,
        'categoriaSearch': categoriaSearch,
        'dataInicioSearch': dataInicioSearch,
        'dataFimSearch': dataFimSearch,
        'userSearch': userSearch,
    }
    return render(request, 'filtraEventos.html', context)

def user_autocomplete(request):
    user_search = request.GET.get('userSearch', '')
    results = []
    if user_search:
        users = User.objects.filter(email__icontains=user_search)[:10]
        results = [{'label': user.email, 'value': user.email} for user in users]
    return JsonResponse({'results': results})