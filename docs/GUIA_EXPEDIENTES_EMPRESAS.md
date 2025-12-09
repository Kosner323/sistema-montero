# GUÍA DE INTEGRACIÓN: Sistema de Expedientes Digitales para Empresas

## 📋 Resumen

Se ha implementado el sistema de gestión de expedientes físicos para empresas, replicando la lógica de usuarios. Ahora cada empresa tiene su propia carpeta física con subcarpetas organizadas y archivos estandarizados.

---

## 🗂️ Estructura de Archivos Generada

### Ruta Base
```
D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\EMPRESAS\
```

### Estructura por Empresa
```
EMPRESAS/
└── 900123456_MiEmpresaSAS/
    ├── datos.txt                    # Información completa de la empresa
    ├── firma_empresa.png            # Firma digital (Base64 → PNG)
    ├── logo.png                     # Logo de la empresa (Base64 → PNG)
    ├── rut.pdf                      # RUT de la empresa
    ├── camara_comercio.pdf          # Certificado de Cámara de Comercio
    ├── cedula_representante.pdf     # Cédula del representante legal
    ├── arl.pdf                      # Certificado ARL
    ├── cuenta_bancaria.pdf          # Certificación bancaria
    ├── carta_autorizacion.pdf       # Carta de autorización
    ├── COTIZACIONES/
    ├── EXTRACTOS BANCARIOS/
    ├── OTROS_ADJUNTOS/
    ├── PAGO DE IMPUESTOS/
    └── USUARIOS Y CONTRASEÑAS/
```

---

## 🛠️ Implementación Backend

### Función Principal: `generar_expediente_empresa()`

**Ubicación:** `routes/empresas.py` (líneas 43-269)

**Parámetros:**
- `empresa_data` (dict): Datos de la empresa (nit, nombre_empresa, etc.)
- `archivos_request` (request.files): Archivos adjuntos (PDFs)

**Retorna:**
```python
{
    "success": bool,
    "files_created": ["datos.txt", "firma_empresa.png", ...],
    "errors": [],
    "path": "D:\\Mi-App-React\\MONTERO_NEGOCIO\\...",
    "rutas_bd": {
        "ruta_carpeta": "MONTERO_TOTAL/EMPRESAS/900123456_...",
        "ruta_firma": "MONTERO_TOTAL/EMPRESAS/.../firma_empresa.png",
        "ruta_logo": "...",
        "ruta_rut": "...",
        "ruta_camara_comercio": "...",
        "ruta_cedula_representante": "...",
        "ruta_arl": "...",
        "ruta_cuenta_bancaria": "...",
        "ruta_carta_autorizacion": "..."
    }
}
```

### Endpoints Modificados

#### 1. **POST /api/empresas** (Crear Empresa)

**Soporta:**
- `application/json` - Datos básicos + Base64 (firma, logo)
- `multipart/form-data` - Datos + archivos PDF

**Ejemplo JSON:**
```javascript
const data = {
    nit: "900123456",
    nombre_empresa: "Mi Empresa SAS",
    direccion: "Calle 123 #45-67",
    telefono: "3001234567",
    email: "contacto@miempresa.com",
    ciudad: "Bogotá",
    representante_legal: "Juan Pérez",
    // Opcionales Base64
    firma_digital: "data:image/png;base64,iVBORw0KGgo...",
    logo_empresa: "data:image/png;base64,iVBORw0KGgo..."
};

fetch('/api/empresas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
});
```

**Ejemplo FormData (con archivos):**
```javascript
const formData = new FormData();
formData.append('nit', '900123456');
formData.append('nombre_empresa', 'Mi Empresa SAS');
formData.append('direccion', 'Calle 123');
formData.append('telefono', '3001234567');

// Archivos PDF
formData.append('rut', archivoRUT); // File object
formData.append('camara_comercio', archivoCamara);
formData.append('cedula_representante', archivoCedula);

fetch('/api/empresas', {
    method: 'POST',
    body: formData // NO enviar Content-Type (se auto-configura)
});
```

**Respuesta exitosa:**
```json
{
    "message": "Empresa creada exitosamente.",
    "id": 42,
    "nit": "900123456",
    "expediente": {
        "archivos_creados": [
            "Estructura de 5 carpetas",
            "datos.txt",
            "firma_empresa.png",
            "logo.png",
            "rut.pdf",
            "camara_comercio.pdf"
        ],
        "errores": [],
        "ruta": "D:\\Mi-App-React\\MONTERO_NEGOCIO\\MONTERO_TOTAL\\EMPRESAS\\900123456_MiEmpresaSAS"
    }
}
```

#### 2. **PUT /api/empresas/<nit>** (Actualizar Empresa)

**Mismo comportamiento que POST**

Actualiza archivos existentes y regenera `datos.txt`.

**Ejemplo:**
```javascript
const formData = new FormData();
formData.append('nombre_empresa', 'Nuevo Nombre SAS');
formData.append('rut', nuevoArchivoRUT); // Reemplaza el anterior

fetch('/api/empresas/900123456', {
    method: 'PUT',
    body: formData
});
```

---

## 🗄️ Actualización de Base de Datos

### Script SQL Requerido

**Ubicación:** `src/dashboard/sql/add_empresas_rutas.sql`

**Ejecutar:**
```powershell
cd D:\Mi-App-React\src\dashboard
sqlite3 data\montero.db < sql\add_empresas_rutas.sql
```

**Columnas agregadas a `empresas`:**
- `ruta_carpeta` TEXT
- `ruta_firma` TEXT
- `ruta_logo` TEXT
- `ruta_rut` TEXT
- `ruta_camara_comercio` TEXT
- `ruta_cedula_representante` TEXT
- `ruta_arl` TEXT
- `ruta_cuenta_bancaria` TEXT
- `ruta_carta_autorizacion` TEXT

---

## 📝 Contenido del Archivo `datos.txt`

```
================================================================================
                     INFORMACIÓN DE LA EMPRESA
================================================================================

DATOS DE IDENTIFICACIÓN
-----------------------
NIT:                 900123456
Razón Social:        Mi Empresa SAS
Tipo de Empresa:     SAS
Sector Económico:    Tecnología
Fecha Constitución:  2020-01-15

DATOS DE UBICACIÓN
------------------
Dirección:           Calle 123 #45-67
Ciudad:              Bogotá
Departamento:        Cundinamarca

DATOS DE CONTACTO
-----------------
Teléfono:            3001234567
Correo Electrónico:  contacto@miempresa.com

REPRESENTANTE LEGAL
-------------------
Nombre:              Juan Pérez
Tipo ID:             CC
Número ID:           1234567890
Teléfono:            3009876543
Correo:              juan.perez@miempresa.com

DATOS LABORALES
---------------
Número de Empleados: 25
Estado:              Activo

DATOS BANCARIOS
---------------
Banco:               Bancolombia
Tipo de Cuenta:      Ahorros
Número de Cuenta:    12345678901

DATOS DE SEGURIDAD SOCIAL
--------------------------
ARL:                 Sura
CCF:                 Compensar

================================================================================
Fecha de Generación: 2025-11-24 14:30:45
================================================================================
```

---

## 🎨 Integración Frontend

### HTML: Formulario con Archivos

```html
<form id="formEmpresa" enctype="multipart/form-data">
    <!-- Datos básicos -->
    <input type="text" name="nit" required>
    <input type="text" name="nombre_empresa" required>
    <input type="text" name="direccion">
    <input type="tel" name="telefono">
    <input type="email" name="email">
    
    <!-- Archivos PDF -->
    <div class="mb-3">
        <label>RUT</label>
        <input type="file" name="rut" accept=".pdf" class="form-control">
    </div>
    
    <div class="mb-3">
        <label>Cámara de Comercio</label>
        <input type="file" name="camara_comercio" accept=".pdf" class="form-control">
    </div>
    
    <div class="mb-3">
        <label>Cédula Representante Legal</label>
        <input type="file" name="cedula_representante" accept=".pdf" class="form-control">
    </div>
    
    <!-- Canvas para firma digital -->
    <canvas id="canvasFirma" width="400" height="200"></canvas>
    <button type="button" onclick="limpiarFirma()">Limpiar</button>
    
    <button type="submit">Guardar Empresa</button>
</form>

<script>
// Configurar canvas de firma
const canvas = document.getElementById('canvasFirma');
const ctx = canvas.getContext('2d');
let dibujando = false;

canvas.addEventListener('mousedown', () => dibujando = true);
canvas.addEventListener('mouseup', () => dibujando = false);
canvas.addEventListener('mousemove', (e) => {
    if (!dibujando) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
});

function limpiarFirma() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

// Enviar formulario
document.getElementById('formEmpresa').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    // Agregar firma como Base64
    const firmaBase64 = canvas.toDataURL('image/png');
    formData.append('firma_digital', firmaBase64);
    
    try {
        const response = await fetch('/api/empresas', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Empresa creada',
                html: `
                    <p><strong>NIT:</strong> ${result.nit}</p>
                    <p><strong>Archivos creados:</strong></p>
                    <ul>
                        ${result.expediente.archivos_creados.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                `
            });
            
            e.target.reset();
            limpiarFirma();
        } else {
            Swal.fire('Error', result.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire('Error', 'Error de conexión', 'error');
    }
});
</script>
```

---

## ✅ Validaciones Implementadas

1. **NIT único:** No permite duplicados
2. **Extensiones de archivo:** Solo `.pdf` para documentos
3. **Tamaño de imágenes:** Máximo 5MB para firma y logo
4. **Nombres de archivo:** Sanitización automática (sin caracteres especiales)
5. **Rutas relativas:** Guardadas desde `MONTERO_NEGOCIO` para portabilidad

---

## 🧪 Pruebas

### Prueba 1: Crear empresa con JSON
```powershell
curl -X POST http://localhost:5000/api/empresas `
  -H "Content-Type: application/json" `
  -d '{
    "nit": "900123456",
    "nombre_empresa": "Test SAS",
    "direccion": "Calle 1",
    "telefono": "3001234567",
    "email": "test@test.com",
    "ciudad": "Bogotá",
    "representante_legal": "Test User"
  }'
```

### Prueba 2: Verificar carpeta creada
```powershell
Get-ChildItem "D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\EMPRESAS\" -Recurse
```

### Prueba 3: Consultar en BD
```sql
SELECT nit, nombre_empresa, ruta_carpeta, ruta_rut 
FROM empresas 
WHERE nit = '900123456';
```

---

## 🔧 Troubleshooting

### Error: "No module named 'base64'"
- **Solución:** Verificar imports en `empresas.py` (línea 7-8)

### Error: "Permission denied" al crear carpeta
- **Solución:** Verificar permisos en `D:\Mi-App-React\MONTERO_NEGOCIO\`

### Error: Archivos PDF no se guardan
- **Solución:** Verificar `enctype="multipart/form-data"` en el form HTML

### Firma Base64 corrupta
- **Solución:** Asegurarse de enviar con prefijo `data:image/png;base64,`

---

## 📚 Referencias

- **Código similar:** `routes/usuarios.py` líneas 30-185
- **Schema BD:** `data/schema.sql`
- **Template form:** `templates/ingresar_empresa.html`

---

## 🎯 Próximos Pasos

1. Ejecutar `add_empresas_rutas.sql` en la base de datos
2. Actualizar formulario HTML con inputs de archivos
3. Implementar canvas de firma digital
4. Agregar vista previa de archivos cargados
5. Implementar botón "Ver Expediente Digital" en la tabla
6. Agregar descarga de `datos.txt` desde el frontend
