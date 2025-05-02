// Configuración global
const DEBUG = true;

// Función de utilidad para depuración
function logDebug(mensaje, datos = null) {
    if (!DEBUG) return;
    
    const estilosBase = 'padding: 4px 8px; border-radius: 4px; font-weight: bold;';
    
    if (typeof mensaje === 'string') {
        console.log(`%c DEBUG %c ${mensaje}`, 
            `${estilosBase} background: #0d6efd; color: white;`, 
            'color: #0d6efd;');
        
        if (datos) {
            console.log('%c DATOS:', 'color: #6c757d;', datos);
        }
    } else {
        console.log('%c DEBUG:', `${estilosBase} background: #0d6efd; color: white;`, mensaje);
    }
}

// Función mejorada para realizar fetch con manejo de errores
async function fetchConRegistro(url, opciones = {}) {
    logDebug(`Enviando solicitud a: ${url}`, opciones);
    
    try {
        const response = await fetch(url, opciones);
        
        if (!response.ok) {
            throw new Error(`Error HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        let data;
        
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            const text = await response.text();
            try {
                data = JSON.parse(text);
            } catch (e) {
                data = text;
            }
        }
        
        logDebug(`Respuesta recibida de ${url}:`, data);
        return data;
    } catch (error) {
        logDebug(`Error en la solicitud a ${url}:`, error);
        throw error;
    }
}

// Función para mostrar mensajes con SweetAlert2
function mostrarMensaje(tipo, mensaje, opciones = {}) {
    const iconos = {
        'success': 'success',
        'error': 'error',
        'warning': 'warning',
        'info': 'info',
        'question': 'question'
    };

    const titulos = {
        'success': 'Éxito',
        'error': 'Error',
        'warning': 'Advertencia',
        'info': 'Información',
        'question': 'Pregunta'
    };

    // Si el tipo no es válido, usar 'info'
    if (!iconos[tipo]) {
        tipo = 'info';
    }

    const config = {
        icon: iconos[tipo],
        title: opciones.titulo || titulos[tipo],
        text: mensaje,
        timer: tipo === 'success' && !opciones.mantenerAbierto ? 1500 : undefined,
        showConfirmButton: tipo !== 'success' || opciones.mantenerAbierto,
        confirmButtonText: opciones.confirmarTexto || 'Aceptar',
        showCancelButton: opciones.mostrarCancelar || false,
        cancelButtonText: opciones.cancelarTexto || 'Cancelar',
        position: opciones.posicion || 'center',
        toast: opciones.toast || false,
        timerProgressBar: opciones.barraProgreso || tipo === 'success',
        customClass: opciones.clases || {}
    };

    return Swal.fire(config);
}

// Función para obtener CSRF token
function getCSRFToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const calendario = document.getElementById('calendario');
    const fechaSeleccionadaElement = document.getElementById('fecha-seleccionada');
    const switchDisponible = document.getElementById('switch-disponible');
    const motivoContainer = document.getElementById('motivo-container');
    const motivoInput = document.getElementById('motivo');
    const btnGuardar = document.getElementById('btn-guardar');
    const btnConfigurarHorarios = document.getElementById('btn-configurar-horarios');
    const configuracionDia = document.getElementById('configuracion-dia');
    const sinSeleccion = document.getElementById('sin-seleccion');
    const btnMarcarDisponible = document.getElementById('btn-marcar-disponible');
    const btnMarcarNoDisponible = document.getElementById('btn-marcar-no-disponible');
    const fechaInicio = document.getElementById('fecha-inicio');
    const fechaFin = document.getElementById('fecha-fin');

    let fechaSeleccionada = null;
    let diasDisponibles = [];
    let diasNoDisponibles = [];

    // Inicializar el datepicker para el calendario
    if (calendario) {
        $(calendario).datepicker({
            format: 'yyyy-mm-dd',
            language: 'es',
            todayHighlight: true,
            multidate: false,
            calendarWeeks: true,
            clearBtn: false,
            autoclose: true,
            beforeShowDay: function(date) {
                const fechaStr = date.toISOString().split('T')[0];
                if (diasDisponibles.includes(fechaStr)) {
                    return {
                        classes: 'dia-disponible',
                        tooltip: 'Día disponible'
                    };
                } else if (diasNoDisponibles.includes(fechaStr)) {
                    return {
                        classes: 'dia-no-disponible',
                        tooltip: 'Día no disponible'
                    };
                }
                return true;
            }
        }).on('changeDate', function(e) {
            const fecha = e.format('yyyy-mm-dd');
            seleccionarFecha(fecha);
        });
    }

    // Inicializar datepickers para rango de fechas
    $('#fecha-inicio, #fecha-fin').datepicker({
        format: 'yyyy-mm-dd',
        language: 'es',
        todayHighlight: true,
        autoclose: true
    });

    // Event listeners
    if (switchDisponible) {
        switchDisponible.addEventListener('change', function() {
            if (this.checked) {
                motivoContainer.classList.add('d-none');
            } else {
                motivoContainer.classList.remove('d-none');
            }
        });
    }

    if (btnGuardar) {
        btnGuardar.addEventListener('click', guardarConfiguracionDia);
    }

    if (btnConfigurarHorarios) {
        btnConfigurarHorarios.addEventListener('click', function() {
            if (fechaSeleccionada) {
                window.location.href = `/admin/dias/horarios/?fecha=${fechaSeleccionada}`;
            }
        });
    }

    if (btnMarcarDisponible) {
        btnMarcarDisponible.addEventListener('click', function() {
            marcarRangoFechas(true);
        });
    }

    if (btnMarcarNoDisponible) {
        btnMarcarNoDisponible.addEventListener('click', function() {
            marcarRangoFechas(false);
        });
    }

    // Cargar datos iniciales
    cargarDiasConfigurados();

    // Funciones
    async function cargarDiasConfigurados() {
        try {
            const dias = await fetchConRegistro('/admin/dias-disponibles/');
            logDebug('Días configurados cargados:', dias);
            
            diasDisponibles = [];
            diasNoDisponibles = [];
            
            dias.forEach(dia => {
                if (dia.disponible) {
                    diasDisponibles.push(dia.fecha);
                } else {
                    diasNoDisponibles.push(dia.fecha);
                }
            });
            
            // Actualizar calendario con los días
            if (calendario) {
                $(calendario).datepicker('update');
            }
            
            // Actualizar tabla de días
            actualizarTablaDias(dias);
            
        } catch (error) {
            mostrarMensaje('error', 'Error al cargar los días configurados: ' + error.message);
        }
    }

    async function seleccionarFecha(fecha) {
        logDebug('Fecha seleccionada:', fecha);
        fechaSeleccionada = fecha;
        
        try {
            // Mostrar indicador de carga
            sinSeleccion.classList.add('d-none');
            configuracionDia.classList.remove('d-none');
            
            fechaSeleccionadaElement.textContent = formatearFecha(fecha);
            
            // Obtener detalles del día
            const detalleDia = await fetchConRegistro(`/admin/dias/${fecha}/detalle/`);
            
            if (detalleDia.status === 'success') {
                switchDisponible.checked = detalleDia.disponible;
                motivoInput.value = detalleDia.motivo || '';
                
                if (detalleDia.disponible) {
                    motivoContainer.classList.add('d-none');
                } else {
                    motivoContainer.classList.remove('d-none');
                }
            } else {
                mostrarMensaje('error', detalleDia.message || 'Error al cargar los detalles del día');
            }
            
        } catch (error) {
            mostrarMensaje('error', 'Error al cargar la información del día: ' + error.message);
        }
    }

    async function guardarConfiguracionDia() {
        if (!fechaSeleccionada) {
            mostrarMensaje('warning', 'Debe seleccionar una fecha primero');
            return;
        }
        
        const disponible = switchDisponible.checked;
        const motivo = !disponible ? motivoInput.value : '';
        
        try {
            // Mostrar indicador de carga
            btnGuardar.disabled = true;
            btnGuardar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
            
            const resultado = await fetchConRegistro('/admin/dias/actualizar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    fecha: fechaSeleccionada,
                    disponible: disponible,
                    motivo: motivo
                })
            });
            
            if (resultado.status === 'success') {
                mostrarMensaje('success', 'Configuración guardada correctamente');
                
                // Actualizar listas de días disponibles/no disponibles
                if (disponible) {
                    diasDisponibles = diasDisponibles.filter(d => d !== fechaSeleccionada);
                    diasDisponibles.push(fechaSeleccionada);
                    diasNoDisponibles = diasNoDisponibles.filter(d => d !== fechaSeleccionada);
                } else {
                    diasNoDisponibles = diasNoDisponibles.filter(d => d !== fechaSeleccionada);
                    diasNoDisponibles.push(fechaSeleccionada);
                    diasDisponibles = diasDisponibles.filter(d => d !== fechaSeleccionada);
                }
                
                // Actualizar calendario
                if (calendario) {
                    $(calendario).datepicker('update');
                }
                
                // Recargar tabla de días
                cargarDiasConfigurados();
                
            } else {
                mostrarMensaje('error', resultado.message || 'Error al guardar la configuración');
            }
            
        } catch (error) {
            mostrarMensaje('error', 'Error al guardar la configuración: ' + error.message);
        } finally {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = '<i class="bi bi-save me-1"></i>Guardar configuración';
        }
    }

    async function marcarRangoFechas(disponible) {
        const inicio = fechaInicio.value;
        const fin = fechaFin.value;
        
        if (!inicio || !fin) {
            mostrarMensaje('warning', 'Debe seleccionar tanto la fecha de inicio como la de fin');
            return;
        }
        
        try {
            // Mostrar indicador de carga
            const boton = disponible ? btnMarcarDisponible : btnMarcarNoDisponible;
            const textoOriginal = boton.innerHTML;
            
            boton.disabled = true;
            boton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...';
            
            const resultado = await fetchConRegistro('/admin/dias/configurar-rango/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({
                    fecha_inicio: inicio,
                    fecha_fin: fin,
                    disponible: disponible
                })
            });
            
            if (resultado.status === 'success') {
                mostrarMensaje('success', resultado.message || `Se han configurado correctamente ${resultado.dias_configurados} días`);
                
                // Recargar los días configurados
                cargarDiasConfigurados();
                
                // Limpiar el formulario
                fechaInicio.value = '';
                fechaFin.value = '';
                
            } else {
                mostrarMensaje('error', resultado.message || 'Error al configurar el rango de fechas');
            }
            
        } catch (error) {
            mostrarMensaje('error', 'Error al configurar el rango de fechas: ' + error.message);
        } finally {
            const boton = disponible ? btnMarcarDisponible : btnMarcarNoDisponible;
            const iconoClass = disponible ? 'bi-check-circle' : 'bi-x-circle';
            const texto = disponible ? 'Disponible' : 'No disponible';
            
            boton.disabled = false;
            boton.innerHTML = `<i class="bi ${iconoClass} me-1"></i>${texto}`;
        }
    }

    function actualizarTablaDias(dias) {
        const tablaDias = document.getElementById('tabla-dias');
        if (!tablaDias) return;
        
        if (!dias || dias.length === 0) {
            tablaDias.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center py-4">
                        <i class="bi bi-calendar-x display-4 text-muted"></i>
                        <p class="mt-2">No hay días configurados</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        // Ordenar días por fecha (más reciente primero)
        dias.sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
        
        let html = '';
        dias.forEach(dia => {
            const fecha = new Date(dia.fecha);
            const fechaFormateada = fecha.toLocaleDateString('es-ES', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            html += `
                <tr>
                    <td>${fechaFormateada}</td>
                    <td>
                        <span class="badge rounded-pill bg-${dia.disponible ? 'success' : 'danger'}">
                            <i class="bi bi-${dia.disponible ? 'check-circle' : 'x-circle'} me-1"></i>
                            ${dia.disponible ? 'Disponible' : 'No disponible'}
                        </span>
                    </td>
                    <td>${dia.motivo || '-'}</td>
                    <td>
                        <div class="btn-group btn-group-sm" role="group">
                            <button type="button" class="btn btn-outline-primary btn-editar" data-fecha="${dia.fecha}">
                                <i class="bi bi-pencil me-1"></i>Editar
                            </button>
                            <button type="button" class="btn btn-outline-info btn-horarios" data-fecha="${dia.fecha}">
                                <i class="bi bi-clock me-1"></i>Horarios
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        tablaDias.innerHTML = html;
        
        // Agregar event listeners a los botones
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', function() {
                const fecha = this.getAttribute('data-fecha');
                if (fecha) {
                    // Seleccionar fecha en el calendario
                    $(calendario).datepicker('update', fecha);
                    // Cargar información del día
                    seleccionarFecha(fecha);
                    // Desplazarse hacia el calendario
                    calendario.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
        
        document.querySelectorAll('.btn-horarios').forEach(btn => {
            btn.addEventListener('click', function() {
                const fecha = this.getAttribute('data-fecha');
                if (fecha) {
                    window.location.href = `/admin/dias/horarios/?fecha=${fecha}`;
                }
            });
        });
    }

    function formatearFecha(fechaStr) {
        const fecha = new Date(fechaStr);
        return fecha.toLocaleDateString('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
}); 