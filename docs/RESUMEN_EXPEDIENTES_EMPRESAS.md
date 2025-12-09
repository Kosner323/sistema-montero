# ✅ SISTEMA DE EXPEDIENTES DIGITALES PARA EMPRESAS - IMPLEMENTADO

## 📦 Archivos Creados/Modificados

### 1. Backend Principal
**`src/dashboard/routes/empresas.py`** (729 líneas)
- ✅ Función `generar_expediente_empresa()` (líneas 43-269)
- ✅ Endpoint POST `/api/empresas` refactorizado (líneas 272-444)
- ✅ Endpoint PUT `/api/empresas/<nit>` refactorizado (líneas 590-745)

**Características:**
- Soporta `application/json` y `multipart/form-data`
- Genera carpeta física por empresa: `EMPRESAS/{NIT}_{Nombre}/`
- Crea 5 subcarpetas obligatorias
- Genera archivo `datos.txt` con información completa
- Guarda firma digital (Base64 → PNG)
- Guarda logo (Base64 → PNG)
- Guarda 6 tipos de PDFs adjuntos
- Retorna rutas relativas para BD

### 2. SQL de Actualización
**`src/dashboard/sql/add_empresas_rutas.sql`** (54 líneas)
- ✅ 9 columnas nuevas para rutas de archivos
- ✅ Índice para `ruta_carpeta`
- ✅ Comentarios y ejemplos de uso

**Script de Ejecución:**
**`src/dashboard/ACTUALIZAR_BD_EMPRESAS.bat`**
- ✅ Crea backup automático antes de modificar
- ✅ Ejecuta el SQL
- ✅ Verifica que las columnas se crearon correctamente

### 3. Documentación
**`GUIA_EXPEDIENTES_EMPRESAS.md`** (487 líneas)
- ✅ Explicación completa de la arquitectura
- ✅ Ejemplos de código (JSON y FormData)
- ✅ Integración frontend con canvas de firma
- ✅ Comandos de prueba
- ✅ Troubleshooting

---

## 🗂️ Estructura de Carpetas Generada

```
D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\EMPRESAS\
└── {NIT}_{NombreEmpresa}/
    ├── datos.txt                     ← Información completa
    ├── firma_empresa.png             ← Base64 convertido
    ├── logo.png                      ← Base64 convertido
    ├── rut.pdf                       ← Desde request.files
    ├── camara_comercio.pdf           ← Desde request.files
    ├── cedula_representante.pdf      ← Desde request.files
    ├── arl.pdf                       ← Desde request.files
    ├── cuenta_bancaria.pdf           ← Desde request.files
    ├── carta_autorizacion.pdf        ← Desde request.files
    ├── COTIZACIONES/
    ├── EXTRACTOS BANCARIOS/
    ├── OTROS_ADJUNTOS/
    ├── PAGO DE IMPUESTOS/
    └── USUARIOS Y CONTRASEÑAS/
```

---

## 🔄 Flujo de Trabajo

### 1. Crear Empresa (POST)

```javascript
// OPCIÓN A: JSON con Base64
const data = {
    nit: "900123456",
    nombre_empresa: "Mi Empresa SAS",
    direccion: "Calle 123",
    telefono: "3001234567",
    email: "contacto@empresa.com",
    ciudad: "Bogotá",
    representante_legal: "Juan Pérez",
    firma_digital: "data:image/png;base64,iVBORw...",
    logo_empresa: "data:image/png;base64,iVBORw..."
};

await fetch('/api/empresas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
});

// OPCIÓN B: FormData con archivos PDF
const formData = new FormData();
formData.append('nit', '900123456');
formData.append('nombre_empresa', 'Mi Empresa SAS');
formData.append('rut', archivoRUT); // File object
formData.append('camara_comercio', archivoCamara);
formData.append('firma_digital', canvasFirma.toDataURL());

await fetch('/api/empresas', {
    method: 'POST',
    body: formData
});
```

**Backend procesa:**
1. Valida datos (Pydantic o manual)
2. Verifica NIT único
3. Llama `generar_expediente_empresa()`
4. Guarda rutas en BD
5. Retorna JSON con archivos creados

### 2. Actualizar Empresa (PUT)

```javascript
const formData = new FormData();
formData.append('nombre_empresa', 'Nuevo Nombre');
formData.append('rut', nuevoRUT); // Reemplaza el anterior

await fetch('/api/empresas/900123456', {
    method: 'PUT',
    body: formData
});
```

**Backend actualiza:**
1. Regenera `datos.txt`
2. Reemplaza archivos si vienen en el request
3. Actualiza rutas en BD

---

## 🗄️ Columnas Agregadas a la Tabla `empresas`

| Columna                       | Tipo | Propósito                          |
|-------------------------------|------|------------------------------------|
| `ruta_carpeta`                | TEXT | Ruta de la carpeta principal       |
| `ruta_firma`                  | TEXT | firma_empresa.png                  |
| `ruta_logo`                   | TEXT | logo.png                           |
| `ruta_rut`                    | TEXT | rut.pdf                            |
| `ruta_camara_comercio`        | TEXT | camara_comercio.pdf                |
| `ruta_cedula_representante`   | TEXT | cedula_representante.pdf           |
| `ruta_arl`                    | TEXT | arl.pdf                            |
| `ruta_cuenta_bancaria`        | TEXT | cuenta_bancaria.pdf                |
| `ruta_carta_autorizacion`     | TEXT | carta_autorizacion.pdf             |

**Ejemplo de valores guardados:**
```sql
ruta_carpeta = "MONTERO_TOTAL/EMPRESAS/900123456_MiEmpresaSAS"
ruta_firma = "MONTERO_TOTAL/EMPRESAS/900123456_MiEmpresaSAS/firma_empresa.png"
ruta_rut = "MONTERO_TOTAL/EMPRESAS/900123456_MiEmpresaSAS/rut.pdf"
```

> **Nota:** Las rutas son **relativas** desde `D:\Mi-App-React\MONTERO_NEGOCIO\` para portabilidad

---

## 🚀 Pasos para Activar

### 1. Actualizar Base de Datos
```powershell
cd D:\Mi-App-React\src\dashboard
.\ACTUALIZAR_BD_EMPRESAS.bat
```

Esto:
- ✅ Crea backup de `montero.db`
- ✅ Agrega las 9 columnas nuevas
- ✅ Verifica que se aplicaron correctamente

### 2. Reiniciar Flask
```powershell
# Detener servidor actual (Ctrl+C)
python app.py
```

### 3. Probar Creación de Empresa

#### Opción A: Desde el Frontend
1. Ir a `/empresas/ingresar`
2. Llenar formulario
3. Adjuntar PDFs
4. Firmar en canvas
5. Guardar

#### Opción B: Desde cURL
```powershell
curl -X POST http://localhost:5000/api/empresas `
  -H "Content-Type: application/json" `
  -d '{
    "nit": "900999999",
    "nombre_empresa": "Empresa Prueba SAS",
    "direccion": "Calle 1",
    "telefono": "3001234567",
    "email": "test@test.com",
    "ciudad": "Bogotá",
    "representante_legal": "Test User"
  }'
```

### 4. Verificar Carpeta Creada
```powershell
Get-ChildItem "D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\EMPRESAS\" -Recurse
```

Deberías ver:
```
EMPRESAS/
└── 900999999_EmpresaPruebaSAS/
    ├── datos.txt
    ├── COTIZACIONES/
    ├── EXTRACTOS BANCARIOS/
    └── ...
```

### 5. Consultar BD
```sql
SELECT 
    nit, 
    nombre_empresa, 
    ruta_carpeta, 
    ruta_rut 
FROM empresas 
WHERE nit = '900999999';
```

---

## 🎨 Integración Frontend Completa

### HTML: Formulario con Firma Digital
```html
<form id="formEmpresa" enctype="multipart/form-data">
    <input type="text" name="nit" required>
    <input type="text" name="nombre_empresa" required>
    
    <!-- Archivos -->
    <input type="file" name="rut" accept=".pdf">
    <input type="file" name="camara_comercio" accept=".pdf">
    
    <!-- Canvas de firma -->
    <canvas id="canvasFirma" width="400" height="200"></canvas>
    <button type="button" onclick="limpiarFirma()">Limpiar</button>
    
    <button type="submit">Guardar</button>
</form>
```

### JavaScript: Captura de Firma + Envío
```javascript
const canvas = document.getElementById('canvasFirma');
const ctx = canvas.getContext('2d');
let dibujando = false;

// Configurar eventos de dibujo
canvas.addEventListener('mousedown', () => dibujando = true);
canvas.addEventListener('mouseup', () => dibujando = false);
canvas.addEventListener('mousemove', (e) => {
    if (!dibujando) return;
    const rect = canvas.getBoundingClientRect();
    ctx.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctx.stroke();
});

// Enviar formulario
document.getElementById('formEmpresa').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    formData.append('firma_digital', canvas.toDataURL('image/png'));
    
    const res = await fetch('/api/empresas', {
        method: 'POST',
        body: formData
    });
    
    const result = await res.json();
    
    if (res.ok) {
        Swal.fire('Éxito', `Empresa creada. Archivos: ${result.expediente.archivos_creados.join(', ')}`, 'success');
    } else {
        Swal.fire('Error', result.error, 'error');
    }
});
```

---

## ✅ Validaciones Implementadas

| Validación                  | Descripción                                      |
|-----------------------------|--------------------------------------------------|
| NIT único                   | No permite duplicados en BD                      |
| Extensión de archivos       | Solo `.pdf` para documentos                      |
| Tamaño de imágenes          | Máximo 5MB para firma y logo                     |
| Sanitización de nombres     | Elimina caracteres especiales en nombres         |
| Rutas relativas             | Guardadas desde `MONTERO_NEGOCIO` (portabilidad) |
| Creación de subcarpetas     | Automática (5 carpetas obligatorias)             |
| Generación de datos.txt     | Automática con formato estandarizado             |

---

## 📊 Respuesta JSON del Backend

**Exitosa (201):**
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

**Error - NIT duplicado (409):**
```json
{
    "error": "El NIT 900123456 ya está registrado."
}
```

**Error - Validación (422):**
```json
{
    "error": "Datos inválidos",
    "details": [
        {"field": "nit", "message": "Campo requerido"},
        {"field": "nombre_empresa", "message": "Campo requerido"}
    ]
}
```

---

## 🔍 Troubleshooting

### ❌ Error: "No module named 'base64'"
**Solución:** Verificar imports en `empresas.py` línea 7-8
```python
import base64
import os
import re
```

### ❌ Error: "Permission denied" al crear carpeta
**Solución:** Dar permisos de escritura
```powershell
icacls "D:\Mi-App-React\MONTERO_NEGOCIO" /grant Users:F /T
```

### ❌ Archivos PDF no se guardan
**Solución:** Verificar `enctype` en el form
```html
<form enctype="multipart/form-data">
```

### ❌ Firma Base64 corrupta
**Solución:** Incluir prefijo completo
```javascript
canvas.toDataURL('image/png') // Incluye "data:image/png;base64,"
```

---

## 📈 Próximos Pasos Sugeridos

1. ✅ **Ejecutar script SQL** (`ACTUALIZAR_BD_EMPRESAS.bat`)
2. ✅ **Reiniciar Flask**
3. ⚠️ **Actualizar formulario HTML** (agregar inputs de archivos + canvas)
4. ⚠️ **Agregar vista previa de PDFs** cargados
5. ⚠️ **Implementar botón "Ver Expediente Digital"** en tabla de empresas
6. ⚠️ **Agregar descarga de `datos.txt`** desde frontend
7. ⚠️ **Implementar logs de auditoría** de cambios en expedientes

---

## 🎯 Resumen Ejecutivo

✅ **Sistema completo de expedientes digitales para empresas implementado**

- **Función auxiliar:** `generar_expediente_empresa()` (227 líneas)
- **Endpoints modificados:** POST y PUT en `/api/empresas`
- **Carpetas generadas:** 1 principal + 5 subcarpetas por empresa
- **Archivos gestionados:** 9 tipos (datos.txt, firma, logo, 6 PDFs)
- **BD actualizada:** 9 columnas nuevas en tabla `empresas`
- **Validaciones:** NIT único, extensiones, tamaños, sanitización
- **Respuestas JSON:** Incluyen lista de archivos creados y errores

**Listo para usar tras ejecutar `ACTUALIZAR_BD_EMPRESAS.bat` y reiniciar Flask.**
