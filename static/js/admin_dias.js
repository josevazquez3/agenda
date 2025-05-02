document.addEventListener('DOMContentLoaded', function() {
    const formAgregarDia = document.getElementById('formAgregarDia');
    const fechaInput = document.getElementById('fecha');
    
    // Establecer fecha mínima como hoy
    const hoy = new Date();
    fechaInput.min = hoy.toISOString().split('T')[0];
    
    formAgregarDia.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('fecha', fechaInput.value);
        formData.append('disponible', document.getElementById('disponible').checked);
        
        fetch('/turnos/admin/dias-disponibles/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: 'El día se ha configurado correctamente',
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    formAgregarDia.reset();
                    cargarDiasDisponibles();
                });
            } else {
                throw new Error(data.message || 'Error al configurar el día');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'Error al configurar el día'
            });
        });
    });

    // Función para cargar los días disponibles
    function cargarDiasDisponibles() {
        fetch('/turnos/admin/dias-disponibles/')
            .then(response => response.json())
            .then(data => {
                const tablaDias = document.getElementById('dias-lista') || document.createElement('tbody');
                tablaDias.id = 'dias-lista';
                tablaDias.innerHTML = '';
                
                data.forEach(dia => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${dia.fecha}</td>
                        <td>
                            <span class="badge bg-${dia.disponible ? 'success' : 'danger'}">
                                ${dia.disponible ? 'Disponible' : 'No disponible'}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-info ver-horarios" data-fecha="${dia.fecha}">
                                <i class="fas fa-clock me-1"></i>Ver horarios
                            </button>
                        </td>
                    `;
                    tablaDias.appendChild(tr);
                });
                
                // Si la tabla no está en el DOM, agregarla
                const tablaExistente = document.getElementById('dias-lista');
                if (!tablaExistente) {
                    document.querySelector('.table tbody').replaceWith(tablaDias);
                }
            })
            .catch(error => {
                console.error('Error al cargar días:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los días disponibles'
                });
            });
    }

    // Cargar días disponibles al iniciar
    cargarDiasDisponibles();

    // Agregar manejador de eventos para los botones de ver horarios
    document.addEventListener('click', function(e) {
        if (e.target.closest('.ver-horarios')) {
            const fecha = e.target.closest('.ver-horarios').dataset.fecha;
            mostrarHorarios(fecha);
        }
    });

    function mostrarHorarios(fecha) {
        fetch(`/turnos/admin/horarios-dia/${fecha}/`)
            .then(response => response.json())
            .then(data => {
                let horariosHTML = '<div class="row">';
                if (data.horarios && data.horarios.length > 0) {
                    horariosHTML += data.horarios.map(horario => `
                        <div class="col-md-3 mb-2">
                            <div class="form-check">
                                <input class="form-check-input horario-check" type="checkbox" value="${horario.hora}" 
                                       id="horario_${horario.hora.replace(':', '_')}" 
                                       data-hora="${horario.hora}" ${horario.disponible ? 'checked' : ''}>
                                <label class="form-check-label" for="horario_${horario.hora.replace(':', '_')}">
                                    ${horario.hora}
                                </label>
                            </div>
                        </div>
                    `).join('');
                } else {
                    horariosHTML += '<p class="text-muted">No hay horarios configurados para este día</p>';
                }
                horariosHTML += '</div>';

                Swal.fire({
                    title: `Horarios para ${fecha}`,
                    html: horariosHTML,
                    showCancelButton: true,
                    confirmButtonText: 'Guardar',
                    cancelButtonText: 'Cancelar',
                    preConfirm: () => {
                        return guardarHorarios(fecha);
                    }
                });
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los horarios'
                });
            });
    }
    
    function guardarHorarios(fecha) {
        const horariosChecks = document.querySelectorAll('.horario-check');
        const horarios = [];
        
        horariosChecks.forEach(check => {
            horarios.push({
                hora: check.getAttribute('data-hora'),
                disponible: check.checked
            });
        });
        
        return fetch('/turnos/admin/horarios-guardar/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                fecha: fecha,
                horarios: horarios
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: 'Horarios guardados correctamente'
                }).then(() => {
                    cargarDiasDisponibles();
                });
                return true;
            } else {
                throw new Error(data.message || 'Error al guardar los horarios');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'Error al guardar los horarios'
            });
            return false;
        });
    }
});