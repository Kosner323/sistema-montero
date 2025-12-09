# ✅ Implementación de Interfaces - Configuración, Cartera y Formularios

## 📋 Resumen de Implementación

Se implementaron **3 interfaces completas** solicitadas por el Tech Lead: Configuración del Sistema, mejoras en Cartera de Clientes y Generador Automático de Formularios.

---

## 1️⃣ Nueva Página: `configuracion.html`

### 🎯 Objetivo
Crear una interfaz limpia para editar parámetros del sistema y descargar copias de seguridad.

### 🔧 Implementación Completa

#### **Estructura de la Página**
La página se divide en 4 secciones principales:

1. **Parámetros Salariales**
   - Salario Mínimo Legal Vigente (SMLV)
   - Auxilio de Transporte

2. **Porcentajes de Seguridad Social**
   - % Salud (EPS): 12.5% (Empleador 8.5% + Empleado 4%)
   - % Pensión (AFP): 16% (Empleador 12% + Empleado 4%)
   - % ARL: 0.522% (variable según riesgo)
   - % Caja de Compensación: 4%
   - % ICBF: 3%
   - % SENA: 2%

3. **Parámetros de Operación**
   - Días de alerta antes del vencimiento PILA
   - Tamaño máximo de archivos PDF (MB)
   - Email para notificaciones del sistema

4. **Zona de Peligro (Backup)**
   - Botón grande rojo para descargar backup completo
   - Estadísticas: último backup, tamaño estimado
   - Información de contenido del backup

#### **Características Visuales**
- ✅ Diseño limpio con secciones bien diferenciadas
- ✅ Input groups con íconos y unidades (COP, %, días, MB)
- ✅ Badges informativos para distribución de porcentajes
- ✅ Zona de peligro con fondo rojo claro y borde destacado
- ✅ Botón de backup animado con gradiente rojo y efecto hover
- ✅ Campos requeridos marcados con asterisco rojo
- ✅ Form text explicativo en cada campo

#### **Funcionalidad JavaScript**

```javascript
// Cargar configuración actual
async function cargarConfiguracion() {
    const response = await fetch('/api/configuracion', {
        method: 'GET',
        credentials: 'include'
    });
    const config = await response.json();
    // Llenar formulario con valores
}

// Guardar configuración
async function guardarConfiguracion() {
    const configData = {
        salario_minimo: parseFloat(document.getElementById('salarioMinimo').value),
        auxilio_transporte: parseFloat(document.getElementById('auxilioTransporte').value),
        porcentaje_salud: parseFloat(document.getElementById('porcentajeSalud').value),
        // ... más campos
    };
    
    const response = await fetch('/api/configuracion', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(configData)
    });
}

// Descargar backup
async function descargarBackup() {
    const response = await fetch('/api/sistema/backup-download', {
        method: 'GET',
        credentials: 'include'
    });
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `backup-sistema-${new Date().toISOString().split('T')[0]}.zip`;
    a.click();
}
```

### 📡 Endpoints Requeridos (Backend)

```
GET /api/configuracion
Response:
{
    "salario_minimo": 1300000,
    "auxilio_transporte": 162000,
    "porcentaje_salud": 12.5,
    "porcentaje_pension": 16,
    "porcentaje_arl": 0.522,
    "porcentaje_caja_comp": 4,
    "porcentaje_icbf": 3,
    "porcentaje_sena": 2,
    "dias_alerta_pila": 5,
    "limite_pdf_mb": 10,
    "email_notificaciones": "admin@montero.com",
    "ultimo_backup": "2025-11-28T14:30:00",
    "tamaño_backup": "47"
}

PUT /api/configuracion
Body: (mismo formato que GET)
Response:
{
    "success": true,
    "message": "Configuración actualizada exitosamente"
}

GET /api/sistema/backup-download
Response: application/zip (archivo binario)
Headers:
- Content-Type: application/zip
- Content-Disposition: attachment; filename="backup-sistema-YYYY-MM-DD.zip"
```

---

## 2️⃣ Actualización: `pagos/cartera.html`

### 🎯 Objetivo
Dividir la vista en 2 tabs: "Deudas Entidades" y "Cobro a Clientes" con funcionalidad completa de cuentas de cobro y WhatsApp.

### 🔧 Cambios Realizados

#### **Estructura de Tabs Actualizada**

**ANTES:**
- Tab 1: Cuentas por Cobrar (Clientes)
- Tab 2: Seguridad Social (Pasivos)

**DESPUÉS:**
- Tab 1: 💳 Deudas Entidades (Seguridad Social) - Lo que existía como "Seguridad Social"
- Tab 2: 📋 Cobro a Clientes - NUEVO con funcionalidad completa

#### **Tab 2: Cobro a Clientes (NUEVO)**

**Tabla con 9 columnas:**
1. Cliente (nombre de la empresa)
2. NIT/CC
3. Contacto (nombre de la persona)
4. Teléfono
5. Concepto (descripción de la deuda)
6. Fecha Vencimiento (con badge rojo si está vencida)
7. Saldo Pendiente (formato moneda COP)
8. Estado (badges: Pendiente, Vencido, Pagado, Parcial)
9. Acciones (botones de cuenta de cobro y WhatsApp)

**Botones de Acción:**

1. **Botón "Generar Cuenta de Cobro"** (azul con icono de factura)
   ```javascript
   window.generarCuentaCobro = async function(cuentaId, clienteNombre) {
       const response = await fetch(`/api/cartera/cobrar/${cuentaId}/cuenta-cobro`, {
           method: 'GET',
           credentials: 'include'
       });
       
       // Descargar PDF
       const blob = await response.blob();
       const url = window.URL.createObjectURL(blob);
       const a = document.createElement('a');
       a.href = url;
       a.download = `cuenta_cobro_${clienteNombre}_${fecha}.pdf`;
       a.click();
   };
   ```

2. **Botón "WhatsApp"** (verde con icono de mensaje)
   - Solo aparece si el cliente tiene teléfono registrado
   - Mensaje predefinido con monto pendiente
   ```javascript
   window.enviarWhatsAppCobro = function(telefono, clienteNombre, montoPendiente) {
       const telefonoLimpio = telefono.replace(/\D/g, '');
       const mensaje = `Hola ${clienteNombre},\n\nLe recordamos que tiene un saldo pendiente de ${formatMoney(montoPendiente)} por concepto de servicios prestados.\n\nPor favor proceda con el pago a la brevedad posible.\n\n¡Gracias!\nMontero y Negocio`;
       const whatsappURL = `https://wa.me/57${telefonoLimpio}?text=${encodeURIComponent(mensaje)}`;
       window.open(whatsappURL, '_blank');
   };
   ```

### 📡 Endpoint Requerido

```
GET /api/cartera/cobrar/{id}/cuenta-cobro
Response: application/pdf (archivo binario)
Headers:
- Content-Type: application/pdf
- Content-Disposition: attachment; filename="cuenta_cobro_CLIENTE_YYYY-MM-DD.pdf"
```

### ✨ Características Visuales
- ✅ Alert informativo en la parte superior del tab
- ✅ Botones agrupados (btn-group) para mejor UX
- ✅ Filas vencidas con fondo rojo claro
- ✅ Badge de "VENCIDA" en fecha de vencimiento
- ✅ Botón de WhatsApp solo visible si hay teléfono
- ✅ SweetAlert2 para loading mientras se genera el PDF

---

## 3️⃣ Mejora: `formularios/index.html`

### 🎯 Objetivo
Agregar sección "Generador Automático" para crear formularios pre-llenados con un solo clic.

### 🔧 Implementación

#### **Nueva Sección al Inicio de la Página**

Se agregó un card con borde azul destacado que contiene:

1. **Select de Plantillas** (con optgroups organizados)
   - 📋 Formularios EPS: Sura, Sanitas, Compensar, Salud Total
   - 💼 Formularios AFP: Porvenir, Protección, Colfondos, Old Mutual
   - 🛡️ Formularios ARL: Sura, Positiva, Bolívar
   - 👨‍👩‍👧 Formularios CCF: Compensar, Colsubsidio, Cafam

2. **Input de Cédula con Autocompletado**
   - Datalist poblado dinámicamente con usuarios
   - Muestra: "1234567890 - Juan Pérez"
   - Se actualiza al cargar usuarios

3. **Botón "Generar y Descargar PDF"**
   - Tamaño grande (btn-lg)
   - Icono de descarga
   - Loading spinner mientras genera

4. **Alert Informativo**
   - Explica cómo funciona el generador automático
   - Icono de información

#### **Función JavaScript Completa**

```javascript
async function generarFormularioAutomatico(event) {
    event.preventDefault();
    
    const plantilla = document.getElementById('selectPlantillaFormulario').value;
    const cedula = document.getElementById('inputCedulaGenerador').value;
    
    // Validaciones
    if (!plantilla || !cedula) {
        showMessage('⚠️ Por favor seleccione una plantilla e ingrese una cédula', 'warning');
        return;
    }

    // Cambiar estado del botón
    btnGenerar.disabled = true;
    btnGenerar.innerHTML = '<span class="spinner-border...">Generando PDF...';

    // Llamar al endpoint
    const response = await fetch('/api/formularios/generar-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
            plantilla: plantilla,
            cedula: cedula
        })
    });

    // Descargar PDF
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `formulario_${plantilla}_${cedula}_${fecha}.pdf`;
    a.click();

    // Resetear formulario
    document.getElementById('formGeneradorAuto').reset();
}

// Poblar datalist con usuarios
function poblarDatalistUsuarios() {
    const datalist = document.getElementById('usuariosDatalist');
    datalist.innerHTML = '';
    
    usuariosStore.forEach(user => {
        const nombreCompleto = `${user.primerNombre} ${user.primerApellido}`.trim();
        const option = document.createElement('option');
        option.value = user.numeroId;
        option.textContent = `${user.numeroId} - ${nombreCompleto}`;
        datalist.appendChild(option);
    });
}
```

#### **Integración con Carga de Usuarios**

Se modificó la función `cargarUsuarios()` para que también llene el datalist:

```javascript
async function cargarUsuarios() {
    // ... código existente ...
    usuariosStore = data.items || data.usuarios || [];
    
    renderizarTablaUsuarios(usuariosStore);
    poblarDatalistUsuarios(); // ✅ NUEVO: llenar datalist para autocompletado
    
    // ... código existente ...
}
```

### 📡 Endpoint Requerido

```
POST /api/formularios/generar-pdf
Content-Type: application/json

Body:
{
    "plantilla": "eps_sura",
    "cedula": "1234567890"
}

Response: application/pdf (archivo binario)
Headers:
- Content-Type: application/pdf
- Content-Disposition: attachment; filename="formulario_eps_sura_1234567890_YYYY-MM-DD.pdf"

Comportamiento:
1. Buscar usuario por cédula en la base de datos
2. Obtener datos completos del usuario (nombre, dirección, empresa, etc.)
3. Cargar plantilla de formulario correspondiente
4. Rellenar campos del formulario con los datos del usuario
5. Generar PDF y devolverlo
```

### ✨ Características
- ✅ Formulario prominente con borde azul destacado
- ✅ Badge "Automático" con icono de varita mágica
- ✅ Autocompletado funcional con todos los usuarios
- ✅ Select organizado por categorías (optgroups)
- ✅ Alert informativo sobre funcionamiento
- ✅ Loading spinner en botón mientras genera
- ✅ Validaciones de campos requeridos
- ✅ Reseteo automático del formulario después de generar

---

## 🧪 Archivos de Prueba

### `test_configuracion.html`

Página de prueba standalone para la interfaz de configuración:

**Contenido:**
- Formulario completo de parámetros salariales
- Formulario de porcentajes de seguridad social
- Botones de acción (Recargar, Guardar)
- Zona de peligro con botón de backup
- Log de acciones en tiempo real
- Valores de ejemplo pre-cargados

**Funcionalidad:**
- Simula carga de configuración (GET)
- Simula guardado de configuración (PUT)
- Simula descarga de backup con confirmación
- Log de todas las acciones con timestamp
- Alertas de éxito para cada operación

---

## 📊 Resumen de Endpoints Pendientes (Backend)

| Módulo | Endpoint | Método | Body/Params | Respuesta |
|--------|----------|--------|-------------|-----------|
| Configuración | `/api/configuracion` | GET | - | JSON con todos los parámetros |
| Configuración | `/api/configuracion` | PUT | JSON config | `{success, message}` |
| Configuración | `/api/sistema/backup-download` | GET | - | ZIP file (binario) |
| Cartera | `/api/cartera/cobrar/{id}/cuenta-cobro` | GET | - | PDF file (binario) |
| Formularios | `/api/formularios/generar-pdf` | POST | `{plantilla, cedula}` | PDF file (binario) |

---

## ✅ Validaciones Implementadas

### Configuración
- ✅ Campos obligatorios marcados con asterisco
- ✅ Validación de números positivos
- ✅ Confirmación antes de descargar backup
- ✅ Feedback visual al guardar/recargar
- ✅ Manejo de errores con mensajes claros

### Cartera - Tab Cobro a Clientes
- ✅ Botón WhatsApp solo si hay teléfono
- ✅ Limpieza automática de número de teléfono
- ✅ SweetAlert2 con loading mientras genera PDF
- ✅ Formato de moneda colombiano (COP)
- ✅ Detección de fechas vencidas con marcado visual

### Formularios - Generador Automático
- ✅ Validación de plantilla seleccionada
- ✅ Validación de cédula ingresada
- ✅ Autocompletado funcional
- ✅ Loading spinner en botón
- ✅ Reseteo automático después de generar
- ✅ Manejo de errores con mensajes claros

---

## 🎨 Elementos Visuales Destacados

### Configuración
- **Zona de Peligro:** Fondo rojo claro (#fef2f2), borde rojo (#dc2626)
- **Botón Backup:** Gradiente rojo animado con efecto hover y sombra
- **Stat Badges:** Fondo azul claro con borde azul
- **Input Groups:** Prefijos/sufijos con fondo gris claro

### Cartera
- **Filas Vencidas:** Fondo rojo claro (#fff5f5), texto rojo (#dc3545)
- **Badges de Estado:** 
  - Pendiente: amarillo (#ffc107)
  - Vencido: rojo (#dc3545)
  - Pagado: verde (#198754)
  - Parcial: cyan (#0dcaf0)
- **Botones:** Info (azul), Success (verde) con iconos Feather

### Formularios
- **Card Generador:** Borde izquierdo azul de 4px
- **Badge Automático:** Fondo azul claro con icono de varita
- **Alert Info:** Fondo azul claro con icono de información

---

## 🚀 Estado de Implementación

| Funcionalidad | Estado | Archivo | Ubicación |
|---------------|--------|---------|-----------|
| Página Configuración | ✅ Completa | `templates/configuracion.html` | Nueva |
| Cartera - Tab Entidades | ✅ Reestructurado | `templates/pagos/cartera.html` | Líneas ~133-160 |
| Cartera - Tab Clientes | ✅ Completo | `templates/pagos/cartera.html` | Líneas ~162-193 |
| Cartera - Función Cuenta Cobro | ✅ Completa | `templates/pagos/cartera.html` | Líneas ~315-348 |
| Cartera - Función WhatsApp | ✅ Completa | `templates/pagos/cartera.html` | Líneas ~350-375 |
| Formularios - Sección Generador | ✅ Completa | `templates/formularios/index.html` | Líneas ~113-183 |
| Formularios - Función Generar | ✅ Completa | `templates/formularios/index.html` | Líneas ~705-774 |
| Formularios - Datalist | ✅ Integrado | `templates/formularios/index.html` | Líneas ~776-789 |
| Test Configuración | ✅ Creado | `test_configuracion.html` | - |

---

## 📝 Notas Técnicas

### Configuración
- Se usa `feather.replace()` para iconos
- Bootstrap 5.3.3 para componentes
- Valores por defecto según normativa colombiana vigente 2025
- El backup debe incluir: BD, archivos, config, logs

### Cartera
- Se mantiene la estructura de tabs de Bootstrap
- Se usa SweetAlert2 para modales y loading
- El mensaje de WhatsApp incluye el monto formateado
- La cuenta de cobro se descarga directamente como PDF

### Formularios
- El datalist se actualiza automáticamente al cargar usuarios
- Las plantillas están organizadas por categoría (optgroups)
- El PDF se genera en el backend con los datos del usuario
- El formulario se resetea automáticamente después de generar

---

## 🎯 Próximos Pasos

1. **Implementar endpoints backend:**
   - `PUT /api/configuracion`
   - `GET /api/sistema/backup-download`
   - `GET /api/cartera/cobrar/{id}/cuenta-cobro`
   - `POST /api/formularios/generar-pdf`

2. **Backend - Generación de PDF:**
   - Implementar lógica de relleno de plantillas
   - Crear plantillas PDF para cada entidad
   - Sistema de mapping de campos (usuario → formulario)

3. **Backend - Backup:**
   - Script para exportar base de datos
   - Compresión de archivos adjuntos
   - Generación de ZIP con todas las partes

4. **Pruebas de integración:**
   - Verificar que la configuración se guarde correctamente
   - Validar que el backup contenga todos los datos
   - Probar generación de PDF con datos reales
   - Confirmar que WhatsApp abre con el mensaje correcto

---

**Documento generado:** 29 de noviembre de 2025  
**Versión del sistema:** 1.0.0  
**Autor:** Tech Lead Frontend
