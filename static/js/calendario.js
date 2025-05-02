document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    
    if (calendarEl) {
        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            locale: 'es',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            buttonText: {
                today: 'Hoy',
                month: 'Mes',
                week: 'Semana',
                day: 'Día'
            },
            events: '/api/turnos/',
            eventClick: function(info) {
                mostrarDetallesTurno(info.event);
            },
            dateClick: function(info) {
                if (puedeCrearTurno()) {
                    solicitarTurno(info.date);
                }
            },
            eventClassNames: function(arg) {
                return ['turno-' + arg.event.extendedProps.estado];
            }
        });

        calendar.render();
    }
});

function mostrarDetallesTurno(evento) {
    // Implementar lógica para mostrar modal con detalles del turno
    const modal = new bootstrap.Modal(document.getElementById('turnoModal'));
    document.getElementById('turnoTitulo').textContent = `Turno: ${evento.title}`;
    document.getElementById('turnoDetalles').innerHTML = `
        <p><strong>Fecha:</strong> ${evento.start.toLocaleDateString()}</p>
        <p><strong>Hora:</strong> ${evento.start.toLocaleTimeString()}</p>
        <p><strong>Estado:</strong> ${evento.extendedProps.estado}</p>
    `;
    modal.show();
}

function solicitarTurno(fecha) {
    // Obtener horarios disponibles para la fecha seleccionada
    fetch(`/api/horarios-disponibles/?fecha=${fecha.toISOString().split('T')[0]}`)
        .then(response => response.json())
        .then(horarios => {
            if (horarios.length > 0) {
                mostrarFormularioTurno(fecha, horarios);
            } else {
                alert('No hay horarios disponibles para la fecha seleccionada');
            }
        })
        .catch(error => console.error('Error:', error));
}

function mostrarFormularioTurno(fecha, horarios) {
    const modal = new bootstrap.Modal(document.getElementById('nuevoTurnoModal'));
    const selectHorario = document.getElementById('horarioTurno');
    
    // Limpiar opciones anteriores
    selectHorario.innerHTML = '';
    
    // Agregar horarios disponibles
    horarios.forEach(horario => {
        const option = document.createElement('option');
        option.value = horario;
        option.textContent = horario;
        selectHorario.appendChild(option);
    });
    
    // Establecer fecha seleccionada
    document.getElementById('fechaTurno').value = fecha.toISOString().split('T')[0];
    
    modal.show();
}

function puedeCrearTurno() {
    // Verificar si el usuario está autenticado
    const userAuthenticated = document.body.dataset.userAuthenticated === 'true';
    if (!userAuthenticated) {
        alert('Debe iniciar sesión para solicitar un turno');
        window.location.href = '/usuarios/login/';
        return false;
    }
    return true;
}