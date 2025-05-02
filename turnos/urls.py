from django.urls import path
from . import views
from . import admin_views
from . import historial_views

urlpatterns = [
    # Rutas principales
    path('', views.inicio, name='inicio'),
    path('contacto/', views.contacto, name='contacto'),
    path('solicitar-turno/', views.solicitar_turno, name='solicitar_turno'),
    path('calendario/', views.calendario, name='calendario'),
    path('dias-disponibles/', views.dias_disponibles, name='dias_disponibles'),    
    path('horarios-disponibles/<str:fecha>/', views.horarios_disponibles, name='horarios_disponibles'),
    path('confirmar-turno/', views.confirmar_turno, name='confirmar_turno'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('cancelar-turno/<int:turno_id>/', views.cancelar_turno, name='cancelar_turno'),
    
    # Rutas administrativas
    path('admin/dias-disponibles/', admin_views.dias_disponibles, name='admin_dias_disponibles'),
    path('admin/dias/agregar/', admin_views.dias_disponibles, name='admin_dias_agregar'),
    path('admin/configurar-dias/', admin_views.configurar_dias, name='admin_configurar_dias'),
    path('admin/dias/<str:fecha>/detalle/', admin_views.obtener_detalle_dia, name='admin_detalle_dia'),
    path('admin/dias/actualizar/', admin_views.actualizar_dia, name='admin_actualizar_dia'),
    path('admin/dias/configurar-rango/', admin_views.configurar_rango_dias, name='admin_configurar_rango_dias'),
    path('admin/solicitar-turno/', views.admin_solicitar_turno, name='admin_solicitar_turno'),
    path('admin/confirmar-turno/', views.admin_confirmar_turno, name='admin_confirmar_turno'),
    path('admin/horarios/configurar/', admin_views.configurar_horarios, name='admin_configurar_horarios'),
    path('admin/horarios/excepcion/', admin_views.agregar_excepcion, name='admin_agregar_excepcion'),
    path('admin/horarios/<int:horario_id>/eliminar/', admin_views.eliminar_horario, name='admin_eliminar_horario'),
    path('admin/crear-disponibilidad/', views.crear_disponibilidad, name='crear_disponibilidad'),
    path('admin/usuarios/', admin_views.usuarios, name='admin_usuarios'),
    path('admin/listado-turnos/', admin_views.listado_turnos, name='admin_listado_turnos'),
    path('admin/horarios/get_horarios/', admin_views.get_horarios, name='admin_get_horarios'),
    path('admin/historial-pacientes/', views.historial_paciente_lista, name='historial_paciente_lista'),
    path('admin/historial-pacientes/<int:paciente_id>/', views.historial_paciente_ver, name='historial_paciente_ver'),
    path('admin/historial-pacientes/<int:paciente_id>/pdf/', views.historial_paciente_pdf, name='historial_paciente_pdf'),
    path('admin/historial-pacientes/<int:paciente_id>/no-disponible/', views.historial_paciente_nodisponible, name='historial_paciente_nodisponible'),
    
    # URLs para la gestión del historial de pacientes
    path('admin/historial/<int:paciente_id>/', historial_views.admin_historial_paciente, name='admin_historial_paciente'),
    path('admin/historial/<int:paciente_id>/get_historial/', historial_views.get_historial, name='get_historial'),
    path('admin/historial/crear/', historial_views.crear_registro, name='crear_historial'),
    path('admin/historial/<int:registro_id>/obtener/', historial_views.obtener_registro, name='obtener_registro'),
    path('admin/historial/<int:registro_id>/actualizar/', historial_views.actualizar_registro, name='actualizar_registro'),
    path('admin/historial/<int:registro_id>/eliminar/', historial_views.eliminar_registro, name='eliminar_registro'),
    
    # Nueva ruta unificada para gestión de días y horarios
    path('admin/gestion-disponibilidad/', admin_views.gestion_disponibilidad, name='admin_gestion_disponibilidad'),
    path('admin/dias/<int:dia_id>/eliminar/', admin_views.eliminar_dia, name='admin_eliminar_dia'),
    
    # Rutas para gestión de horarios por día
    path('admin/horarios-dia/<str:fecha>/', admin_views.horarios_dia, name='admin_horarios_dia'),
    path('admin/dias/horarios/', admin_views.horarios_dia, name='admin_horarios_dia_ver'),
    path('admin/dias/horarios/guardar/', admin_views.horarios_guardar, name='admin_horarios_guardar'),
    path('admin/calendario/', admin_views.admin_calendario, name='admin_calendario'),
    path('admin/turnos/', admin_views.listado_turnos, name='admin_turnos'),
    
    # Rutas faltantes necesarias para el JavaScript
    path('admin/horarios/guardar/<int:dia_id>/', admin_views.guardar_horarios_dia_id, name='admin_guardar_horarios_dia_id'),
    path('admin/reparar-horarios-dia/<str:fecha>/', admin_views.reparar_horarios_dia, name='admin_reparar_horarios_dia'),
    
    # Rutas para horarios predeterminados
    path('turnos/admin/horarios-predeterminados/', admin_views.horarios_predeterminados, name='turnos_admin_horarios_predeterminados'),
    path('turnos/admin/horarios-predeterminados/<int:horario_id>/', admin_views.horario_predeterminado_detalle, name='turnos_admin_horario_predeterminado_detalle'),
    path('admin/horarios-predeterminados/', admin_views.horarios_predeterminados, name='admin_horarios_predeterminados'),
    path('admin/horarios-predeterminados/<int:horario_id>/', admin_views.horario_predeterminado_detalle, name='admin_horario_predeterminado_detalle'),
    
    # Rutas para reparación de horarios
    path('turnos/admin/reparar-horarios-dia/<str:fecha>/', admin_views.reparar_horarios_dia, name='turnos_admin_reparar_horarios_dia'),
    
    # Rutas con prefijo turnos/admin para compatibilidad con el JavaScript
    path('turnos/admin/horarios-dia/<str:fecha>/', admin_views.horarios_dia, name='turnos_admin_horarios_dia'),
    path('turnos/admin/dias/horarios/guardar/', admin_views.horarios_guardar, name='turnos_admin_horarios_guardar'),
    path('turnos/admin/dias/<int:dia_id>/eliminar/', admin_views.eliminar_dia, name='turnos_admin_eliminar_dia'),
    path('turnos/admin/dias/<str:fecha>/detalle/', admin_views.obtener_detalle_dia, name='turnos_admin_detalle_dia'),
    path('turnos/admin/dias/configurar-rango/', admin_views.configurar_rango_dias, name='turnos_admin_configurar_rango_dias'),
    path('turnos/admin/dias-disponibles/', admin_views.dias_disponibles, name='turnos_admin_dias_disponibles'),
    path('turnos/admin/horarios/get_horarios/', admin_views.get_horarios, name='turnos_admin_get_horarios'),
    path('turnos/admin/horarios/<int:horario_id>/eliminar/', admin_views.eliminar_horario, name='turnos_admin_eliminar_horario'),
    path('turnos/admin/horarios/configurar/', admin_views.configurar_horarios, name='turnos_admin_configurar_horarios'),
    path('turnos/admin/horarios/excepcion/', admin_views.agregar_excepcion, name='turnos_admin_excepcion'),
    path('turnos/admin/dias-disponibles/<int:dia_id>/', admin_views.dia_disponible_detalle, name='turnos_admin_dia_disponible_detalle'),

    # Rutas para usuarios
    path('dias_disponibles/', views.obtener_dias_disponibles, name='dias_disponibles'),
    path('horarios/<str:fecha>/', views.obtener_horarios_dia, name='horarios_dia_usuario'),
    path('confirmar_turno/', views.confirmar_turno, name='confirmar_turno'),
    path('mis_turnos/', views.mis_turnos, name='mis_turnos'),
    
    # Rutas para administradores
    path('admin/dias/', admin_views.dias_disponibles, name='admin_dias_disponibles'),
    path('admin/dias/<str:fecha>/', admin_views.obtener_detalle_dia, name='admin_obtener_detalle_dia'),
    path('admin/dias/actualizar/', admin_views.actualizar_dia, name='admin_actualizar_dia'),
    path('admin/horarios-dia/<str:fecha>/', admin_views.horarios_dia, name='admin_horarios_dia'),
    path('admin/dias/horarios/guardar/', admin_views.horarios_guardar, name='admin_horarios_guardar'),
]