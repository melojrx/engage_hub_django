from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import EventoSerializer, CategoriaSerializer, SubcategoriaSerializer
from pages.models import Evento, Categoria, Subcategoria


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# View para listar e criar demandas (Eventos)
class EventoListCreateAPIView(generics.ListCreateAPIView):
    """
    Lista todos os eventos do usuário autenticado ou cria um novo evento.

    **Métodos:**
    - GET: Retorna uma lista de eventos.
    - POST: Cria um novo evento.

    **Autenticação:**
    - Requer que o usuário esteja autenticado.
    """
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """
        Retorna todos os eventos de todos os usuários que ainda não estão finalizados
        (onde `dataFim` está vazio) e ordenados do mais recente para o mais antigo.
        """
        return Evento.objects.filter(
            dataFim__isnull=True  # Apenas eventos onde `dataFim` está vazio (não finalizados)
        ).order_by('-dataInicio')  # Ordenar do mais recente para o mais antigo

    def perform_create(self, serializer):
        # Define o usuário autenticado como o criador do evento
        serializer.save(idUsuario=self.request.user)

# View para listar categorias
class CategoriaListAPIView(generics.ListAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

# View para listar subcategorias
class SubcategoriaListAPIView(generics.ListAPIView):
    queryset = Subcategoria.objects.all()
    serializer_class = SubcategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria_id')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset
 
#Visualizar Detalhes de um Evento    
class EventoRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Evento.objects.filter(idUsuario=self.request.user)