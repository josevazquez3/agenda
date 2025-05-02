# turnos/admin_views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
# Corregir importaciones
from .models import DiasDisponibles as DiaDisponible, HorarioDisponible, Turno, ConfiguracionHorario, ExcepcionHorario
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime, time, timedelta
import traceback
from django.utils import timezone

# Función para registro de logs
def logDebug(mensaje, datos=None):
    """Registra un mensaje de depuración en la consola del servidor"""
    prefix = "[DEBUG] "
    if datos:
        print(f"{prefix}{mensaje}", datos)
    else:
        print(f"{prefix}{mensaje}")

def es_admin(user):
    return user.is_authenticated and (user.is_staff or user.rol == 'admin')

@login_required
def usuarios(request):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener lista de usuarios
    usuarios = User.objects.all().order_by('-date_joined')
    
    return render(request, 'admin/usuarios.html', {
        'title': 'Gestión de Usuarios',
        'usuarios': usuarios
    })

@user_passes_test(es_admin)
def dias_disponibles(request):
    """Gestiona los días disponibles para turnos"""
    if request.method == 'POST':
        try:
            fecha = request.POST.get('fecha')
            disponible = request.POST.get('disponible') == 'true'
            
            dia, created = DiaDisponible.objects.update_or_create(
                fecha=fecha,
                defaults={'disponible': disponible}
            )
            
            # Si el día es creado o actualizado como disponible
            if disponible:
                # Comprobar si es un día recién creado
                if created:
                    # Obtener horarios base existentes o usar predeterminados
                    horarios_base = list(HorarioDisponible.objects.values_list('hora_inicio', flat=True).distinct())
                    if not horarios_base:
                        # Horarios predeterminados si no hay existentes
                        horarios_base = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', 
                                        '12:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']
                        
                    for hora in horarios_base:
                        # Convertir hora a time si es string
                        if isinstance(hora, str):
                            try:
                                hora_obj = datetime.strptime(hora, '%H:%M').time()
                            except ValueError:
                                hora_obj = hora
                        else:
                            hora_obj = hora
                            
                        HorarioDisponible.objects.create(
                            dia=dia,
                            hora_inicio=hora_obj,
                            disponible=True
                        )
                else:
                    # Si no es un día nuevo, usar horarios predeterminados
                    horarios = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', 
                               '12:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']
                    
                    for hora in horarios:
                        # Convertir hora a time
                        hora_obj = datetime.strptime(hora, '%H:%M').time()
                        
                        HorarioDisponible.objects.get_or_create(
                            dia=dia,
                            hora_inicio=hora_obj,
                            defaults={'disponible': True}
                        )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Día configurado correctamente'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    # GET request - retornar lista de días disponibles
    dias = DiaDisponible.objects.all().order_by('fecha')
    dias_list = [{
        'id': dia.id,
        'fecha': dia.fecha.strftime('%Y-%m-%d'),
        'disponible': dia.disponible
    } for dia in dias]
    
    # Para la vista de la página (no la API)
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(dias_list, safe=False)
    else:
        return render(request, 'admin/dias_disponibles.html', {
            'title': 'Gestión de Días Disponibles',
            'dias': dias
        })

@user_passes_test(es_admin)
def configurar_horarios(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            horario = ConfiguracionHorario.objects.create(
                dia_semana=int(data['dia_semana']),
                hora_inicio=data['hora_inicio'],
                hora_fin=data['hora_fin'],
                duracion_turno=int(data['duracion_turno'])
            )
            return JsonResponse({
                'status': 'success',
                'message': 'Horario configurado correctamente',
                'id': horario.id
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    configuraciones = ConfiguracionHorario.objects.filter(activo=True).order_by('dia_semana', 'hora_inicio')
    excepciones = ExcepcionHorario.objects.all().order_by('fecha')
    
    return render(request, 'admin/configurar_horarios.html', {
        'configuraciones': configuraciones,
        'excepciones': excepciones
    })

@user_passes_test(es_admin)
def get_horarios(request):
    try:
        # Obtener los horarios únicos ordenados por hora 
        horarios = HorarioDisponible.objects.all()
        
        # Verificar si hay horarios
        if not horarios.exists():
            # Devolver lista vacía si no hay horarios configurados
            return JsonResponse([], safe=False)
        
        # Agrupar por hora_inicio y obtener valores únicos
        horarios_unicos = {}
        for horario in horarios:
            hora_key = horario.hora_inicio.strftime('%H:%M') if isinstance(horario.hora_inicio, time) else str(horario.hora_inicio)
            if hora_key not in horarios_unicos:
                horarios_unicos[hora_key] = {
                    'id': horario.id,
                    'hora_inicio': hora_key,
                    'disponible': horario.disponible
                }
        
        # Convertir a lista ordenada
        horarios_list = list(horarios_unicos.values())
        horarios_list.sort(key=lambda x: x['hora_inicio'])
        
        logDebug(f"Devolviendo {len(horarios_list)} horarios únicos")
        
        return JsonResponse(horarios_list, safe=False)
    except Exception as e:
        # Registrar el error y devolver una respuesta útil
        error_msg = f"Error en get_horarios: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Imprimir en la consola del servidor
        return JsonResponse({"error": str(e)}, status=500, safe=False)

@user_passes_test(es_admin)
@require_http_methods(['POST', 'DELETE'])
def eliminar_horario(request, horario_id):
    # Manejar solicitudes DELETE para ConfiguracionHorario
    if request.method == 'DELETE':
        try:
            horario = ConfiguracionHorario.objects.get(id=horario_id)
            horario.delete()
            return JsonResponse({'status': 'success', 'message': 'Horario eliminado correctamente'})
        except ConfiguracionHorario.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Horario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    # Manejar solicitudes POST para HorarioDisponible
    try:
        horario = HorarioDisponible.objects.get(id=horario_id)
        horario.delete()
        return JsonResponse({'success': True})
    except HorarioDisponible.DoesNotExist:
        return JsonResponse({'error': 'Horario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@user_passes_test(es_admin)
def horarios_dia(request, fecha=None):
    """Obtiene o actualiza los horarios para una fecha específica"""
    if request.method == 'GET':
        try:
            # Si no se proporcionó fecha, intentar obtenerla de los parámetros
            if not fecha:
                fecha = request.GET.get('fecha')
            
            if not fecha:
                return JsonResponse({'success': False, 'message': 'No se proporcionó fecha'}, status=400)
            
            # Convertir string a fecha
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # Obtener o crear el día
            dia, created = DiaDisponible.objects.get_or_create(
                fecha=fecha_obj,
                defaults={'disponible': True}
            )
            
            # Si es un nuevo día, crear horarios predeterminados
            if created:
                horarios = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', 
                           '12:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']
                
                for hora in horarios:
                    try:
                        hora_obj = datetime.strptime(hora, '%H:%M').time()
                    except:
                        hora_obj = hora
                    HorarioDisponible.objects.create(
                        dia=dia,
                        hora_inicio=hora_obj,
                        disponible=True
                    )
            
            # Obtener todos los horarios para este día
            horarios = HorarioDisponible.objects.filter(dia=dia).order_by('hora_inicio')
            
            # Formatear para JSON
            horarios_json = []
            for horario in horarios:
                hora = horario.hora_inicio
                if isinstance(hora, time):
                    hora = hora.strftime('%H:%M')
                
                horarios_json.append({
                    'id': horario.id,
                    'hora': hora,
                    'disponible': horario.disponible
                })
            
            return JsonResponse({'success': True, 'horarios': horarios_json})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    elif request.method == 'POST':
        try:
            # Actualizar horarios del día
            data = json.loads(request.body)
            horarios_data = data.get('horarios', [])
            
            # Convertir fecha a formato adecuado
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # Obtener día disponible o crear si no existe
            dia, created = DiaDisponible.objects.get_or_create(
                fecha=fecha_obj,
                defaults={'disponible': True}
            )
            
            # Procesar cada horario
            for horario_data in horarios_data:
                horario_id = horario_data.get('id')
                hora_inicio = horario_data.get('hora_inicio')
                disponible = horario_data.get('disponible', True)
                
                if horario_id and horario_id != '':
                    # Actualizar horario existente
                    try:
                        horario = HorarioDisponible.objects.get(id=horario_id)
                        horario.disponible = disponible
                        horario.save()
                    except HorarioDisponible.DoesNotExist:
                        continue
                elif hora_inicio:
                    # Crear nuevo horario
                    try:
                        # Convertir la hora a objeto time
                        if isinstance(hora_inicio, str) and ':' in hora_inicio:
                            hora = datetime.strptime(hora_inicio, '%H:%M').time()
                        else:
                            # Si no tiene formato adecuado, usar el valor tal cual
                            hora = hora_inicio
                        
                        # Verificar si ya existe un horario con esa hora
                        horario_existente = HorarioDisponible.objects.filter(
                            dia=dia,
                            hora_inicio=hora
                        ).first()
                        
                        if not horario_existente:
                            HorarioDisponible.objects.create(
                                dia=dia,
                                hora_inicio=hora,
                                disponible=disponible
                            )
                    except Exception as e:
                        print(f"Error al crear horario: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Horarios actualizados correctamente'
            })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@user_passes_test(es_admin)
@require_http_methods(['POST'])
def agregar_excepcion(request):
    try:
        data = json.loads(request.body)
        fecha = datetime.strptime(data.get('fecha'), '%Y-%m-%d').date()
        disponible = data.get('disponible', False)
        motivo = data.get('motivo', '')

        excepcion, created = ExcepcionHorario.objects.update_or_create(
            fecha=fecha,
            defaults={
                'disponible': disponible,
                'motivo': motivo
            }
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Excepción agregada correctamente'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@user_passes_test(es_admin)
@require_http_methods(['POST'])
def horarios_guardar(request):
    """Guarda los horarios configurados para un día específico"""
    try:
        data = json.loads(request.body)
        fecha = data.get('fecha')
        horarios = data.get('horarios', [])
        
        # Obtener el día o crear si no existe
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        dia, created = DiaDisponible.objects.get_or_create(
            fecha=fecha_obj,
            defaults={'disponible': True}
        )
        
        # Actualizar horarios
        for horario_data in horarios:
            # Compatibilidad con diferentes formatos de JSON
            hora = horario_data.get('hora') or horario_data.get('hora_inicio')
            disponible = horario_data.get('disponible')
            
            # Convertir la hora a objeto time si es necesario
            try:
                hora_obj = datetime.strptime(hora, '%H:%M').time()
            except:
                hora_obj = hora
                
            # Actualizar o crear el horario
            HorarioDisponible.objects.update_or_create(
                dia=dia,
                hora_inicio=hora_obj,
                defaults={'disponible': disponible}
            )
        
        return JsonResponse({
            'success': True,
            'message': 'Horarios guardados correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
def listado_turnos(request):
    # Verificar si el usuario es administrador
    if not request.user.is_staff:
        return redirect('inicio')
    
    # Obtener filtros opcionales
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    estado = request.GET.get('estado')
    
    # Consulta base
    turnos = Turno.objects.all()
    
    # Aplicar filtros si existen
    if fecha_desde:
        turnos = turnos.filter(dia__fecha__gte=fecha_desde)
    
    if fecha_hasta:
        turnos = turnos.filter(dia__fecha__lte=fecha_hasta)
        
    if estado:
        turnos = turnos.filter(estado=estado)
        
    # Ordenar por fecha y hora
    turnos = turnos.order_by('dia__fecha', 'horario__hora_inicio')
    
    # Contexto para la plantilla
    context = {
        'title': 'Listado de Turnos',
        'turnos': turnos,
        'filtros': {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'estado': estado
        }
    }
    
    return render(request, 'admin/listado_turnos.html', context)

@user_passes_test(es_admin)
def eliminar_dia(request, dia_id):
    """Elimina un día disponible"""
    try:
        dia = DiaDisponible.objects.get(id=dia_id)
        dia.delete()
        return JsonResponse({'status': 'success', 'message': 'Día eliminado correctamente'})
    except DiaDisponible.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Día no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@user_passes_test(es_admin)
def gestion_disponibilidad(request):
    """Vista unificada para gestionar días y horarios disponibles"""
    dias = DiaDisponible.objects.all().order_by('-fecha')
    configuraciones = ConfiguracionHorario.objects.filter(activo=True).order_by('dia_semana', 'hora_inicio')
    excepciones = ExcepcionHorario.objects.all().order_by('fecha')
    
    return render(request, 'admin/gestion_disponibilidad.html', {
        'title': 'Gestión de Disponibilidad',
        'dias': dias,
        'configuraciones': configuraciones,
        'excepciones': excepciones
    })

@user_passes_test(es_admin)
def admin_calendario(request):
    """Vista que muestra el calendario para configurar días y horarios disponibles"""
    return render(request, 'admin/admin_calendario.html', {
        'title': 'Configuración de Calendario',
    })

@user_passes_test(es_admin)
def configurar_dias(request):
    """Vista que muestra la pantalla para configurar días disponibles"""
    return render(request, 'admin/configurar_dias.html', {
        'title': 'Configurar Días Disponibles',
    })

@user_passes_test(es_admin)
@require_http_methods(['GET'])
def obtener_detalle_dia(request, fecha):
    """Obtiene los detalles de un día específico, incluyendo sus horarios"""
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        dia, created = DiaDisponible.objects.get_or_create(
            fecha=fecha_obj,
            defaults={'disponible': True}
        )
        
        # Si es un día nuevo y está disponible, crear horarios predeterminados
        if created and dia.disponible:
            horarios_base = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', 
                           '11:00', '11:30', '12:00', '12:30', '15:00', '15:30', 
                           '16:00', '16:30', '17:00', '17:30', '18:00', '18:30']
            
            for hora in horarios_base:
                HorarioDisponible.objects.create(
                    dia=dia,
                    hora_inicio=hora,
                    disponible=True
                )
        
        # Obtener los horarios para este día
        horarios = HorarioDisponible.objects.filter(dia=dia).order_by('hora_inicio')
        horarios_data = [{
            'id': h.id,
            'hora': h.hora_inicio.strftime('%H:%M'),
            'disponible': h.disponible
        } for h in horarios]
        
        return JsonResponse({
            'status': 'success',
            'fecha': fecha,
            'disponible': dia.disponible,
            'motivo': dia.motivo if hasattr(dia, 'motivo') else '',
            'horarios': horarios_data
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@user_passes_test(es_admin)
@require_http_methods(['POST'])
def actualizar_dia(request):
    """Actualiza la configuración de un día específico"""
    try:
        data = json.loads(request.body)
        fecha = data.get('fecha')
        disponible = data.get('disponible')
        motivo = data.get('motivo', '')
        
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Verificar si el modelo tiene campo motivo
        if hasattr(DiaDisponible, 'motivo'):
            dia, created = DiaDisponible.objects.update_or_create(
                fecha=fecha_obj,
                defaults={
                    'disponible': disponible,
                    'motivo': motivo if not disponible else ''
                }
            )
        else:
            dia, created = DiaDisponible.objects.update_or_create(
                fecha=fecha_obj,
                defaults={
                    'disponible': disponible
                }
            )
        
        # Si es un día nuevo y disponible, crear horarios predeterminados
        if created and disponible:
            horarios_base = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', 
                           '11:00', '11:30', '12:00', '12:30', '15:00', '15:30', 
                           '16:00', '16:30', '17:00', '17:30', '18:00', '18:30']
            
            for hora in horarios_base:
                HorarioDisponible.objects.create(
                    dia=dia,
                    hora_inicio=hora,
                    disponible=True
                )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Día actualizado correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@user_passes_test(es_admin)
@require_http_methods(['POST'])
def configurar_rango_dias(request):
    """Configura un rango de fechas como disponibles o no disponibles"""
    try:
        data = json.loads(request.body)
        fecha_inicio = datetime.strptime(data.get('fecha_inicio'), '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(data.get('fecha_fin'), '%Y-%m-%d').date()
        disponible = data.get('disponible', True)
        
        # Calcular el rango de fechas
        dias_configurados = 0
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            # Crear o actualizar día
            dia, created = DiaDisponible.objects.update_or_create(
                fecha=fecha_actual,
                defaults={'disponible': disponible}
            )
            
            # Si se marca como disponible y es un día nuevo, crear horarios predeterminados
            if disponible and created:
                horarios = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', 
                           '12:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']
                
                for hora in horarios:
                    HorarioDisponible.objects.create(
                        dia=dia,
                        hora_inicio=hora,
                        disponible=True
                    )
            
            dias_configurados += 1
            fecha_actual = (datetime.combine(fecha_actual, time.min) + timedelta(days=1)).date()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Se han configurado {dias_configurados} días correctamente',
            'dias_configurados': dias_configurados
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

# FUNCIONES NUEVAS AÑADIDAS 

@user_passes_test(es_admin)
def guardar_horarios_dia_id(request, dia_id):
    """Guarda los horarios para un día específico utilizando su ID"""
    try:
        # Buscar el día por ID
        dia = DiaDisponible.objects.get(id=dia_id)
        
        if request.method == 'POST':
            data = json.loads(request.body)
            horarios_data = data.get('horarios', [])
            
            # Procesar cada horario
            for horario_data in horarios_data:
                horario_id = horario_data.get('id')
                hora_inicio = horario_data.get('hora_inicio')
                disponible = horario_data.get('disponible', True)
                
                if horario_id and horario_id != '':
                    # Actualizar horario existente
                    try:
                        horario = HorarioDisponible.objects.get(id=horario_id)
                        horario.disponible = disponible
                        horario.save()
                    except HorarioDisponible.DoesNotExist:
                        continue
                elif hora_inicio:
                    # Crear nuevo horario
                    try:
                        # Convertir la hora a objeto time
                        if isinstance(hora_inicio, str) and ':' in hora_inicio:
                            hora = datetime.strptime(hora_inicio, '%H:%M').time()
                        else:
                            # Si no tiene formato adecuado, omitir
                            continue
                        
                        # Verificar si ya existe un horario con esa hora
                        horario_existente = HorarioDisponible.objects.filter(
                            dia=dia,
                            hora_inicio=hora
                        ).first()
                        
                        if not horario_existente:
                            HorarioDisponible.objects.create(
                                dia=dia,
                                hora_inicio=hora,
                                disponible=disponible
                            )
                    except Exception as e:
                        print(f"Error al crear horario: {e}")
            
            return JsonResponse({
                'success': True,
                'message': 'Horarios actualizados correctamente'
            })
        
        return JsonResponse({
            'success': False,
            'message': 'Método no permitido'
        })
    
    except DiaDisponible.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Día no encontrado'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })

@user_passes_test(es_admin)
def reparar_horarios_dia(request, fecha):
    """Repara los horarios de un día eliminando los existentes y creando los predeterminados"""
    if request.method == 'POST':
        try:
            # Convertir fecha a formato adecuado
            if isinstance(fecha, str):
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            else:
                fecha_obj = fecha
            
            # Buscar día disponible
            dia = DiaDisponible.objects.filter(fecha=fecha_obj).first()
            if not dia:
                # Crear día si no existe
                dia = DiaDisponible.objects.create(
                    fecha=fecha_obj,
                    disponible=True
                )
            
            # Eliminar horarios existentes
            HorarioDisponible.objects.filter(dia=dia).delete()
            
            # Crear horarios predeterminados
            crear_horarios_predeterminados(dia)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Horarios reparados correctamente'
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    })

@user_passes_test(es_admin)
def horarios_predeterminados(request):
    """Obtiene o crea horarios predeterminados"""
    if request.method == 'GET':
        # Obtener todos los horarios predeterminados
        horarios = obtener_horarios_predeterminados()
        return JsonResponse(horarios, safe=False)
    
    elif request.method == 'POST':
        try:
            # Crear nuevo horario predeterminado
            data = json.loads(request.body)
            dia_semana = int(data.get('dia_semana'))
            hora_inicio = data.get('hora_inicio')
            hora_fin = data.get('hora_fin')
            duracion_turno = int(data.get('duracion_turno', 30))
# Crear horarios entre hora_inicio y hora_fin con duración especificada
            crear_horarios_entre_horas(dia_semana, hora_inicio, hora_fin, duracion_turno)
            
            return JsonResponse({
                'status': 'success',
                'message': 'Horarios configurados correctamente'
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    })

@user_passes_test(es_admin)
def horario_predeterminado_detalle(request, horario_id):
    """Operaciones sobre un horario predeterminado específico"""
    try:
        horario = HorarioDisponible.objects.get(id=horario_id)
    except HorarioDisponible.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Horario no encontrado'
        })
    
    if request.method == 'PUT':
        try:
            # Actualizar disponibilidad del horario
            data = json.loads(request.body)
            disponible = data.get('disponible', True)
            
            horario.disponible = disponible
            horario.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Horario actualizado correctamente'
            })
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    elif request.method == 'DELETE':
        # Eliminar horario
        horario.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Horario eliminado correctamente'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    })

@user_passes_test(es_admin)
def dia_disponible_detalle(request, dia_id):
    """Operaciones sobre un día disponible específico"""
    try:
        dia = DiaDisponible.objects.get(id=dia_id)
    except DiaDisponible.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Día no encontrado'
        })
    
    if request.method == 'DELETE':
        # Eliminar día y sus horarios
        dia.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Día eliminado correctamente'
        })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Método no permitido'
    })

# Funciones auxiliares

def obtener_horarios_predeterminados():
    """Obtiene la lista de horarios predeterminados"""
    horarios = []
    
    # Ejemplo: horarios cada 30 minutos entre 8:00 y 18:00
    hora_inicio = datetime.strptime('08:00', '%H:%M').time()
    hora_fin = datetime.strptime('18:00', '%H:%M').time()
    
    hora_actual = datetime.combine(datetime.today(), hora_inicio)
    hora_final = datetime.combine(datetime.today(), hora_fin)
    
    while hora_actual < hora_final:
        horarios.append({
            'hora': hora_actual.strftime('%H:%M'),
            'disponible': True
        })
        hora_actual += timedelta(minutes=30)
    
    return horarios

def crear_horarios_entre_horas(dia_semana, hora_inicio_str, hora_fin_str, duracion_turno):
    """Crea horarios entre las horas especificadas para el día de la semana indicado"""
    hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
    hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
    
    hora_actual = datetime.combine(datetime.today(), hora_inicio)
    hora_final = datetime.combine(datetime.today(), hora_fin)
    
    # Guardar para cada día en el futuro (próximos 3 meses) que coincida con dia_semana
    fecha_actual = timezone.now().date()
    fecha_limite = fecha_actual + timedelta(days=90)
    
    while fecha_actual <= fecha_limite:
        if fecha_actual.weekday() == dia_semana:
            # Buscar o crear día
            dia, created = DiaDisponible.objects.get_or_create(
                fecha=fecha_actual,
                defaults={'disponible': True}
            )
            
            # Crear horarios para este día
            hora_turno = datetime.combine(datetime.today(), hora_inicio)
            while hora_turno < hora_final:
                HorarioDisponible.objects.get_or_create(
                    dia=dia,
                    hora_inicio=hora_turno.time(),
                    defaults={'disponible': True}
                )
                hora_turno += timedelta(minutes=duracion_turno)
        
        fecha_actual += timedelta(days=1)

def crear_horarios_predeterminados(dia):
    """Crea horarios predeterminados para un día específico"""
    horarios = obtener_horarios_predeterminados()
    
    for horario in horarios:
        hora = datetime.strptime(horario['hora'], '%H:%M').time()
        
        # Verificar si ya existe
        existe = HorarioDisponible.objects.filter(
            dia=dia,
            hora_inicio=hora
        ).exists()
        
        if not existe:
            HorarioDisponible.objects.create(
                dia=dia,
                hora_inicio=hora,
                disponible=horario['disponible']
            )

@user_passes_test(es_admin)
def horarios_dia(request, fecha=None):
    """Obtiene o actualiza los horarios para una fecha específica"""
    if request.method == 'GET':
        try:
            # Si no se proporcionó fecha, intentar obtenerla de los parámetros
            if not fecha:
                fecha = request.GET.get('fecha')
            
            if not fecha:
                return JsonResponse({'success': False, 'message': 'No se proporcionó fecha'}, status=400)
            
            # Convertir string a fecha
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            # Obtener o crear el día
            dia, created = DiaDisponible.objects.get_or_create(
                fecha=fecha_obj,
                defaults={'disponible': True}
            )
            
            # Si es un nuevo día, crear horarios predeterminados
            if created:
                horarios_base = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', 
                               '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', 
                               '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00']
                
                for hora in horarios_base:
                    hora_obj = datetime.strptime(hora, '%H:%M').time()
                    HorarioDisponible.objects.create(
                        dia=dia,
                        hora_inicio=hora_obj,
                        disponible=True
                    )
            
            # Obtener todos los horarios para este día
            horarios = HorarioDisponible.objects.filter(dia=dia).order_by('hora_inicio')
            
            # Formatear para JSON
            horarios_json = []
            for horario in horarios:
                hora_str = horario.hora_inicio.strftime('%H:%M') if isinstance(horario.hora_inicio, time) else str(horario.hora_inicio)
                
                horarios_json.append({
                    'id': horario.id,
                    'hora': hora_str,
                    'disponible': horario.disponible
                })
            
            return JsonResponse({'success': True, 'horarios': horarios_json})
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'message': str(e)}, status=400)