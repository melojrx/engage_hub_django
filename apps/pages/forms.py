from django import forms
from pages.models import Evento, Categoria, Subcategoria

class EventoForm(forms.ModelForm):
    problema = forms.CharField(
        label='Qual o problema?',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descreva o problema'})
    )
    
    endereco = forms.CharField(
        label='Qual o endereço da ocorrência:',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Informe o endereço'})
    )
    latitude = forms.CharField(
        label='Lat:',
        required=True,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    longitude = forms.CharField(
        label='Long:',
        required=True,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(dataFim__isnull=True),
        empty_label="Selecione...",
        label="Categoria",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subcategoria = forms.ModelChoiceField(
        queryset=Subcategoria.objects.filter(dataFim__isnull=True),
        empty_label="Selecione...",
        label="Subcategoria",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    file = forms.FileField(
        label='Insira uma foto:',
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Evento
        fields = ['problema', 'endereco', 'latitude', 'longitude', 'categoria', 'subcategoria', 'file']
