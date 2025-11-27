/**
 * pcoded.js
 * Archivo de configuración del tema Datta Able
 * Generado automáticamente - Funcionalidad básica
 */

(function() {
    'use strict';

    // Layout functions para configuración del tema
    window.layout_change = function(value) {
        // Layout configuration
    };

    window.layout_theme_sidebar_change = function(value) {
        // Sidebar theme configuration
    };

    window.change_box_container = function(value) {
        // Container configuration
    };

    window.layout_caption_change = function(value) {
        // Caption configuration
    };

    window.layout_rtl_change = function(value) {
        // RTL configuration
    };

    window.preset_change = function(value) {
        // Preset configuration
    };

    window.main_layout_change = function(value) {
        // Main layout configuration
    };

    // Mobile menu toggle
    document.addEventListener('DOMContentLoaded', function() {
        const mobileToggle = document.querySelector('[data-pc-toggle="offcanvas"]');
        const sidebar = document.querySelector('.pc-sidebar');

        if (mobileToggle && sidebar) {
            mobileToggle.addEventListener('click', function() {
                sidebar.classList.toggle('mob-sidebar-active');
            });
        }

        // Dropdowns manejados por Bootstrap automáticamente
        console.log('✅ pcoded.js cargado - dropdowns delegados a Bootstrap');
    });

})();
