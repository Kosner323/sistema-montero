/**
 * ========================================================================
 * UNIVERSAL SEARCH - Búsqueda y Autocompletado de Usuarios
 * ========================================================================
 *
 * Módulo reutilizable para buscar usuarios y autocompletar formularios.
 * Basado en novedades-autocomplete.js pero extendido para ser universal.
 *
 * CARACTERÍSTICAS:
 * - Configuración flexible mediante options
 * - Endpoint: /api/usuarios/buscar
 * - Mapeo customizable de campos BD -> inputs del form
 * - Callbacks para eventos success/notFound
 * - Bloqueo opcional de campos autocompletados
 *
 * INSTALACIÓN:
 * 1. Incluir este script en tu HTML: <script src="/assets/js/universal-search.js"></script>
 * 2. Inicializar en tu página:
 *    const buscador = initUniversalSearch({
 *      tipoIdField: 'tipoDocumento',
 *      numeroIdField: 'numeroDocumento',
 *      fieldMapping: {
 *        ibc: 'salarioBase',
 *        claseRiesgoARL: 'nivelRiesgo'
 *      },
 *      onSuccess: (usuario) => console.log('Usuario encontrado:', usuario)
 *    });
 *
 * @version 1.0.0
 * @author Sistema Montero - Automation Engineer
 * @date 2025-12-02
 */

(function(window) {
    'use strict';

    /**
     * Configuración por defecto del Universal Search
     */
    const DEFAULT_CONFIG = {
        // IDs de los campos del formulario
        tipoIdField: 'tipoDocumento',        // Campo select para tipo de ID
        numeroIdField: 'numeroDocumento',    // Campo input para número de ID

        // Endpoint del backend
        endpoint: '/api/usuarios/buscar',

        // Mapeo de campos de la BD a campos del formulario
        // Formato: { campo_bd: 'id_input_formulario' }
        fieldMapping: {
            // Información personal
            primerNombre: 'primerNombre',
            segundoNombre: 'segundoNombre',
            primerApellido: 'primerApellido',
            segundoApellido: 'segundoApellido',
            correoElectronico: 'correoElectronico',
            telefonoCelular: 'telefonoCelular',
            direccion: 'direccion',

            // Información laboral
            ibc: 'ibc',
            claseRiesgoARL: 'claseRiesgoARL',
            empresa_nit: 'empresa_nit',

            // Afiliaciones
            epsNombre: 'epsNombre',
            afpNombre: 'afpNombre',
            arlNombre: 'arlNombre',
            ccfNombre: 'ccfNombre'
        },

        // Callbacks
        onSuccess: null,    // function(usuario) - Se ejecuta cuando se encuentra el usuario
        onNotFound: null,   // function() - Se ejecuta cuando NO se encuentra el usuario
        onError: null,      // function(error) - Se ejecuta en caso de error de red

        // Configuración UI
        autoLock: true,     // Si true, bloquea los campos autocompletados (readonly)
        showMessages: true, // Si true, muestra mensajes de feedback al usuario
        messageContainer: null, // ID del contenedor de mensajes (si null, se crea automáticamente)

        // Validación
        minDigits: 5        // Mínimo de dígitos para disparar la búsqueda
    };

    /**
     * Clase UniversalSearch
     * Gestiona la búsqueda y autocompletado de usuarios
     */
    class UniversalSearch {
        constructor(options = {}) {
            // ✅ RETROCOMPATIBILIDAD: Soportar ambas interfaces
            // Interfaz nueva: inputId, mapping, callback
            // Interfaz original: tipoIdField, numeroIdField, fieldMapping, onSuccess
            
            if (options.inputId) {
                // Modo simplificado (usado por simulador_pila.html, cartera.html, etc.)
                options.numeroIdField = options.inputId;
                options.tipoIdField = options.tipoIdField || 'tipoId'; // Default
            }
            if (options.mapping) {
                options.fieldMapping = options.mapping;
            }
            if (options.callback) {
                options.onSuccess = options.callback;
            }

            this.config = { ...DEFAULT_CONFIG, ...options };
            this.tipoIdField = null;
            this.numeroIdField = null;
            this.autocompletedFields = [];
            
            // Modo simplificado: solo usa el input principal (sin tipoId)
            this.simplifiedMode = !!options.inputId;

            console.log('🔍 Inicializando Universal Search...', this.config);

            this.init();
        }

        /**
         * Inicializa el módulo
         */
        init() {
            // Obtener referencias a los campos
            this.tipoIdField = document.getElementById(this.config.tipoIdField);
            this.numeroIdField = document.getElementById(this.config.numeroIdField);

            // En modo simplificado, solo el campo principal es requerido
            if (this.simplifiedMode) {
                if (!this.numeroIdField) {
                    console.error('❌ Universal Search: No se encontró el campo de ID', {
                        inputId: this.config.numeroIdField
                    });
                    return;
                }
            } else {
                if (!this.tipoIdField || !this.numeroIdField) {
                    console.error('❌ Universal Search: No se encontraron los campos de ID', {
                        tipoIdField: this.config.tipoIdField,
                        numeroIdField: this.config.numeroIdField
                    });
                    return;
                }
            }

            // Vincular eventos
            this.attachEventListeners();

            console.log('✅ Universal Search inicializado correctamente');
        }

        /**
         * Vincula los event listeners a los campos
         */
        attachEventListeners() {
            // Evento blur: cuando el usuario sale del campo número de ID
            this.numeroIdField.addEventListener('blur', () => {
                setTimeout(() => this.buscarYAutocompletar(), 300);
            });

            // Evento Enter: búsqueda inmediata
            this.numeroIdField.addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    this.buscarYAutocompletar();
                }
            });

            // Evento change en tipo de ID: limpiar campos (solo si existe tipoIdField)
            if (this.tipoIdField) {
                this.tipoIdField.addEventListener('change', () => {
                    this.limpiarCampos();
                    this.habilitarCampos();
                    this.ocultarMensaje();
                });
            }

            // Evento input: detectar modificación de número de ID
            this.numeroIdField.addEventListener('input', () => {
                // Si hay datos autocompletados y el usuario modifica el número, limpiar
                if (this.autocompletedFields.length > 0) {
                    this.ocultarMensaje();
                }
            });
        }

        /**
         * Función principal: busca el usuario y autocompleta el formulario
         */
        async buscarYAutocompletar() {
            // En modo simplificado, tipoId es opcional (usa 'CC' por defecto)
            const tipoId = this.tipoIdField ? this.tipoIdField.value : 'CC';
            const numeroId = this.numeroIdField.value.trim();

            // Validar que el campo número tenga valor
            if (!numeroId) {
                return;
            }

            // En modo completo, también validar tipoId
            if (!this.simplifiedMode && !tipoId) {
                return;
            }

            // Validar formato del número de ID (solo números y mínimo N dígitos)
            const regex = new RegExp(`^\\d{${this.config.minDigits},}$`);
            if (!regex.test(numeroId)) {
                return; // Esperar a que el usuario termine de escribir
            }

            console.log(`🔍 Buscando usuario: ${tipoId} ${numeroId}`);

            try {
                // Mostrar indicador de carga
                this.numeroIdField.classList.add('is-loading');

                // Llamar al endpoint del backend
                const url = `${this.config.endpoint}?tipoId=${encodeURIComponent(tipoId)}&numeroId=${encodeURIComponent(numeroId)}`;

                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    },
                    credentials: 'include'
                });

                // Remover indicador de carga
                this.numeroIdField.classList.remove('is-loading');

                if (!response.ok) {
                    // Usuario no encontrado
                    if (response.status === 404) {
                        console.log('ℹ️ Usuario no encontrado en la base de datos');
                        this.mostrarMensaje('Usuario no encontrado. Por favor complete los datos manualmente.', 'warning');
                        this.limpiarCampos();
                        this.habilitarCampos();

                        // Callback onNotFound
                        if (typeof this.config.onNotFound === 'function') {
                            this.config.onNotFound();
                        }

                        return;
                    }

                    // Otro tipo de error
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error al buscar usuario');
                }

                // Usuario encontrado - obtener datos
                const usuario = await response.json();
                console.log('✅ Usuario encontrado:', usuario);

                // Rellenar el formulario
                this.rellenarFormulario(usuario);

                // Mostrar mensaje de éxito
                this.mostrarMensaje('✅ Usuario encontrado. Datos cargados automáticamente.', 'success');

                // Callback onSuccess
                if (typeof this.config.onSuccess === 'function') {
                    this.config.onSuccess(usuario);
                }

            } catch (error) {
                console.error('❌ Error al buscar usuario:', error);
                this.numeroIdField.classList.remove('is-loading');
                this.mostrarMensaje('Error al buscar usuario: ' + error.message, 'danger');
                this.habilitarCampos();

                // Callback onError
                if (typeof this.config.onError === 'function') {
                    this.config.onError(error);
                }
            }
        }

        /**
         * Rellena el formulario con los datos del usuario
         * @param {Object} usuario - Datos del usuario obtenidos del backend
         */
        rellenarFormulario(usuario) {
            this.autocompletedFields = [];

            // Iterar sobre el mapeo de campos
            for (const [campoBD, campoFormulario] of Object.entries(this.config.fieldMapping)) {
                const valor = usuario[campoBD];

                if (valor !== undefined && valor !== null) {
                    this.setFieldValue(campoFormulario, valor);
                    this.autocompletedFields.push(campoFormulario);
                }
            }

            // Bloquear campos si está configurado
            if (this.config.autoLock) {
                this.bloquearCamposAutocompletados();
            }

            console.log(`📝 ${this.autocompletedFields.length} campos autocompletados`);
        }

        /**
         * Establece el valor de un campo de forma segura
         * @param {string} fieldIdOrSelector - ID del campo o selector CSS (con #)
         * @param {any} value - Valor a establecer
         */
        setFieldValue(fieldIdOrSelector, value) {
            // Soportar tanto IDs simples como selectores CSS
            let field;
            if (fieldIdOrSelector.startsWith('#') || fieldIdOrSelector.startsWith('.')) {
                field = document.querySelector(fieldIdOrSelector);
            } else {
                field = document.getElementById(fieldIdOrSelector);
            }
            
            if (field) {
                field.value = value || '';
            }
        }

        /**
         * Bloquea los campos autocompletados (readonly)
         */
        bloquearCamposAutocompletados() {
            this.autocompletedFields.forEach(fieldIdOrSelector => {
                let field;
                if (fieldIdOrSelector.startsWith('#') || fieldIdOrSelector.startsWith('.')) {
                    field = document.querySelector(fieldIdOrSelector);
                } else {
                    field = document.getElementById(fieldIdOrSelector);
                }
                
                if (field) {
                    field.setAttribute('readonly', 'readonly');
                    field.classList.add('bg-light');
                }
            });
        }

        /**
         * Habilita todos los campos para edición
         */
        habilitarCampos() {
            Object.values(this.config.fieldMapping).forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.removeAttribute('readonly');
                    field.classList.remove('bg-light');
                }
            });
        }

        /**
         * Limpia todos los campos mapeados
         */
        limpiarCampos() {
            Object.values(this.config.fieldMapping).forEach(fieldId => {
                this.setFieldValue(fieldId, '');
            });
            this.autocompletedFields = [];
        }

        /**
         * Muestra un mensaje de feedback al usuario
         * @param {string} mensaje - Mensaje a mostrar
         * @param {string} tipo - Tipo de mensaje: 'success', 'warning', 'danger', 'info'
         */
        mostrarMensaje(mensaje, tipo = 'info') {
            if (!this.config.showMessages) return;

            let messageContainer = document.getElementById(this.config.messageContainer || 'userSearchMessage');

            if (!messageContainer) {
                // Crear el contenedor si no existe
                messageContainer = document.createElement('div');
                messageContainer.id = this.config.messageContainer || 'userSearchMessage';
                messageContainer.className = 'alert alert-dismissible fade show mt-2';
                messageContainer.setAttribute('role', 'alert');

                // Insertar después del campo numeroId
                const numeroIdParent = this.numeroIdField.parentElement;
                if (numeroIdParent) {
                    numeroIdParent.appendChild(messageContainer);
                }
            }

            // Actualizar el contenido y estilo del mensaje
            messageContainer.className = `alert alert-${tipo} alert-dismissible fade show mt-2`;
            messageContainer.innerHTML = `
                ${mensaje}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            // Auto-ocultar después de 5 segundos (solo para mensajes de éxito)
            if (tipo === 'success') {
                setTimeout(() => {
                    if (messageContainer && messageContainer.parentNode) {
                        messageContainer.remove();
                    }
                }, 5000);
            }
        }

        /**
         * Oculta el mensaje de feedback
         */
        ocultarMensaje() {
            const messageContainer = document.getElementById(this.config.messageContainer || 'userSearchMessage');
            if (messageContainer) {
                messageContainer.remove();
            }
        }

        /**
         * Destruye la instancia y limpia event listeners
         */
        destroy() {
            // En una implementación completa, aquí se deberían remover los event listeners
            console.log('🗑️ Universal Search destruido');
        }
    }

    /**
     * Función inicializadora global
     * @param {Object} options - Opciones de configuración
     * @returns {UniversalSearch} - Instancia del buscador
     */
    window.initUniversalSearch = function(options) {
        return new UniversalSearch(options);
    };

    // ✅ Exponer la clase globalmente para uso directo: new UniversalSearch({...})
    window.UniversalSearch = UniversalSearch;

    console.log('📦 Universal Search Module cargado');

})(window);
