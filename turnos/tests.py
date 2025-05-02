from django.test import TestCase
from django.contrib.auth.models import User
from .models import Paciente, Turno, Horario
from datetime import date, time

class PacienteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.paciente = Paciente.objects.create(
            usuario=self.user,
            nombre='Juan',
            apellido='Pérez',
            email='juan@example.com',
            telefono='1234567890',
            fecha_nacimiento=date(1990, 1, 1)
        )

    def test_paciente_creation(self):
        self.assertTrue(isinstance(self.paciente, Paciente))
        self.assertEqual(str(self.paciente), 'Juan Pérez')

class TurnoTests(TestCase):
    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre='María',
            apellido='García',
            email='maria@example.com',
            telefono='0987654321',
            fecha_nacimiento=date(1995, 5, 15)
        )
        self.turno = Turno.objects.create(
            paciente=self.paciente,
            fecha=date(2024, 1, 1),
            hora=time(10, 0),
            motivo_consulta='Consulta de rutina',
            estado='pendiente'
        )

    def test_turno_creation(self):
        self.assertTrue(isinstance(self.turno, Turno))
        self.assertEqual(self.turno.estado, 'pendiente')

class HorarioTests(TestCase):
    def setUp(self):
        self.horario = Horario.objects.create(
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(18, 0)
        )

    def test_horario_creation(self):
        self.assertTrue(isinstance(self.horario, Horario))
        self.assertEqual(self.horario.dia_semana, 1)