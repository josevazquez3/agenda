// Agregar nuevo horario al día
function agregarHorarioDia(fecha) {
    const inputHora = document.getElementById('nuevoHorarioDia');
    if (!inputHora || !inputHora.value) {
        mostrarAlerta('error', 'Debe seleccionar una hora', 'modalHorariosDia');
        return;
    }
    
    const hora = inputHora.value;
    
    // Verificar si ya existe un horario con esa hora
    const horariosExistentes = document.querySelectorAll(`#modalHorariosDiaBody tr[data-hora="${hora}"]`);
    if (horariosExistentes.length > 0) {
        mostrarAlerta('error', 'Ya existe un horario para esa hora', 'modalHorariosDia');
        return;
    }
    
    // Agregar fila a la tabla
    const tabla = document.querySelector('#modalHorariosDiaBody tbody');
    if (!tabla) {
        // Si no hay tabla, recargar todo el modal
        cargarHorariosDia(fecha);
        return;
    }
    
    const newRow = document.createElement('tr');
    newRow.dataset.hora = hora;
    newRow.innerHTML = `
        <td>${hora}</td>
        <td>
            <div class="form-check form-switch">
                <input class="form-check-input horario-dia-switch" type="checkbox" checked>
                <label class="form-check-label">Disponible</label>
            </div>
        </td>
        <td>
            <button class="btn btn-sm btn-danger eliminar-horario-dia">
                <i class="bi bi-trash me-1"></i>Eliminar
            </button>
        </td>
    `;
    
    tabla.appendChild(newRow);
    
    // Configurar botón de eliminar
    const btnEliminar = newRow.querySelector('.eliminar-horario-dia');
    if (btnEliminar) {
        btnEliminar.addEventListener('click', function() {
            newRow.remove();
        });
    }
    
    // Limpiar el input
    inputHora.value = '';
}

// Guardar cambios en los horarios de un día
function guardarHorariosDia() {
    const btnGuardar = document.getElementById('guardarHorariosDia');
    if (!btnGuardar) return;
    
    const fecha = btnGuardar.dataset.fecha;
    if (!fecha) {
        mostrarAlerta('error', 'No se ha seleccionado una fecha', 'modalHorariosDia');
        return;
    }
    
    // Recolectar datos de los horarios
    const horarios = [];
    document.querySelectorAll('#modalHorariosDiaBody tr[data-hora]').forEach(row => {
        const hora = row.dataset.hora;
        const id = row.dataset.id || '';
        const disponible = row.querySelector('.horario-dia-switch').checked;
        
        horarios.push({
            id: id,
            hora_inicio: hora,
            disponible: disponible
        });
    });
    
    // Mostrar indicador de carga
    const modalBody = document.getElementById('modalHorariosDiaBody');
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Guardando...</span>
                </div>
                <p class="mt-2">Guardando cambios...</p>
            </div>
        `;
    }
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Intentar con la primera ruta
    fetch(`/turnos/admin/horarios-dia/${fecha}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ horarios })
    })
    .then(response => {
        if (!response.ok) {
            // Si falla, intentar con ruta alternativa
            return fetch(`/admin/dias/horarios/guardar/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    fecha: fecha,
                    horarios: horarios
                })
            });
        }
        return response;
    })
    .then(response => {
        if (!response.ok) {
            // Si ambas fallan, intentar con otra ruta
            return fetch(`/admin/horarios/guardar/${fecha}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ horarios })
            });
        }
        return response;
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al guardar los horarios');
        }
        return response.json();
    })
    .then(data => {
        const success = data.success || data.status === 'success';
        
        if (success) {
            // Cerrar modal después de 1 segundo
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalHorariosDia'));
                if (modal) {
                    modal.hide();
                }
                
                mostrarAlerta('success', 'Horarios guardados correctamente');
            }, 1000);
        } else {
            mostrarAlerta('error', data.message || 'Error al guardar los horarios', 'modalHorariosDia');
            cargarHorariosDia(fecha);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarAlerta('error', error.message, 'modalHorariosDia');
        cargarHorariosDia(fecha);
    });
}

// Mostrar alerta con SweetAlert2
function mostrarAlerta(tipo, mensaje, modalId = null) {
    if (typeof Swal !== 'undefined') {
        if (modalId) {
            // Si se especifica un modal, mostrar la alerta dentro del modal
            const modalBody = document.getElementById(`${modalId}Body`);
            if (modalBody) {
                const alertDiv = document.createElement('div');
                alertDiv.className = `alert alert-${tipo === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
                alertDiv.innerHTML = `
                    ${mensaje}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
                `;
                
                // Insertar al principio del modal
                modalBody.insertBefore(alertDiv, modalBody.firstChild);
                
                // Eliminar la alerta después de 3 segundos
                setTimeout(() => {
                    alertDiv.remove();
                }, 3000);
            }
        } else {
            // Mostrar SweetAlert2
            Swal.fire({
                icon: tipo === 'success' ? 'success' : 'error',
                title: tipo === 'success' ? '¡Éxito!' : 'Error',
                text: mensaje,
                timer: 3000,
                timerProgressBar: true
            });
        }
    } else {
        // Fallback a alert normal si SweetAlert2 no está disponible
        alert(`${tipo === 'success' ? 'Éxito' : 'Error'}: ${mensaje}`);
    }
}