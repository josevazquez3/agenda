document.addEventListener('DOMContentLoaded', function() {
    const userSelect = document.getElementById('usuario_id');
    const formSolicitarTurno = document.getElementById('formSolicitarTurno');
    const calendar = document.getElementById('calendar');
    const horariosContainer = document.getElementById('horarios-container');
    const listaHorarios = document.getElementById('lista-horarios');
    const confirmarContainer = document.getElementById('confirmar-container');
    const resumenTurno = document.getElementById('resumen-turno');
    const horarioIdInput = document.getElementById('horario_id');
    const mensajeError = document.getElementById('mensaje-error');

    // Validar selección de usuario
    function validarUsuarioSeleccionado() {
        if (!userSelect.value) {
            Swal.fire({
                icon: 'warning',
                title: 'Selección requerida',
                text: 'Por favor, seleccione un paciente antes de continuar.'
            });
            return false;
        }
        return true;
    }

    // Inicializar el calendario
    let diasDisponibles = [];
    let calendarInstance = null;
    
    // Cargar días disponibles desde el servidor
    fetch('/turnos/dias-disponibles/')
        .then(response => response.json())
        .then(data => {
            diasDisponibles = data.dias_disponibles;
            initializeCalendar();
        })
        .catch(error => {
            console.error('Error al cargar días disponibles:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'No se pudieron cargar los días disponibles'
            });
        });

    function initializeCalendar() {
        const calendarEl = calendar;
        calendarInstance = new FullCalendar.Calendar(calendarEl, {
            locale: 'es',
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth'
            },
            dayMaxEvents: true,
            selectable: true,
            unselectAuto: true,
            selectConstraint: {
                start: new Date().toISOString().split('T')[0],
                end: '2100-01-01'
            },
            dayCellDidMount: function(arg) {
                const dateStr = arg.date.toISOString().split('T')[0];
                if (diasDisponibles.includes(dateStr)) {
                    arg.el.classList.add('available');
                    arg.el.style.backgroundColor = '#e8f5e9';
                    arg.el.style.cursor = 'pointer';
                }
            },
            dateClick: handleDateClick
        });

        calendarInstance.render();
    }

    function handleDateClick(info) {
        const clickedDate = info.dateStr;
        
        if (!diasDisponibles.includes(clickedDate)) {
            Swal.fire({
                icon: 'error',
                title: 'Fecha no disponible',
                text: 'Por favor selecciona una fecha marcada como disponible.'
            });
            return;
        }

        if (!validarUsuarioSeleccionado()) return;

        document.getElementById('fecha-seleccionada').textContent = `Horarios para el ${new Date(clickedDate).toLocaleDateString()}`;
        
        // Verificar si el elemento existe antes de manipularlo
        const mensajeHorarios = document.getElementById('mensaje-horarios');
        if (mensajeHorarios) {
            mensajeHorarios.classList.add('d-none');
        }
        
        listaHorarios.classList.remove('d-none');
        confirmarContainer.classList.add('d-none');
        
        // Mostrar indicador de carga
        listaHorarios.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2">Cargando horarios disponibles...</p>
            </div>
        `;

        fetch(`/turnos/horarios-disponibles/${clickedDate}/`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.horarios && data.horarios.length > 0) {
                    listaHorarios.innerHTML = data.horarios.map(horario => `
                        <button class="btn btn-outline-primary horario-btn mb-2 me-2" 
                                data-horario-id="${horario.id}" 
                                data-hora="${horario.hora}">
                            <i class="far fa-clock me-1"></i>${horario.hora}
                        </button>
                    `).join('');

                    // Agregar eventos a los botones de horario
                    document.querySelectorAll('.horario-btn').forEach(btn => {
                        btn.addEventListener('click', function() {
                            const horarioId = this.dataset.horarioId;
                            const hora = this.dataset.hora;
                            const usuario = userSelect.options[userSelect.selectedIndex].text;

                            document.querySelectorAll('.horario-btn').forEach(b => b.classList.remove('active'));
                            this.classList.add('active');

                            horarioIdInput.value = horarioId;
                            resumenTurno.innerHTML = `
                                <div class="card border-primary">
                                    <div class="card-header bg-primary text-white">
                                        <i class="fas fa-info-circle me-2"></i>Resumen del Turno
                                    </div>
                                    <div class="card-body">
                                        <p class="mb-2"><i class="far fa-calendar me-2"></i><strong>Fecha:</strong> ${new Date(clickedDate).toLocaleDateString()}</p>
                                        <p class="mb-2"><i class="far fa-clock me-2"></i><strong>Hora:</strong> ${hora}</p>
                                        <p class="mb-2"><i class="far fa-user me-2"></i><strong>Paciente:</strong> ${usuario}</p>
                                    </div>
                                </div>
                            `;
                            confirmarContainer.classList.remove('d-none');
                        });
                    });
                } else {
                    listaHorarios.innerHTML = `
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            No hay horarios disponibles para esta fecha.
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                listaHorarios.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        Error al cargar los horarios disponibles. Por favor intente nuevamente.
                    </div>
                `;
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los horarios disponibles'
                });
            });
    }

    // Opcional: Evento para el envío del formulario
    if (formSolicitarTurno) {
        formSolicitarTurno.addEventListener('submit', function(event) {
            if (!horarioIdInput.value) {
                event.preventDefault();
                Swal.fire({
                    icon: 'warning',
                    title: 'Información incompleta',
                    text: 'Por favor, seleccione un horario antes de confirmar el turno.'
                });
            }
        });
    }
});