# ✅ Implementación de Acciones de Botones

## 📋 Resumen de Implementación

Se implementaron **3 acciones críticas** en los módulos de Planillas, Envío de Planillas y Cotizaciones, cumpliendo con los requisitos del Tech Lead.

---

## 1️⃣ Botón "Retirar" - Planillas (`planillas.html`)

### 🎯 Objetivo
Permitir retirar empleados cambiando su estado a "Inactivo" mediante una simple confirmación.

### 🔧 Cambios Realizados

#### **Botón en la Tabla** (Línea ~353)
```html
<button type="button" class="btn btn-sm btn-danger" 
        onclick="retirarEmpleado('${user.numeroId}', '${user.primerNombre || ''} ${user.segundoNombre || ''} ${user.primerApellido || ''} ${user.segundoApellido || ''}')" 
        title="Retirar Empleado">
    <i data-feather="user-x" class="w-4 h-4"></i> Retirar
</button>
```

#### **Función JavaScript** (Línea ~524)
```javascript
async function retirarEmpleado(empleadoId, empleadoNombre) {
    // Confirmar acción
    const confirmacion = confirm(`¿Estás seguro de retirar al empleado ${empleadoNombre}?\n\nEsto cambiará su estado a Inactivo.\n\nEsta acción no se puede deshacer.`);
    if (!confirmacion) return;
    
    try {
        showMessage('⏳ Procesando retiro del empleado...', 'info');
        
        // Llamada a la API
        const response = await fetch(`${API_URL}/usuarios/${empleadoId}/estado`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ estado: 'Inactivo' })
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showMessage(`✅ ${result.message || 'Empleado retirado exitosamente.'}`, 'success');
            await filterAndRender(); // Recargar tabla
        } else {
            throw new Error(result.error || 'Error al procesar el retiro');
        }
        
    } catch (error) {
        console.error('❌ Error al retirar empleado:', error);
        showMessage(`❌ Error: ${error.message}`, 'danger');
    }
}
```

### 📡 Endpoint Requerido (Backend)
```
PUT /api/usuarios/{id}/estado
Content-Type: application/json

Body:
{
    "estado": "Inactivo"
}

Response:
{
    "success": true,
    "message": "Usuario actualizado exitosamente"
}
```

### ✨ Características
- ✅ Confirmación de seguridad antes de ejecutar
- ✅ Feedback visual con mensajes de estado
- ✅ Recarga automática de la tabla después del retiro
- ✅ Icono rojo `user-x` para indicar acción crítica
- ✅ Eliminado modal complejo (ahora es una acción directa)

---

## 2️⃣ Botón "WhatsApp" - Enviar Planillas (`enviar_planillas.html`)

### 🎯 Objetivo
Abrir WhatsApp Web con el número del cliente y un mensaje predefinido para facilitar el envío de planillas.

### 🔧 Cambios Realizados

#### **Botón en la Tabla** (Línea ~230)
```html
${envio.telefono ? 
    `<button class="btn btn-sm btn-success ms-1 btn-whatsapp" 
             data-telefono="${envio.telefono}" 
             title="Enviar por WhatsApp">
         <i data-feather="message-circle" class="w-4 h-4 mr-1"></i> WhatsApp
     </button>` 
    : ''}
```

#### **Event Listener** (Línea ~328)
```javascript
tbody.addEventListener('click', function(e) {
    const target = e.target.closest('.btn-enviar');
    if (target) {
        enviarPlanilla(target);
    }
    
    // Nuevo: Event listener para WhatsApp
    const whatsappBtn = e.target.closest('.btn-whatsapp');
    if (whatsappBtn) {
        enviarPorWhatsApp(whatsappBtn);
    }
});
```

#### **Función de WhatsApp** (Línea ~338)
```javascript
function enviarPorWhatsApp(button) {
    const telefono = button.dataset.telefono;
    if (!telefono) {
        alert('⚠️ No hay número de teléfono registrado para este cliente.');
        return;
    }
    
    // Limpiar el número (quitar espacios, guiones, etc.)
    const telefonoLimpio = telefono.replace(/\D/g, '');
    
    // Mensaje predefinido (personalizable)
    const mensaje = 'Hola, adjunto su planilla/comprobante de pago de seguridad social.';
    
    // Generar URL de WhatsApp (con código de país 57 para Colombia)
    const whatsappURL = `https://wa.me/57${telefonoLimpio}?text=${encodeURIComponent(mensaje)}`;
    
    // Abrir en nueva pestaña
    window.open(whatsappURL, '_blank');
    
    console.log('📱 Abriendo WhatsApp Web para:', telefono);
}
```

### ✨ Características
- ✅ Botón verde con icono de mensaje
- ✅ Solo aparece si el cliente tiene teléfono registrado
- ✅ Limpieza automática del número (remueve caracteres no numéricos)
- ✅ Código de país 57 (Colombia) automático
- ✅ Mensaje predefinido (personalizable)
- ✅ Abre WhatsApp Web en nueva pestaña
- ✅ Validación de existencia de número

### 🌐 URL Generada
```
https://wa.me/573001234567?text=Hola%2C%20adjunto%20su%20planilla%2Fcomprobante%20de%20pago%20de%20seguridad%20social.
```

---

## 3️⃣ Botón "Aceptar Oferta" - Cotizaciones (`cotizaciones.html`)

### 🎯 Objetivo
Permitir aceptar cotizaciones pendientes con un solo clic, cambiando su estado a "Aceptada".

### 🔧 Cambios Realizados

#### **Botón Condicional en la Tabla** (Línea ~374)
```javascript
const isPendiente = cot.estado === 'Pendiente';

const row = `
    <tr>
        <td>${cotId}</td>
        <td>${cot.cliente}</td>
        <td>${cot.servicio}</td>
        <td>${montoFormateado}</td>
        <td>${cot.fecha_creacion}</td>
        <td><span class="badge ${badgeClass}">${cot.estado}</span></td>
        <td>
            <button class="btn btn-sm btn-info" 
                    onclick="alert('Funcionalidad de descarga de PDF no implementada.')" 
                    title="Descargar PDF">
                <i data-feather="download" class="w-4 h-4"></i>
            </button>
            ${isPendiente ? 
                `<button class="btn btn-sm btn-success ms-1" 
                         onclick="aceptarCotizacion(${cotId}, '${cot.cliente}')" 
                         title="Aceptar Oferta">
                     <i data-feather="check-circle" class="w-4 h-4 mr-1"></i> Aceptar Oferta
                 </button>` 
                : ''}
        </td>
    </tr>
`;
```

#### **Función JavaScript** (Línea ~437)
```javascript
window.aceptarCotizacion = async function(cotizacionId, clienteNombre) {
    // Confirmar acción
    const confirmacion = confirm(`¿Estás seguro de aceptar la cotización para ${clienteNombre}?\n\nEsto cambiará el estado a "Aceptada".`);
    if (!confirmacion) return;
    
    try {
        showMessage('⏳ Aceptando cotización...', 'info');
        
        // Enviar petición al backend
        const response = await fetch(`${API_URL}/cotizaciones/${cotizacionId}/aceptar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (response.ok && result.success) {
            showMessage(`✅ ${result.message || 'Cotización aceptada exitosamente.'}`, 'success');
            await loadCotizaciones(); // Recargar tabla
        } else {
            throw new Error(result.error || 'Error al aceptar cotización');
        }
        
    } catch (error) {
        console.error('❌ Error al aceptar cotización:', error);
        showMessage(`❌ Error: ${error.message}`, 'danger');
    }
}
```

### 📡 Endpoint Requerido (Backend)
```
POST /api/cotizaciones/{id}/aceptar
Content-Type: application/json

Response:
{
    "success": true,
    "message": "Cotización aceptada exitosamente",
    "estado": "Aceptada"
}
```

### ✨ Características
- ✅ Botón verde con icono `check-circle`
- ✅ Solo visible en cotizaciones con estado "Pendiente"
- ✅ Confirmación antes de ejecutar
- ✅ Feedback visual con mensajes
- ✅ Recarga automática de tabla después de aceptar
- ✅ Validación de respuesta del servidor

---

## 🧪 Archivo de Prueba

Se creó `test_botones_acciones.html` para validar el renderizado y funcionalidad de los 3 botones:

### Contenido del Test
1. **Tabla de Empleados** con 2 registros simulados y botón "Retirar"
2. **Tabla de Planillas** con 3 registros (con/sin teléfono) y botón "WhatsApp"
3. **Tabla de Cotizaciones** con 4 registros en diferentes estados (Pendiente, Aceptada, Rechazada)
4. **Log de Acciones** que registra todas las interacciones

### Cómo usar el test
1. Abrir `test_botones_acciones.html` en el navegador
2. Hacer clic en cada botón para ver la simulación
3. Verificar el log de acciones en la parte inferior
4. Comprobar que los modales de confirmación aparecen correctamente

---

## 📊 Resumen de Endpoints Pendientes (Backend)

| Módulo | Endpoint | Método | Body | Descripción |
|--------|----------|--------|------|-------------|
| Planillas | `/api/usuarios/{id}/estado` | PUT | `{ "estado": "Inactivo" }` | Cambiar estado de empleado |
| Cotizaciones | `/api/cotizaciones/{id}/aceptar` | POST | - | Aceptar cotización pendiente |

**Nota:** El botón de WhatsApp no requiere endpoint backend, solo abre WhatsApp Web en el navegador.

---

## ✅ Validaciones Implementadas

### Botón Retirar
- ✅ Confirmación obligatoria antes de ejecutar
- ✅ Validación de respuesta del servidor
- ✅ Manejo de errores con mensajes claros
- ✅ Recarga automática de tabla

### Botón WhatsApp
- ✅ Verificación de existencia de número de teléfono
- ✅ Limpieza de caracteres no numéricos
- ✅ Codificación correcta del mensaje (URL encoding)
- ✅ Apertura en nueva pestaña

### Botón Aceptar Oferta
- ✅ Solo visible para cotizaciones pendientes
- ✅ Confirmación obligatoria
- ✅ Validación de respuesta del servidor
- ✅ Recarga automática de tabla

---

## 🎨 Elementos Visuales

### Iconos Utilizados (Feather Icons)
- `user-x` - Retirar empleado (rojo)
- `message-circle` - WhatsApp (verde)
- `check-circle` - Aceptar oferta (verde)
- `download` - Descargar PDF (azul)

### Clases de Bootstrap
- `btn-danger` - Botón de retiro (rojo)
- `btn-success` - Botones de WhatsApp y Aceptar (verde)
- `btn-info` - Botón de descarga (azul)
- `badge bg-warning` - Estado pendiente (amarillo)
- `badge bg-success` - Estado aceptada/enviada (verde)
- `badge bg-danger` - Estado rechazada (rojo)

---

## 🚀 Estado de Implementación

| Funcionalidad | Estado | Archivo | Líneas |
|---------------|--------|---------|--------|
| Botón Retirar | ✅ Completo | `planillas.html` | 353, 524-557 |
| Botón WhatsApp | ✅ Completo | `enviar_planillas.html` | 230, 328-358 |
| Botón Aceptar Oferta | ✅ Completo | `cotizaciones.html` | 374, 437-469 |
| Archivo de Test | ✅ Creado | `test_botones_acciones.html` | - |

---

## 📝 Notas Técnicas

### Eliminaciones
- ❌ Removido modal complejo de retiro de empleado (líneas 217-275 de planillas.html)
- ❌ Removida función `abrirModalRetiro()` y `confirmarRetiro()` con validación de archivos

### Simplificaciones
- ✅ Retiro ahora es una acción directa (sin modal)
- ✅ WhatsApp abre directamente sin confirmaciones adicionales
- ✅ Aceptar oferta con confirmación simple

### Consideraciones de Seguridad
- ⚠️ Los endpoints PUT/POST deben validar permisos de usuario en el backend
- ⚠️ El cambio de estado a "Inactivo" debería ser auditable (log de cambios)
- ⚠️ La aceptación de cotizaciones debería registrar quién la aceptó y cuándo

---

## 🎯 Próximos Pasos

1. **Implementar endpoints backend:**
   - `PUT /api/usuarios/{id}/estado`
   - `POST /api/cotizaciones/{id}/aceptar`

2. **Pruebas de integración:**
   - Validar que los empleados retirados no aparezcan en reportes activos
   - Verificar que las cotizaciones aceptadas actualicen su estado en la BD
   - Confirmar que el link de WhatsApp se genera correctamente

3. **Mejoras opcionales:**
   - Permitir personalizar el mensaje de WhatsApp desde la interfaz
   - Agregar confirmación visual cuando se abre WhatsApp
   - Implementar sistema de auditoría para retiros y aceptaciones

---

**Documento generado:** 29 de noviembre de 2025  
**Versión del sistema:** 1.0.0  
**Autor:** Tech Lead Frontend
