// Funciones para gestionar el historial de pacientes

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const formHistorial = document.getElementById('formHistorial');
    const btnGuardarHistorial = document.getElementById('guardarHistorial');
    const listaHistorial = document.getElementById('historial-lista');

    // Función para cargar el historial
    function cargarHistorial(pacienteId) {
        if (!listaHistorial) return;

        listaHistorial.innerHTML = '<tr><td colspan="4" class="text-center"><div class="spinner-border text-primary" role="status"></div></td></tr>';
        
        fetch(`/admin/historial/${pacienteId}/get_historial/`)
            .then(response => response.json())
            .then(data => {
                listaHistorial.innerHTML = '';
                if (data.length === 0) {
                    listaHistorial.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center py-4">
                                <i class="fas fa-notes-medical fa-2x text-muted mb-3"></i>
                                <p class="mb-0">No hay registros en el historial</p>
                            </td>
                        </tr>
                    `;
                    return;
                }
                
                data.forEach(registro => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>
                            <div class="d-flex align-items-center">
                                <i class="fas fa-calendar text-primary me-2"></i>
                                ${registro.fecha}
                            </div>
                        </td>
                        <td>${registro.observaciones}</td>
                        <td>
                            ${registro.imagenes.map(img => `
                                <a href="${img.url}" target="_blank" class="btn btn-sm btn-outline-info me-1">
                                    <i class="fas fa-image"></i>
                                </a>
                            `).join('')}
                        </td>
                        <td>
                            <div class="btn-group">
                                <button type="button" class="btn btn-sm btn-outline-primary editar-registro" data-id="${registro.id}">
                                    <i class="fas fa-edit me-1"></i>Editar
                                </button>
                                <button type="button" class="btn btn-sm btn-outline-danger eliminar-registro" data-id="${registro.id}">
                                    <i class="fas fa-trash me-1"></i>Eliminar
                                </button>
                            </div>
                        </td>
                    `;
                    listaHistorial.appendChild(row);
                });

                // Actualizar event listeners
                document.querySelectorAll('.editar-registro').forEach(btn => {
                    btn.addEventListener('click', editarRegistro);
                });
                document.querySelectorAll('.eliminar-registro').forEach(btn => {
                    btn.addEventListener('click', eliminarRegistro);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'No se pudo cargar el historial'
                });
            });
    }

    // Función para guardar un nuevo registro o actualizar uno existente
    function guardarRegistro(event) {
        event.preventDefault();
        const formData = new FormData(formHistorial);
        const registroId = formHistorial.dataset.registroId;
        const url = registroId ? 
            `/admin/historial/${registroId}/actualizar/` : 
            '/admin/historial/crear/';

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message,
                    timer: 1500,
                    showConfirmButton: false
                });
                const modalHistorial = bootstrap.Modal.getInstance(document.getElementById('modalHistorial'));
                modalHistorial.hide();
                cargarHistorial(formHistorial.dataset.pacienteId);
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.message || 'Error al guardar el registro'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al procesar la solicitud'
            });
        });
    }

    // Función para editar un registro
    function editarRegistro() {
        const registroId = this.dataset.id;
        fetch(`/admin/historial/${registroId}/obtener/`)
            .then(response => response.json())
            .then(data => {
                formHistorial.dataset.registroId = registroId;
                formHistorial.querySelector('[name="observaciones"]').value = data.observaciones;
                // Mostrar imágenes actuales si las hay
                const modalHistorial = new bootstrap.Modal(document.getElementById('modalHistorial'));
                modalHistorial.show();
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar el registro'
                });
            });
    }

    // Función para eliminar un registro
    function eliminarRegistro() {
        const registroId = this.dataset.id;
        Swal.fire({
            title: '¿Estás seguro?',
            text: 'Esta acción no se puede deshacer',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`/admin/historial/${registroId}/eliminar/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Éxito',
                            text: 'Registro eliminado correctamente',
                            timer: 1500,
                            showConfirmButton: false
                        });
                        cargarHistorial(formHistorial.dataset.pacienteId);
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: data.message || 'Error al eliminar el registro'
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Error al procesar la solicitud'
                    });
                });
            }
        });
    }

    // Event Listeners
    if (formHistorial) {
        formHistorial.addEventListener('submit', guardarRegistro);
    }

    // Inicializar
    const pacienteId = document.getElementById('paciente-id')?.value;
    if (pacienteId) {
        cargarHistorial(pacienteId);
    }
});