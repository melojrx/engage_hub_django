from rest_framework import serializers
from pages.models import Evento, Categoria, Subcategoria


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
            'dataFim'
        ]
        read_only_fields = ['id', 'numOcorrencia', 'dataInicio', 'dataFim']

    def create(self, validated_data):
        # Gerar numOcorrencia automaticamente, se necessário
        evento = Evento.objects.create(**validated_data)
        return evento