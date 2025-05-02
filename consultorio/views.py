from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from turnos.models import HorarioDisponible, DiasDisponibles


def inicio(request):
    return render(request, 'index.html')

@login_required
def admin_configurar_horarios(request):
    if not request.user.is_staff:
        return redirect('inicio')
    
    if request.method == 'POST':
        horarios = request.POST.getlist('horarios[]')
        try:
            with transaction.atomic():
                # Eliminar horarios anteriores
                HorarioDisponible.objects.all().delete()
                
                # Crear nuevos horarios predeterminados
                for hora in horarios:
                    for dia in DiasDisponibles.objects.filter(disponible=True):
                        HorarioDisponible.objects.create(
                            dia=dia,
                            hora_inicio=hora,
                            disponible=True
                        )
            messages.success(request, 'Horarios actualizados correctamente')
        except Exception as e:
            messages.error(request, 'Error al actualizar los horarios')
        
        return redirect('admin_configurar_horarios')
    
    return render(request, 'admin/configurar_horarios.html')

@login_required
def get_horarios(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    horarios = HorarioDisponible.objects.values('id', 'hora_inicio', 'disponible').distinct()
    return JsonResponse(list(horarios), safe=False)

@login_required
def eliminar_horario(request, horario_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        horario = HorarioDisponible.objects.get(id=horario_id)
        horario.delete()
        return JsonResponse({'success': True})
    except HorarioDisponible.DoesNotExist:
        return JsonResponse({'error': 'Horario no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)