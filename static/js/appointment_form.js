// Manejo dinámico de horarios en el formulario de citas
document.addEventListener('DOMContentLoaded', function() {
    const diaSelect = document.getElementById('id_dia');
    const horarioSelect = document.getElementById('id_horario');

    // Función para cargar horarios disponibles según el día seleccionado
    async function cargarHorarios(diaId) {
        try {
            const response = await fetch(`/api/horarios-disponibles/${diaId}/`);
            if (!response.ok) throw new Error('Error al cargar horarios');
            
            const horarios = await response.json();
            
            // Limpiar opciones actuales
            horarioSelect.innerHTML = '<option value="">Seleccione un horario</option>';
            
            // Agregar nuevas opciones
            horarios.forEach(horario => {
                const option = document.createElement('option');
                option.value = horario.id;
                option.textContent = horario.hora;
                horarioSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error:', error);
            horarioSelect.innerHTML = '<option value="">Error al cargar horarios</option>';
        }
    }

    // Evento para cuando cambia el día seleccionado
    diaSelect.addEventListener('change', function() {
        const diaId = this.value;
        if (diaId) {
            cargarHorarios(diaId);
        } else {
            horarioSelect.innerHTML = '<option value="">Primero seleccione un día</option>';
        }
    });

    // Inicializar horarios si hay un día seleccionado
    if (diaSelect.value) {
        cargarHorarios(diaSelect.value);
    }
});