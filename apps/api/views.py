from requests import Response
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import EventoSerializer, CategoriaSerializer, SubcategoriaSerializer
from pages.models import Evento, Categoria, Subcategoria
from django.contrib.auth import authenticate, login, logout
from rest_framework import status


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        logout(request)
        return Response({'message': 'Logout bem-sucedido.'}, status=status.HTTP_200_OK)
    
class LoginAPIView(APIView):
    """
    Endpoint para autenticação de usuários.

    **Métodos:**
    - POST: Autentica o usuário com email e senha.
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)  # Cria a sessão
            return Response({'message': 'Login bem-sucedido'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

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
        # Retorna apenas os eventos do usuário autenticado
        return Evento.objects.filter(idUsuario=self.request.user)

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
 
#Visualizar Detalhes de um Evento    
class EventoRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = EventoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Evento.objects.filter(idUsuario=self.request.user)