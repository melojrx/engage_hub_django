from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.enum import statusEventoEnum
from contas.permissions import grupo_administrador_required
from .forms import EventoForm
from .models import Evento, EventoHistorico, Categoria, Subcategoria, StatusEvento
from geopy.geocoders import Nominatim
from core.enum import statusEventoEnum


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
                idStatusEvento=status_aguardando_atendimento,  # Associando o StatusEvento correto
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