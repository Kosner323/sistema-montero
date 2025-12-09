/**
 * ========================================
 * SIMULADOR PILA - Motor de Seguridad Social
 * Versión: 1.0.0
 * Fecha: 2025
 * ========================================
 * 
 * Frontend para consumir el endpoint POST /api/cotizaciones/simular-pila
 * Integra con Motor PILA v1.1.0 (Backend)
 * 
 * Funcionalidades:
 * - Validación de formulario
 * - Llamada AJAX a API REST
 * - Renderizado dinámico de resultados
 * - Manejo de errores visuales
 * - Formateo de moneda colombiana
 */

// ========== CONSTANTES ==========
const SMMLV_2025 = 1300000;
const API_ENDPOINT = '/api/cotizaciones/simular-pila';

// ========== UTILIDADES ==========

/**
 * Formatea un número como moneda colombiana (COP)
 * @param {number} valor - Valor numérico a formatear
 * @returns {string} Valor formateado como "$1,300,000"
 */
function formatearMoneda(valor) {
  if (valor === null || valor === undefined || isNaN(valor)) {
    return '$0';
  }
  
  // Convertir a número entero
  const valorEntero = Math.round(valor);
  
  // Formatear con separadores de miles
  const formateado = valorEntero.toLocaleString('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  });
  
  return formateado;
}

/**
 * Formatea un número como porcentaje con 3 decimales
 * @param {number} valor - Valor numérico (0.12 = 12%)
 * @returns {string} Valor formateado como "12.000%"
 */
function formatearPorcentaje(valor) {
  if (valor === null || valor === undefined || isNaN(valor)) {
    return '0.000%';
  }
  
  return (valor * 100).toFixed(3) + '%';
}

/**
 * Muestra el overlay de carga
 */
function mostrarLoader() {
  const loader = document.getElementById('loaderOverlay');
  if (loader) {
    loader.style.display = 'flex';
  }
}

/**
 * Oculta el overlay de carga
 */
function ocultarLoader() {
  const loader = document.getElementById('loaderOverlay');
  if (loader) {
    loader.style.display = 'none';
  }
}

/**
 * Muestra un mensaje de error con SweetAlert
 * @param {string} mensaje - Mensaje de error
 * @param {string} titulo - Título del error (opcional)
 */
function mostrarError(mensaje, titulo = 'Error en la simulación') {
  // Verificar si SweetAlert está disponible
  if (typeof Swal !== 'undefined') {
    Swal.fire({
      icon: 'error',
      title: titulo,
      html: mensaje,
      confirmButtonText: 'Entendido',
      confirmButtonColor: '#dc3545'
    });
  } else {
    // Fallback a alert nativo
    alert(`${titulo}\n\n${mensaje}`);
  }
}

/**
 * Muestra un mensaje de éxito
 * @param {string} mensaje - Mensaje de éxito
 */
function mostrarExito(mensaje) {
  if (typeof Swal !== 'undefined') {
    Swal.fire({
      icon: 'success',
      title: '¡Cálculo exitoso!',
      text: mensaje,
      timer: 2000,
      showConfirmButton: false,
      toast: true,
      position: 'top-end'
    });
  }
}

// ========== VALIDACIÓN DEL FORMULARIO ==========

/**
 * Valida los datos del formulario antes de enviar
 * @param {Object} datos - Datos del formulario
 * @returns {Object} {valido: boolean, errores: string[]}
 */
function validarFormulario(datos) {
  const errores = [];
  
  // Validar salario base
  if (!datos.salario_base || datos.salario_base <= 0) {
    errores.push('El salario base debe ser mayor a $0');
  }
  
  if (datos.salario_base < SMMLV_2025 * 0.5) {
    errores.push(`El salario base parece muy bajo. SMMLV 2025 = ${formatearMoneda(SMMLV_2025)}`);
  }
  
  // Validar nivel de riesgo
  if (!datos.nivel_riesgo || datos.nivel_riesgo < 1 || datos.nivel_riesgo > 5) {
    errores.push('El nivel de riesgo ARL debe estar entre 1 y 5');
  }
  
  return {
    valido: errores.length === 0,
    errores: errores
  };
}

// ========== LLAMADA A LA API ==========

/**
 * Envía los datos a la API y retorna la respuesta
 * @param {Object} datos - Datos de la simulación
 * @returns {Promise<Object>} Respuesta de la API
 */
async function enviarSimulacion(datos) {
  try {
    const response = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(datos),
      credentials: 'same-origin' // Incluir cookies de sesión
    });
    
    // Verificar si la respuesta es JSON válida
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('La respuesta del servidor no es JSON válida');
    }
    
    const resultado = await response.json();
    
    // Manejar errores HTTP
    if (!response.ok) {
      // HTTP 400 - Error de validación
      if (response.status === 400) {
        throw new Error(resultado.error || 'Datos inválidos. Verifica los valores ingresados.');
      }
      
      // HTTP 401 - No autenticado
      if (response.status === 401) {
        window.location.href = '/login';
        throw new Error('Sesión expirada. Redirigiendo al login...');
      }
      
      // HTTP 500 - Error del servidor
      if (response.status === 500) {
        throw new Error('Error interno del servidor. Intenta nuevamente más tarde.');
      }
      
      // Otros errores
      throw new Error(resultado.error || `Error HTTP ${response.status}`);
    }
    
    return resultado;
    
  } catch (error) {
    // Error de red o fetch
    if (error.name === 'TypeError' || error.message.includes('Failed to fetch')) {
      throw new Error('No se pudo conectar con el servidor. Verifica tu conexión a internet.');
    }
    
    // Re-lanzar el error original
    throw error;
  }
}

// ========== RENDERIZADO DE RESULTADOS ==========

/**
 * Renderiza los datos de entrada en la sección correspondiente
 * @param {Object} datos - Sección "datos_entrada" de la respuesta
 */
function renderizarDatosEntrada(datos) {
  const container = document.getElementById('datosEntrada');
  if (!container) return;
  
  const html = `
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-currency-dollar"></i> Salario Base
      </span>
      <span class="resultado-valor">${formatearMoneda(datos.salario_base)}</span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-calculator"></i> IBC (Ingreso Base Cotización)
      </span>
      <span class="resultado-valor">${formatearMoneda(datos.ibc)}</span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-shield"></i> Nivel Riesgo ARL
      </span>
      <span class="resultado-valor">Nivel ${datos.nivel_riesgo}</span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-percentage"></i> Salario Integral
      </span>
      <span class="info-badge ${datos.es_salario_integral ? 'success' : 'info'}">
        ${datos.es_salario_integral ? 'SÍ (IBC = 70%)' : 'NO'}
      </span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-discount"></i> Empresa Exonerada
      </span>
      <span class="info-badge ${datos.es_empresa_exonerada ? 'success' : 'warning'}">
        ${datos.es_empresa_exonerada ? 'SÍ (Salud = $0)' : 'NO'}
      </span>
    </div>
  `;
  
  container.innerHTML = html;
}

/**
 * Renderiza los aportes del empleado
 * @param {Object} datos - Secciones "salud", "pension" de la respuesta
 */
function renderizarAportesEmpleado(datos) {
  const container = document.getElementById('aportesEmpleado');
  if (!container) return;
  
  const { salud, pension } = datos;
  const totalEmpleado = salud.aporte_empleado + pension.aporte_empleado;
  
  const html = `
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-heart"></i> Salud (${formatearPorcentaje(salud.porcentaje_empleado)})
      </span>
      <span class="resultado-valor empleado">${formatearMoneda(salud.aporte_empleado)}</span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-user-shield"></i> Pensión (${formatearPorcentaje(pension.porcentaje_empleado)})
      </span>
      <span class="resultado-valor empleado">${formatearMoneda(pension.aporte_empleado)}</span>
    </div>
    <div class="resultado-item" style="border-top: 2px solid #dc3545; margin-top: 0.5rem; padding-top: 1rem;">
      <span class="resultado-label">
        <strong><i class="ti ti-sum"></i> TOTAL EMPLEADO</strong>
      </span>
      <span class="resultado-valor empleado destacado">${formatearMoneda(totalEmpleado)}</span>
    </div>
  `;
  
  container.innerHTML = html;
  
  // Actualizar badge del header
  const badge = document.getElementById('badgeTotalEmpleado');
  if (badge) {
    badge.textContent = formatearMoneda(totalEmpleado);
  }
}

/**
 * Renderiza los aportes del empleador
 * @param {Object} datos - Secciones "salud", "pension", "arl", "parafiscales" de la respuesta
 */
function renderizarAportesEmpleador(datos) {
  const container = document.getElementById('aportesEmpleador');
  if (!container) return;
  
  const { salud, pension, arl, parafiscales } = datos;
  
  const totalEmpleador = 
    salud.aporte_empleador + 
    pension.aporte_empleador + 
    arl.aporte_empleador + 
    parafiscales.sena + 
    parafiscales.icbf + 
    parafiscales.ccf;
  
  const html = `
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-heart"></i> Salud (${formatearPorcentaje(salud.porcentaje_empleador)})
      </span>
      <span class="resultado-valor empleador">${formatearMoneda(salud.aporte_empleador)}</span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-user-shield"></i> Pensión (${formatearPorcentaje(pension.porcentaje_empleador)})
      </span>
      <span class="resultado-valor empleador">${formatearMoneda(pension.aporte_empleador)}</span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-shield"></i> ARL (${formatearPorcentaje(arl.porcentaje_total)})
      </span>
      <span class="resultado-valor empleador">${formatearMoneda(arl.aporte_empleador)}</span>
    </div>
    <div class="resultado-item" style="background: rgba(13, 110, 253, 0.05); padding: 0.75rem; margin: 0.5rem 0; border-radius: 4px;">
      <span class="resultado-label">
        <strong><i class="ti ti-building-bank"></i> PARAFISCALES</strong>
      </span>
      <span class="resultado-valor empleador">
        <strong>${formatearMoneda(parafiscales.total)}</strong>
      </span>
    </div>
    <div class="resultado-item" style="padding-left: 2rem; font-size: 0.95rem;">
      <span class="resultado-label">
        <i class="ti ti-school"></i> SENA (${formatearPorcentaje(parafiscales.porcentaje_sena)})
      </span>
      <span class="resultado-valor">${formatearMoneda(parafiscales.sena)}</span>
    </div>
    <div class="resultado-item" style="padding-left: 2rem; font-size: 0.95rem;">
      <span class="resultado-label">
        <i class="ti ti-users"></i> ICBF (${formatearPorcentaje(parafiscales.porcentaje_icbf)})
      </span>
      <span class="resultado-valor">${formatearMoneda(parafiscales.icbf)}</span>
    </div>
    <div class="resultado-item" style="padding-left: 2rem; font-size: 0.95rem;">
      <span class="resultado-label">
        <i class="ti ti-home"></i> CCF (${formatearPorcentaje(parafiscales.porcentaje_ccf)})
      </span>
      <span class="resultado-valor">${formatearMoneda(parafiscales.ccf)}</span>
    </div>
    <div class="resultado-item" style="border-top: 2px solid #0d6efd; margin-top: 0.5rem; padding-top: 1rem;">
      <span class="resultado-label">
        <strong><i class="ti ti-sum"></i> TOTAL EMPLEADOR</strong>
      </span>
      <span class="resultado-valor empleador destacado">${formatearMoneda(totalEmpleador)}</span>
    </div>
  `;
  
  container.innerHTML = html;
  
  // Actualizar badge del header
  const badge = document.getElementById('badgeTotalEmpleador');
  if (badge) {
    badge.textContent = formatearMoneda(totalEmpleador);
  }
}

/**
 * Renderiza el resumen de totales
 * @param {Object} totales - Sección "totales" de la respuesta
 */
function renderizarTotales(totales) {
  const container = document.getElementById('totalesResumen');
  if (!container) return;
  
  const html = `
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-user-minus"></i> Total Empleado
      </span>
      <span class="resultado-valor empleado">${formatearMoneda(totales.total_empleado)}</span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-building"></i> Total Empleador
      </span>
      <span class="resultado-valor empleador">${formatearMoneda(totales.total_empleador)}</span>
    </div>
    <div class="resultado-item" style="border-top: 3px solid #198754; margin-top: 0.75rem; padding-top: 1rem; background: rgba(25, 135, 84, 0.1); padding: 1rem; border-radius: 4px;">
      <span class="resultado-label">
        <strong><i class="ti ti-sum"></i> COSTO TOTAL NÓMINA</strong>
      </span>
      <span class="resultado-valor destacado" style="color: #198754; font-size: 1.75rem;">
        ${formatearMoneda(totales.total_general)}
      </span>
    </div>
    <div class="resultado-item">
      <span class="resultado-label">
        <i class="ti ti-percentage"></i> Carga Prestacional
      </span>
      <span class="info-badge warning">
        ${formatearPorcentaje(totales.porcentaje_carga_prestacional)} del salario base
      </span>
    </div>
  `;
  
  container.innerHTML = html;
}

/**
 * Renderiza las advertencias si existen
 * @param {Array} advertencias - Array de advertencias
 */
function renderizarAdvertencias(advertencias) {
  const container = document.getElementById('advertenciasContainer');
  const listContainer = document.getElementById('advertenciasList');
  
  if (!container || !listContainer) return;
  
  if (!advertencias || advertencias.length === 0) {
    container.style.display = 'none';
    return;
  }
  
  container.style.display = 'block';
  
  const html = advertencias.map(adv => `
    <div class="advertencia-item">
      <i class="ti ti-alert-triangle me-2"></i>
      <strong>${adv}</strong>
    </div>
  `).join('');
  
  listContainer.innerHTML = html;
}

/**
 * Renderiza los resultados completos de la simulación PILA
 * @param {Object} resultado - Respuesta completa de la API
 */
function renderizarResultados(resultado) {
  // ✅ GUARDAR LA SIMULACIÓN EN MEMORIA (para poder guardarla después)
  window.ultimaSimulacion = resultado;
  console.log('💾 Simulación guardada en memoria para posterior guardado');
  
  // Mostrar el contenedor de resultados
  const container = document.getElementById('resultadosContainer');
  if (container) {
    container.style.display = 'block';
    
    // Scroll suave hacia los resultados
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  
  // Actualizar versión del motor
  const badgeVersion = document.getElementById('badgeVersion');
  if (badgeVersion && resultado.metadata) {
    badgeVersion.textContent = `Motor ${resultado.metadata.version}`;
  }
  
  // Renderizar cada sección
  renderizarDatosEntrada(resultado.datos_entrada);
  renderizarAportesEmpleado(resultado);
  renderizarAportesEmpleador(resultado);
  renderizarTotales(resultado.totales);
  renderizarAdvertencias(resultado.metadata?.advertencias || []);
  
  // Mostrar mensaje de éxito
  mostrarExito('Cálculo completado exitosamente');
}

// ========== MANEJADOR DEL FORMULARIO ==========

/**
 * Procesa el formulario y ejecuta la simulación
 * @param {Event} event - Evento submit del formulario
 */
async function procesarFormulario(event) {
  event.preventDefault();
  
  // Deshabilitar botón de envío
  const btnCalcular = document.getElementById('btnCalcular');
  const btnTextoOriginal = btnCalcular.innerHTML;
  btnCalcular.disabled = true;
  btnCalcular.innerHTML = '<i class="ti ti-loader-2 ti-spin me-2"></i> Calculando...';
  
  try {
    // Recopilar datos del formulario
    const formData = new FormData(event.target);
    const datos = {
      salario_base: parseFloat(formData.get('salario_base')),
      nivel_riesgo: parseInt(formData.get('nivel_riesgo')),
      es_salario_integral: formData.get('es_salario_integral') === 'on',
      es_empresa_exonerada: formData.get('es_empresa_exonerada') === 'on'
    };
    
    // Validar datos
    const validacion = validarFormulario(datos);
    if (!validacion.valido) {
      mostrarError(
        '<ul style="text-align: left; padding-left: 1.5rem;">' +
        validacion.errores.map(err => `<li>${err}</li>`).join('') +
        '</ul>',
        'Errores de validación'
      );
      return;
    }
    
    // Mostrar loader
    mostrarLoader();
    
    // Enviar a la API
    const resultado = await enviarSimulacion(datos);
    
    // Renderizar resultados
    renderizarResultados(resultado);
    
  } catch (error) {
    console.error('Error en la simulación:', error);
    mostrarError(
      error.message || 'Ocurrió un error inesperado. Intenta nuevamente.',
      'Error en la simulación'
    );
    
  } finally {
    // Ocultar loader y restaurar botón
    ocultarLoader();
    btnCalcular.disabled = false;
    btnCalcular.innerHTML = btnTextoOriginal;
  }
}

// ========== INICIALIZACIÓN ==========

document.addEventListener('DOMContentLoaded', function() {
  console.log('✅ Simulador PILA v1.0.0 inicializado');
  
  // ========== INICIALIZAR BUSCADOR UNIVERSAL DE USUARIOS ==========
  let buscadorUniversal = null;

  if (typeof initUniversalSearch !== 'undefined') {
    try {
      buscadorUniversal = initUniversalSearch({
        tipoIdField: 'tipoDocBusqueda',
        numeroIdField: 'numeroDocBusqueda',
        fieldMapping: {
          // Mapeo específico para Simulador PILA
          ibc: 'salarioBase', // El IBC se mapea al campo salario base
          claseRiesgoARL: 'nivelRiesgo' // Nivel de riesgo ARL
        },
        autoLock: false, // NO bloquear campos (permitir edición)
        onSuccess: function(usuario) {
          console.log('✅ Usuario encontrado, aplicando lógica específica del simulador');

          // Lógica especial para switches basada en tipo de contrato
          if (usuario.tipo_contrato) {
            const tipoContrato = usuario.tipo_contrato.toUpperCase();

            // Switch de Salario Integral
            const switchIntegral = document.getElementById('salarioIntegral');
            if (switchIntegral) {
              const esIntegral = (tipoContrato === 'INTEGRAL' || tipoContrato === 'SALARIO INTEGRAL' || tipoContrato.includes('INTEGRAL'));
              switchIntegral.checked = esIntegral;
              console.log(`🔄 Tipo de contrato: ${tipoContrato} -> Salario Integral: ${esIntegral}`);
            }

            // Switch de Empresa Exonerada (por defecto true, pero se puede ajustar según datos)
            // Si el usuario tiene datos de exoneración específicos, aplicarlos aquí
          }

          // Si el usuario tiene nivel de riesgo específico en formato numérico o texto
          if (usuario.claseRiesgoARL) {
            const nivelRiesgoField = document.getElementById('nivelRiesgo');
            if (nivelRiesgoField) {
              // Intentar parsear el nivel de riesgo (puede ser "1", "Nivel 1", "I", etc.)
              let riesgo = parseInt(usuario.claseRiesgoARL);

              if (isNaN(riesgo)) {
                // Si no es numérico, intentar extraer el número
                const match = usuario.claseRiesgoARL.match(/\d+/);
                if (match) {
                  riesgo = parseInt(match[0]);
                }
              }

              if (riesgo >= 1 && riesgo <= 5) {
                nivelRiesgoField.value = riesgo.toString();
                console.log(`🛡️ Nivel de riesgo ARL asignado: ${riesgo}`);
              }
            }
          }
        },
        onNotFound: function() {
          console.log('ℹ️ Usuario no encontrado, campos listos para ingreso manual');
        }
      });

      console.log('🔍 Buscador Universal inicializado en Simulador PILA');
    } catch (error) {
      console.error('❌ Error al inicializar Buscador Universal:', error);
    }
  } else {
    console.warn('⚠️ universal-search.js no está cargado. Asegúrate de incluir el script antes de simulador-pila.js');
  }
  // ========== FIN INICIALIZACIÓN BUSCADOR ==========
  
  // Vincular evento submit del formulario
  const form = document.getElementById('formSimulador');
  if (form) {
    form.addEventListener('submit', procesarFormulario);
  } else {
    console.error('❌ Formulario #formSimulador no encontrado');
  }
  
  // Event listeners para switches (opcional: logging)
  const salarioIntegralSwitch = document.getElementById('salarioIntegral');
  const empresaExoneradaSwitch = document.getElementById('empresaExonerada');
  
  if (salarioIntegralSwitch) {
    salarioIntegralSwitch.addEventListener('change', function() {
      console.log('Salario Integral:', this.checked);
    });
  }
  
  if (empresaExoneradaSwitch) {
    empresaExoneradaSwitch.addEventListener('change', function() {
      console.log('Empresa Exonerada:', this.checked);
    });
  }
  
  // ========== EVENTO: GUARDAR COMO COTIZACIÓN ==========
  const btnGuardarCotizacion = document.getElementById('btnGuardarCotizacion');
  
  if (btnGuardarCotizacion) {
    btnGuardarCotizacion.addEventListener('click', async function() {
      console.log('💾 Iniciando guardado de simulación como cotización...');
      
      // Verificar que hay resultados calculados
      if (!window.ultimaSimulacion) {
        Swal.fire({
          icon: 'warning',
          title: 'No hay simulación',
          text: 'Debes calcular una simulación primero antes de guardarla.',
          confirmButtonText: 'Entendido'
        });
        return;
      }
      
      // Solicitar nombre de empresa con SweetAlert2
      const { value: empresa } = await Swal.fire({
        title: 'Guardar Simulación PILA',
        html: `
          <div class="mb-3 text-start">
            <label for="swal-empresa" class="form-label fw-bold">Nombre de la Empresa/Cliente *</label>
            <input type="text" id="swal-empresa" class="form-control" placeholder="Ej: Empresa XYZ S.A.S.">
          </div>
          <div class="mb-3 text-start">
            <label for="swal-email" class="form-label fw-bold">Email (opcional)</label>
            <input type="email" id="swal-email" class="form-control" placeholder="contacto@empresa.com">
          </div>
          <div class="mb-3 text-start">
            <label for="swal-notas" class="form-label fw-bold">Notas adicionales (opcional)</label>
            <textarea id="swal-notas" class="form-control" rows="3" placeholder="Información adicional sobre esta cotización..."></textarea>
          </div>
        `,
        focusConfirm: false,
        showCancelButton: true,
        confirmButtonText: '💾 Guardar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#28a745',
        preConfirm: () => {
          const empresaInput = document.getElementById('swal-empresa').value;
          const emailInput = document.getElementById('swal-email').value;
          const notasInput = document.getElementById('swal-notas').value;
          
          if (!empresaInput || empresaInput.trim() === '') {
            Swal.showValidationMessage('El nombre de la empresa es obligatorio');
            return false;
          }
          
          return {
            empresa: empresaInput.trim(),
            email: emailInput.trim(),
            notas: notasInput.trim()
          };
        }
      });
      
      // Si el usuario canceló
      if (!empresa) {
        console.log('Guardado cancelado por el usuario');
        return;
      }
      
      // Preparar datos para enviar
      const datosGuardar = {
        empresa: empresa.empresa,
        email: empresa.email,
        notas: empresa.notas,
        salario_base: window.ultimaSimulacion.datos_entrada.salario_base,
        nivel_riesgo: window.ultimaSimulacion.datos_entrada.nivel_riesgo_arl,
        total_empleado: window.ultimaSimulacion.totales.total_empleado,
        total_empleador: window.ultimaSimulacion.totales.total_empleador,
        total_general: window.ultimaSimulacion.totales.total_general
      };
      
      console.log('📤 Enviando datos:', datosGuardar);
      
      // Mostrar loader
      const loaderOverlay = document.getElementById('loaderOverlay');
      if (loaderOverlay) {
        loaderOverlay.style.display = 'flex';
        loaderOverlay.querySelector('p.fw-bold').textContent = 'Guardando cotización...';
      }
      
      try {
        const response = await fetch('/api/cotizaciones/guardar-simulacion', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(datosGuardar)
        });
        
        // Ocultar loader
        if (loaderOverlay) loaderOverlay.style.display = 'none';
        
        const resultado = await response.json();
        
        if (!response.ok) {
          throw new Error(resultado.error || `Error HTTP ${response.status}`);
        }
        
        // Éxito
        console.log('✅ Simulación guardada:', resultado);
        
        await Swal.fire({
          icon: 'success',
          title: '¡Guardado Exitoso!',
          html: `
            <p class="mb-2">La simulación se ha guardado como cotización real.</p>
            <div class="alert alert-info mt-3 mb-0">
              <strong>ID:</strong> ${resultado.id_cotizacion}<br>
              <strong>Empresa:</strong> ${empresa.empresa}<br>
              <strong>Monto Total:</strong> ${formatearMoneda(datosGuardar.total_general)}
            </div>
          `,
          confirmButtonText: 'Ver Cotizaciones',
          showCancelButton: true,
          cancelButtonText: 'Continuar Simulando',
          confirmButtonColor: '#007bff'
        }).then((result) => {
          if (result.isConfirmed) {
            // Redirigir a la página de cotizaciones
            window.location.href = '/cotizaciones';
          }
        });
        
      } catch (error) {
        console.error('❌ Error al guardar:', error);
        
        // Ocultar loader
        if (loaderOverlay) loaderOverlay.style.display = 'none';
        
        Swal.fire({
          icon: 'error',
          title: 'Error al Guardar',
          text: error.message || 'No se pudo guardar la simulación. Intenta nuevamente.',
          confirmButtonText: 'Entendido'
        });
      }
    });
  }
  
  // Autocompletar con valores de prueba (solo en desarrollo)
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('🔧 Modo desarrollo: valores de prueba disponibles');
    
    // Descomentar para autocompletar en desarrollo
    // document.getElementById('salarioBase').value = '1300000';
    // document.getElementById('nivelRiesgo').value = '1';
  }
});

// ========== EXPORTAR FUNCIONES (opcional, para testing) ==========
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    formatearMoneda,
    formatearPorcentaje,
    validarFormulario,
    enviarSimulacion
  };
}
