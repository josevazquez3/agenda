/**
 * Archivo principal de JavaScript para el consultorio odontológico
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicialización de tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Inicialización de popovers de Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Animación de desplazamiento suave para enlaces de anclaje
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70, // Ajuste para el header fijo
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Agregar clase 'active' a enlaces de navegación según URL actual
    const currentLocation = window.location.pathname;
    document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
    
    // Desaparecer alertas después de 5 segundos
    setTimeout(function() {
        document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Código específico para ciertas páginas
    if (document.querySelector('#solicitar-turno-btn')) {
        setupTurnosSolicitudPage();
    }
    
    if (document.querySelector('#form-historial')) {
        setupHistorialPage();
    }
    
    // Setup de campos de fecha con flatpickr si están presentes
    if (document.querySelector('.datepicker')) {
        setupDatepickers();
    }
    
    // Inicializar componentes personalizados
    initCustomFileInputs();
    setupResponsiveTables();
});

/**
 * Configuración específica para la página de solicitud de turnos
 */
function setupTurnosSolicitudPage() {
    const solicitudBtn = document.querySelector('#solicitar-turno-btn');
    if (solicitudBtn) {
        solicitudBtn.addEventListener('click', function() {
            // Navegar a la página de calendario
            window.location.href = '/turnos/calendario/';
        });
    }
}

/**
 * Configuración para la página de historial de pacientes
 */
function setupHistorialPage() {
    // Previsualización de imágenes al subirlas
    const inputImagenes = document.querySelector('input[type="file"][multiple]');
    const contenedorPreview = document.querySelector('#preview-imagenes');
    
    if (inputImagenes && contenedorPreview) {
        inputImagenes.addEventListener('change', function() {
            // Limpiar previsualizaciones anteriores
            contenedorPreview.innerHTML = '';
            
            if (this.files.length > 0) {
                contenedorPreview.classList.remove('d-none');
                
                // Crear previsualización para cada imagen
                Array.from(this.files).forEach(file => {
                    if (file.type.match('image.*')) {
                        const reader = new FileReader();
                        
                        reader.onload = function(e) {
                            const previewDiv = document.createElement('div');
                            previewDiv.className = 'col-sm-4 col-md-3 col-lg-2 mb-2';
                            
                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.className = 'img-thumbnail';
                            img.alt = 'Vista previa';
                            
                            previewDiv.appendChild(img);
                            contenedorPreview.appendChild(previewDiv);
                        };
                        
                        reader.readAsDataURL(file);
                    }
                });
            } else {
                contenedorPreview.classList.add('d-none');
            }
        });
    }
}

/**
 * Configuración de selectores de fecha con flatpickr
 */
function setupDatepickers() {
    const datepickers = document.querySelectorAll('.datepicker');
    
    if (datepickers.length > 0) {
        datepickers.forEach(input => {
            flatpickr(input, {
                locale: 'es',
                dateFormat: 'Y-m-d',
                altInput: true,
                altFormat: 'd/m/Y',
                minDate: 'today'
            });
        });
    }
}

/**
 * Personalización de inputs de tipo file
 */
function initCustomFileInputs() {
    // Mostrar nombre del archivo seleccionado en inputs de tipo file
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const label = this.nextElementSibling;
            
            if (label && label.classList.contains('custom-file-label')) {
                if (fileName) {
                    label.textContent = fileName;
                } else {
                    label.textContent = 'Seleccionar archivo';
                }
            }
        });
    });
}

/**
 * Configuración para tablas responsivas
 */
function setupResponsiveTables() {
    const tables = document.querySelectorAll('.table-responsive');
    
    if (tables.length > 0) {
        tables.forEach(table => {
            const headers = table.querySelectorAll('th');
            const dataCells = table.querySelectorAll('tbody td');
            
            if (headers.length && dataCells.length) {
                dataCells.forEach((cell, index) => {
                    const headerIndex = index % headers.length;
                    cell.setAttribute('data-label', headers[headerIndex].textContent);
                });
            }
        });
    }
}