// ============================================
// THEME-FIX.JS - Parche para corregir cambio de tema
// ============================================
// Este archivo debe cargarse DESPUÉS de theme.js
// Sobrescribe las funciones para asegurar que funcionen

console.log('🔧 Cargando parche de tema...');

// Guardar referencias a las funciones originales
const original_layout_change = window.layout_change;
const original_layout_change_default = window.layout_change_default;

// Función mejorada para cambiar el icono del tema
function updateThemeIcon(theme) {
    console.log('🎨 Actualizando icono para tema:', theme);
    const themeIcon = document.getElementById('themeIcon');
    
    if (themeIcon) {
        // Cambiar el atributo data-feather
        const iconName = theme === 'dark' ? 'moon' : 'sun';
        themeIcon.setAttribute('data-feather', iconName);
        
        // Reemplazar el icono
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        console.log('✅ Icono actualizado a:', iconName);
    } else {
        console.warn('⚠️ No se encontró #themeIcon');
    }
}

// Función mejorada para aplicar estilos del tema
function applyThemeStyles(theme) {
    console.log('🎨 Aplicando estilos para tema:', theme);
    
    const html = document.documentElement;
    const body = document.body;
    
    // Aplicar clases y atributos
    html.setAttribute('data-pc-theme', theme);
    
    // Forzar cambios en el DOM
    if (theme === 'dark') {
        html.classList.add('dark');
        html.classList.remove('light');
        body.classList.add('dark-mode');
        body.classList.remove('light-mode');
        
        // Forzar colores inline como fallback
        body.style.backgroundColor = '#1a1d2e';
        body.style.color = '#c5cdd9';
    } else {
        html.classList.add('light');
        html.classList.remove('dark');
        body.classList.add('light-mode');
        body.classList.remove('dark-mode');
        
        // Restaurar colores light
        body.style.backgroundColor = '#f3f4f6';
        body.style.color = '#1f2937';
    }
    
    console.log('✅ Atributos y clases aplicados');
}

// Sobrescribir layout_change con versión mejorada
window.layout_change = function(layout) {
    console.log('🔄 layout_change llamada con:', layout);
    
    try {
        // Llamar a la función original
        if (typeof original_layout_change === 'function') {
            original_layout_change(layout);
            console.log('✅ Función original ejecutada');
        }
        
        // Aplicar estilos adicionales
        applyThemeStyles(layout);
        
        // Actualizar icono
        updateThemeIcon(layout);
        
        // Guardar en localStorage
        localStorage.setItem('pc-theme', layout);
        console.log('✅ Tema guardado en localStorage:', layout);
        
        // Disparar evento personalizado
        window.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme: layout } 
        }));
        
        console.log('✅ layout_change completada exitosamente');
        
    } catch (error) {
        console.error('❌ Error en layout_change:', error);
    }
};

// Sobrescribir layout_change_default con versión mejorada
window.layout_change_default = function() {
    console.log('🔄 layout_change_default llamada');
    
    try {
        // Detectar preferencia del sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = prefersDark ? 'dark' : 'light';
        
        console.log('🌓 Preferencia del sistema detectada:', theme);
        
        // Aplicar el tema
        window.layout_change(theme);
        
        // Limpiar localStorage para que siempre use el sistema
        localStorage.removeItem('pc-theme');
        
        console.log('✅ layout_change_default completada');
        
    } catch (error) {
        console.error('❌ Error en layout_change_default:', error);
    }
};

// Función para inicializar el tema al cargar la página
function initializeTheme() {
    console.log('🚀 Inicializando tema...');
    
    try {
        // Obtener tema guardado o usar el del sistema
        const savedTheme = localStorage.getItem('pc-theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
        
        console.log('📋 Tema inicial detectado:', initialTheme);
        
        // Aplicar tema inicial
        window.layout_change(initialTheme);
        
        console.log('✅ Tema inicializado correctamente');
        
    } catch (error) {
        console.error('❌ Error inicializando tema:', error);
    }
}

// Configurar event listeners para botones de tema
function setupThemeButtons() {
    console.log('🔘 Configurando botones de tema...');
    
    try {
        // Método 1: Botones con data-theme-action
        const dataButtons = document.querySelectorAll('[data-theme-action]');
        console.log(`   Encontrados ${dataButtons.length} botones con data-theme-action`);
        
        dataButtons.forEach((button, index) => {
            const action = button.getAttribute('data-theme-action');
            
            // Remover listeners anteriores clonando el botón
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            // Agregar nuevo listener
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                console.log(`🖱️ Click en botón ${index + 1}, acción:`, action);
                
                if (action === 'default') {
                    window.layout_change_default();
                } else {
                    window.layout_change(action);
                }
            });
        });
        
        // Método 2: Botones con onclick (backup)
        const onclickButtons = document.querySelectorAll('[onclick*="layout_change"]');
        console.log(`   Encontrados ${onclickButtons.length} botones con onclick`);
        
        onclickButtons.forEach((button, index) => {
            // No hacemos nada aquí, el onclick inline debería funcionar
            console.log(`   Botón onclick ${index + 1}:`, button.getAttribute('onclick'));
        });
        
        console.log('✅ Botones de tema configurados');
        
    } catch (error) {
        console.error('❌ Error configurando botones:', error);
    }
}

// Escuchar cambios en la preferencia del sistema
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    console.log('🌓 Cambio en preferencia del sistema:', e.matches ? 'dark' : 'light');
    
    // Solo aplicar si no hay tema guardado (usando modo sistema)
    if (!localStorage.getItem('pc-theme')) {
        window.layout_change(e.matches ? 'dark' : 'light');
    }
});

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('📄 DOM cargado, inicializando parche de tema...');
        setTimeout(() => {
            initializeTheme();
            setupThemeButtons();
        }, 100);
    });
} else {
    // DOM ya está listo
    console.log('📄 DOM ya estaba listo, inicializando inmediatamente...');
    setTimeout(() => {
        initializeTheme();
        setupThemeButtons();
    }, 100);
}

// Exponer funciones globalmente
window.initializeTheme = initializeTheme;
window.setupThemeButtons = setupThemeButtons;
window.updateThemeIcon = updateThemeIcon;

console.log('✅ Parche de tema cargado completamente');