from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Turno

@receiver(post_save, sender=Turno)
def notificar_turno_creado(sender, instance, created, **kwargs):
    """Envía una notificación por correo cuando se crea un nuevo turno."""
    if created:
        subject = 'Nuevo turno registrado'
        message = f'Se ha registrado un nuevo turno para {instance.paciente} el {instance.fecha} a las {instance.hora}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.paciente.email]
        
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print(f'Error al enviar el correo: {e}')

@receiver(post_save, sender=Turno)
def notificar_turno_actualizado(sender, instance, created, **kwargs):
    """Envía una notificación por correo cuando se actualiza un turno."""
    if not created:
        subject = 'Turno actualizado'
        message = f'Su turno para el {instance.fecha} a las {instance.hora} ha sido actualizado. Estado: {instance.estado}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.paciente.email]
        
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print(f'Error al enviar el correo: {e}')

@receiver(pre_delete, sender=Turno)
def notificar_turno_cancelado(sender, instance, **kwargs):
    """Envía una notificación por correo cuando se cancela un turno."""
    subject = 'Turno cancelado'
    message = f'Su turno para el {instance.fecha} a las {instance.hora} ha sido cancelado.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [instance.paciente.email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(f'Error al enviar el correo: {e}')