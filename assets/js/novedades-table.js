// ============================================
// NOVEDADES-TABLE.JS
// Lógica de la tabla DataTables
// ============================================

const NovedadesTable = {
    table: null, // Referencia a la instancia de DataTable

    /**
     * Inicializa la tabla DataTables con la configuración base.
     */
    initialize() {
        // Asegúrate de que jQuery esté cargado antes de esto
        if (typeof $ === 'undefined') {
            console.error('jQuery no está cargado. DataTables no funcionará.');
            return;
        }

        this.table = $('#novedadesTable').DataTable({
            // Usar configuración de NOVEDADES_CONFIG
            ...NOVEDADES_CONFIG.DATATABLE,
            // Definir las columnas que DataTables debe manejar
            // ✅ CORRECCIÓN: Añadir defaultContent a columnas opcionales/potencialmente nulas
            columns: [
                { data: 'id', title: '# Caso' }, // Asumimos que ID siempre existe
                {
                    data: 'client',
                    title: 'Empresa',
                    defaultContent: '<i>N/A</i>' // <-- AÑADIDO: Si 'client' falta
                },
                // Para las siguientes columnas, asignamos 'data' a null porque las renderizaremos manualmente
                // usando datos de otras propiedades del objeto 'row' en columnDefs.
                // 'defaultContent' asegura que no haya error si la fila completa falta.
                { data: null, title: 'Empleado', defaultContent: '<i>N/A</i>' },
                { data: null, title: 'ID', defaultContent: '<i>N/A</i>' },
                { data: null, title: 'Asignado', defaultContent: '<i>N/A</i>' },
                { data: 'subject', title: 'Tipo Novedad', defaultContent: '<i>N/A</i>' }, // Asumimos que subject suele existir
                { data: 'status', title: 'Estado', defaultContent: '' }, // Para badges, default vacío
                { data: 'priority', title: 'Prioridad', defaultContent: '' }, // Para badges, default vacío
                { data: 'creationDate', title: 'Creación', defaultContent: '<i>N/A</i>' },
                { data: 'updateDate', title: 'Actualización', defaultContent: '<i>N/A</i>' },
                { data: null, title: 'Acciones', className: 'text-center', orderable: false, defaultContent: '' } // Botones
            ],
            // Procesamiento de datos para renderizado personalizado
            columnDefs: [
                 // Columna # Caso (ID) - Enlace para ver detalles
                 {
                     targets: 0, // Primera columna (índice 0)
                     render: (data, type, row, meta) => {
                         // meta.row es el índice original en caseDataStore
                         // Asegurarse de que 'data' (el ID) no sea null o undefined
                         const displayId = data !== null && data !== undefined ? data : 'N/A';
                         return `<a href="#" class="text-primary-500 view-details-btn" data-index="${meta.row}">${displayId}</a>`;
                     }
                 },
                 // Columna Empleado (Combina firstName y lastName)
                 {
                     targets: 2, // Índice de la columna 'Empleado'
                     render: (data, type, row) => `${row.firstName || ''} ${row.lastName || ''}`.trim() || 'N/A'
                 },
                 // Columna ID Completo (Combina idType y idNumber)
                 {
                     targets: 3, // Índice de la columna 'ID'
                     render: (data, type, row) => `${row.idType || ''} ${row.idNumber || ''}`.trim() || 'N/A'
                 },
                 // Columna Asignado (corto)
                 {
                      targets: 4, // Índice de la columna 'Asignado'
                      render: (data, type, row) => (row.assignedTo || 'Sistema').split(' ')[0] // Tomar solo la primera palabra
                 },
                 // Columna Estado (Badge)
                 {
                     targets: 6, // Índice de la columna 'Estado'
                     render: (data, type, row) => NovedadesUI.getStatusBadge(row.status || 'Desconocido') // Manejar status null/undefined
                 },
                 // Columna Prioridad (Badge)
                 {
                     targets: 7, // Índice de la columna 'Prioridad'
                     render: (data, type, row) => NovedadesUI.getPriorityBadge(row.priority || 'baja', row.priorityText || row.priority || 'Baja') // Manejar priority null/undefined
                 },
                 // Columnas de Fecha (Formateo)
                 {
                     targets: [8, 9], // Creación y Actualización (índices 8 y 9)
                     render: (data, type, row) => NovedadesUI.formatDate(data) // La función formatDate debería manejar null/undefined
                 },
                 // Columna Acciones (Botones)
                 {
                     targets: 10, // Última columna (índice 10)
                     render: (data, type, row, meta) => {
                         const isResolved = row.status === 'Resuelto';
                         // meta.row es el índice original en caseDataStore
                         return NovedadesUI.getActionButtons(meta.row, isResolved);
                     }
                 }
            ],
            // Callback al dibujar la tabla (para inicializar tooltips, etc.)
            drawCallback: function(settings) {
                NovedadesUI.initializeTooltips(); // Reinicializar tooltips de Bootstrap
                // Asegurarse de que Feather se llame después de que los iconos estén en el DOM
                if (typeof feather !== 'undefined') {
                     feather.replace(); // Actualizar iconos Feather
                }
            }
        });

        this.attachEvents(); // Adjuntar eventos después de inicializar
        console.log('DataTable inicializada.');
    },

    /**
     * Carga o recarga los datos en la tabla.
     * @param {Array} data - Array de objetos de novedad (usualmente window.caseDataStore).
     */
    loadData(data) {
        if (!this.table) {
            console.error('Intento de cargar datos antes de inicializar DataTable.');
            return;
        }

        this.table.clear(); // Limpiar datos existentes

        // Filtrar datos nulos o inválidos antes de añadir para evitar errores
        const validData = data ? data.filter(item => item && typeof item === 'object') : [];
        if (data && validData.length !== data.length) {
            console.warn(`Se filtraron ${data.length - validData.length} registros inválidos antes de cargar en DataTable.`);
        }

        if (validData.length > 0) {
            this.table.rows.add(validData);
        }

        this.table.draw(); // Redibujar la tabla (mostrará "No hay datos..." si validData está vacío)
        console.log(`Datos cargados en DataTable: ${validData.length} filas.`);
    },

    /**
     * Adjunta los manejadores de eventos necesarios para la tabla y sus controles.
     */
    attachEvents() {
        if (!this.table) return;

        // Usar .off() antes de .on() para evitar duplicar listeners si se llama initialize múltiples veces
        const tableBody = $('#novedadesTable tbody');

        // Evento para ver detalles
        tableBody.off('click', '.view-details-btn').on('click', '.view-details-btn', (e) => {
            e.preventDefault();
            const index = $(e.currentTarget).data('index');
            if (this.isValidIndex(index)) {
                 NovedadesModals.showDetails(index);
            } else { this.handleInvalidIndex('ver detalles', index); }
        });

        // Evento para editar
        tableBody.off('click', '.edit-case-btn').on('click', '.edit-case-btn', (e) => {
            const index = $(e.currentTarget).data('index');
            if (this.isValidIndex(index)) {
                 NovedadesModals.showEdit(index);
             } else { this.handleInvalidIndex('editar', index); }
        });

        // Evento para cerrar caso
        tableBody.off('click', '.close-case-btn').on('click', '.close-case-btn', async (e) => {
            const index = $(e.currentTarget).data('index');
            if (this.isValidIndex(index)) {
                 await this.closeCase(index);
             } else { this.handleInvalidIndex('cerrar caso', index); }
        });

        // Evento para Descargar ZIP (Simulado)
        tableBody.off('click', '.download-zip').on('click', '.download-zip', (e) => {
            const index = $(e.currentTarget).data('index');
             if (this.isValidIndex(index)) {
                 const novedad = window.caseDataStore[index];
                 console.log("Simulando descarga ZIP para caso ID:", novedad.id);
                 NovedadesUI.showToast(`Descarga ZIP para caso ${novedad.id} (simulado).`, 'info');
             } else { this.handleInvalidIndex('descargar', index); }
        });

        // --- Eventos de Controles Externos ---
        const priorityContainer = document.getElementById('priority-filters-container');
        if (priorityContainer) {
             $(priorityContainer).off('click', '.filter-priority-btn').on('click', '.filter-priority-btn', (e) => {
                 this.filterByPriority(e.target.dataset.priority);
             });
        }

        const searchInput = document.getElementById('customSearchInput');
        if (searchInput) {
             $(searchInput).off('keyup').on('keyup', (e) => {
                 this.table.search(e.target.value).draw();
             });
        }

        console.log('Eventos de DataTable adjuntados.');
    },

    /**
     * Verifica si un índice es válido para acceder a caseDataStore.
     * @param {*} index - El índice a verificar.
     * @returns {boolean} - true si el índice es válido, false si no.
     */
    isValidIndex(index) {
        const numIndex = parseInt(index, 10);
        return !isNaN(numIndex) && numIndex >= 0 && window.caseDataStore && numIndex < window.caseDataStore.length;
    },

    /**
     * Maneja el caso de un índice inválido mostrando un error.
     * @param {string} actionDescription - Descripción de la acción fallida.
     * @param {*} index - El índice inválido.
     */
    handleInvalidIndex(actionDescription, index) {
        console.error(`Índice inválido (${index}) o caseDataStore no disponible para ${actionDescription}.`);
        NovedadesUI.showError(`Error interno: No se pudo procesar la acción para este caso.`);
    },


    /**
     * Filtra la tabla por prioridad usando la API de DataTables.
     * @param {string} priorityValue - Valor de la prioridad (ej: 'alta', 'media', '').
     */
    filterByPriority(priorityValue) {
        if (!this.table) return;

        // Columna de Prioridad es la 8va (índice 7)
        // Buscamos el valor exacto ('baja', 'media', etc.) usando regex
        const searchTerm = priorityValue ? `^${priorityValue}$` : ''; // Si es '', busca todo
        this.table.column(7).search(searchTerm, true, false).draw(); // true=regex, false=smart search

        // Actualizar botón activo
         document.querySelectorAll('.filter-priority-btn').forEach(btn => btn.classList.remove('active'));
         const activeButton = document.querySelector(`.filter-priority-btn[data-priority="${priorityValue}"]`);
         if (activeButton) activeButton.classList.add('active');

        console.log(`Filtrado por prioridad: ${priorityValue || 'Todas'}`);
    },

    /**
     * Lógica para cerrar un caso (marcarlo como resuelto).
     * @param {number} index - Índice del caso en window.caseDataStore.
     */
    async closeCase(index) {
        if (!this.table) return;

        const caseIndex = parseInt(index, 10); // Asegurar que sea número
        if (!this.isValidIndex(caseIndex)) {
             this.handleInvalidIndex('cerrar caso (interno)', index);
             return;
        }

        const novedad = window.caseDataStore[caseIndex];

        if (novedad.status === 'Resuelto') {
            NovedadesUI.showToast('Este caso ya se encuentra resuelto.', 'info');
            return;
        }

        const confirmed = await NovedadesUI.confirm(NOVEDADES_CONFIG.MESSAGES.CONFIRM.CLOSE + ` (#${novedad.id})`);
        if (!confirmed) return;

        try {
            NovedadesUI.showLoading();
            const updatedNovedad = await NovedadesAPI.closeCase(novedad.id);
            window.caseDataStore[caseIndex] = updatedNovedad;
            this.updateRow(caseIndex); // Actualizar solo la fila
            NovedadesUI.hideLoading();
            NovedadesUI.showSuccess(NOVEDADES_CONFIG.MESSAGES.SUCCESS.CLOSE + ` (#${novedad.id})`);
            const stats = NovedadesUI.calculateStats(window.caseDataStore);
            NovedadesUI.renderDashboardStats(stats);
        } catch (error) {
            NovedadesUI.hideLoading();
            console.error("Error al cerrar caso:", error);
            NovedadesUI.showError(NOVEDADES_CONFIG.MESSAGES.ERROR.UPDATE + `: ${error.message}`);
        }
    },

    /**
     * Actualiza los datos de una fila específica en DataTable sin redibujar todo.
     * @param {number} index - Índice de la fila en window.caseDataStore.
     */
    updateRow(index) {
        if (!this.table) return;

        const caseIndex = parseInt(index, 10);
        if (!this.isValidIndex(caseIndex)) {
            console.error("Índice inválido para actualizar fila:", index);
            this.refresh(); // Recargar todo como fallback si no se encuentra
            return;
        }

        const novedad = window.caseDataStore[caseIndex];
        let dtRow = null;

        // Buscar la fila correspondiente en DataTable por el índice original guardado
        this.table.rows((idx, data, node) => {
             const rowIndexAttr = $(node).find('[data-index]').data('index'); // Busca en cualquier elemento con data-index
             if (rowIndexAttr !== undefined && rowIndexAttr == caseIndex) { // Usar == para comparación flexible
                 dtRow = this.table.row(idx);
                 return true; // Encontrado
             }
             return false;
        });

        if (dtRow) {
            // Actualizar datos y redibujar solo esa fila
            dtRow.data(novedad).invalidate().draw(false);
            console.log(`Fila (Caso ID ${novedad.id}) actualizada en DataTable.`);
            // Reinicializar tooltips y feather para la fila actualizada
             setTimeout(() => {
                const rowNode = dtRow.node();
                if(rowNode) {
                    const tooltips = rowNode.querySelectorAll('[data-bs-toggle="tooltip"]');
                    tooltips.forEach(el => {
                        const existingTooltip = bootstrap.Tooltip.getInstance(el);
                        if (existingTooltip) existingTooltip.dispose();
                        new bootstrap.Tooltip(el);
                    });
                    if (typeof feather !== 'undefined') feather.replace();
                }
             }, 50);
        } else {
            console.warn(`No se encontró la fila en DataTable para actualizar el índice ${caseIndex} (Caso ID ${novedad.id}). Recargando toda la tabla.`);
            this.refresh(); // Fallback: recargar todo
        }
    },

    /**
     * Refresca toda la tabla cargando de nuevo los datos del store y recalcula stats.
     */
    refresh() {
        if (!this.table) return;
        const validData = (window.caseDataStore || []).filter(item => item && typeof item === 'object');
        this.loadData(validData); // Carga los datos filtrados
        const stats = NovedadesUI.calculateStats(window.caseDataStore || []);
        NovedadesUI.renderDashboardStats(stats);
        console.log('Tabla y estadísticas refrescadas.');
    }
};

// Exponer globalmente
window.NovedadesTable = NovedadesTable;