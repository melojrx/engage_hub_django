from django.shortcuts import redirect
from django.contrib import messages

def grupo_administrador_required(groups):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Você não tem permissão para acessar esta página.')
                return redirect('home')
                # return HttpResponseForbidden('Você não tem permissão para acessar esta página.')
        return wrapper
    return decorator

def grupo_usuario_required(groups):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'Você não tem permissão para acessar esta página.')
                return redirect('home')  # Substitua 'home' pela URL apropriada
        return wrapper
    return decorator