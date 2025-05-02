from django.apps import AppConfig

class TurnosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'turnos'
    verbose_name = 'Gestión de Turnos'

    def ready(self):
        import turnos.signals