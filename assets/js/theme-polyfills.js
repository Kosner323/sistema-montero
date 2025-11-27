/**
 * Polyfills para Tema Datta Able
 * Este archivo previene errores de ReferenceError cuando script.js
 * intenta llamar funciones que no existen en todas las configuraciones.
 *
 * IMPORTANTE: Este archivo debe cargarse ANTES de script.js
 */

// Polyfills para funciones de tema
window.layout_change = window.layout_change || function() {};
window.layout_theme_sidebar_change = window.layout_theme_sidebar_change || function() {};
window.change_box_container = window.change_box_container || function() {};
window.layout_caption_change = window.layout_caption_change || function() {};
window.layout_rtl_change = window.layout_rtl_change || function() {};
window.preset_change = window.preset_change || function() {};
window.main_layout_change = window.main_layout_change || function() {};

console.log('✅ Theme polyfills cargados correctamente');
