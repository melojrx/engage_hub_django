from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from pages.models import Evento, Categoria, Subcategoria


User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD  # Define o campo de identificação como email

    def validate(self, attrs):
        # Assegura que o email e senha foram fornecidos
        email = attrs.get("email")
        password = attrs.get("password")

        if email is None or password is None:
            raise serializers.ValidationError("Email e senha são necessários.")

        return super().validate(attrs)

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'txtCategoria']

class SubcategoriaSerializer(serializers.ModelSerializer):
    idCategoria = CategoriaSerializer(read_only=True)

    class Meta:
        model = Subcategoria
        fields = ['id', 'txtSubcategoria', 'idCategoria']

class EventoSerializer(serializers.ModelSerializer):
    nome_usuario = serializers.CharField(source='idUsuario.first_name', read_only=True)
    """
    Serializer para o modelo Evento.

    **Campos:**
    - id: ID do evento.
    - idSubcategoria: ID da subcategoria associada.
    - txtProblema: Descrição do problema.
    - txtEndereco: Endereço do evento.
    - txtLat: Latitude do local.
    - txtLong: Longitude do local.
    - file: Foto associada ao evento.
    - dataInicio: Data e hora de início do evento.
    - dataFim: Data e hora de término do evento.
    """
    class Meta:
        model = Evento
        fields = [
            'id',
            'idSubcategoria',
            'txtProblema',
            'txtEndereco',
            'txtLat',
            'txtLong',
            'file',
            'dataInicio',
            'dataFim',
            'nome_usuario',
        ]
        read_only_fields = ['id', 'numOcorrencia', 'dataInicio', 'dataFim']
        
    def create(self, validated_data):
        # Gerar numOcorrencia automaticamente, se necessário
        evento = Evento.objects.create(**validated_data)
        return evento
    
    def to_representation(self, instance):
        """
        Sobrescreve a representação para capitalizar o nome do usuário.
        """
        representation = super().to_representation(instance)
        nome_usuario = representation.get('nome_usuario', '')
        if nome_usuario:
            representation['nome_usuario'] = nome_usuario.title()  # Converte para primeira letra maiúscula
        return representation