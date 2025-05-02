// Funcionalidades específicas de la página de inicio
document.addEventListener('DOMContentLoaded', function() {
    // Animación del banner principal
    const banner = document.querySelector('.card.bg-primary');
    if (banner) {
        banner.style.opacity = '0';
        banner.style.transform = 'translateY(20px)';
        banner.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        
        setTimeout(() => {
            banner.style.opacity = '1';
            banner.style.transform = 'translateY(0)';
        }, 100);
    }

    // Animación de las tarjetas de servicios
    const servicios = document.querySelectorAll('.col-md-4 .card');
    servicios.forEach((servicio, index) => {
        servicio.style.opacity = '0';
        servicio.style.transform = 'translateY(20px)';
        servicio.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        servicio.style.transitionDelay = `${index * 0.2}s`;

        setTimeout(() => {
            servicio.style.opacity = '1';
            servicio.style.transform = 'translateY(0)';
        }, 300 + (index * 200));
    });

    // Efecto hover en las tarjetas
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
            this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = 'none';
        });
    });

    // Animación para la sección "Por qué elegirnos"
    const razones = document.querySelectorAll('.col-md-4 .text-center');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const razonesObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    razones.forEach(razon => {
        razon.style.opacity = '0';
        razon.style.transform = 'translateY(20px)';
        razon.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        razonesObserver.observe(razon);
    });

    // Animación para los horarios y contacto
    const infoCards = document.querySelectorAll('.col-md-6 .card');
    infoCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateX(-20px)';
        card.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
    });

    const infoObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateX(0)';
            }
        });
    }, observerOptions);

    infoCards.forEach(card => {
        infoObserver.observe(card);
    });
});