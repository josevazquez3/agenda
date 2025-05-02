from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.contrib import messages
from django import forms
from django.http import Http404, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import UsuarioRolEstadoForm
from turnos.forms import UsuarioRegistroForm

def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, 'Registro exitoso. Ahora puede iniciar sesión.')
            return redirect('login')
    else:
        form = UsuarioRegistroForm()
    
    return render(request, 'usuarios/registro.html', {
        'form': form
    })

@login_required
def obtener_paciente(request, paciente_id):
    # Verificar si el usuario es staff o es el propio paciente
    if not request.user.is_staff and request.user.id != paciente_id:
        raise Http404("No tiene permisos para ver este paciente")
    
    # Obtener el paciente
    User = get_user_model()
    paciente = get_object_or_404(User, id=paciente_id)
    
    return paciente

class UsuarioCreacionForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 
                 'DNI', 'telefono', 'obra_social', 'calle', 'numero', 'piso', 'departamento', 'foto']

class PerfilForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'DNI', 'telefono', 'obra_social',
                 'calle', 'numero', 'piso', 'departamento', 'foto']

@login_required
def admin_usuarios(request):
    # Verificar si el usuario es staff
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener todos los usuarios
    User = get_user_model()
    usuarios = User.objects.all().order_by('-date_joined')
    
    return render(request, 'usuarios/gestionar_usuarios.html', {
        'usuarios': usuarios
    })

@login_required
def admin_usuario_crear(request):
    # Verificar si el usuario es staff
    if not request.user.is_staff:
        return redirect('inicio')
    
    if request.method == 'POST':
        form = UsuarioCreacionForm(request.POST, request.FILES)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, 'Usuario creado exitosamente')
            return redirect('admin_usuarios')
    else:
        form = UsuarioCreacionForm()
    
    return render(request, 'admin/usuarios_crear.html', {
        'form': form
    })

@login_required
def perfil(request):
    # Obtener el usuario actual
    usuario = request.user
    
    if request.method == 'POST':
        form = PerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=usuario)
    
    return render(request, 'usuarios/perfil.html', {
        'form': form
    })

@login_required
def admin_usuario_editar(request, usuario_id):
    # Verificar si el usuario es staff
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener el usuario a editar
    User = get_user_model()
    usuario = get_object_or_404(User, id=usuario_id)
    
    if request.method == 'POST':
        perfil_form = PerfilForm(request.POST, request.FILES, instance=usuario)
        rol_form = UsuarioRolEstadoForm(request.POST, instance=usuario)
        
        if perfil_form.is_valid() and rol_form.is_valid():
            # Guardar cambios del perfil
            perfil_form.save()
            
            # Guardar cambios de rol y estado
            usuario = rol_form.save(commit=False)
            
            # Actualizar permisos basados en el rol
            if rol_form.cleaned_data['rol'] == 'admin':
                usuario.is_staff = True
            elif rol_form.cleaned_data['rol'] == 'secretaria':
                usuario.is_staff = True
            else:
                usuario.is_staff = False
            
            usuario.save()
            
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('admin_usuarios')
    else:
        perfil_form = PerfilForm(instance=usuario)
        rol_form = UsuarioRolEstadoForm(instance=usuario)
    
    return render(request, 'admin/usuario_editar.html', {
        'perfil_form': perfil_form,
        'rol_form': rol_form,
        'usuario': usuario
    })

@login_required
def admin_usuario_eliminar(request, usuario_id):
    # Verificar si el usuario es staff
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener el usuario a eliminar
    User = get_user_model()
    usuario = get_object_or_404(User, id=usuario_id)
    
    # No permitir eliminar el propio usuario
    if usuario.id == request.user.id:
        messages.error(request, 'No puede eliminar su propio usuario')
        return redirect('admin_usuarios')
    
    # Eliminar el usuario
    usuario.delete()
    messages.success(request, 'Usuario eliminado exitosamente')
    return redirect('admin_usuarios')

def logout_view(request):
    # Forzar el cierre de sesión
    logout(request)
    
    # Establecer cabeceras para evitar caché
    response = HttpResponse("<script>window.location.href = '/usuarios/login/';</script>")
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    # Eliminar cookies de sesión
    if 'sessionid' in request.COOKIES:
        response.delete_cookie('sessionid')
    if 'csrftoken' in request.COOKIES:
        response.delete_cookie('csrftoken')
    
    return response
