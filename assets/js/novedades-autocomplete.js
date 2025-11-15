/**
 * MÓDULO DE AUTOCOMPLETADO DE USUARIO PARA NOVEDADES
 * 
 * Este script implementa la funcionalidad de autocompletado automático
 * de información del usuario cuando se ingresa su número de identificación
 * en el formulario de "Nueva Novedad".
 * 
 * INSTALACIÓN:
 * 1. Incluir este script en novedades.html después de novedades-main.js
 * 2. Asegurarse de que el endpoint /api/depuraciones/buscar-usuario esté actualizado
 */

(function() {
    'use strict';

    // Esperar a que el DOM esté completamente cargado
    document.addEventListener('DOMContentLoaded', function() {
        
        console.log('🔧 Inicializando módulo de autocompletado de usuarios para Novedades');

        // Obtener referencias a los campos del formulario
        const idTypeField = document.getElementById('idType');
        const idNumberField = document.getElementById('idNumber');

        if (!idTypeField || !idNumberField) {
            console.warn('⚠️ No se encontraron los campos de ID en el formulario');
            return;
        }

        /**
         * Función principal que busca y autocompleta la información del usuario
         */
        async function buscarYAutocompletarUsuario() {
            const tipoId = idTypeField.value;
            const numeroId = idNumberField.value.trim();

            // Validar que ambos campos tengan valor
            if (!tipoId || !numeroId) {
                return; // No hacer nada si faltan datos
            }

            // Validar que el número de ID sea válido (solo números y mínimo 5 dígitos)
            if (!/^\d{5,}$/.test(numeroId)) {
                return; // Esperar a que el usuario termine de escribir
            }

            console.log(`🔍 Buscando usuario: ${tipoId} ${numeroId}`);

            try {
                // Mostrar indicador visual de carga (opcional)
                idNumberField.classList.add('is-loading');
                
                // Llamar al endpoint del backend
                const response = await fetch(
                    `/api/depuraciones/buscar-usuario?tipo=${encodeURIComponent(tipoId)}&numero=${encodeURIComponent(numeroId)}`,
                    {
                        method: 'GET',
                        headers: {
                            'Accept': 'application/json'
                        },
                        credentials: 'include'
                    }
                );

                // Remover indicador de carga
                idNumberField.classList.remove('is-loading');

                if (!response.ok) {
                    // Usuario no encontrado
                    if (response.status === 404) {
                        console.log('ℹ️ Usuario no encontrado en la base de datos');
                        mostrarMensajeUsuario('Usuario no encontrado. Por favor complete los datos manualmente.', 'warning');
                        limpiarCamposUsuario();
                        habilitarCamposParaEdicion();
                        return;
                    }
                    
                    // Otro tipo de error
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error al buscar usuario');
                }

                // Usuario encontrado - obtener datos
                const usuario = await response.json();
                console.log('✅ Usuario encontrado:', usuario);

                // Rellenar el formulario con los datos del usuario
                rellenarFormularioUsuario(usuario);
                
                // Mostrar mensaje de éxito
                mostrarMensajeUsuario('✅ Usuario encontrado correctamente. Datos cargados automáticamente.', 'success');

            } catch (error) {
                console.error('❌ Error al buscar usuario:', error);
                idNumberField.classList.remove('is-loading');
                mostrarMensajeUsuario('Error al buscar usuario: ' + error.message, 'danger');
                habilitarCamposParaEdicion();
            }
        }

        /**
         * Rellena el formulario con los datos del usuario obtenidos del backend
         */
        function rellenarFormularioUsuario(usuario) {
            // Construir nombre completo
            const primerNombre = usuario.primerNombre || '';
            const segundoNombre = usuario.segundoNombre || '';
            const primerApellido = usuario.primerApellido || '';
            const segundoApellido = usuario.segundoApellido || '';
            
            const nombreCompleto = `${primerNombre} ${segundoNombre}`.trim();
            const apellidoCompleto = `${primerApellido} ${segundoApellido}`.trim();

            // Rellenar campos de información básica
            setFieldValue('firstName', nombreCompleto);
            setFieldValue('lastName', apellidoCompleto);
            setFieldValue('phone', usuario.telefonoCelular || '');
            setFieldValue('email', usuario.correoElectronico || '');
            
            // Rellenar campos de información personal
            setFieldValue('nationality', usuario.nacionalidad || '');
            setFieldValue('gender', usuario.genero || '');
            setFieldValue('birthDate', usuario.fechaNacimiento || '');
            
            // Rellenar campos de ubicación
            setFieldValue('department', usuario.departamento || '');
            setFieldValue('city', usuario.ciudad || '');
            setFieldValue('address', usuario.direccion || '');
            setFieldValue('neighborhood', usuario.barrio || '');
            
            // Rellenar campos de afiliación
            setFieldValue('eps', usuario.epsNombre || '');
            setFieldValue('arl', usuario.arlNombre || '');
            setFieldValue('ccf', usuario.ccfNombre || '');
            setFieldValue('pensionFund', usuario.afpNombre || '');
            setFieldValue('ibc', usuario.ibc || '');

            // Marcar los campos como readonly (solo lectura) para evitar modificaciones accidentales
            deshabilitarCamposAutocompletados();
        }

        /**
         * Función auxiliar para establecer el valor de un campo de forma segura
         */
        function setFieldValue(fieldId, value) {
            const field = document.getElementById(fieldId);
            if (field) {
                field.value = value || '';
            }
        }

        /**
         * Deshabilita los campos autocompletados para evitar modificaciones
         */
        function deshabilitarCamposAutocompletados() {
            const camposAutocompletados = [
                'firstName', 'lastName', 'phone', 'email',
                'nationality', 'gender', 'birthDate',
                'department', 'city', 'address', 'neighborhood',
                'eps', 'arl', 'ccf', 'pensionFund', 'ibc'
            ];

            camposAutocompletados.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.setAttribute('readonly', 'readonly');
                    field.classList.add('bg-light'); // Agregar clase visual para indicar readonly
                }
            });
        }

        /**
         * Habilita los campos para edición manual
         */
        function habilitarCamposParaEdicion() {
            const camposAutocompletados = [
                'firstName', 'lastName', 'phone', 'email',
                'nationality', 'gender', 'birthDate',
                'department', 'city', 'address', 'neighborhood',
                'eps', 'arl', 'ccf', 'pensionFund', 'ibc'
            ];

            camposAutocompletados.forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.removeAttribute('readonly');
                    field.classList.remove('bg-light');
                }
            });
        }

        /**
         * Limpia todos los campos de usuario
         */
        function limpiarCamposUsuario() {
            const campos = [
                'firstName', 'lastName', 'phone', 'email',
                'nationality', 'gender', 'birthDate',
                'department', 'city', 'address', 'neighborhood',
                'eps', 'arl', 'ccf', 'pensionFund', 'ibc'
            ];

            campos.forEach(fieldId => {
                setFieldValue(fieldId, '');
            });
        }

        /**
         * Muestra un mensaje al usuario en el formulario
         */
        function mostrarMensajeUsuario(mensaje, tipo = 'info') {
            // Buscar o crear el contenedor de mensajes
            let messageContainer = document.getElementById('userSearchMessage');
            
            if (!messageContainer) {
                // Crear el contenedor si no existe
                messageContainer = document.createElement('div');
                messageContainer.id = 'userSearchMessage';
                messageContainer.className = 'alert alert-dismissible fade show mt-2';
                messageContainer.setAttribute('role', 'alert');
                
                // Insertar después del campo idNumber
                const idNumberParent = idNumberField.closest('.col-md-8');
                if (idNumberParent) {
                    idNumberParent.appendChild(messageContainer);
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

        // ==================== EVENT LISTENERS ====================

        /**
         * Evento cuando el usuario sale del campo de número de ID (blur)
         * Se ejecuta cuando el campo pierde el foco
         */
        idNumberField.addEventListener('blur', function() {
            // Pequeño delay para permitir que el usuario termine de escribir
            setTimeout(buscarYAutocompletarUsuario, 300);
        });

        /**
         * Evento cuando el usuario presiona Enter en el campo de número de ID
         */
        idNumberField.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Evitar que se envíe el formulario
                buscarYAutocompletarUsuario();
            }
        });

        /**
         * Evento cuando cambia el tipo de ID
         * Limpia los campos si ya había información cargada
         */
        idTypeField.addEventListener('change', function() {
            limpiarCamposUsuario();
            habilitarCamposParaEdicion();
            
            // Remover mensaje anterior
            const messageContainer = document.getElementById('userSearchMessage');
            if (messageContainer) {
                messageContainer.remove();
            }
        });

        /**
         * Evento cuando el usuario modifica el número de ID después de haber cargado datos
         * Esto permite que el usuario busque un nuevo usuario sin tener que recargar la página
         */
        idNumberField.addEventListener('input', function() {
            // Si hay datos cargados y el usuario modifica el número, limpiar los campos
            const firstName = document.getElementById('firstName');
            if (firstName && firstName.value && firstName.hasAttribute('readonly')) {
                // Hay datos autocompletados, preguntar si desea buscar de nuevo
                const messageContainer = document.getElementById('userSearchMessage');
                if (messageContainer) {
                    messageContainer.remove();
                }
            }
        });

        // ==================== LIMPIAR DATOS AL ABRIR MODAL ====================
        
        /**
         * Cuando se abre el modal de nueva novedad, limpiar todos los campos
         */
        const newCaseModal = document.getElementById('newCaseModal');
        if (newCaseModal) {
            newCaseModal.addEventListener('show.bs.modal', function() {
                console.log('🔄 Modal abierto - Limpiando campos de usuario');
                limpiarCamposUsuario();
                habilitarCamposParaEdicion();
                
                // Limpiar también los campos de ID
                if (idTypeField) idTypeField.value = '';
                if (idNumberField) idNumberField.value = '';
                
                // Remover mensaje anterior
                const messageContainer = document.getElementById('userSearchMessage');
                if (messageContainer) {
                    messageContainer.remove();
                }
            });
        }

        console.log('✅ Módulo de autocompletado de usuarios inicializado correctamente');
    });

})();
