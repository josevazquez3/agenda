// Script para limpiar cookies y almacenamiento local al cerrar sesión
document.addEventListener('DOMContentLoaded', function() {
    // Limpiar cookies de forma más efectiva
    document.cookie.split(';').forEach(function(c) {
        const cookieName = c.trim().split('=')[0];
        document.cookie = cookieName + '=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/';
        document.cookie = cookieName + '=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;domain=' + window.location.hostname;
    });

    // Limpiar localStorage
    localStorage.clear();

    // Limpiar sessionStorage
    sessionStorage.clear();
    
    // Redirigir a la página de login después de un breve retraso
    setTimeout(function() {
        window.location.href = '/usuarios/login/';
    }, 500);
});