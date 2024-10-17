from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from pages.models import Evento, Categoria, Subcategoria
from django.utils import timezone


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
    file_path = serializers.CharField(write_only=True, required=False)
    file = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            'id',
            'idSubcategoria',
            'txtProblema',
            'txtEndereco',
            'txtLat',
            'txtLong',
            'file_path',
            'file',
            'dataInicio',
            'dataFim',
            'nome_usuario',
            'numOcorrencia',  # Certifique-se de incluir o campo aqui
        ]
        read_only_fields = ['id', 'numOcorrencia', 'dataInicio', 'dataFim']

    def create(self, validated_data):
        file_path = validated_data.pop('file_path', None)
        idUsuario = validated_data.get('idUsuario')
        dataInicio = timezone.now()

        # Gerando o número de ocorrência
        numOcorrencia = f"{dataInicio.year}{idUsuario.id}{dataInicio.day}{dataInicio.month}{dataInicio.hour}{dataInicio.minute}{dataInicio.second}"

        # Criando o evento com numOcorrencia e dataInicio
        evento = Evento.objects.create(
            numOcorrencia=numOcorrencia,
            dataInicio=dataInicio,
            **validated_data
        )

        if file_path:
            evento.file.name = file_path  # Atribui o caminho relativo ao campo 'file'
            evento.save()
        return evento

    def get_file(self, obj):
        request = self.context.get('request')
        if obj.file:
            return request.build_absolute_uri(obj.file.url)
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        nome_usuario = representation.get('nome_usuario', '')
        if nome_usuario:
            representation['nome_usuario'] = nome_usuario.title()
        return representation