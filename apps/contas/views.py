from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from contas.forms import CustomUserCreationForm

def timeout_view(request):
    return render(request, 'timeout.html')

@csrf_exempt
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Verifica os grupos do usuário autenticado
            if user.groups.filter(name__in=['Administrador', 'Governo']).exists():
                return redirect('homeGoverno')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Email ou senha inválidos')
    
    return render(request, 'login.html')

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_valid = False
            usuario.save()
            group = Group.objects.get(name='Usuario')
            usuario.groups.add(group)
            messages.success(request, 'Registrado. Agora faça o login para começar!')
            return redirect('login')
        else:
            # Tratar quando usuario já existe, senhas... etc...
            messages.error(request, 'A senha deve ter pelo menos 1 caractere maiúsculo, \
                1 caractere especial e no minimo 8 caracteres.')
    form = CustomUserCreationForm()
    return render(request, "register.html",{"form": form})

def logout_view(request):
    logout(request)
    return redirect('index')