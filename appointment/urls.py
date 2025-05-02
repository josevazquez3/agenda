from django.urls import path
from . import views


app_name = 'appointment'

urlpatterns = [
    path('list/', views.DentalAppointmentListView.as_view(), name='list'),
    path('create/', views.DentalAppointmentView.as_view(), name='create'),
    path('api/horarios-disponibles/<int:dia_id>/', views.horarios_disponibles_api, name='horarios_disponibles_api'),
]