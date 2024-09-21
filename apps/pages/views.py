from django.shortcuts import render
from django.contrib import messages

# Create your views here.
def index(request):
        messages.debug(request, 'Mensagem de debug')
        return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')