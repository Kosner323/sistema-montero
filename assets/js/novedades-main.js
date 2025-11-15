// ============================================
// NOVEDADES-MAIN.JS
// Inicialización principal del módulo
// ============================================

document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Inicializando módulo de Novedades...');
    const loader = document.querySelector('.loader-bg'); // Obtener referencia al loader global

    try {
        // Mostrar loader mientras se inicializa
        if(loader) loader.style.display = 'flex';

        // 1. Renderizar UI inicial básica (filtros, etc.)
        NovedadesUI.renderPriorityFilters();
        // NovedadesUI.showLoading(); // Usaremos el loader global en lugar del overlay específico

        // 2. Cargar datos esenciales desde API (novedades, empresas, usuarios)
        // Usamos Promise.all para cargar en paralelo
        const [novedades, empresas, usuarios] = await Promise.all([
            NovedadesAPI.getAll(),
            NovedadesAPI.getEmpresas(),
            NovedadesAPI.getUsuarios() // Cargar todos los usuarios al inicio
        ]);

        // Guardar datos en caché/store global
        window.caseDataStore = novedades;
        window.empresasCache = empresas;
        window.usuariosCache = usuarios; // Guardar usuarios para autocompletar

        console.log(`Datos cargados: ${novedades.length} novedades, ${empresas.length} empresas, ${usuarios.length} usuarios.`);

        // 3. Calcular y mostrar estadísticas en el Dashboard
        const stats = NovedadesUI.calculateStats(novedades);
        NovedadesUI.renderDashboardStats(stats);

        // 4. Inicializar la tabla DataTables
        NovedadesTable.initialize(); // Inicializar estructura y eventos
        NovedadesTable.loadData(novedades); // Cargar los datos iniciales

        // 5. Inicializar la lógica de los modales
        NovedadesModals.initialize(); // Inicializar instancias y eventos

        // 6. Inicializar tooltips de Bootstrap (después de que la tabla y modales estén listos)
        NovedadesUI.initializeTooltips();

        // 7. Ocultar loader una vez todo esté listo
        if(loader) loader.style.display = 'none';
        console.log('✅ Módulo de Novedades cargado correctamente');
        NovedadesUI.showToast('Módulo de Novedades listo.', 'success'); // Mensaje de éxito opcional

    } catch (error) {
        console.error('❌ Error fatal al inicializar el módulo de Novedades:', error);
        if(loader) loader.style.display = 'none'; // Asegurarse de ocultar el loader en caso de error
        // Mostrar error en la UI principal
        NovedadesUI.showError(NOVEDADES_CONFIG.MESSAGES.ERROR.LOAD + `: ${error.message}. Intente recargar la página.`);
        // Podrías deshabilitar botones o mostrar un mensaje más prominente si la carga falla
        const tableBody = document.querySelector('#novedadesTable tbody');
        if(tableBody) tableBody.innerHTML = `<tr><td colspan="11" class="text-center text-danger">Error crítico al cargar los datos. ${error.message}</td></tr>`;
    } finally {
        // Asegurar que feather icons se ejecuten después de cargar contenido dinámico
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
});