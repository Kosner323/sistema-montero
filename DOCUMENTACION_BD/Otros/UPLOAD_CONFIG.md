# CONFIGURACIÓN CENTRALIZADA DE SUBIDA DE ARCHIVOS - SISTEMA MONTERO

## 📁 Estructura de Carpetas

El sistema utiliza una configuración global de uploads definida en `app.py`:

```
static/
└── uploads/
    ├── docs/          # Documentos del gestor documental (admin_routes)
    ├── formularios/   # Archivos CSV/Excel importados (formularios_routes)
    ├── tutelas/       # Soportes PDF de tutelas (tutelas_routes)
    ├── impuestos/     # Comprobantes de impuestos (pago_impuestos)
    └── temp/          # Archivos temporales
```

## ⚙️ Configuración Global (app.py)

```python
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'}
```

## 🔧 Uso en Blueprints

### Opción 1: Usar current_app.config directamente

```python
from flask import current_app
import os

@bp.route('/upload', methods=['POST'])
def upload_file():
    # Obtener carpeta de uploads
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'docs')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Verificar extensión permitida
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    if not filename.rsplit('.', 1)[1].lower() in allowed:
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
    
    # Guardar archivo
    filepath = os.path.join(upload_folder, secure_filename(filename))
    file.save(filepath)
```

### Opción 2: Usar función auxiliar centralizada

```python
from utils import get_upload_folder, allowed_file

@bp.route('/upload', methods=['POST'])
def upload_file():
    if not allowed_file(filename):
        return jsonify({'error': 'Archivo no permitido'}), 400
    
    upload_folder = get_upload_folder('docs')
    filepath = os.path.join(upload_folder, secure_filename(filename))
    file.save(filepath)
```

## 📝 Funciones Auxiliares Disponibles

### En `routes/admin_routes.py`:

- **`allowed_file(filename)`**: Verifica si la extensión está permitida
- **`get_file_hash(file_content)`**: Genera hash SHA-256 para prevenir duplicados

### NOTA IMPORTANTE:

Los módulos que usan estructuras especiales (como `pago_impuestos` con `COMPANY_DATA_FOLDER`) 
mantienen su lógica personalizada pero pueden aprovechar la validación centralizada de 
extensiones mediante `current_app.config['ALLOWED_EXTENSIONS']`.

## 🔒 Límites de Seguridad

- **Tamaño máximo por archivo**: 16MB (configurable en `app.config['MAX_CONTENT_LENGTH']`)
- **Extensiones permitidas**: PDF, JPG, JPEG, PNG, DOC, DOCX, XLS, XLSX, TXT, CSV
- **Sanitización obligatoria**: Usar `secure_filename()` de Werkzeug
- **Validación de rutas**: Prevenir path traversal con `os.path.normpath()`

## 🎯 Ventajas de la Centralización

✅ **Consistencia**: Todos los módulos usan la misma configuración
✅ **Mantenibilidad**: Cambios en un solo lugar (`app.py`)
✅ **Seguridad**: Validaciones uniformes en toda la aplicación
✅ **Escalabilidad**: Fácil migración a almacenamiento externo (S3, Azure Blob)

## 🔄 Migración de Código Legacy

### Antes (configuración local):
```python
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '../static/uploads/docs')
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'png'}
```

### Después (configuración global):
```python
from flask import current_app
upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'docs')
allowed = current_app.config['ALLOWED_EXTENSIONS']
```

---

**Última actualización**: 17 de noviembre de 2025  
**Responsable**: Arquitectura de Sistemas Montero
