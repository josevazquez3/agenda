from django.contrib import admin
from .models import Usuario, Turno, DiasDisponibles, HorarioDisponible, HistorialPaciente, ImagenHistorial, HistorialClinico, RegistroHistorial

# Registrar modelos en el panel de administración
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'DNI', 'rol', 'is_active')
    list_filter = ('rol', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'DNI')
    list_editable = ('rol', 'is_active')
    actions = ['activar_usuarios', 'desactivar_usuarios', 'establecer_rol_paciente', 'establecer_rol_secretaria', 'establecer_rol_admin']
    change_list_template = 'admin/usuario_changelist.html'
    
    def activar_usuarios(self, request, queryset):
        queryset.update(is_active=True)
    activar_usuarios.short_description = "Activar usuarios seleccionados"
    
    def desactivar_usuarios(self, request, queryset):
        queryset.update(is_active=False)
    desactivar_usuarios.short_description = "Desactivar usuarios seleccionados"
    
    def establecer_rol_paciente(self, request, queryset):
        queryset.update(rol='paciente')
    establecer_rol_paciente.short_description = "Establecer como Paciente"
    
    def establecer_rol_secretaria(self, request, queryset):
        queryset.update(rol='secretaria')
    establecer_rol_secretaria.short_description = "Establecer como Secretaria"
    
    def establecer_rol_admin(self, request, queryset):
        queryset.update(rol='admin')
    establecer_rol_admin.short_description = "Establecer como Administrador"
    
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (
                ('Información de acceso', {
                    'fields': ('username', 'email', 'password')
                }),
                ('Información personal', {
                    'fields': ('first_name', 'last_name', 'DNI', 'telefono', 'foto')
                }),
                ('Dirección', {
                    'fields': ('calle', 'numero', 'piso', 'departamento')
                }),
                ('Información médica', {
                    'fields': ('obra_social',)
                }),
                ('Permisos', {
                    'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
                }),
            )
        return (
            ('Información de acceso', {
                'fields': ('username', 'email')
            }),
            ('Información personal', {
                'fields': ('first_name', 'last_name', 'DNI', 'telefono', 'foto')
            }),
            ('Dirección', {
                'fields': ('calle', 'numero', 'piso', 'departamento')
            }),
            ('Información médica', {
                'fields': ('obra_social',)
            }),
        )
    
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        return ()

    fieldsets = (
        ('Información de acceso', {
            'fields': ('username', 'email', 'password')
        }),
        ('Información personal', {
            'fields': ('first_name', 'last_name', 'DNI', 'telefono', 'foto')
        }),
        ('Dirección', {
            'fields': ('calle', 'numero', 'piso', 'departamento')
        }),
        ('Información médica', {
            'fields': ('obra_social',)
        }),
        ('Permisos', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )

class ImagenHistorialInline(admin.TabularInline):
    model = ImagenHistorial
    extra = 1

@admin.register(HistorialPaciente)
class HistorialPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha', 'get_observaciones')
    list_filter = ('fecha',)
    search_fields = ('paciente__first_name', 'paciente__last_name', 'observaciones')
    inlines = [ImagenHistorialInline]
    change_list_template = 'admin/change_list.html'
    
    def get_observaciones(self, obj):
        return obj.observaciones[:100] + '...' if len(obj.observaciones) > 100 else obj.observaciones
    get_observaciones.short_description = 'Observaciones'
    
    def get_queryset(self, request):
        # Aseguramos que devuelva un QuerySet y no un objeto único
        queryset = super().get_queryset(request)
        return queryset.select_related('paciente').order_by('-fecha')
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Historial de Pacientes'
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'dia', 'horario', 'estado', 'fecha_solicitud')
    list_filter = ('estado', 'dia__fecha')
    search_fields = ('paciente__first_name', 'paciente__last_name', 'paciente__DNI')
    date_hierarchy = 'fecha_solicitud'
    list_editable = ('estado',)
    raw_id_fields = ('paciente',)
    autocomplete_fields = ['paciente']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "horario":
            kwargs["queryset"] = HorarioDisponible.objects.filter(disponible=True)
        if db_field.name == "dia":
            kwargs["queryset"] = DiasDisponibles.objects.filter(disponible=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo turno
            obj.horario.disponible = False
            obj.horario.save()
        super().save_model(request, obj, form, change)

class HorarioInline(admin.TabularInline):
    model = HorarioDisponible
    extra = 1
    fields = ['hora_inicio', 'disponible']

@admin.register(DiasDisponibles)
class DiasDisponiblesAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'disponible', 'motivo')
    list_filter = ('disponible',)
    list_editable = ('disponible', 'motivo',)
    date_hierarchy = 'fecha'
    search_fields = ('fecha', 'motivo')
    actions = ['marcar_como_disponible', 'marcar_como_no_disponible']
    inlines = [HorarioInline]
    
    def get_queryset(self, request):
        # Aseguramos que devuelva un QuerySet y no un objeto único
        queryset = super().get_queryset(request)
        return queryset.order_by('fecha')
    
    def marcar_como_disponible(self, request, queryset):
        queryset.update(disponible=True)
    marcar_como_disponible.short_description = "Marcar días como disponibles"
    
    def marcar_como_no_disponible(self, request, queryset):
        queryset.update(disponible=False)
    marcar_como_no_disponible.short_description = "Marcar días como no disponibles"

@admin.register(HorarioDisponible)
class HorarioDisponibleAdmin(admin.ModelAdmin):
    list_display = ('dia', 'hora_inicio', 'disponible')
    list_filter = ('disponible', 'dia__fecha')
    list_editable = ('disponible',)
    actions = ['marcar_como_disponible', 'marcar_como_no_disponible']
    
    def marcar_como_disponible(self, request, queryset):
        queryset.update(disponible=True)
    marcar_como_disponible.short_description = "Marcar horarios como disponibles"
    
    def marcar_como_no_disponible(self, request, queryset):
        queryset.update(disponible=False)
    marcar_como_no_disponible.short_description = "Marcar horarios como no disponibles"

@admin.register(HistorialClinico)
class HistorialClinicoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'fecha_creacion', 'ultima_actualizacion')
    search_fields = ('paciente__first_name', 'paciente__last_name')
    
    def get_queryset(self, request):
        # Aseguramos que devuelva un QuerySet y no un objeto único
        queryset = super().get_queryset(request)
        return queryset.select_related('paciente')

@admin.register(RegistroHistorial)
class RegistroHistorialAdmin(admin.ModelAdmin):
    list_display = ('historial', 'fecha', 'get_descripcion')
    list_filter = ('fecha',)
    search_fields = ('historial__paciente__first_name', 'historial__paciente__last_name', 'descripcion')
    
    def get_descripcion(self, obj):
        return obj.descripcion[:100] + '...' if len(obj.descripcion) > 100 else obj.descripcion
    get_descripcion.short_description = 'Descripción'