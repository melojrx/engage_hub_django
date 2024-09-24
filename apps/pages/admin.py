from django.contrib import admin
from pages.models import Categoria, Subcategoria, Evento, StatusEvento, EventoHistorico, EventoObservacao

# Register your models here.
class EventoAdmin(admin.ModelAdmin):
    list_display = ('numOcorrencia', 'txtProblema', 'dataInicio', 'idUsuario')
    search_fields = ('numOcorrencia', 'txtProblema', 'Categoria', 'StatusEvento')
    list_filter = ('dataInicio',)
    
admin.site.register(Categoria)
admin.site.register(Subcategoria)
admin.site.register(Evento, EventoAdmin)
admin.site.register(StatusEvento)
admin.site.register(EventoHistorico)
admin.site.register(EventoObservacao)