import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'consultorio.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

def fix_duplicate_emails():
    User = get_user_model()
    
    # Obtener todos los usuarios ordenados por fecha de registro
    users = User.objects.all().order_by('date_joined')
    
    # Diccionario para mantener un registro de los correos electrónicos vistos
    seen_emails = {}
    
    # Iterar sobre los usuarios y modificar los correos duplicados
    for user in users:
        email = user.email.lower()  # Normalizar el email a minúsculas
        
        if email in seen_emails:
            # Si el email ya existe, agregar un sufijo numérico
            base_email = email.split('@')[0]
            domain = email.split('@')[1]
            counter = 1
            
            while f"{base_email}_{counter}@{domain}" in seen_emails:
                counter += 1
            
            new_email = f"{base_email}_{counter}@{domain}"
            user.email = new_email
            user.save()
            
            print(f"Correo duplicado encontrado: {email}")
            print(f"Nuevo correo asignado: {new_email}")
        
        seen_emails[user.email] = user

if __name__ == '__main__':
    try:
        fix_duplicate_emails()
        print("\nProceso completado exitosamente.")
        print("Ahora puede ejecutar 'python manage.py migrate' para aplicar los cambios.")
    except Exception as e:
        print(f"\nError durante el proceso: {str(e)}")