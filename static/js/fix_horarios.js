// fix_horarios.js - Solución para el error "No se pudieron cargar los horarios"
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script fix_horarios.js cargado correctamente');
    
    // Interceptar todos los botones de "Ver Horarios"
    document.querySelectorAll('.btn-ver-horarios').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Obtener fecha del botón
            const fecha = this.dataset.fecha || this.getAttribute('data-fecha');
            if (!fecha) {
                console.error('Error: No se proporcionó fecha');
                return;
            }
            
            console.log('Click en Ver Horarios para fecha:', fecha);
            
            // Mostrar modal con spinner
            const modal = new bootstrap.Modal(document.getElementById('modalHorarios') || document.getElementById('modalHorariosDia'));
            modal.show();
            
            // Intentar múltiples rutas para obtener los horarios
            obtenerHorariosMultiple(fecha);
        });
    });
});

// Función para intentar múltiples rutas de API
function obtenerHorariosMultiple(fecha) {
    console.log('Intentando obtener horarios para la fecha:', fecha);
    
    // Determinar los elementos del modal
    const modalTitle = document.getElementById('modalHorariosTitle') || document.getElementById('modalHorariosDiaTitle');
    const modalBody = document.getElementById('modalHorariosDiaBody') || document.getElementById('horariosContainer');
    
    // Mostrar spinner
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando horarios...</span>
                </div>
                <p class="mt-3">Cargando horarios...</p>
            </div>
        `;
    }
    
    // Actualizar título si existe
    if (modalTitle) {
        // Formatear fecha para mostrar
        let fechaFormateada = fecha;
        try {
            const fechaObj = new Date(fecha);
            fechaFormateada = fechaObj.toLocaleDateString('es-ES', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        } catch (e) {
            console.warn('Error al formatear fecha:', e);
        }
        
        modalTitle.textContent = `Configurar Horarios - ${fechaFormateada}`;
    }
    
    // Guardar fecha en el botón de guardar
    const btnGuardar = document.getElementById('btnGuardarHorarios') || document.getElementById('guardarHorariosDia');
    if (btnGuardar) {
        btnGuardar.setAttribute('data-fecha', fecha);
    }
    
    // Lista de rutas a intentar
    const rutas = [
        `/turnos/admin/horarios-dia/${fecha}/`,
        `/admin/dias/horarios/?fecha=${fecha}`,
        `/admin/horarios-dia/${fecha}/`,
        `/horarios-disponibles/${fecha}/`
    ];
    
    // Intentar cada ruta secuencialmente
    intentarSiguienteRuta(rutas, 0, fecha);
}

// Función para intentar rutas secuencialmente
function intentarSiguienteRuta(rutas, indice, fecha) {
    if (indice >= rutas.length) {
        // Si se agotaron las rutas, mostrar opción para crear horarios manualmente
        mostrarOpcionCrearHorarios(fecha);
        return;
    }
    
    console.log(`Intentando ruta ${indice + 1}/${rutas.length}: ${rutas[indice]}`);
    
    fetch(rutas[indice])
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if ((data.success === true && data.horarios) || 
                (data.status === 'success' && data.horarios)) {
                // Éxito, mostrar horarios
                mostrarHorariosEnModal(data.horarios, fecha);
            } else {
                // Respuesta sin formato esperado, intentar siguiente ruta
                console.warn('Formato de respuesta inesperado:', data);
                intentarSiguienteRuta(rutas, indice + 1, fecha);
            }
        })
        .catch(error => {
            console.error(`Error con ruta ${rutas[indice]}:`, error);
            // Intentar siguiente ruta
            intentarSiguienteRuta(rutas, indice + 1, fecha);
        });
}

// Función para mostrar horarios en el modal
function mostrarHorariosEnModal(horarios, fecha) {
    const modalBody = document.getElementById('modalHorariosDiaBody') || document.getElementById('horariosContainer');
    if (!modalBody) return;
    
    let html = '';
    
    // Si no hay horarios, mostrar mensaje
    if (!horarios || horarios.length === 0) {
        html = `
            <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                No hay horarios configurados para este día
            </div>
        `;
    } else {
        // Generar tabla de horarios
        html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Hora</th>
                            <th>Disponible</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        // Ordenar horarios por hora
        horarios.sort((a, b) => {
            const horaA = a.hora || a.hora_inicio;
            const horaB = b.hora || b.hora_inicio;
            return String(horaA).localeCompare(String(horaB));
        });
        
        horarios.forEach(horario => {
            // Compatibilidad con diferentes formatos
            const hora = horario.hora || horario.hora_inicio;
            const disponible = horario.disponible === undefined ? true : horario.disponible;
            const id = horario.id || '';
            
            html += `
                <tr data-id="${id}" data-hora="${hora}">
                    <td>${hora}</td>
                    <td>
                        <div class="form-check form-switch">
                            <input class="form-check-input horario-dia-switch" type="checkbox" 
                                   ${disponible ? 'checked' : ''}>
                            <label class="form-check-label">
                                ${disponible ? 'Disponible' : 'No disponible'}
                            </label>
                        </div>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-danger eliminar-horario-dia">
                            <i class="bi bi-trash me-1"></i>Eliminar
                        </button>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
    }
    
    // Agregar formulario para nuevo horario
    html += `
        <div class="mt-4 border-top pt-3">
            <h6>Agregar Nuevo Horario</h6>
            <div class="row g-3 align-items-center">
                <div class="col-auto">
                    <label for="nuevoHorarioDia" class="col-form-label">Hora:</label>
                </div>
                <div class="col-auto">
                    <input type="time" id="nuevoHorarioDia" class="form-control" step="1800">
                </div>
                <div class="col-auto">
                    <button type="button" class="btn btn-success" id="btnAgregarHorarioDia">
                        <i class="bi bi-plus me-1"></i>Agregar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Actualizar contenido del modal
    modalBody.innerHTML = html;
    
    // Configurar eventos para los nuevos elementos
    configurarEventosHorarios(fecha);
}

// Función para mostrar opción de crear horarios manualmente
function mostrarOpcionCrearHorarios(fecha) {
    const modalBody = document.getElementById('modalHorariosDiaBody') || document.getElementById('horariosContainer');
    if (!modalBody) return;
    
    modalBody.innerHTML = `
        <div class="alert alert-warning">
            <i class="bi bi-exclamation-triangle me-2"></i>
            No se pudieron cargar los horarios para esta fecha.
        </div>
        <div class="text-center mt-4">
            <p>¿Desea crear horarios predeterminados para este día?</p>
            <button class="btn btn-primary" id="btnCrearHorariosPredeterminados" data-fecha="${fecha}">
                <i class="bi bi-plus-circle me-2"></i>Crear Horarios Predeterminados
            </button>
        </div>
    `;
    
    // Configurar evento para el botón de crear horarios
    const btnCrearHorarios = document.getElementById('btnCrearHorariosPredeterminados');
    if (btnCrearHorarios) {
        btnCrearHorarios.addEventListener('click', function() {
            crearHorariosPredeterminados(fecha);
        });
    }
}

// Función para crear horarios predeterminados manualmente
function crearHorariosPredeterminados(fecha) {
    const modalBody = document.getElementById('modalHorariosDiaBody') || document.getElementById('horariosContainer');
    if (!modalBody) return;
    
    // Mostrar indicador de carga
    modalBody.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Creando horarios...</span>
            </div>
            <p class="mt-3">Creando horarios predeterminados...</p>
        </div>
    `;
    
    // Horarios predeterminados
    const horariosBase = [
        '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', 
        '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', 
        '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', 
        '17:00', '17:30', '18:00'
    ];
    
    // Crear horarios manualmente
    const horarios = horariosBase.map(hora => ({
        id: `nuevo_${hora.replace(':', '_')}`,
        hora: hora,
        disponible: true
    }));
    
    // Mostrar horarios en el modal
    setTimeout(() => {
        mostrarHorariosEnModal(horarios, fecha);
    }, 500);
}

// Configurar eventos para los elementos de horarios
function configurarEventosHorarios(fecha) {
    // Botón para agregar horario
    const btnAgregarHorarioDia = document.getElementById('btnAgregarHorarioDia');
    if (btnAgregarHorarioDia) {
        btnAgregarHorarioDia.addEventListener('click', function() {
            agregarHorarioDia(fecha);
        });
    }
    
    // Botones para eliminar horario
    document.querySelectorAll('.eliminar-horario-dia').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            row.remove();
        });
    });
    
    // Configurar evento para guardar cambios
    const btnGuardar = document.getElementById('btnGuardarHorarios') || document.getElementById('guardarHorariosDia');
    if (btnGuardar) {
        // Remover eventos anteriores
        btnGuardar.replaceWith(btnGuardar.cloneNode(true));
        
        // Volver a obtener el botón y agregar evento
        const nuevoBtn = document.getElementById('btnGuardarHorarios') || document.getElementById('guardarHorariosDia');
        if (nuevoBtn) {
            nuevoBtn.addEventListener('click', function() {
                guardarCambiosHorarios(fecha);
            });
        }
    }
}

// Función para agregar nuevo horario
function agregarHorarioDia(fecha) {
    const inputHora = document.getElementById('nuevoHorarioDia');
    if (!inputHora || !inputHora.value) {
        mostrarAlerta('No ha seleccionado una hora', 'danger');
        return;
    }
    
    const hora = inputHora.value;
    
    // Verificar si ya existe un horario con esa hora
    const horariosExistentes = document.querySelectorAll(`tr[data-hora="${hora}"]`);
    if (horariosExistentes.length > 0) {
        mostrarAlerta('Ya existe un horario para esa hora', 'danger');
        return;
    }
    
    // Agregar fila a la tabla
    const tabla = document.querySelector('tbody');
    if (!tabla) {
        mostrarAlerta('Error al agregar horario', 'danger');
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

// Función para guardar cambios
function guardarCambiosHorarios(fecha) {
    // Recolectar datos de los horarios
    const horarios = [];
    document.querySelectorAll('tr[data-hora]').forEach(row => {
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
    const modalBody = document.getElementById('modalHorariosDiaBody') || document.getElementById('horariosContainer');
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="text-center p-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Guardando...</span>
                </div>
                <p class="mt-3">Guardando cambios...</p>
            </div>
        `;
    }
    
    // Obtener token CSRF
    const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
    
    // Lista de rutas a intentar para guardar
    const rutasGuardar = [
        `/turnos/admin/horarios-dia/${fecha}/`,
        `/admin/dias/horarios/guardar/`,
        `/admin/horarios/guardar/${fecha}/`
    ];
    
    // Intentar cada ruta secuencialmente
    intentarGuardarEnRuta(rutasGuardar, 0, fecha, horarios, csrfToken);
}

// Función para intentar guardar en diferentes rutas
function intentarGuardarEnRuta(rutas, indice, fecha, horarios, csrfToken) {
    if (indice >= rutas.length) {
        // Si se agotaron las rutas, mostrar error
        mostrarAlerta('No se pudieron guardar los cambios. Inténtelo nuevamente.', 'danger');
        obtenerHorariosMultiple(fecha);
        return;
    }
    
    console.log(`Intentando guardar en ruta ${indice + 1}/${rutas.length}: ${rutas[indice]}`);
    
    // Preparar datos según la ruta
    let bodyData;
    if (rutas[indice].includes('/dias/horarios/guardar/')) {
        bodyData = JSON.stringify({
            fecha: fecha,
            horarios: horarios
        });
    } else {
        bodyData = JSON.stringify({ horarios });
    }
    
    fetch(rutas[indice], {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: bodyData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success === true || data.status === 'success') {
            // Éxito al guardar
            mostrarAlerta('Cambios guardados correctamente', 'success');
            
            // Cerrar modal después de un segundo
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(
                    document.getElementById('modalHorarios') || document.getElementById('modalHorariosDia')
                );
                if (modal) {
                    modal.hide();
                }
                
                // Recargar página para reflejar cambios
                window.location.reload();
            }, 1000);
        } else {
            // Respuesta sin éxito, intentar siguiente ruta
            intentarGuardarEnRuta(rutas, indice + 1, fecha, horarios, csrfToken);
        }
    })
    .catch(error => {
        console.error(`Error al guardar en ruta ${rutas[indice]}:`, error);
        // Intentar siguiente ruta
        intentarGuardarEnRuta(rutas, indice + 1, fecha, horarios, csrfToken);
    });
}

// Función para mostrar alertas
function mostrarAlerta(mensaje, tipo) {
    // Buscar contenedor para mensajes
    let contenedor = document.getElementById('mensajesHorarios');
    
    // Si no existe, crearlo al inicio del modal
    if (!contenedor) {
        const modalBody = document.getElementById('modalHorariosDiaBody') || document.getElementById('horariosContainer');
        if (modalBody) {
            contenedor = document.createElement('div');
            contenedor.id = 'mensajesHorarios';
            modalBody.insertBefore(contenedor, modalBody.firstChild);
        }
    }
    
    if (contenedor) {
        // Crear alerta
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
        alerta.role = 'alert';
        alerta.innerHTML = `
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
        `;
        
        // Agregar al contenedor
        contenedor.appendChild(alerta);
        
        // Auto-cerrar después de 3 segundos
        setTimeout(() => {
            alerta.remove();
        }, 3000);
    } else {
        // Fallback a alert normal
        alert(`${mensaje}`);
    }
}