from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Turno, HistorialPaciente, ImagenHistorial, DiasDisponibles, HorarioDisponible

class UsuarioRegistroForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nombres',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese sus nombres'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Apellidos',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese sus apellidos'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.com'})
    )
    DNI = forms.CharField(
        max_length=20,
        required=True,
        label='DNI',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su DNI'})
    )
    telefono = forms.CharField(
        max_length=20,
        required=True,
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su teléfono'})
    )
    calle = forms.CharField(
        max_length=100,
        required=True,
        label='Calle',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre de la calle'})
    )
    numero = forms.CharField(
        max_length=10,
        required=True,
        label='Número',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de casa/edificio'})
    )
    piso = forms.CharField(
        max_length=10,
        required=False,
        label='Piso',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Piso (opcional)'})
    )
    departamento = forms.CharField(
        max_length=10,
        required=False,
        label='Departamento',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Departamento (opcional)'})
    )
    obra_social = forms.CharField(
        max_length=100,
        required=False,
        label='Obra Social o particular',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la obra social (opcional)'})
    )
    foto = forms.ImageField(
        required=False,
        label='Foto de perfil',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Nombre de usuario'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirmar contraseña'})

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'DNI', 'telefono', 
                 'calle', 'numero', 'piso', 'departamento', 'obra_social', 'foto', 'password1', 'password2')

    def clean_DNI(self):
        dni = self.cleaned_data.get('DNI')
        if not dni.isdigit():
            raise forms.ValidationError('El DNI debe contener solo números')
        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError('El teléfono debe contener solo números')
        return telefono

class UsuarioLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        if email and username:
            try:
                user = Usuario.objects.get(username=username)
                if user.email != email:
                    raise forms.ValidationError('El correo electrónico no coincide con el usuario ingresado.')
            except Usuario.DoesNotExist:
                pass
        return cleaned_data

class TurnoForm(forms.Form):
    fecha = forms.DateField(widget=forms.HiddenInput(), required=False)
    horario = forms.ModelChoiceField(queryset=HorarioDisponible.objects.none(), required=False, empty_label=None)
    
    def __init__(self, *args, **kwargs):
        fecha_seleccionada = kwargs.pop('fecha_seleccionada', None)
        super(TurnoForm, self).__init__(*args, **kwargs)
        
        if fecha_seleccionada:
            try:
                dia = DiasDisponibles.objects.get(fecha=fecha_seleccionada, disponible=True)
                self.fields['horario'].queryset = HorarioDisponible.objects.filter(dia=dia, disponible=True)
                self.fields['fecha'].initial = fecha_seleccionada
            except DiasDisponibles.DoesNotExist:
                pass

class HistorialPacienteForm(forms.ModelForm):
    class Meta:
        model = HistorialPaciente
        fields = ['observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class ImagenHistorialForm(forms.ModelForm):
    class Meta:
        model = ImagenHistorial
        fields = ['imagen']

class DiasDisponiblesForm(forms.ModelForm):
    class Meta:
        model = DiasDisponibles
        fields = ['fecha', 'disponible']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class HorarioDisponibleForm(forms.ModelForm):
    class Meta:
        model = HorarioDisponible
        fields = ['dia', 'hora_inicio', 'disponible']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class UsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'DNI', 'telefono', 
                 'calle', 'numero', 'piso', 'departamento', 'obra_social', 'foto', 'rol', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'DNI': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'piso': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'obra_social': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }