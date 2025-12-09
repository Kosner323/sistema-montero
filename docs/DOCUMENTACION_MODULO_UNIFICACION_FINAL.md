# MÓDULO DE UNIFICACIÓN - VERSIÓN FINAL
## Sistema Montero - Gestión de Vinculación Laboral

**Fecha:** 23 de noviembre de 2025  
**Desarrollador:** Sistema Montero  
**Versión:** 1.0.0 FINAL

---

## 📋 RESUMEN EJECUTIVO

El módulo de **Unificación** permite gestionar la vinculación laboral de usuarios a empresas de forma individual o masiva, con **trazabilidad completa** de todos los cambios mediante auditoría en base de datos.

### Características Principales

✅ **Vinculación Individual:** Editar datos de usuario y asignar empresa  
✅ **Vinculación Masiva:** Asignar múltiples usuarios a una empresa simultáneamente  
✅ **Historial Completo:** Registro automático de cada cambio con responsable y fecha  
✅ **Visualización Profesional:** Scroll horizontal en tablas extensas  
✅ **Estilo Ejecutivo:** Colores sobrios (gris/blanco/azul institucional)  
✅ **Transacciones ACID:** Garantía de integridad de datos  

---

## 📂 ESTRUCTURA DE ARCHIVOS

### Backend (Python/Flask)

```
src/dashboard/
├── routes/
│   └── unificacion.py          # Blueprint con todas las rutas
├── sql/
│   └── crear_historial_laboral.sql  # Script DDL para tabla de auditoría
└── data/
    └── mi_sistema.db           # Base de datos SQLite
```

### Frontend (Jinja2/Bootstrap)

```
src/dashboard/templates/
├── unificacion/
│   ├── panel.html              # Interfaz principal (vinculación masiva)
│   ├── historial_usuario.html  # Timeline de cambios por usuario
│   └── form_vinculacion.html   # Formulario individual
└── empresas/
    └── editar_empresa.html     # Formulario de edición de empresa
```

---

## 🗄️ ESQUEMA DE BASE DE DATOS

### Tabla: `historial_laboral`

```sql
CREATE TABLE historial_laboral (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    empresa_anterior_nit TEXT,
    empresa_nueva_nit TEXT,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo TEXT,
    responsable_id INTEGER,
    responsable_nombre TEXT,
    tipo_operacion TEXT DEFAULT 'VINCULACION',
    ibc_anterior REAL,
    ibc_nuevo REAL,
    fecha_ingreso_anterior DATE,
    fecha_ingreso_nueva DATE,
    observaciones TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (responsable_id) REFERENCES usuarios(id),
    FOREIGN KEY (empresa_anterior_nit) REFERENCES empresas(nit),
    FOREIGN KEY (empresa_nueva_nit) REFERENCES empresas(nit)
);
```

### Índices Optimizados

- `idx_historial_usuario` → Búsquedas por usuario
- `idx_historial_fecha` → Ordenamiento cronológico
- `idx_historial_empresa_nueva` → Filtros por empresa destino
- `idx_historial_empresa_anterior` → Filtros por empresa origen
- `idx_historial_responsable` → Trazabilidad por responsable

---

## 🚀 ENDPOINTS API

### 1. Panel Principal
**GET** `/api/unificacion/panel`
- Renderiza interfaz de vinculación masiva
- Carga lista completa de usuarios y empresas

### 2. Datos Completos
**GET** `/api/unificacion/master_completo`
```json
{
  "success": true,
  "usuarios": [...],
  "empresas": [...],
  "timestamp": "2025-11-23 15:30:00"
}
```

### 3. Actualizar Vinculación Individual
**PUT** `/api/unificacion/update_vinculacion`
```json
{
  "user_id": 123,
  "primerNombre": "Juan",
  "primerApellido": "Pérez",
  "numeroId": "1234567890",
  "correoElectronico": "juan@email.com",
  "role": "EMPLEADO",
  "estado": "activo",
  "empresa_nit": "900123456-1",
  "motivo": "Cambio de contrato"
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Vinculación actualizada exitosamente (VINCULADO)",
  "usuario": {...}
}
```

**✅ Acción Automática:** Guarda registro en `historial_laboral` si cambió la empresa

### 4. Vinculación Masiva
**POST** `/api/unificacion/vincular_masivo`
```json
{
  "empresa_nit": "900123456-1",
  "usuarios_ids": [1, 5, 10, 15, 20]
}
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Vinculación masiva completada exitosamente",
  "empresa_nit": "900123456-1",
  "empresa_nombre": "Empresa XYZ S.A.S",
  "usuarios_actualizados": 5,
  "registros_historial": 5,
  "usuarios_detalle": [...]
}
```

**✅ Garantías:**
- Transacción ACID (todo o nada)
- Historial guardado para cada usuario
- Rollback automático en caso de error

### 5. Historial de Usuario
**GET** `/api/unificacion/historial_usuario/<user_id>`
- Renderiza timeline con todos los cambios
- Consulta JOIN entre `historial_laboral` y `empresas`
- Muestra: empresa anterior, empresa nueva, fecha, responsable, motivo

### 6. Editar Empresa
**GET** `/api/empresas/editar/<nit>`
- Formulario completo de edición de empresa
- Actualización mediante **PUT** `/api/empresas/<nit>`

---

## 🎨 DISEÑO UI/UX

### Paleta de Colores (Estilo Ejecutivo)

| Color | Código | Uso |
|-------|--------|-----|
| Gris Claro | `#f8f9fa` | Fondos de encabezados |
| Gris Medio | `#dee2e6` | Bordes, separadores |
| Gris Oscuro | `#495057` | Textos secundarios |
| Azul Institucional | `#007bff` | Acciones primarias, enlaces |
| Verde Éxito | `#28a745` | Confirmaciones |
| Texto Principal | `#2c3e50` | Contenido |

### Componentes Bootstrap 5

- **Tablas:** `table-responsive`, `table-bordered`, `table-hover`, `thead-light`
- **Cards:** `card`, `card-header`, `card-body`
- **Botones:** `btn-outline-primary`, `btn-outline-info`, `btn-outline-secondary`
- **Iconos:** Feather Icons (`icon-edit-2`, `icon-clock`, `icon-briefcase`)

### Responsive Design

✅ Todas las tablas tienen scroll horizontal automático  
✅ Diseño adaptable a móviles (breakpoints Bootstrap)  
✅ Grids CSS para formularios (repeat(auto-fit, minmax(280px, 1fr)))

---

## 🔐 SEGURIDAD Y VALIDACIONES

### Backend

1. **Autenticación:** Decorator `@login_required` en todas las rutas
2. **Validación de Roles:** Solo usuarios con rol `USER`, `EMPLEADO`, `AFILIADO`, `OPERATIVO` pueden ser vinculados
3. **Validación de Existencia:** 
   - Verifica que usuario existe antes de actualizar
   - Verifica que empresa existe antes de asignar
4. **Integridad Referencial:** Foreign keys en `historial_laboral`
5. **Transacciones:** Commit/Rollback automático

### Frontend

1. **Validación HTML5:** Campos `required`, tipos `email`, `number`, `date`
2. **Confirmaciones SweetAlert2:** Antes de operaciones masivas
3. **Feedback Visual:** Spinners durante carga, mensajes de éxito/error
4. **Protección XSS:** Templates Jinja2 con auto-escape

---

## 📊 FLUJO DE TRABAJO

### Vinculación Masiva (Panel Principal)

```
1. Usuario accede a /api/unificacion/panel
2. Sistema carga todos los usuarios sin empresa asignada
3. Sistema carga todas las empresas disponibles
4. Usuario selecciona usuarios (checkboxes)
5. Usuario selecciona empresa destino (radio button)
6. Usuario hace clic en "Unificar Selección"
7. Confirmación con SweetAlert2
8. POST a /vincular_masivo con {empresa_nit, usuarios_ids[]}
9. Backend:
   - Obtiene datos anteriores de usuarios
   - Ejecuta UPDATE masivo
   - Inserta registros en historial_laboral
   - Commit transacción
10. Respuesta JSON con usuarios_actualizados
11. Actualización automática de tablas en frontend
12. Mensaje de éxito con contador
```

### Historial de Usuario

```
1. Click en botón "Historial" (icon-clock)
2. Abre nueva pestaña con /historial_usuario/<user_id>
3. Backend ejecuta JOIN:
   - historial_laboral
   - LEFT JOIN empresas (anterior)
   - LEFT JOIN empresas (nueva)
4. Renderiza timeline ordenada por fecha DESC
5. Muestra:
   - Datos actuales del usuario
   - Cada cambio con fecha, empresas, responsable
```

---

## 🧪 TESTING

### Script de Creación de Tabla

```bash
cd d:\Mi-App-React\src\dashboard
python -c "import sqlite3; conn = sqlite3.connect('data/mi_sistema.db'); conn.executescript(open('sql/crear_historial_laboral.sql', 'r', encoding='utf-8').read()); conn.commit(); conn.close(); print('✅ Tabla historial_laboral creada')"
```

### Verificar Estructura

```sql
-- Ver esquema de tabla
SELECT sql FROM sqlite_master WHERE name = 'historial_laboral';

-- Ver índices
SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = 'historial_laboral';

-- Consultar registros
SELECT * FROM vista_historial_laboral_completo ORDER BY fecha_cambio DESC LIMIT 10;
```

---

## 📝 REGISTRO DE CAMBIOS

### v1.0.0 (2025-11-23)

#### ✨ Nuevas Funcionalidades
- Tabla `historial_laboral` con 5 índices optimizados
- Vista `vista_historial_laboral_completo` con JOINs pre-calculados
- Ruta `PUT /update_vinculacion` con registro automático en historial
- Ruta `POST /vincular_masivo` con transacciones ACID y auditoría
- Ruta `GET /historial_usuario/<id>` con timeline completo
- Ruta `GET /empresas/editar/<nit>` con formulario profesional

#### 🎨 Mejoras UI/UX
- Eliminados todos los colores morados/fantasía
- Aplicado estilo ejecutivo (gris/blanco/azul)
- Agregado `table-responsive` a todas las tablas
- Botón "Historial" con icono `icon-clock` en tabla usuarios
- Botón "Editar Empresa" con icono `icon-edit` en tabla empresas
- Timeline profesional en historial_usuario.html

#### 🔧 Refactorización
- Separación de datos anteriores antes de UPDATE
- Determinación automática de tipo_operacion (VINCULACION/CAMBIO/DESVINCULACION)
- Captura de responsable desde `session.get('user_id')`
- Logging detallado con emojis para debugging

---

## 🚦 CHECKLIST DE VALIDACIÓN

- [x] Tabla `historial_laboral` creada en base de datos
- [x] Índices aplicados correctamente
- [x] Vista `vista_historial_laboral_completo` funcional
- [x] PUT `/update_vinculacion` guarda historial
- [x] POST `/vincular_masivo` guarda historial masivo
- [x] GET `/historial_usuario` muestra datos reales
- [x] Scroll horizontal en todas las tablas
- [x] Estilo ejecutivo sin colores fantasía
- [x] Botones "Historial" y "Editar" agregados
- [x] Templates sin errores de sintaxis
- [x] Routes sin errores de importación

---

## 📞 SOPORTE

Para consultas o reportes de bugs, contactar al equipo de desarrollo del Sistema Montero.

**Repositorio:** sistema-montero  
**Branch:** main  
**Autor:** Kosner323

---

## 📄 LICENCIA

Propiedad del Sistema Montero. Uso interno únicamente.

---

**FIN DEL DOCUMENTO**
