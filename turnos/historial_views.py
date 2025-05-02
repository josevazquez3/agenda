# historial_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
import json
from datetime import datetime
from .models import HistorialClinico, RegistroHistorial, Turno

def es_admin(user):
    return user.is_authenticated and (user.is_staff or user.rol == 'admin')

@user_passes_test(es_admin)
def admin_historial_paciente(request, paciente_id):
    """
    Vista para mostrar y gestionar el historial clínico de un paciente específico.
    """
    paciente = get_object_or_404(User, id=paciente_id)
    
    # Intentar obtener el historial clínico del paciente, o crearlo si no existe
    historial, created = HistorialClinico.objects.get_or_create(paciente=paciente)
    
    # Obtener todos los turnos del paciente para referencia
    turnos = Turno.objects.filter(usuario=paciente).order_by('-dia__fecha')
    
    context = {
        'title': f'Historial Clínico - {paciente.get_full_name() or paciente.username}',
        'paciente': paciente,
        'historial': historial,
        'turnos': turnos[:10],  # Mostrar los últimos 10 turnos
    }
    
    return render(request, 'admin/historial_paciente.html', context)

@user_passes_test(es_admin)
def get_historial(request, paciente_id):
    """
    Obtiene todos los registros del historial clínico de un paciente en formato JSON.
    """
    try:
        # Verificar que el paciente existe
        paciente = get_object_or_404(User, id=paciente_id)
        
        # Obtener el historial clínico
        historial, created = HistorialClinico.objects.get_or_create(paciente=paciente)
        
        # Obtener todos los registros ordenados por fecha
        registros = RegistroHistorial.objects.filter(historial=historial).order_by('-fecha_creacion')
        
        # Preparar datos para la respuesta JSON
        registros_data = []
        for registro in registros:
            registros_data.append({
                'id': registro.id,
                'fecha': registro.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'titulo': registro.titulo,
                'descripcion': registro.descripcion,
                'procedimiento': registro.procedimiento,
                'odontograma': registro.odontograma,
                'observaciones': registro.observaciones,
                'creado_por': registro.creado_por.get_full_name() if registro.creado_por else 'Sistema'
            })
        
        return JsonResponse({
            'status': 'success',
            'registros': registros_data
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@user_passes_test(es_admin)
@require_http_methods(['POST'])
def crear_registro(request):
    """
    Crea un nuevo registro en el historial clínico del paciente.
    """
    try:
        data = json.loads(request.body)
        paciente_id = data.get('paciente_id')
        
        # Verificar que los datos requeridos estén presentes
        if not paciente_id:
            return JsonResponse({
                'status': 'error',
                'message': 'ID de paciente requerido'
            }, status=400)
        
        # Obtener el paciente y su historial
        paciente = get_object_or_404(User, id=paciente_id)
        historial, created = HistorialClinico.objects.get_or_create(paciente=paciente)
        
        # Crear el nuevo registro
        registro = RegistroHistorial.objects.create(
            historial=historial,
            titulo=data.get('titulo', 'Consulta odontológica'),
            descripcion=data.get('descripcion', ''),
            procedimiento=data.get('procedimiento', ''),
            odontograma=data.get('odontograma', ''),
            observaciones=data.get('observaciones', ''),
            creado_por=request.user
        )
        
        # Si hay un turno asociado, vincularlo
        turno_id = data.get('turno_id')
        if turno_id:
            try:
                turno = Turno.objects.get(id=turno_id)
                registro.turno = turno
                registro.save()
            except Turno.DoesNotExist:
                pass  # Ignorar si el turno no existe
        
        return JsonResponse({
            'status': 'success',
            'message': 'Registro creado correctamente',
            'registro_id': registro.id
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@user_passes_test(es_admin)
def obtener_registro(request, registro_id):
    """
    Obtiene los detalles de un registro específico.
    """
    try:
        registro = get_object_or_404(RegistroHistorial, id=registro_id)
        
        # Verificar que el usuario tenga permisos para ver este registro
        if not request.user.is_staff:
            return JsonResponse({
                'status': 'error',
                'message': 'No tienes permisos para ver este registro'
            }, status=403)
        
        # Preparar los datos del registro
        registro_data = {
            'id': registro.id,
            'fecha': registro.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'titulo': registro.titulo,
            'descripcion': registro.descripcion,
            'procedimiento': registro.procedimiento,
            'odontograma': registro.odontograma,
            'observaciones': registro.observaciones,
            'creado_por': registro.creado_por.get_full_name() if registro.creado_por else 'Sistema',
            'turno_id': registro.turno.id if registro.turno else None
        }
        
        return JsonResponse({
            'status': 'success',
            'registro': registro_data
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@user_passes_test(es_admin)
@require_http_methods(['POST'])
def actualizar_registro(request, registro_id):
    """
    Actualiza un registro existente en el historial clínico.
    """
    try:
        registro = get_object_or_404(RegistroHistorial, id=registro_id)
        data = json.loads(request.body)
        
        # Actualizar los campos del registro
        if 'titulo' in data:
            registro.titulo = data['titulo']
        if 'descripcion' in data:
            registro.descripcion = data['descripcion']
        if 'procedimiento' in data:
            registro.procedimiento = data['procedimiento']
        if 'odontograma' in data:
            registro.odontograma = data['odontograma']
        if 'observaciones' in data:
            registro.observaciones = data['observaciones']
        
        # Actualizar el turno asociado si se proporciona
        if 'turno_id' in data and data['turno_id']:
            try:
                turno = Turno.objects.get(id=data['turno_id'])
                registro.turno = turno
            except Turno.DoesNotExist:
                pass
        
        # Guardar los cambios
        registro.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Registro actualizado correctamente'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@user_passes_test(es_admin)
@require_http_methods(['DELETE', 'POST'])
def eliminar_registro(request, registro_id):
    """
    Elimina un registro del historial clínico.
    """
    try:
        registro = get_object_or_404(RegistroHistorial, id=registro_id)
        
        # Guardar información para el mensaje
        fecha = registro.fecha_creacion.strftime('%d/%m/%Y')
        titulo = registro.titulo
        
        # Eliminar el registro
        registro.delete()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Registro "{titulo}" del {fecha} eliminado correctamente'
        })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)