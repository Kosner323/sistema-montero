// ============================================
// NOVEDADES-UI.JS
// Funciones de interfaz de usuario
// ============================================

const NovedadesUI = {
    /**
     * Muestra un mensaje de éxito
     * @param {string} message - Mensaje a mostrar
     */
    showSuccess(message) {
        this.showToast(message, 'success');
    },

    /**
     * Muestra un mensaje de error
     * @param {string} message - Mensaje a mostrar
     */
    showError(message) {
        this.showToast(message, 'danger');
    },

    /**
     * Muestra un toast notification
     * @param {string} message - Mensaje
     * @param {string} type - Tipo (success, danger, warning, info)
     */
    showToast(message, type = 'info') {
        // Crear elemento de toast si no existe contenedor
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toast);

        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();

        // Eliminar del DOM después de ocultarse
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    /**
     * Muestra un diálogo de confirmación
     * @param {string} message - Mensaje
     * @returns {Promise<boolean>} true si confirma, false si cancela
     */
    async confirm(message) {
        return new Promise((resolve) => {
            if (confirm(message)) {
                resolve(true);
            } else {
                resolve(false);
            }
        });
    },

    /**
     * Muestra el overlay de carga
     */
    showLoading() {
        let overlay = document.getElementById('loading-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loading-overlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = `
                <div class="spinner-border text-light loading-spinner" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            `;
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    },

    /**
     * Oculta el overlay de carga
     */
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    },

    /**
     * Genera un badge HTML para prioridad
     * @param {string} priority - Prioridad
     * @param {string} priorityText - Texto de prioridad
     * @returns {string} HTML del badge
     */
    getPriorityBadge(priority, priorityText) {
        const badges = {
            'critica': 'badge-priority-critical',
            'alta': 'badge-priority-high',
            'media': 'badge-priority-medium',
            'baja': 'badge-priority-low'
        };

        const badgeClass = badges[priority] || 'bg-secondary';
        return `<span class="badge ${badgeClass}">${priorityText || priority}</span>`;
    },

    /**
     * Genera un badge HTML para estado
     * @param {string} status - Estado
     * @returns {string} HTML del badge
     */
    getStatusBadge(status) {
        const badges = {
            'Nuevo': 'badge-status-new',
            'En Progreso': 'badge-status-in-progress',
            'Pendiente': 'badge-status-pending',
            'Resuelto': 'badge-status-resolved'
        };

        const badgeClass = badges[status] || 'bg-secondary';
        return `<span class="badge ${badgeClass}">${status}</span>`;
    },

    /**
     * Genera los botones de acción para una fila
     * @param {number} index - Índice en caseDataStore
     * @param {boolean} isResolved - Si el caso está resuelto
     * @returns {string} HTML de los botones
     */
    getActionButtons(index, isResolved) {
        return `
            <div class="action-buttons text-center">
                <button class="btn btn-sm btn-light-success p-2 view-details-btn" 
                        data-index="${index}" data-bs-toggle="tooltip" title="Ver Detalle">
                    <i class="ti ti-eye"></i>
                </button>
                <button class="btn btn-sm btn-light-info p-2 edit-case-btn" 
                        data-index="${index}" data-bs-toggle="tooltip" title="Editar" 
                        ${isResolved ? 'disabled' : ''}>
                    <i class="ti ti-edit"></i>
                </button>
                <button class="btn btn-sm btn-light-secondary p-2 download-zip" 
                        data-index="${index}" data-bs-toggle="tooltip" title="Descargar ZIP">
                    <i class="ti ti-download"></i>
                </button>
                <button class="btn btn-sm ${isResolved ? 'btn-light-secondary' : 'btn-light-danger'} p-2 close-case-btn" 
                        data-index="${index}" data-bs-toggle="tooltip" 
                        title="${isResolved ? 'Caso Cerrado' : 'Cerrar Caso'}" 
                        ${isResolved ? 'disabled' : ''}>
                    <i class="ti ${isResolved ? 'ti-lock' : 'ti-lock-open'}"></i>
                </button>
            </div>
        `;
    },

    /**
     * Renderiza las tarjetas de estadísticas en el dashboard
     * @param {Object} stats - Objeto con las estadísticas
     */
    renderDashboardStats(stats) {
        const container = document.getElementById('dashboard-stats-container');
        if (!container) return;

        container.innerHTML = `
            <div class="row">
                <!-- Total de Casos -->
                <div class="col-lg-3 col-md-6 col-sm-6 mb-4">
                    <div class="card stats-card h-100 p-3">
                        <div class="d-flex align-items-center justify-content-between mb-2">
                            <div class="d-flex align-items-center">
                                <h5 class="stats-number text-primary-500 me-2 mb-0">${stats.total || 0}</h5>
                                <h6 class="stats-label mb-0">Total</h6>
                            </div>
                            <i class="ti ti-folder stats-icon text-primary-500"></i>
                        </div>
                        <p class="text-xs text-muted mb-0 border-t pt-2">Casos registrados en el sistema.</p>
                    </div>
                </div>

                <!-- Casos Críticos -->
                <div class="col-lg-3 col-md-6 col-sm-6 mb-4">
                    <div class="card stats-card h-100 p-3">
                        <div class="d-flex align-items-center justify-content-between mb-2">
                            <div class="d-flex align-items-center">
                                <h5 class="stats-number text-danger-500 me-2 mb-0">${stats.critical || 0}</h5>
                                <h6 class="stats-label mb-0">Críticos</h6>
                            </div>
                            <i class="ti ti-alert-triangle stats-icon text-danger-500"></i>
                        </div>
                        <p class="text-xs text-muted mb-0 border-t pt-2">Casos activos de atención inmediata.</p>
                    </div>
                </div>

                <!-- Nuevos Hoy -->
                <div class="col-lg-3 col-md-6 col-sm-6 mb-4">
                    <div class="card stats-card h-100 p-3">
                        <div class="d-flex align-items-center justify-content-between mb-2">
                            <div class="d-flex align-items-center">
                                <h5 class="stats-number text-warning-500 me-2 mb-0">${stats.today || 0}</h5>
                                <h6 class="stats-label mb-0">Nuevos Hoy</h6>
                            </div>
                            <i class="ti ti-bell-ringing stats-icon text-warning-500"></i>
                        </div>
                        <p class="text-xs text-muted mb-0 border-t pt-2">Novedades ingresadas en la fecha actual.</p>
                    </div>
                </div>

                <!-- Tasa de Resolución -->
                <div class="col-lg-3 col-md-6 col-sm-6 mb-4">
                    <div class="card stats-card h-100 p-3">
                        <div class="d-flex align-items-center justify-content-between mb-2">
                            <div class="d-flex align-items-center">
                                <h5 class="stats-number text-success-500 me-2 mb-0">${stats.resolvedRate || '0%'}</h5>
                                <h6 class="stats-label mb-0">Resueltos</h6>
                            </div>
                            <i class="ti ti-checks stats-icon text-success-500"></i>
                        </div>
                        <p class="text-xs text-muted mb-0 border-t pt-2">Tasa de cierre total de casos.</p>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Calcula estadísticas desde el datastore
     * @param {Array} data - Array de novedades
     * @returns {Object} Objeto con estadísticas
     */
    calculateStats(data) {
        const today = new Date().toISOString().split('T')[0];
        
        const stats = {
            total: data.length,
            critical: data.filter(n => n.priority === 'critica').length,
            today: data.filter(n => n.creationDate === today).length,
            resolved: data.filter(n => n.status === 'Resuelto').length
        };

        stats.resolvedRate = stats.total > 0 
            ? `${Math.round((stats.resolved / stats.total) * 100)}%` 
            : '0%';

        return stats;
    },

    /**
     * Renderiza los botones de filtro de prioridad
     */
    renderPriorityFilters() {
        const container = document.getElementById('priority-filters-container');
        if (!container) return;

        const filters = [
            { priority: '', text: 'Todas', color: 'secondary' },
            { priority: 'critica', text: 'Crítica', color: 'danger' },
            { priority: 'alta', text: 'Alta', color: 'warning' },
            { priority: 'media', text: 'Media', color: 'info' },
            { priority: 'baja', text: 'Baja', color: 'primary' },
            { priority: 'resuelto', text: 'Resuelto', color: 'success' }
        ];

        container.innerHTML = filters.map(f => `
            <button class="btn btn-sm btn-light-${f.color} filter-priority-btn ${f.priority === '' ? 'active' : ''}" 
                    data-priority="${f.priority}">
                ${f.text}
            </button>
        `).join('');
    },

    /**
     * Inicializa tooltips de Bootstrap
     */
    initializeTooltips() {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        [...tooltipTriggerList].map(el => new bootstrap.Tooltip(el));
    },

    /**
     * Formatea una fecha para mostrar
     * @param {string} dateString - Fecha en formato ISO
     * @returns {string} Fecha formateada
     */
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CO', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    },

    /**
     * Formatea una fecha y hora para mostrar
     * @param {string} dateString - Fecha en formato ISO
     * @returns {string} Fecha y hora formateadas
     */
    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        return date.toLocaleString('es-CO', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};

// Exportar para uso global
window.NovedadesUI = NovedadesUI;