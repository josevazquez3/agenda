from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from .models import DiasDisponibles, HorarioDisponible, Turno
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import messages
import datetime
import json
from datetime import datetime


def inicio(request):
    return render(request, 'inicio.html')

def contacto(request):
    return render(request, 'contacto.html')

@login_required
def solicitar_turno(request):
    if request.user.is_staff:
        # Si es administrador, redirigir a la vista de admin para solicitar turno
        return redirect('admin_solicitar_turno')
    return render(request, 'turnos/solicitar_turno.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_solicitar_turno(request):
    """Vista para que los administradores soliciten turnos para pacientes"""
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
        
    if request.method == 'POST':
        # Procesar el formulario
        paciente_id = request.POST.get('paciente')
        fecha_str = request.POST.get('fecha')
        horario_id = request.POST.get('horario')
        motivo = request.POST.get('motivo', '')
        
        try:
            # Obtener los objetos necesarios
            User = get_user_model()
            paciente = User.objects.get(id=paciente_id)
            horario = HorarioDisponible.objects.get(id=horario_id)
            
            # Crear el turno
            turno = Turno.objects.create(
                paciente=paciente,
                dia=horario.dia,
                horario=horario,
                fecha_solicitud=timezone.now(),
                estado='confirmado',  # Los turnos creados por admin están confirmados automáticamente
                motivo=motivo
            )
            
            # Marcar el horario como no disponible
            horario.disponible = False
            horario.save()
            
            messages.success(request, f'Turno creado exitosamente para {paciente.get_full_name()} el {horario.dia.fecha.strftime("%d/%m/%Y")} a las {horario.hora_inicio.strftime("%H:%M")}')
            return redirect('admin_listado_turnos')
            
        except Exception as e:
            messages.error(request, f'Error al crear el turno: {str(e)}')
    
    # GET request - mostrar formulario
    # Obtener lista de pacientes (usuarios que no son staff)
    User = get_user_model()
    pacientes = User.objects.filter(is_staff=False)
    
    # Obtener días disponibles
    dias_disponibles = DiasDisponibles.objects.filter(
        disponible=True, 
        fecha__gte=timezone.now().date()
    ).order_by('fecha')
    
    return render(request, 'admin/solicitar_turno.html', {
        'title': 'Solicitar Turno para Paciente',
        'pacientes': pacientes,
        'dias_disponibles': dias_disponibles
    })

@login_required
def admin_confirmar_turno(request):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    if request.method == 'POST':
        horario_id = request.POST.get('horario_id')
        usuario_id = request.POST.get('usuario_id')
        
        if not horario_id or not usuario_id:
            messages.error(request, 'Datos incompletos')
            return redirect('admin_solicitar_turno')
        
        try:
            # Obtener el usuario y el horario
            User = get_user_model()
            usuario = get_object_or_404(User, id=usuario_id)
            horario = get_object_or_404(HorarioDisponible, id=horario_id, disponible=True)
            
            # Crear el turno
            turno = Turno.objects.create(
                paciente=usuario,
                dia=horario.dia,
                horario=horario,
                fecha_solicitud=timezone.now(),
                estado='confirmado'
            )
            
            # Marcar el horario como no disponible
            horario.disponible = False
            horario.save()
            
            # Si no hay más horarios disponibles para este día, marcar el día como no disponible
            if not HorarioDisponible.objects.filter(dia=horario.dia, disponible=True).exists():
                horario.dia.disponible = False
                horario.dia.save()
            
            messages.success(request, f'Turno confirmado para {usuario.get_full_name()}')
            return redirect('admin_solicitar_turno')
            
        except Exception as e:
            messages.error(request, f'Error al confirmar el turno: {str(e)}')
            return redirect('admin_solicitar_turno')
    
    return redirect('admin_solicitar_turno')

@login_required
def dias_disponibles(request):
    # Obtener todas las fechas disponibles
    dias = DiasDisponibles.objects.filter(disponible=True)
    dias_json = [dia.fecha.strftime('%Y-%m-%d') for dia in dias]
    return JsonResponse({'dias_disponibles': dias_json})

@login_required
def calendario(request):
    # Obtener todas las fechas disponibles
    dias_disponibles = DiasDisponibles.objects.filter(disponible=True)
    
    # Formatear las fechas para FullCalendar
    dias_json = [dia.fecha.strftime('%Y-%m-%d') for dia in dias_disponibles]
    
    return render(request, 'calendario.html', {
        'dias_disponibles': json.dumps(dias_json)
    })

@login_required
def dias_disponibles(request):
    """
    Vista para obtener los días disponibles en formato JSON
    Usado por calendario_turnos.js (flatpickr)
    """
    dias = DiasDisponibles.objects.filter(disponible=True)
    dias_json = [dia.fecha.strftime('%Y-%m-%d') for dia in dias]
    
    return JsonResponse({'dias_disponibles': dias_json})

# La vista admin_configurar_dias ha sido eliminada por solicitud del usuario

@login_required
def horarios_disponibles(request, fecha):
    """Devuelve los horarios disponibles para una fecha específica en formato JSON"""
    try:
        # Convertir string a fecha
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Obtener el día disponible
        dia = DiasDisponibles.objects.get(fecha=fecha_obj, disponible=True)
        
        # Obtener los horarios disponibles
        horarios = HorarioDisponible.objects.filter(dia=dia, disponible=True).order_by('hora_inicio')
        
        # Formatear los horarios para la respuesta JSON
        horarios_data = []
        for horario in horarios:
            horarios_data.append({
                'id': horario.id,
                'hora_inicio': horario.hora_inicio.strftime('%H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'horarios': horarios_data
        })
    
    except DiasDisponibles.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'No hay horarios disponibles para esta fecha',
            'horarios': []
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener horarios: {str(e)}',
            'horarios': []
        })

@login_required
def confirmar_turno(request):
    if request.method == 'POST':
        horario_id = request.POST.get('horario_id')
        
        if not horario_id:
            # Si no hay horario seleccionado, volver a solicitar_turno
            return redirect('solicitar_turno')
        
        # Obtener el horario
        horario = get_object_or_404(HorarioDisponible, id=horario_id, disponible=True)
        
        # Obtener el día correspondiente
        dia = horario.dia
        
        # Crear el turno
        turno = Turno.objects.create(
            paciente=request.user,
            dia=dia,
            horario=horario,
            fecha_solicitud=timezone.now(),
            estado='confirmado'
        )
        
        # Marcar el horario como no disponible
        horario.disponible = False
        horario.save()
        
        # Si no hay más horarios disponibles para este día, marcar el día como no disponible
        if not HorarioDisponible.objects.filter(dia=dia, disponible=True).exists():
            dia.disponible = False
            dia.save()
        
        # Redirigir a la página de confirmación
        return render(request, 'confirmacion.html', {'turno': turno})
    
    # Si no es POST, redirigir a solicitar_turno
    return redirect('solicitar_turno')

@login_required
def mis_turnos(request):
    """
    Vista para mostrar los turnos del usuario autenticado
    """
    # Obtener todos los turnos del usuario
    turnos = Turno.objects.filter(paciente=request.user).order_by('-dia__fecha')
    
    return render(request, 'turnos/mis_turnos.html', {
        'turnos': turnos,
        'title': 'Mis Turnos'
    })

@login_required
def cancelar_turno(request, turno_id):
    # Obtener el turno
    turno = get_object_or_404(Turno, id=turno_id, paciente=request.user)
    
    if request.method == 'POST':
        # Cambiar el estado del turno a cancelado
        turno.estado = 'cancelado'
        turno.save()
        
        # Marcar el horario como disponible nuevamente
        horario = turno.horario
        horario.disponible = True
        horario.save()
        
        # Marcar el día como disponible si no lo estaba
        dia = turno.dia
        if not dia.disponible:
            dia.disponible = True
            dia.save()
        
        # Redirigir a mis turnos
        return redirect('mis_turnos')
    
    # Si no es POST, mostrar la página de confirmación
    return render(request, 'cancelar_turnos.html', {'turno': turno})

# Función para crear días y horarios disponibles (utilidad de administración)
@login_required
def crear_disponibilidad(request):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    if request.method == 'POST':
        # Procesar el formulario
        pass
    
    return render(request, 'crear_disponibilidad.html')

@login_required
def admin_configurar_horarios(request):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Si es una solicitud AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET':
            fecha = request.GET.get('fecha')
            try:
                # Convertir string a fecha
                fecha_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                
                # Obtener el día
                dia, created = DiasDisponibles.objects.get_or_create(
                    fecha=fecha_obj,
                    defaults={'disponible': True}
                )
                
                # Si es un nuevo día, crear horarios predeterminados
                if created:
                    horas_default = ['09:00', '10:00', '11:00', '12:00', '16:00', '17:00', '18:00']
                    for hora in horas_default:
                        hora_obj = datetime.datetime.strptime(hora, '%H:%M').time()
                        HorarioDisponible.objects.create(
                            dia=dia,
                            hora_inicio=hora_obj,
                            disponible=True
                        )
                
                # Obtener todos los horarios para este día
                horarios = HorarioDisponible.objects.filter(dia=dia).order_by('hora_inicio')
                
                # Formatear para JSON
                horarios_json = [
                    {
                        'id': horario.id,
                        'hora': horario.hora_inicio.strftime('%H:%M'),
                        'disponible': horario.disponible
                    }
                    for horario in horarios
                ]
                
                return JsonResponse({'success': True, 'horarios': horarios_json})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
        
        elif request.method == 'POST':
            # Procesar cambios en los horarios
            data = json.loads(request.body)
            fecha = data.get('fecha')
            horarios_data = data.get('horarios', [])
            
            try:
                # Convertir string a fecha
                fecha_obj = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                
                # Obtener el día
                dia = DiasDisponibles.objects.get(fecha=fecha_obj)
                
                # Actualizar cada horario
                for horario_data in horarios_data:
                    hora = horario_data.get('hora')
                    disponible = horario_data.get('disponible')
                    
                    hora_obj = datetime.datetime.strptime(hora, '%H:%M').time()
                    
                    # Obtener o crear el horario
                    horario, created = HorarioDisponible.objects.get_or_create(
                        dia=dia,
                        hora_inicio=hora_obj,
                        defaults={'disponible': disponible}
                    )
                    
                    if not created:
                        horario.disponible = disponible
                        horario.save()
                
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    # Si es una solicitud normal GET
    # Obtener días configurados
    dias = DiasDisponibles.objects.all().order_by('-fecha')
    
    # Renderizar plantilla
    return render(request, 'turnos/admin_horarios.html', {
        'title': 'Configurar Horarios',
        'dias': dias
    })

@login_required
def historial_paciente_lista(request):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener todos los pacientes que tienen turnos
    from django.contrib.auth import get_user_model
    from django.db.models import Count, Q
    User = get_user_model()
    
    pacientes = User.objects.filter(
        turnos__isnull=False
    ).annotate(
        total_turnos=Count('turnos'),
        turnos_pendientes=Count('turnos', filter=Q(turnos__estado='confirmado')),
        turnos_completados=Count('turnos', filter=Q(turnos__estado='completado')),
        turnos_cancelados=Count('turnos', filter=Q(turnos__estado='cancelado'))
    ).distinct().order_by('first_name', 'last_name')
    
    return render(request, 'historial_paciente_lista.html', {
        'pacientes': pacientes,
        'title': 'Historial de Pacientes'
    })

@login_required
def historial_paciente_ver(request, paciente_id):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener el paciente y sus turnos
    User = get_user_model()
    paciente = get_object_or_404(User, id=paciente_id)
    turnos = Turno.objects.filter(paciente=paciente).order_by('-dia__fecha', '-horario__hora_inicio')
    
    return render(request, 'historial_paciente_ver.html', {
        'paciente': paciente,
        'turnos': turnos,
        'title': f'Historial de {paciente.first_name} {paciente.last_name}'
    })

@login_required
def historial_paciente_pdf(request, paciente_id):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener el paciente
    User = get_user_model()
    paciente = get_object_or_404(User, id=paciente_id)
    
    # Obtener los turnos del paciente
    turnos = Turno.objects.filter(paciente=paciente).order_by('-dia__fecha', '-horario__hora_inicio')
    
    try:
        # Intentar generar el PDF
        from .pdf_utils import generar_pdf_historial
        return generar_pdf_historial(request, paciente, 'historial_paciente_pdf.html', turnos)
    except OSError as e:
        # Si hay un error con las dependencias de WeasyPrint, redirigir a la página de no disponible
        if 'cannot load library' in str(e):
            return redirect('historial_paciente_nodisponible', paciente_id=paciente_id)
        raise  # Re-raise other OSErrors

@login_required
def historial_paciente_nodisponible(request, paciente_id):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener el paciente
    paciente = get_object_or_404(get_user_model(), id=paciente_id)
    
    return render(request, 'historial_paciente_nodisponible.html', {
        'paciente': paciente,
        'mensaje': 'La exportación a PDF requiere la instalación de WeasyPrint en el servidor.'
    })