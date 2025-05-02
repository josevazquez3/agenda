from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name='inicio'),
    path('turnos/', include('turnos.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('appointments/', include('appointment.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)