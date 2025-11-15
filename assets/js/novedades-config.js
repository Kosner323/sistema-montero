// ============================================
// NOVEDADES-CONFIG.JS
// Configuración y constantes globales
// ============================================

const NOVEDADES_CONFIG = {
    // URLs de la API
    API: {
        BASE_URL: '/api/novedades', // Base (aunque no se use directamente aquí)
        GET_ALL: '/api/novedades',      // Ruta para obtener todas las novedades
        CREATE: '/api/novedades',       // Ruta para crear una novedad
        UPDATE: (id) => `/api/novedades/${id}`, // Ruta para actualizar (por ID)
        DELETE: (id) => `/api/novedades/${id}`, // Ruta para eliminar (por ID)
        GET_EMPRESAS: '/api/empresas',      // Ruta para obtener empresas
        GET_USUARIOS: '/api/usuarios'       // Ruta para obtener usuarios
    },

    // Configuración de DataTables
    DATATABLE: {
        language: {
            // ✅ **RUTA CORREGIDA** Apuntar al archivo local servido por Flask
            url: '/assets/js/plugins/datatables/i18n/es-ES.json'
        },
        pageLength: 25, // Número de filas por página por defecto
        order: [[8, 'desc']], // Ordenar por la 9ª columna (Fecha Creación) descendente por defecto
        columnDefs: [
            { orderable: false, targets: [10] }, // Columna de acciones no ordenable (última columna)
            { className: 'text-center', targets: [10] } // Centrar columna de acciones
            // Puedes añadir más definiciones si necesitas ajustar otras columnas
        ],
        responsive: true, // Habilitar diseño responsivo
        // Puedes añadir más opciones de DataTables aquí si las necesitas
        // Por ejemplo: dom, buttons, etc.
    },

    // Prioridades disponibles
    PRIORIDADES: [
        { value: 'baja', text: 'Baja', color: 'secondary' },
        { value: 'media', text: 'Media', color: 'info' },
        { value: 'alta', text: 'Alta', color: 'warning' },
        { value: 'critica', text: 'Crítica', color: 'danger' }
    ],

    // Estados disponibles
    ESTADOS: [
        { value: 'Nuevo', text: 'Nuevo', color: 'primary' },
        { value: 'En Progreso', text: 'En Progreso', color: 'success' }, // Ajustado color si prefieres
        { value: 'Pendiente', text: 'Pendiente', color: 'warning' },
        { value: 'Resuelto', text: 'Resuelto', color: 'success' }
    ],

    // Tipos de identificación (Usados en el modal)
    TIPOS_ID: [
        { value: 'CC', text: 'Cédula de Ciudadanía' },
        { value: 'CE', text: 'Cédula de Extranjería' },
        { value: 'PA', text: 'Pasaporte' },
        { value: 'TI', text: 'Tarjeta de Identidad' },
        { value: 'PT', text: 'Permiso Temporal' }
        // Puedes añadir más si son necesarios
    ],

    // Mensajes estándar para la UI
    MESSAGES: {
        SUCCESS: {
            CREATE: 'Novedad creada exitosamente',
            UPDATE: 'Novedad actualizada correctamente',
            DELETE: 'Novedad eliminada',
            CLOSE: 'Caso cerrado exitosamente',
            COMMENT: 'Comentario agregado',
            LOAD: 'Datos cargados correctamente'
        },
        ERROR: {
            LOAD: 'Error al cargar los datos',
            CREATE: 'Error al crear la novedad',
            UPDATE: 'Error al actualizar la novedad',
            DELETE: 'Error al eliminar la novedad',
            NETWORK: 'Error de conexión con el servidor',
            NOT_FOUND: 'Elemento no encontrado',
            VALIDATION: 'Por favor, corrija los errores en el formulario.'
        },
        CONFIRM: {
            DELETE: '¿Está seguro de eliminar esta novedad? Esta acción no se puede deshacer.',
            CLOSE: '¿Está seguro de cerrar este caso (marcarlo como Resuelto)?'
        },
        INFO: {
            LOADING: 'Cargando datos...',
            SAVING: 'Guardando cambios...',
            NO_DATA: 'No hay datos disponibles para mostrar.',
            USER_NOT_FOUND: 'Usuario no encontrado en la base de datos.'
        }
    },

    // Configuración de validación para el formulario de nuevo/editar caso
    VALIDATION: {
        REQUIRED_FIELDS: ['client', 'subject', 'priority', 'status', 'description'], // IDs de los campos obligatorios
        MIN_DESCRIPTION_LENGTH: 10,  // Longitud mínima para la descripción
        MAX_DESCRIPTION_LENGTH: 5000 // Longitud máxima para la descripción
    }
};

// Variables globales (declaradas aquí para claridad, inicializadas en main.js o donde corresponda)
let novedadesTable = null;      // Instancia de DataTable
let caseDataStore = [];         // Almacén de datos de novedades
let empresasCache = [];         // Caché de empresas
let usuariosCache = [];         // Caché de usuarios

// Exportar configuración y variables globales al scope window para fácil acceso
window.NOVEDADES_CONFIG = NOVEDADES_CONFIG;
window.novedadesTable = novedadesTable; // Permitir acceso global a la tabla
window.caseDataStore = caseDataStore;   // Permitir acceso global al store de datos
window.empresasCache = empresasCache;     // Permitir acceso global a la caché de empresas
window.usuariosCache = usuariosCache;     // Permitir acceso global a la caché de usuarios

console.log('NOVEDADES_CONFIG cargado.'); // Mensaje de confirmación en consola