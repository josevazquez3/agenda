# Script para crear datos de prueba
# Ejecutar con: python manage.py shell < script_crear_datos_prueba.py

from turnos.models import DiasDisponibles, HorarioDisponible
from datetime import date, time, timedelta

# Crear fechas disponibles para los próximos 30 días
fecha_actual = date.today()
for i in range(30):
    fecha = fecha_actual + timedelta(days=i)
    # Solo días de semana (lunes a viernes)
    if fecha.weekday() < 5:  # 0-4 son lunes a viernes
        dia, created = DiasDisponibles.objects.get_or_create(
            fecha=fecha,
            defaults={'disponible': True}
        )
        
        # Si el día fue creado, agregar horarios disponibles
        if created:
            print(f"Día creado: {fecha}")
            
            # Horarios de mañana: 8:00 a 12:00 cada 30 minutos
            for hora in range(8, 13):
                for minuto in [0, 30]:
                    horario = time(hora, minuto)
                    HorarioDisponible.objects.create(
                        dia=dia,
                        hora_inicio=horario,
                        disponible=True
                    )
                    print(f"  Horario creado: {horario}")
            
            # Horarios de tarde: 14:00 a 18:00 cada 30 minutos
            for hora in range(14, 19):
                for minuto in [0, 30]:
                    horario = time(hora, minuto)
                    HorarioDisponible.objects.create(
                        dia=dia,
                        hora_inicio=horario,
                        disponible=True
                    )
                    print(f"  Horario creado: {horario}")

print("Datos de prueba creados exitosamente!")