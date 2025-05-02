// Funciones para la gestión de turnos
const turnosApp = {
    init: function() {
        this.bindEvents();
        this.initializeDatePickers();
    },

    bindEvents: function() {
        // Formulario de solicitud de turno
        const formSolicitudTurno = document.getElementById('formSolicitudTurno');
        if (formSolicitudTurno) {
            formSolicitudTurno.addEventListener('submit', this.handleSolicitudTurno);
        }

        // Botones de confirmación/cancelación
        document.querySelectorAll('.btn-confirmar-turno').forEach(btn => {
            btn.addEventListener('click', this.confirmarTurno);
        });

        document.querySelectorAll('.btn-cancelar-turno').forEach(btn => {
            btn.addEventListener('click', this.cancelarTurno);
        });

        // Filtros de búsqueda en listados
        const filtroTurnos = document.getElementById('filtroTurnos');
        if (filtroTurnos) {
            filtroTurnos.addEventListener('input', this.filtrarTurnos);
        }
    },

    initializeDatePickers: function() {
        // Inicializar datepickers para campos de fecha
        document.querySelectorAll('.date-picker').forEach(input => {
            if (input) {
                // Configurar datepicker con opciones locales
                const datepicker = new Datepicker(input, {
                    language: 'es',
                    autohide: true,
                    format: 'yyyy-mm-dd',
                    weekStart: 1,
                    daysOfWeekDisabled: [0], // Domingo deshabilitado
                    beforeShowDay: this.validarFechaDisponible
                });
            }
        });
    },

    handleSolicitudTurno: async function(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (response.ok) {
                const data = await response.json();
                window.location.href = data.redirect_url;
            } else {
                this.mostrarError('Error al procesar la solicitud');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error de conexión');
        }
    },

    confirmarTurno: async function(e) {
        const turnoId = e.target.dataset.turnoId;
        if (confirm('¿Confirmar este turno?')) {
            try {
                const response = await fetch(`/api/turnos/${turnoId}/confirmar/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': turnosApp.getCsrfToken()
                    }
                });

                if (response.ok) {
                    location.reload();
                } else {
                    turnosApp.mostrarError('Error al confirmar el turno');
                }
            } catch (error) {
                console.error('Error:', error);
                turnosApp.mostrarError('Error de conexión');
            }
        }
    },

    cancelarTurno: async function(e) {
        const turnoId = e.target.dataset.turnoId;
        if (confirm('¿Cancelar este turno?')) {
            try {
                const response = await fetch(`/api/turnos/${turnoId}/cancelar/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': turnosApp.getCsrfToken()
                    }
                });

                if (response.ok) {
                    location.reload();
                } else {
                    turnosApp.mostrarError('Error al cancelar el turno');
                }
            } catch (error) {
                console.error('Error:', error);
                turnosApp.mostrarError('Error de conexión');
            }
        }
    },

    filtrarTurnos: function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const turnos = document.querySelectorAll('.turno-row');

        turnos.forEach(turno => {
            const texto = turno.textContent.toLowerCase();
            turno.style.display = texto.includes(searchTerm) ? '' : 'none';
        });
    },

    validarFechaDisponible: function(date) {
        const dia = date.getDay();
        // Deshabilitar domingos y fechas pasadas
        return dia !== 0 && date >= new Date();
    },

    getCsrfToken: function() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    },

    mostrarError: function(mensaje) {
        const alertaDiv = document.createElement('div');
        alertaDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertaDiv.role = 'alert';
        alertaDiv.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        document.querySelector('.container').insertAdjacentElement('afterbegin', alertaDiv);

        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            alertaDiv.remove();
        }, 5000);
    }
};

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => turnosApp.init());