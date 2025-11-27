# GUÍA DE MIGRACIÓN A CONFIGURACIÓN CENTRALIZADA DE UPLOADS

## 📋 Estado Actual de los Módulos

| Módulo | Archivo | Estado | Acción Requerida |
|--------|---------|--------|------------------|
| **Gestor Documental** | `admin_routes.py` | ✅ MIGRADO | Ninguna |
| **Impuestos** | `pago_impuestos.py` | 🟡 ESTRUCTURA ESPECIAL | Validar extensiones con config global |
| **Tutelas** | `tutelas.py` | 🟡 USA USER_DATA_FOLDER | Validar extensiones con config global |
| **Formularios** | `formularios_routes.py` | ⚠️ PENDIENTE | Migrar a config global |

---

## ✅ EJEMPLO DE MIGRACIÓN COMPLETADA: `admin_routes.py`

### **ANTES** (Configuración Local):
```python
# routes/admin_routes.py - VERSIÓN ANTIGUA

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(__file__), "..", "static", "uploads", "docs"
)
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "xls", "xlsx", "txt"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/api/documentos/upload', methods=['POST'])
def upload_documento():
    # ...
    filepath = os.path.join(UPLOAD_FOLDER, nombre_interno)
    file.save(filepath)
```

### **DESPUÉS** (Configuración Global):
```python
# routes/admin_routes.py - VERSIÓN MIGRADA

from flask import current_app

def allowed_file(filename):
    """Verifica si la extensión del archivo está permitida"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'txt'})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

@admin_bp.route('/api/documentos/upload', methods=['POST'])
def upload_documento():
    # ...
    # Guardar archivo en disco (usando configuración centralizada)
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'docs')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, nombre_interno)
    file.save(filepath)
```

**Cambios clave:**
1. ❌ Eliminada variable global `UPLOAD_FOLDER`
2. ❌ Eliminada variable global `ALLOWED_EXTENSIONS`
3. ✅ Uso de `current_app.config['UPLOAD_FOLDER']`
4. ✅ Uso de `current_app.config['ALLOWED_EXTENSIONS']`
5. ✅ Creación de subcarpeta específica (`docs`)

---

## 🟡 MÓDULOS CON ESTRUCTURA ESPECIAL

### **Caso: `pago_impuestos.py`** (Usa `COMPANY_DATA_FOLDER`)

Este módulo guarda archivos en una estructura personalizada:
```
MONTERO_TOTAL/
└── EMPRESAS/
    └── {nombre_empresa}/
        └── PAGO DE IMPUESTOS/
            └── {tipo_impuesto}/
                ├── comprobante.pdf
                └── info.txt
```

**Migración Recomendada:**
```python
# pago_impuestos.py - VALIDACIÓN DE EXTENSIONES

from flask import current_app
from utils import is_file_allowed, validate_file_size

@bp_impuestos.route('/registrar', methods=['POST'])
def registrar_pago():
    file = request.files.get('comprobante_pdf')
    
    # ✅ USAR VALIDACIÓN CENTRALIZADA
    if not is_file_allowed(file.filename):
        return jsonify({
            'error': f'Tipo de archivo no permitido. Extensiones válidas: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
        }), 400
    
    # Leer contenido y validar tamaño
    file_content = file.read()
    is_valid, error_msg = validate_file_size(file_content)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    file.seek(0)  # Resetear puntero
    
    # ✅ MANTENER LÓGICA DE CARPETAS PERSONALIZADA
    impuestos_path = _get_company_folder(nit, nombre_empresa, tipo_impuesto)
    filepath = sanitize_and_save_file(file, impuestos_path, pdf_custom_name)
    
    # ... resto del código
```

**Resultado:** Validación centralizada + Estructura de carpetas personalizada ✅

---

### **Caso: `tutelas.py`** (Usa `USER_DATA_FOLDER`)

Estructura personalizada:
```
MONTERO_TOTAL/
└── USUARIOS/
    └── {numero_id}/
        └── TUTELAS/
            └── tutela_{motivo}_{fecha}.pdf
```

**Migración Recomendada:**
```python
# tutelas.py - VALIDACIÓN DE EXTENSIONES

from flask import current_app
from utils import is_file_allowed, validate_file_size

@bp_tutelas.route('/agregar', methods=['POST'])
def agregar_tutela():
    file = request.files.get('soporte_pdf')
    
    # ✅ USAR VALIDACIÓN CENTRALIZADA
    if not is_file_allowed(file.filename):
        return jsonify({
            'error': f'Tipo de archivo no permitido. Solo se permiten archivos PDF'
        }), 400
    
    # Validar tamaño
    file_content = file.read()
    is_valid, error_msg = validate_file_size(file_content)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    file.seek(0)
    
    # ✅ MANTENER LÓGICA DE CARPETAS PERSONALIZADA
    upload_path = _get_user_tutela_folder(numero_id)
    filepath = sanitize_and_save_file(file, upload_path, custom_name)
    
    # ... resto del código
```

---

## 🆕 NUEVO MÓDULO: Uso de `utils.save_uploaded_file()`

Para módulos nuevos, usa la función auxiliar completa:

```python
# ejemplo_routes.py - MÓDULO NUEVO

from flask import Blueprint, request, jsonify
from utils import save_uploaded_file, login_required

bp_ejemplo = Blueprint('ejemplo', __name__)

@bp_ejemplo.route('/upload', methods=['POST'])
@login_required
def upload_archivo():
    """Sube un archivo usando configuración centralizada"""
    
    file = request.files.get('archivo')
    if not file:
        return jsonify({'error': 'No se proporcionó archivo'}), 400
    
    # ✅ USAR FUNCIÓN AUXILIAR COMPLETA
    # Parámetros: (file, subcarpeta, nombre_personalizado_opcional)
    filepath, relative_path, error = save_uploaded_file(file, 'docs', f'doc_{session["user_id"]}.pdf')
    
    if error:
        return jsonify({'error': error}), 400
    
    # Guardar en base de datos
    # ... tu lógica aquí
    
    return jsonify({
        'message': 'Archivo subido exitosamente',
        'path': relative_path,
        'url': f'/assets/uploads/{relative_path}'
    }), 201
```

**Ventajas:**
- ✅ Validación automática de extensión
- ✅ Validación automática de tamaño
- ✅ Creación automática de carpetas
- ✅ Sanitización de nombres
- ✅ Logs automáticos
- ✅ Manejo de errores incluido

---

## 📊 CHECKLIST DE MIGRACIÓN

### Para cada módulo que maneja archivos:

- [ ] **Paso 1:** Identificar variables locales `UPLOAD_FOLDER` y `ALLOWED_EXTENSIONS`
- [ ] **Paso 2:** Reemplazar por `current_app.config['UPLOAD_FOLDER']`
- [ ] **Paso 3:** Actualizar función `allowed_file()` para usar `current_app.config['ALLOWED_EXTENSIONS']`
- [ ] **Paso 4:** Agregar subcarpeta específica del módulo (e.g., `os.path.join(config['UPLOAD_FOLDER'], 'docs')`)
- [ ] **Paso 5:** Asegurar creación de carpeta con `os.makedirs(upload_folder, exist_ok=True)`
- [ ] **Paso 6:** Validar tamaño de archivo usando `current_app.config['MAX_CONTENT_LENGTH']`
- [ ] **Paso 7:** Probar subida de archivos (casos: válido, extensión inválida, tamaño excedido)
- [ ] **Paso 8:** Verificar logs en `MONTERO_NEGOCIO/LOGS_APLICACION/app.log`

---

## 🧪 PRUEBAS DE VALIDACIÓN

### Comando para validar configuración:
```bash
cd d:\Mi-App-React\src\dashboard
python VALIDAR_UPLOAD_CONFIG.py
```

### Pruebas manuales recomendadas:

#### 1. Prueba de Extensión Permitida (PDF):
```bash
# Subir archivo PDF (debe pasar)
curl -X POST http://localhost:5000/api/documentos/upload \
  -F "file=@test.pdf" \
  -H "Cookie: session=..."
```

#### 2. Prueba de Extensión Bloqueada (EXE):
```bash
# Subir archivo EXE (debe rechazarse)
curl -X POST http://localhost:5000/api/documentos/upload \
  -F "file=@virus.exe" \
  -H "Cookie: session=..."
# Respuesta esperada: 400 Bad Request - "Tipo de archivo no permitido"
```

#### 3. Prueba de Tamaño Excedido:
```bash
# Crear archivo de 20MB (excede límite de 16MB)
dd if=/dev/zero of=test_large.pdf bs=1M count=20

# Subir archivo grande (debe rechazarse)
curl -X POST http://localhost:5000/api/documentos/upload \
  -F "file=@test_large.pdf" \
  -H "Cookie: session=..."
# Respuesta esperada: 400 Bad Request - "Archivo demasiado grande"
```

---

## 🎯 BENEFICIOS DE LA CENTRALIZACIÓN

### Antes (Configuración Fragmentada):
```
❌ admin_routes.py: UPLOAD_FOLDER = '../static/uploads/docs', MAX=10MB
❌ formularios.py:  UPLOAD_FOLDER = '../static/uploads/forms', MAX=5MB
❌ tutelas.py:      UPLOAD_FOLDER = USER_DATA_FOLDER, MAX=15MB
```
**Problema:** Inconsistencias, difícil mantenimiento, duplicación de código

### Después (Configuración Centralizada):
```
✅ app.py: UPLOAD_FOLDER = 'static/uploads', MAX=16MB, EXTENSIONS=11 tipos
✅ Todos los módulos usan current_app.config
✅ Funciones auxiliares en utils.py
```
**Beneficio:** Consistencia, un solo punto de cambio, código DRY (Don't Repeat Yourself)

---

## 📞 SOPORTE

Si encuentras problemas durante la migración:
1. Revisar logs en `MONTERO_NEGOCIO/LOGS_APLICACION/app.log`
2. Ejecutar `python VALIDAR_UPLOAD_CONFIG.py`
3. Verificar que `current_app` esté disponible (dentro de request context)
4. Consultar `UPLOAD_CONFIG.md` para referencia completa

---

**Última actualización:** 17 de noviembre de 2025  
**Estado:** Migración en progreso - admin_routes.py completado ✅
