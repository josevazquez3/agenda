from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    email = models.EmailField(unique=True, error_messages={'unique': 'Ya existe un usuario con este correo electrónico.'})
    DNI = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    calle = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    piso = models.CharField(max_length=10, blank=True, null=True)
    departamento = models.CharField(max_length=10, blank=True, null=True)
    obra_social = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    
    # Roles de usuario
    ROL_CHOICES = (
        ('paciente', 'Paciente'),
        ('secretaria', 'Secretaria'),
        ('admin', 'Administrador'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='paciente')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class DiasDisponibles(models.Model):
    fecha = models.DateField()
    disponible = models.BooleanField(default=True)
    motivo = models.CharField(max_length=255, blank=True, null=True, help_text="Motivo por el cual el día no está disponible")
    
    def __str__(self):
        return f"{self.fecha} - {'Disponible' if self.disponible else 'No disponible'}"
    
    class Meta:
        verbose_name = "Día disponible"
        verbose_name_plural = "Días disponibles"
        ordering = ['fecha']

class HorarioDisponible(models.Model):
    dia = models.ForeignKey(DiasDisponibles, on_delete=models.CASCADE, related_name='horarios')
    hora_inicio = models.TimeField()
    disponible = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.dia.fecha} - {self.hora_inicio} - {'Disponible' if self.disponible else 'Ocupado'}"
    
    class Meta:
        # Asegurar que no haya horarios duplicados para un mismo día
        unique_together = ('dia', 'hora_inicio')
        # Ordenar los horarios por hora
        ordering = ['hora_inicio']

class Turno(models.Model):
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='turnos')
    dia = models.ForeignKey(DiasDisponibles, on_delete=models.CASCADE)
    horario = models.ForeignKey(HorarioDisponible, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
        ('completado', 'Completado'),
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    def __str__(self):
        return f"Turno de {self.paciente} - {self.dia.fecha} {self.horario.hora_inicio}"
    
    class Meta:
        # Ordenar los turnos por fecha y hora
        ordering = ['dia__fecha', 'horario__hora_inicio']

class HistorialPaciente(models.Model):
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historial')
    fecha = models.DateTimeField(default=timezone.now)
    observaciones = models.TextField()
    
    def __str__(self):
        return f"Historial de {self.paciente} - {self.fecha.strftime('%d/%m/%Y')}"

class HistorialClinico(models.Model):
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='historial_clinico')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Historial Clínico de {self.paciente}"

class RegistroHistorial(models.Model):
    historial = models.ForeignKey(HistorialClinico, on_delete=models.CASCADE, related_name='registros')
    fecha = models.DateTimeField(default=timezone.now)
    descripcion = models.TextField()
    tratamiento = models.TextField(blank=True, null=True)
    medicamentos = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Registro de {self.historial.paciente} - {self.fecha.strftime('%d/%m/%Y')}"

class ImagenHistorial(models.Model):
    historial = models.ForeignKey(HistorialPaciente, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='historial_imagenes/')
    
    def __str__(self):
        return f"Imagen de {self.historial.paciente} - {self.historial.fecha.strftime('%d/%m/%Y')}"

# Modelos adicionales para la configuración de horarios

class ConfiguracionHorario(models.Model):
    """
    Modelo para representar configuraciones de horarios regulares por día de la semana
    """
    DIAS_SEMANA = (
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    )
    
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_turno = models.IntegerField(default=30, help_text="Duración del turno en minutos")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Configuración de horario"
        verbose_name_plural = "Configuraciones de horarios"
        ordering = ['dia_semana', 'hora_inicio']
        unique_together = ['dia_semana', 'hora_inicio', 'hora_fin']
    
    def __str__(self):
        return f"{self.get_dia_semana_display()} - {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"

class ExcepcionHorario(models.Model):
    """
    Modelo para representar excepciones en el calendario (feriados, vacaciones, etc.)
    """
    fecha = models.DateField(unique=True)
    disponible = models.BooleanField(default=False)
    motivo = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Excepción"
        verbose_name_plural = "Excepciones"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.fecha.strftime('%d/%m/%Y')} - {self.motivo}"