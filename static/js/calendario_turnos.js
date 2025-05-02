document.addEventListener('DOMContentLoaded', function() {
    // Verificar si el elemento calendario existe
    const calendarElement = document.querySelector('#calendar');
    if (!calendarElement) return;

    // Obtener días disponibles del backend
    let diasDisponibles = [];
    try {
        diasDisponibles = JSON.parse(document.getElementById('calendar').dataset.diasDisponibles || '[]');
    } catch (error) {
        console.error('Error al parsear días disponibles:', error);
        diasDisponibles = window.diasDisponibles || [];
    }

    // Inicializar el calendario con Flatpickr
    const calendar = flatpickr('#calendar', {
        locale: 'es',
        inline: true,
        minDate: 'today',
        dateFormat: 'Y-m-d',
        disable: [
            function(date) {
                // Deshabilitar domingos y días no disponibles
                const formattedDate = date.toISOString().split('T')[0];
                return date.getDay() === 0 || !diasDisponibles.includes(formattedDate);
            }
        ],
        onChange: function(selectedDates, dateStr) {
            if (selectedDates.length > 0) {
                mostrarHorariosDisponibles(dateStr);
            } else {
                // Limpiar la selección si no hay fechas seleccionadas
                document.getElementById('fecha-seleccionada').textContent = 'Selecciona una fecha';
                document.getElementById('lista-horarios').classList.add('d-none');
                document.getElementById('confirmar-container').classList.add('d-none');
                document.getElementById('mensaje-horarios').classList.remove('d-none');
            }
        },
        onReady: function() {
            // Marcar visualmente los días disponibles
            diasDisponibles.forEach(fecha => {
                const element = document.querySelector(`[data-date="${fecha}"]`);
                if (element) {
                    element.classList.add('dia-disponible');
                }
            });
        }
    });

    // Función para mostrar los horarios disponibles
    async function mostrarHorariosDisponibles(fecha) {
        // Actualizar el título con la fecha seleccionada
        const fechaFormateada = new Date(fecha).toLocaleDateString('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        document.getElementById('fecha-seleccionada').textContent = `Horarios disponibles para el ${fechaFormateada}`;

        // Mostrar indicador de carga
        const listaHorarios = document.getElementById('lista-horarios');
        const mensajeHorarios = document.getElementById('mensaje-horarios');
        const confirmarContainer = document.getElementById('confirmar-container');

        listaHorarios.classList.add('d-none');
        confirmarContainer.classList.add('d-none');

        mensajeHorarios.innerHTML = `
            <div class="text-center py-3">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="text-muted mt-2">Cargando horarios disponibles...</p>
            </div>
        `;
        mensajeHorarios.classList.remove('d-none');

        try {

            // Obtener horarios disponibles del servidor
            const response = await fetch(`/turnos/horarios/${fecha}/`);
            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            const horarios = data.horarios;
            if (!Array.isArray(horarios)) {
                throw new Error('Formato de respuesta inválido');
            }

            // Mostrar horarios disponibles
            if (horarios.length > 0) {
                let horariosHTML = '<div class="row g-3">';
                horarios.forEach(horario => {
                    horariosHTML += `
                        <div class="col-sm-6 col-md-4">
                            <button class="btn btn-outline-primary w-100 horario-btn" 
                                    data-horario-id="${horario.id}"
                                    data-hora="${horario.hora}"
                                    onclick="seleccionarHorario(this)">
                                <i class="far fa-clock me-2"></i>${horario.hora}
                            </button>
                        </div>
                    `;
                });
                horariosHTML += '</div>';
                listaHorarios.innerHTML = horariosHTML;
                listaHorarios.classList.remove('d-none');
                mensajeHorarios.classList.add('d-none');
            } else {
                mensajeHorarios.innerHTML = `
                    <div class="text-center py-3">
                        <i class="fas fa-calendar-times fa-2x mb-3 d-block text-muted"></i>
                        <p class="text-muted">No hay horarios disponibles para esta fecha.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error:', error);
            mensajeHorarios.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error al cargar los horarios disponibles. Por favor, intente nuevamente.
                </div>
            `;
        }
    }

    // Función para seleccionar un horario
    window.seleccionarHorario = function(btn) {
        try {
            // Remover selección previa
            document.querySelectorAll('.horario-btn').forEach(button => {
                button.classList.remove('btn-primary');
                button.classList.add('btn-outline-primary');
            });

            // Marcar el horario seleccionado
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-primary');

            // Obtener elementos necesarios
            const confirmarContainer = document.getElementById('confirmar-container');
            const resumenTurno = document.getElementById('resumen-turno');
            const horarioIdInput = document.getElementById('horario_id');

            if (!confirmarContainer || !resumenTurno || !horarioIdInput) {
                throw new Error('No se encontraron todos los elementos necesarios');
            }

            // Obtener datos del horario seleccionado
            const fechaSeleccionada = document.getElementById('fecha-seleccionada')?.textContent || 'Fecha no disponible';
            const horaSeleccionada = btn.dataset.hora || 'Hora no disponible';
            const horarioId = btn.dataset.horarioId;

            if (!horarioId) {
                throw new Error('ID de horario no disponible');
            }

            // Actualizar resumen y mostrar contenedor de confirmación
            resumenTurno.innerHTML = `
                <p class="mb-1"><i class="fas fa-calendar-day me-2"></i>${fechaSeleccionada}</p>
                <p class="mb-0"><i class="fas fa-clock me-2"></i>${horaSeleccionada}</p>
            `;

            horarioIdInput.value = horarioId;
            confirmarContainer.classList.remove('d-none');
        } catch (error) {
            console.error('Error al seleccionar horario:', error);
            alert('Hubo un error al seleccionar el horario. Por favor, intente nuevamente.');
        }
    };
});