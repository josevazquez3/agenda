from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

class UsuarioRolEstadoForm(forms.ModelForm):
    ROL_CHOICES = [
        ('paciente', 'Paciente'),
        ('secretaria', 'Secretaría'),
        ('admin', 'Administrador')
    ]
    
    rol = forms.ChoiceField(
        choices=ROL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Usuario activo'
    )
    
    is_staff = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Permisos de administrador'
    )
    
    class Meta:
        model = get_user_model()
        fields = ['rol', 'is_active', 'is_staff']

class UsuarioLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
    def clean_username(self):
        email = self.cleaned_data.get('username')
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            return user.username
        except User.DoesNotExist:
            raise forms.ValidationError('No existe una cuenta con este correo electrónico.')