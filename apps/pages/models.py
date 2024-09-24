from django.db import models
from django.utils import timezone
from contas.models import MyUser
from django.contrib.auth import get_user_model

user = get_user_model()

class Categoria(models.Model):
    id = models.AutoField('id_categoria', primary_key=True)
    txtCategoria = models.CharField('categoria', max_length=50)
    dataInicio = models.DateTimeField('data_inicio', default=timezone.now)
    dataFim = models.DateTimeField('data_fim', blank=True, null=True)
    
    def __str__(self):
        return self.txtCategoria


class Subcategoria(models.Model):
    id = models.AutoField('id_subcategoria', primary_key=True)
    txtSubcategoria = models.CharField('subcategoria', max_length=100)
    dataInicio = models.DateTimeField('dat_inicio', default=timezone.now)
    txtDescricao = models.CharField('txt_descricao', max_length=500)
    dataFim = models.DateTimeField('data_fim', blank=True, null=True)
    
    idCategoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.txtSubcategoria

    
class Evento(models.Model):
    id = models.AutoField(primary_key=True)
    idSubcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE)
    idUsuario = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    numOcorrencia = models.CharField('num_ocorrencia', max_length=11)
    txtProblema = models.CharField('Problema', max_length=1000)
    txtEndereco = models.CharField('Endereco', max_length=500)
    txtLat = models.CharField('latitude', max_length=20)
    txtLong = models.CharField('longitude', max_length=20)
    file = models.FileField('Insira uma foto:', upload_to='uploads/', blank=True, null=True)
    dataInicio = models.DateTimeField('dat_inicio', default=timezone.now)
    dataFim = models.DateTimeField('dat_fim', blank=True, null=True)
    
    def __str__(self):
        return self.numOcorrencia

    
class StatusEvento(models.Model):
    id = models.AutoField('id_status_evento', primary_key=True)
    txtStatusEvento = models.CharField('status_evento', max_length=50)
    dataInicio = models.DateTimeField('data_inicio', default=timezone.now)
    dataFim = models.DateTimeField('data_fim', blank=True, null=True)

    def __str__(self):
        return self.txtStatusEvento


class EventoHistorico(models.Model):    
    id = models.AutoField('id_evento_historico_ehi', primary_key=True)
    idEvento = models.ForeignKey('Evento', on_delete=models.CASCADE, db_column='id_evento_ehi', related_name="historicos")
    idStatusEvento = models.ForeignKey('StatusEvento', on_delete=models.CASCADE, db_column='id_status_evento_ehi', related_name="historicos")
    idUsuario = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='id_usuario_ehi', related_name="historicos")  # Ajustado para MyUser
    dataInicio = models.DateTimeField('dat_inicio_ehi', null=False)
    dataFim = models.DateTimeField('dat_fim_ehi', blank=True, null=True)

    listObservacao = models.ManyToManyField("EventoObservacao", related_name="observacoesHistorico")

    def __str__(self):
        return f"Histórico do Evento {self.idEvento} - {self.idStatusEvento}"


class EventoObservacao(models.Model): 
    id = models.AutoField('id_evento_observacao_eob', primary_key=True)
    idEventoHistorico = models.ForeignKey('EventoHistorico', on_delete=models.CASCADE, db_column='id_evento_historico_eob', related_name="observacoes")
    idUsuario = models.ForeignKey(MyUser, on_delete=models.CASCADE, db_column='id_usuario_eob', related_name="observacoesUsuario")  # Ajustado para MyUser
    txtObservacao = models.CharField('txt_evento_observacao_eob', max_length=500)
    dataInicio = models.DateTimeField('dat_inicio_eob', null=False)
    dataFim = models.DateTimeField('dat_fim_eob', blank=True, null=True)

    def __str__(self):
        return self.txtObservacao

