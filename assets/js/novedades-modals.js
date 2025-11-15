// ============================================
// NOVEDADES-MODALS.JS
// Lógica de los modales (Nuevo/Ver/Editar/Importar)
// ============================================

const NovedadesModals = {
    // Referencias a los modales de Bootstrap (se inicializan en initialize)
    newCaseModal: null,
    viewCaseModal: null,
    importCaseModal: null, // Si existe

    /**
     * Inicializa las referencias a los modales y adjunta eventos.
     */
    initialize() {
        // Inicializar instancias de modales de Bootstrap
        const newCaseModalEl = document.getElementById('newCaseModal');
        const viewCaseModalEl = document.getElementById('viewCaseModal');
        const importCaseModalEl = document.getElementById('importCaseModal'); // Si tienes este modal

        if (newCaseModalEl) this.newCaseModal = new bootstrap.Modal(newCaseModalEl);
        if (viewCaseModalEl) this.viewCaseModal = new bootstrap.Modal(viewCaseModalEl);
        if (importCaseModalEl) this.importCaseModal = new bootstrap.Modal(importCaseModalEl);

        this.attachEvents();
        console.log('Modales inicializados.');
    },

    /**
     * Adjunta los manejadores de eventos a los elementos dentro de los modales.
     */
    attachEvents() {
        // --- Modal Nuevo/Editar Caso ---
        const newCaseForm = document.getElementById('newCaseForm');
        if (newCaseForm) {
            // Evento submit para guardar/actualizar
            newCaseForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSave();
            });

             // Autocompletar usuario al cambiar ID o perder foco
             $('#idNumber').on('change blur', () => this.findAndFillUser()); // Usar jQuery para blur
            // Buscar empresa al cambiar NIT
            $('#clientNit').on('change blur', () => this.findAndFillCompany());
        }

        // Botón para simular datos (si existe)
        $('#simulateDataButton').on('click', () => this.fillSimulationData());

         // Botón para agregar beneficiario (si existe)
         $('#addBeneficiaryButton').on('click', () => this.addBeneficiaryEntry());

         // Limpiar modal al cerrarse
         $('#newCaseModal').on('hidden.bs.modal', () => this.resetNewCaseModal());


        // --- Modal Ver Detalles ---
        const addCommentButton = document.getElementById('addCommentButton');
        if (addCommentButton) {
            addCommentButton.addEventListener('click', () => this.handleAddComment());
        }

        // --- Modal Importar (si existe) ---
        const importForm = document.getElementById('importCaseForm');
        if (importForm) {
             importForm.addEventListener('submit', (e) => {
                 e.preventDefault();
                 this.handleImport(); // Necesitarás implementar esta función
             });
        }

        console.log('Eventos de modales adjuntados.');
    },

    // ===========================================
    // FUNCIONES PARA MODAL NUEVO/EDITAR CASO
    // ===========================================

    /**
     * Muestra el modal para crear una nueva novedad (limpiando datos previos).
     */
    showNew() {
        this.resetNewCaseModal();
        $('#newCaseModalLabel').text('Registrar Nueva Novedad');
        $('#editCaseIndex').val(''); // Asegurar que no esté en modo edición
        if (this.newCaseModal) this.newCaseModal.show();
    },

    /**
     * Muestra el modal precargado para editar una novedad existente.
     * @param {number} index - Índice del caso en window.caseDataStore.
     */
    showEdit(index) {
        const novedad = window.caseDataStore[index];
        if (!novedad) {
            NovedadesUI.showError('No se encontró el caso para editar.');
            return;
        }

        this.resetNewCaseModal(); // Limpiar primero
        $('#newCaseModalLabel').text(`Editar Novedad #${novedad.id}`);
        $('#editCaseIndex').val(index); // Guardar índice para saber que estamos editando
        $('#caseIdDisplay').text(novedad.id || 'N/A').closest('div').show(); // Mostrar ID

        // Llenar campos del formulario
        $('#client').val(novedad.client || '');
        $('#clientNit').val( /* Necesitarías buscar el NIT si solo tienes el nombre */ '' ); // O ajustar API/datos
        $('#subject').val(novedad.subject || '');
        $('#priority').val(novedad.priority || 'baja');
        $('#status').val(novedad.status || 'Nuevo');
        $('#description').val(novedad.description || '');
        $('#radicado').val(novedad.radicado || '');
        $('#assignedTo').val(novedad.assignedTo || 'Sistema');

        // Llenar datos del usuario (si existen)
        $('#idType').val(novedad.idType || '');
        $('#idNumber').val(novedad.idNumber || '');
        $('#firstName').val(novedad.firstName || '');
        $('#lastName').val(novedad.lastName || '');
        $('#nationality').val(novedad.nationality || '');
        $('#gender').val(novedad.gender || '');
        $('#birthDate').val(novedad.birthDate || '');
        $('#phone').val(novedad.phone || '');
        $('#department').val(novedad.department || '');
        $('#city').val(novedad.city || '');
        $('#address').val(novedad.address || '');
        $('#neighborhood').val(novedad.neighborhood || '');
        $('#email').val(novedad.email || '');

        // Llenar datos de afiliación
        $('#eps').val(novedad.eps || '');
        $('#arl').val(novedad.arl || '');
        $('#arlClass').val(novedad.arlClass || '');
        $('#ccf').val(novedad.ccf || '');
        $('#pensionFund').val(novedad.pensionFund || '');
        $('#ibc').val(novedad.ibc || '');

        // Llenar beneficiarios
        $('#beneficiariesContainer').empty(); // Limpiar existentes
        if (novedad.beneficiaries && Array.isArray(novedad.beneficiaries)) {
            novedad.beneficiaries.forEach((ben, i) => {
                this.addBeneficiaryEntry(ben.name, ben.relationship, ben.idNumber);
            });
        }

        if (this.newCaseModal) this.newCaseModal.show();
    },

    /**
     * Limpia completamente el formulario del modal de nuevo/editar caso.
     */
    resetNewCaseModal() {
        const form = document.getElementById('newCaseForm');
        if (form) form.reset();
        $('#editCaseIndex').val(''); // Limpiar índice de edición
        $('#newCaseModalLabel').text('Registrar Nueva Novedad');
        $('#beneficiariesContainer').empty(); // Limpiar beneficiarios
         $('#caseIdDisplay').text('').closest('div').hide(); // Ocultar ID
        // Quitar clases de validación si existen
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback').hide();
        console.log('Modal de nuevo caso reseteado.');
    },

    /**
     * Maneja el evento de guardar/actualizar desde el modal.
     * Valida, obtiene datos, llama a la API y actualiza la UI.
     */
    async handleSave() {
        // 1. Validar formulario
        if (!this.validateForm()) {
            return; // La validación muestra mensajes de error
        }

        // 2. Obtener datos del formulario
        const formData = this.getFormData();
        const editIndex = $('#editCaseIndex').val(); // Índice si estamos editando
        const isEditing = editIndex !== '';

        const saveButton = document.getElementById('saveCaseButton');
        const originalButtonHtml = saveButton.innerHTML;
        saveButton.disabled = true;
        saveButton.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Guardando...`;

        try {
            NovedadesUI.showLoading(); // Mostrar overlay general

            let result;
            if (isEditing) {
                // --- Modo Edición ---
                const novedadId = window.caseDataStore[editIndex].id;
                // Enviar solo los campos que podrían cambiar (o todos si es más simple)
                // Asegúrate que la API maneje bien la actualización parcial o total
                result = await NovedadesAPI.update(novedadId, formData);

                // Actualizar el dato en el store local
                window.caseDataStore[editIndex] = result;
                NovedadesUI.showSuccess(NOVEDADES_CONFIG.MESSAGES.SUCCESS.UPDATE + ` (#${novedadId})`);
                // Actualizar la fila en la tabla
                NovedadesTable.updateRow(editIndex);

            } else {
                // --- Modo Creación ---
                result = await NovedadesAPI.create(formData);

                // Añadir el nuevo caso al store local (al principio)
                window.caseDataStore.unshift(result);
                NovedadesUI.showSuccess(NOVEDADES_CONFIG.MESSAGES.SUCCESS.CREATE + ` (#${result.id})`);
                // Recargar toda la tabla para mostrar el nuevo registro
                NovedadesTable.refresh();
            }

            // Cerrar modal
            if (this.newCaseModal) this.newCaseModal.hide(); // Usa la instancia guardada
             // Recalcular y mostrar stats actualizadas
             const stats = NovedadesUI.calculateStats(window.caseDataStore);
             NovedadesUI.renderDashboardStats(stats);


        } catch (error) {
            console.error("Error al guardar:", error);
            NovedadesUI.showError(
                (isEditing ? NOVEDADES_CONFIG.MESSAGES.ERROR.UPDATE : NOVEDADES_CONFIG.MESSAGES.ERROR.CREATE) + `: ${error.message}`
            );
            // No cerrar el modal si hubo error para que el usuario pueda corregir

        } finally {
            NovedadesUI.hideLoading(); // Ocultar overlay general
            saveButton.disabled = false; // Reactivar botón
            saveButton.innerHTML = originalButtonHtml;
            feather.replace(); // Recargar icono del botón
        }
    },

    /**
     * Valida los campos requeridos del formulario de nuevo/editar caso.
     * Muestra mensajes de error si es necesario.
     * @returns {boolean} - true si el formulario es válido, false si no.
     */
    validateForm() {
        let isValid = true;
        const form = document.getElementById('newCaseForm');
        // Quitar validaciones previas
        $('.is-invalid').removeClass('is-invalid');
        $('.invalid-feedback').hide();

        // Validar campos requeridos definidos en config
        for (const fieldId of NOVEDADES_CONFIG.VALIDATION.REQUIRED_FIELDS) {
            const field = $(`#${fieldId}`);
            if (!field.val() || field.val().trim() === '') {
                field.addClass('is-invalid');
                 // Podrías añadir un div .invalid-feedback después de cada campo en el HTML
                field.next('.invalid-feedback').text('Este campo es obligatorio.').show();
                isValid = false;
                if(isValid) field.focus(); // Enfocar el primer campo inválido
            }
        }

        // Validación específica de longitud para descripción
        const descriptionField = $('#description');
        const descriptionLength = descriptionField.val().trim().length;
        if (descriptionLength > 0 && descriptionLength < NOVEDADES_CONFIG.VALIDATION.MIN_DESCRIPTION_LENGTH) {
            descriptionField.addClass('is-invalid');
            descriptionField.next('.invalid-feedback').text(`La descripción debe tener al menos ${NOVEDADES_CONFIG.VALIDATION.MIN_DESCRIPTION_LENGTH} caracteres.`).show();
            isValid = false;
            if(isValid) descriptionField.focus();
        } else if (descriptionLength > NOVEDADES_CONFIG.VALIDATION.MAX_DESCRIPTION_LENGTH) {
             descriptionField.addClass('is-invalid');
             descriptionField.next('.invalid-feedback').text(`La descripción no puede exceder ${NOVEDADES_CONFIG.VALIDATION.MAX_DESCRIPTION_LENGTH} caracteres.`).show();
             isValid = false;
             if(isValid) descriptionField.focus();
        }

         // Validar que el ID del usuario exista si se ingresó un número
         const idNumber = $('#idNumber').val().trim();
         const firstName = $('#firstName').val().trim();
         if(idNumber && !firstName) { // Si hay ID pero no se autocompletó el nombre
              $('#idNumber').addClass('is-invalid');
              $('#idNumber').next('.invalid-feedback').text('Usuario no encontrado o no válido.').show();
              isValid = false;
              if(isValid) $('#idNumber').focus();
         }


        if (!isValid) {
            NovedadesUI.showError('Por favor, corrija los campos marcados en rojo.');
        }

        return isValid;
    },

    /**
     * Recoge los datos del formulario y los estructura en un objeto.
     * Incluye la recolección de datos de beneficiarios.
     * @returns {Object} - Objeto con los datos de la novedad.
     */
    getFormData() {
        const beneficiaries = [];
        $('#beneficiariesContainer .beneficiary-entry').each(function() {
            const entry = $(this);
            beneficiaries.push({
                name: entry.find('input[name^="beneficiaryName"]').val(),
                relationship: entry.find('select[name^="beneficiaryRelationship"]').val(),
                idNumber: entry.find('input[name^="beneficiaryId"]').val()
            });
        });

        return {
            client: $('#client').val(),
            // clientNit: $('#clientNit').val(), // Descomentar si usas este campo
            subject: $('#subject').val(),
            priority: $('#priority').val(),
            priorityText: $('#priority option:selected').text(), // Guardar texto para UI
            status: $('#status').val(),
            description: $('#description').val(),
            radicado: $('#radicado').val(),
            assignedTo: $('#assignedTo').val(),
            idType: $('#idType').val(),
            idNumber: $('#idNumber').val(),
            firstName: $('#firstName').val(),
            lastName: $('#lastName').val(),
            nationality: $('#nationality').val(),
            gender: $('#gender').val(),
            birthDate: $('#birthDate').val(),
            phone: $('#phone').val(),
            department: $('#department').val(),
            city: $('#city').val(),
            address: $('#address').val(),
            neighborhood: $('#neighborhood').val(),
            email: $('#email').val(),
            eps: $('#eps').val(),
            arl: $('#arl').val(),
            arlClass: $('#arlClass').val(),
            ccf: $('#ccf').val(),
            pensionFund: $('#pensionFund').val(),
            ibc: $('#ibc').val(),
            beneficiaries: beneficiaries // Array de objetos beneficiario
        };
    },

    /**
     * Busca un usuario por ID (Cédula) en la caché o API y rellena campos.
     */
    async findAndFillUser() {
        const numeroId = $('#idNumber').val().trim();
        const tipoId = $('#idType').val(); // Opcional: podrías usarlo para buscar

        // Limpiar campos relacionados si el ID está vacío
        if (!numeroId) {
            $('#firstName').val('');
            $('#lastName').val('');
            $('#email').val('');
            $('#phone').val('');
            // ... limpiar otros campos de usuario ...
            $('#idNumber').removeClass('is-invalid'); // Quitar posible error previo
            $('#idNumber').next('.invalid-feedback').hide();
            return;
        }

        // Mostrar indicador de búsqueda (opcional)
        $('#firstName').val('Buscando...');
        $('#lastName').val('');

        try {
            const usuario = await NovedadesAPI.findUsuarioById(numeroId); // Usar función de API

            if (usuario) {
                // Rellenar campos del formulario
                $('#firstName').val(usuario.primerNombre || '');
                // Combinar apellidos
                $('#lastName').val(`${usuario.primerApellido || ''} ${usuario.segundoApellido || ''}`.trim());
                $('#nationality').val(usuario.nacionalidad || '');
                $('#gender').val(usuario.sexoIdentificacion || usuario.sexoBiologico || ''); // Priorizar identificación
                $('#birthDate').val(usuario.fechaNacimiento || '');
                $('#phone').val(usuario.telefonoCelular || usuario.telefonoFijo || '');
                $('#department').val(usuario.departamentoNacimiento || ''); // Usar de nacimiento como fallback
                $('#city').val(usuario.municipioNacimiento || ''); // Usar de nacimiento como fallback
                $('#address').val(usuario.direccion || '');
                $('#neighborhood').val(usuario.comunaBarrio || '');
                $('#email').val(usuario.correoElectronico || '');

                 // Rellenar afiliaciones si coinciden
                 $('#eps').val(usuario.epsNombre || '');
                 $('#arl').val(usuario.arlNombre || '');
                 $('#arlClass').val(usuario.claseRiesgoARL || '');
                 $('#ccf').val(usuario.ccfNombre || '');
                 $('#pensionFund').val(usuario.afpNombre || '');
                 $('#ibc').val(usuario.ibc || '');

                 // Intentar rellenar el campo 'client' si el usuario tiene empresa asociada
                 if(usuario.administracion && !$('#client').val()) {
                     $('#client').val(usuario.administracion);
                     // Opcional: buscar y rellenar NIT si tienes la caché de empresas
                 }


                NovedadesUI.showToast('Usuario encontrado y datos cargados.', 'success');
                $('#idNumber').removeClass('is-invalid');
                $('#idNumber').next('.invalid-feedback').hide();
            } else {
                // Limpiar campos si no se encontró
                $('#firstName').val('');
                $('#lastName').val('');
                $('#email').val('');
                $('#phone').val('');
                 // ... limpiar otros campos de usuario ...
                NovedadesUI.showToast('Usuario no encontrado en la base de datos.', 'warning');
                 $('#idNumber').addClass('is-invalid');
                 $('#idNumber').next('.invalid-feedback').text('Usuario no encontrado.').show();
            }
        } catch (error) {
            console.error("Error al buscar usuario:", error);
            $('#firstName').val(''); // Limpiar en caso de error
            $('#lastName').val('');
            NovedadesUI.showError('Error al conectar con el servidor para buscar usuario.');
             $('#idNumber').addClass('is-invalid');
             $('#idNumber').next('.invalid-feedback').text('Error de conexión.').show();
        }
    },

    /**
      * Busca una empresa por NIT en la caché y rellena el campo de nombre.
      */
     async findAndFillCompany() {
         const nit = $('#clientNit').val().trim();
         const clientNameInput = $('#client');

         if (!nit) {
             clientNameInput.val(''); // Limpiar si el NIT está vacío
             return;
         }

         // Buscar en caché primero (asumiendo que window.empresasCache está poblado)
         const cachedCompany = window.empresasCache.find(e => e.nit === nit);

         if (cachedCompany) {
             clientNameInput.val(cachedCompany.nombre_empresa || '');
             NovedadesUI.showToast('Empresa encontrada en caché.', 'info');
         } else {
             // Si no está en caché, podrías hacer una llamada API específica (opcional)
             // O simplemente indicar que no se encontró en la caché cargada
             console.warn(`Empresa con NIT ${nit} no encontrada en caché.`);
             // No limpiar el campo de nombre si el usuario ya lo escribió
             // clientNameInput.val(''); // Podrías limpiar o no, según preferencia
         }
     },


    /**
     * Añade una nueva entrada para un beneficiario en el formulario.
     * @param {string} [name=''] - Nombre inicial (para edición).
     * @param {string} [relationship=''] - Parentesco inicial.
     * @param {string} [idNumber=''] - ID inicial.
     */
    addBeneficiaryEntry(name = '', relationship = '', idNumber = '') {
        const container = document.getElementById('beneficiariesContainer');
        const index = container.children.length + 1; // Índice basado en 1

        const entryHtml = `
            <div class="beneficiary-entry row g-3 mb-3 p-3 border rounded bg-light" data-index="${index}">
                <div class="col-12 d-flex justify-content-between align-items-center mb-2">
                    <h6 class="mb-0 fw-bold">Beneficiario #${index}</h6>
                    <button type="button" class="btn btn-sm btn-outline-danger remove-beneficiary-btn">
                        <i class="ti ti-trash"></i>
                    </button>
                </div>
                <div class="col-md-6">
                    <label class="form-label form-label-sm">Nombre Completo</label>
                    <input type="text" class="form-control form-control-sm" name="beneficiaryName_${index}" value="${name}">
                </div>
                <div class="col-md-3">
                    <label class="form-label form-label-sm">Parentesco</label>
                    <select class="form-select form-select-sm" name="beneficiaryRelationship_${index}">
                        <option value="">Seleccione...</option>
                        <option value="Conyuge" ${relationship === 'Conyuge' ? 'selected' : ''}>Cónyuge</option>
                        <option value="Hijo" ${relationship === 'Hijo' ? 'selected' : ''}>Hijo/a</option>
                        <option value="Padre" ${relationship === 'Padre' ? 'selected' : ''}>Padre/Madre</option>
                        <option value="Otro" ${relationship === 'Otro' ? 'selected' : ''}>Otro</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <label class="form-label form-label-sm">Documento ID</label>
                    <input type="text" class="form-control form-control-sm" name="beneficiaryId_${index}" value="${idNumber}">
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', entryHtml);

        // Adjuntar evento al nuevo botón de eliminar
        const newEntry = container.lastElementChild;
        const removeBtn = newEntry.querySelector('.remove-beneficiary-btn');
        if(removeBtn) {
            removeBtn.addEventListener('click', () => {
                newEntry.remove();
                // Opcional: Re-numerar los beneficiarios restantes
                this.renumberBeneficiaries();
            });
        }
         feather.replace(); // Actualizar icono de basura
    },

    /**
     * Re-numera visualmente los beneficiarios después de eliminar uno.
     */
     renumberBeneficiaries() {
         const container = document.getElementById('beneficiariesContainer');
         const entries = container.querySelectorAll('.beneficiary-entry');
         entries.forEach((entry, i) => {
             const index = i + 1;
             entry.dataset.index = index;
             const header = entry.querySelector('h6');
             if(header) header.childNodes[0].nodeValue = `Beneficiario #${index}`; // Actualizar texto del encabezado

             // Actualizar atributos name/id/for (opcional si la recolección no depende de ellos estrictamente)
             entry.querySelectorAll('input, select').forEach(input => {
                 const nameAttr = input.getAttribute('name');
                 if (nameAttr) {
                     const newName = nameAttr.replace(/_\d+$/, `_${index}`);
                     input.setAttribute('name', newName);
                     // Actualizar id y for si existen y coinciden
                     // ...
                 }
             });
         });
     },

    /**
     * Llena el formulario con datos de simulación (para pruebas).
     */
    fillSimulationData() {
        this.resetNewCaseModal(); // Limpiar primero
        $('#client').val('Empresa Simulada XYZ');
        $('#clientNit').val('900123456-1');
        $('#subject').val('Problema con Acceso Plataforma X');
        $('#priority').val('alta');
        $('#status').val('Nuevo');
        $('#description').val('El usuario reporta que no puede ingresar a la plataforma X desde ayer. Error "Credenciales inválidas" a pesar de usar las correctas. Urgente revisar.');
        $('#radicado').val('SIM-' + Date.now().toString().slice(-5));
        $('#assignedTo').val('Analista_Soporte');
        $('#idType').val('CC');
        $('#idNumber').val('100200300'); // ID para buscar
        this.findAndFillUser(); // Intentar autocompletar usuario
        this.addBeneficiaryEntry('Beneficiario Uno', 'Hijo', '100200301');
        this.addBeneficiaryEntry('Beneficiario Dos', 'Conyuge', '100200302');
        NovedadesUI.showToast('Datos de simulación cargados.', 'info');
    },

    // ===========================================
    // FUNCIONES PARA MODAL VER DETALLES
    // ===========================================

    /**
     * Muestra el modal de detalles para una novedad específica.
     * @param {number} index - Índice del caso en window.caseDataStore.
     */
    showDetails(index) {
        const novedad = window.caseDataStore[index];
        if (!novedad) {
            NovedadesUI.showError('No se encontró el caso para ver detalles.');
            return;
        }

        this.populateViewModal(novedad, index); // Llenar con datos

        if (this.viewCaseModal) this.viewCaseModal.show();
    },

    /**
     * Llena el contenido del modal de visualización con los datos de la novedad.
     * @param {Object} novedad - El objeto de la novedad.
     * @param {number} index - El índice del caso en el store.
     */
    populateViewModal(novedad, index) {
        // Guardar índice actual en el modal para referencia (ej. para añadir comentario)
        $('#viewCaseModal').data('case-index', index);

        // Llenar campos de información básica
        $('#viewCaseId').text(novedad.id || 'N/A');
        $('#viewClient').text(novedad.client || 'N/A');
        $('#viewSubject').text(novedad.subject || 'N/A');
        $('#viewPriority').html(NovedadesUI.getPriorityBadge(novedad.priority, novedad.priorityText));
        $('#viewStatus').html(NovedadesUI.getStatusBadge(novedad.status));
        $('#viewAssignedTo').text(novedad.assignedTo || 'N/A');
        $('#viewCreationDate').text(NovedadesUI.formatDateTime(novedad.creationDate));
        $('#viewUpdateDate').text(NovedadesUI.formatDateTime(novedad.updateDate));
        $('#viewRadicado').text(novedad.radicado || 'N/A');

        // Llenar descripción y solución
        $('#viewDescription').text(novedad.description || 'Sin descripción.');
        $('#viewSolutionDescription').text(novedad.solutionDescription || 'Sin solución registrada.');

        // Llenar datos del usuario
        $('#viewIdType').text(novedad.idType || 'N/A');
        $('#viewIdNumber').text(novedad.idNumber || 'N/A');
        $('#viewFullName').text(`${novedad.firstName || ''} ${novedad.lastName || ''}`.trim() || 'N/A');
        $('#viewNationality').text(novedad.nationality || 'N/A');
        $('#viewGender').text(novedad.gender || 'N/A');
        $('#viewBirthDate').text(NovedadesUI.formatDate(novedad.birthDate));
        $('#viewPhone').text(novedad.phone || 'N/A');
        $('#viewDepartment').text(novedad.department || 'N/A');
        $('#viewCity').text(novedad.city || 'N/A');
        $('#viewAddress').text(novedad.address || 'N/A');
        $('#viewNeighborhood').text(novedad.neighborhood || 'N/A');
        $('#viewEmail').text(novedad.email || 'N/A');

        // Llenar datos de afiliación
        $('#viewEps').text(novedad.eps || 'N/A');
        $('#viewArl').text(`${novedad.arl || 'N/A'} (${novedad.arlClass || 'N/A'})`);
        $('#viewCcf').text(novedad.ccf || 'N/A');
        $('#viewPensionFund').text(novedad.pensionFund || 'N/A');
        $('#viewIbc').text(novedad.ibc ? NovedadesUI.formatCurrency(novedad.ibc) : 'N/A'); // Formatear IBC

        // Llenar beneficiarios
        const benContainer = $('#viewBeneficiariesList');
        benContainer.empty();
        if (novedad.beneficiaries && novedad.beneficiaries.length > 0) {
            novedad.beneficiaries.forEach(b => {
                benContainer.append(`<li>${b.name} (${b.relationship || 'N/A'}) - ID: ${b.idNumber || 'N/A'}</li>`);
            });
        } else {
            benContainer.append('<li class="text-muted">No hay beneficiarios registrados.</li>');
        }

        // Llenar historial
        const historyContainer = $('#viewHistoryTimeline');
        historyContainer.empty();
        if (novedad.history && novedad.history.length > 0) {
             novedad.history.forEach(entry => {
                 const commentHtml = entry.comment ? `<div class="history-comment">${entry.comment}</div>` : '';
                 historyContainer.append(`
                     <div class="history-entry">
                         <div class="history-timestamp">${NovedadesUI.formatDateTime(entry.timestamp)}</div>
                         <div class="history-user">Por: ${entry.user || 'Sistema'}</div>
                         <div class="history-action">${entry.action || 'Actualización'}</div>
                         ${commentHtml}
                     </div>
                 `);
             });
        } else {
             historyContainer.append('<p class="text-muted">No hay historial para este caso.</p>');
        }
        // Limpiar campo de nuevo comentario
        $('#newCommentText').val('');
    },

    /**
     * Maneja el envío de un nuevo comentario desde el modal de detalles.
     */
    async handleAddComment() {
        const index = $('#viewCaseModal').data('case-index'); // Obtener índice guardado
        const comment = $('#newCommentText').val().trim();
        const addCommentButton = document.getElementById('addCommentButton');
        const originalButtonHtml = addCommentButton.innerHTML;

        if (index === undefined || !window.caseDataStore || !window.caseDataStore[index]) {
            NovedadesUI.showError('Error: No se pudo identificar el caso actual.');
            return;
        }

        if (!comment) {
            NovedadesUI.showError('Debe escribir un comentario para agregarlo.');
            $('#newCommentText').focus();
            return;
        }

        addCommentButton.disabled = true;
        addCommentButton.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Agregando...`;

        try {
            NovedadesUI.showLoading(); // Usar overlay para acción importante

            const novedadId = window.caseDataStore[index].id;
            // Llamar a la API para agregar el comentario
            const updatedNovedad = await NovedadesAPI.addComment(novedadId, comment);

            // Actualizar el dato en el store local
            window.caseDataStore[index] = updatedNovedad;

            // Actualizar la vista del modal con la novedad actualizada (incluye el nuevo historial)
            this.populateViewModal(updatedNovedad, index);

            // Actualizar la fila en la tabla (para reflejar cambio en fecha de actualización)
            NovedadesTable.updateRow(index);

            NovedadesUI.hideLoading();
            NovedadesUI.showSuccess('Comentario agregado exitosamente.');
            // El campo de comentario ya se limpia en populateViewModal

        } catch (error) {
            NovedadesUI.hideLoading();
            console.error("Error al agregar comentario:", error);
            NovedadesUI.showError('Error al agregar comentario: ' + error.message);

        } finally {
            addCommentButton.disabled = false; // Reactivar botón
            addCommentButton.innerHTML = originalButtonHtml;
            feather.replace(); // Recargar icono del botón
        }
    },

    // ===========================================
    // FUNCIONES PARA MODAL IMPORTAR (Esqueleto)
    // ===========================================
    /**
     * Maneja el evento de importar casos desde un archivo (necesita implementación).
     */
    async handleImport() {
         console.warn("Función handleImport no implementada.");
         NovedadesUI.showToast("La importación de casos aún no está disponible.", "warning");
         // Aquí iría la lógica para:
         // 1. Obtener el archivo del input #importFile
         // 2. Validar el archivo (tipo, tamaño)
         // 3. Crear FormData y enviarlo a un endpoint API '/api/novedades/importar' (a crear en backend)
         // 4. Procesar la respuesta (éxito/error, cuántos importados)
         // 5. Cerrar modal y refrescar tabla si es exitoso
    }

};

// Exponer globalmente
window.NovedadesModals = NovedadesModals;