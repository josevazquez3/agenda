from django.db import models

class ConfiguracionHorario(models.Model):
    DIAS_SEMANA = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ]

    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_turno = models.IntegerField(default=30)  # duración en minutos
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Configuración de Horario'
        verbose_name_plural = 'Configuraciones de Horarios'
        unique_together = ['dia_semana', 'hora_inicio', 'hora_fin']

    def __str__(self):
        return f"{self.get_dia_semana_display()} - {self.hora_inicio} a {self.hora_fin}"

class ExcepcionHorario(models.Model):
    fecha = models.DateField(unique=True)
    disponible = models.BooleanField(default=False)
    motivo = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = 'Excepción de Horario'
        verbose_name_plural = 'Excepciones de Horarios'

    def __str__(self):
        estado = 'disponible' if self.disponible else 'no disponible'
        return f"{self.fecha} - {estado}"