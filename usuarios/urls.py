from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views
from .forms import UsuarioLoginForm
from turnos.forms import UsuarioRegistroForm

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='usuarios/login.html',
        authentication_form=UsuarioLoginForm,
        redirect_authenticated_user=True
    ), name='login'),
    path('admin/usuarios/<int:usuario_id>/eliminar/', views.admin_usuario_eliminar, name='admin_usuario_eliminar'),
    path('admin/usuarios/crear/', views.admin_usuario_crear, name='admin_usuario_crear'),
    path('admin/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin/usuarios/<int:usuario_id>/editar/', views.admin_usuario_editar, name='admin_usuario_editar'),
    path('perfil/', views.perfil, name='perfil'),
    path('logout/', LogoutView.as_view(
        template_name='usuarios/logout.html',
        next_page='login',
        http_method_names=['get', 'post'],
        extra_context={'clear_session': True}
    ), name='logout'),
    # Ruta alternativa para forzar el cierre de sesión
    path('logout-force/', views.logout_view, name='logout_force'),

    path('registro/', views.registro, name='registro'),
    path('password_reset/', PasswordResetView.as_view(
        template_name='usuarios/password_reset_form.html',
        email_template_name='usuarios/password_reset_email.html',
        subject_template_name='usuarios/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='usuarios/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='usuarios/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='usuarios/password_reset_complete.html'
    ), name='password_reset_complete'),
]