# 📋 GUÍA DE ACTUALIZACIÓN DE RUTAS FLASK

**Fecha:** 2025-01-24
**Proyecto:** Sistema Montero
**Propósito:** Actualizar `render_template()` después de reorganizar la carpeta `templates/`

---

## ✅ ARCHIVOS MOVIDOS EXITOSAMENTE

### 1. **Módulo AUTH (Autenticación)**
| Archivo Original | Nueva Ubicación | Actualizar en |
|------------------|-----------------|---------------|
| `ingresoportal.html` | `auth/login.html` | `routes/auth.py` |
| `registroportal.html` | `auth/register.html` | `routes/auth.py` |

**Cambios necesarios en `routes/auth.py`:**
```python
# ANTES:
return render_template('ingresoportal.html')
return render_template('registroportal.html')

# DESPUÉS:
return render_template('auth/login.html')
return render_template('auth/register.html')
```

---

### 2. **Módulo MAIN (Dashboard Principal)**
| Archivo Original | Nueva Ubicación | Actualizar en |
|------------------|-----------------|---------------|
| `index.html` | `main/dashboard.html` | `routes/index.py` o `app.py` |
| `configuracion.html` | `main/configuracion.html` | `routes/user_settings.py` o similar |

**Cambios necesarios:**
```python
# ANTES:
return render_template('index.html')
return render_template('configuracion.html')

# DESPUÉS:
return render_template('main/dashboard.html')
return render_template('main/configuracion.html')
```

---

### 3. **Módulo FORMULARIOS**
| Archivo Original | Nueva Ubicación | Actualizar en |
|------------------|-----------------|---------------|
| `formularios.html` | `formularios/index.html` | `routes/formularios.py` |

**Cambios necesarios en `routes/formularios.py`:**
```python
# ANTES:
return render_template('formularios.html')

# DESPUÉS:
return render_template('formularios/index.html')
```

---

### 4. **Módulo UNIFICACIÓN**
| Archivo Original | Nueva Ubicación | Actualizar en |
|------------------|-----------------|---------------|
| `unificacion.html` | `unificacion/index.html` | `routes/unificacion.py` |

**Cambios necesarios en `routes/unificacion.py`:**
```python
# ANTES:
return render_template('unificacion.html')

# DESPUÉS:
return render_template('unificacion/index.html')
```

---

## ⚠️ ARCHIVOS QUE NO SE ENCONTRARON (Ya estaban movidos o no existen)

Los siguientes archivos no se encontraron en la raíz de `templates/`, probablemente porque ya estaban organizados en carpetas o porque los nombres no coinciden exactamente:

- `usuarios-y-contrasenas.html` ❓
- `informacion-empleados.html` ❓
- `pagos.html` ❓
- `tabla.html` ❓
- `pago-impuestos.html` ❓
- `pago-planillas.html` ❓
- `enviar-planillas.html` ❓
- `cotizaciones.html` ❓
- `ingresar_empresa.html` ❓
- `tutelas.html` ❓
- `incapacidades.html` ❓
- `depuraciones.html` ❓
- `novedades.html` ❓
- `novedades-modals.html` ❓

**ACCIÓN REQUERIDA:** Verifica manualmente en qué carpetas están estos archivos actualmente.

---

## 📂 ESTRUCTURA DE CARPETAS ACTUAL

```
templates/
├── auth/
│   ├── login.html ✅ (antes: ingresoportal.html)
│   ├── register.html ✅ (antes: registroportal.html)
│   └── lockscreen.html (ya existía)
│
├── main/
│   ├── dashboard.html ✅ (antes: index.html)
│   └── configuracion.html ✅ (antes: configuracion.html)
│
├── formularios/
│   └── index.html ✅ (antes: formularios.html)
│
├── unificacion/
│   ├── index.html ✅ (antes: unificacion.html)
│   ├── panel.html (ya existía)
│   ├── historial_usuario.html (ya existía)
│   └── ... (otros archivos ya existentes)
│
├── usuarios/
│   └── (pendiente de mover archivos)
│
├── pagos/
│   ├── cartera.html (ya existía)
│   ├── impuestos.html (ya existía)
│   └── ... (otros archivos ya existentes)
│
├── empresas/
│   └── editar_empresa.html (ya existía)
│
├── juridico/
│   └── (pendiente de mover archivos)
│
├── novedades/
│   └── crear.html (ya existía)
│
├── marketing/
│   ├── redes.html (ya existía)
│   ├── campanas.html (ya existía)
│   └── ... (otros archivos ya existentes)
│
├── copiloto/
│   └── arl.html (ya existía)
│
├── errors/
│   ├── 404.html (ya existía)
│   └── 500.html (ya existía)
│
└── ... (archivos parciales como _sidebar.html, _header.html, _footer.html)
```

---

## 🔍 CÓMO ENCONTRAR TODAS LAS RUTAS A ACTUALIZAR

### 1. Buscar en todos los archivos Python:

```bash
# En la raíz del proyecto:
grep -r "render_template" src/dashboard/routes/ src/dashboard/app.py
```

### 2. Buscar referencias específicas:

```bash
# Buscar uso de 'index.html':
grep -r "render_template.*index\.html" src/dashboard/

# Buscar uso de 'ingresoportal.html':
grep -r "render_template.*ingresoportal\.html" src/dashboard/

# Buscar uso de 'formularios.html':
grep -r "render_template.*formularios\.html" src/dashboard/

# Buscar uso de 'unificacion.html':
grep -r "render_template.*unificacion\.html" src/dashboard/
```

### 3. Archivos Python a revisar:

- ✅ `src/dashboard/app.py`
- ✅ `src/dashboard/routes/auth.py`
- ✅ `src/dashboard/routes/index.py` (o `main.py`)
- ✅ `src/dashboard/routes/formularios.py`
- ✅ `src/dashboard/routes/unificacion.py`
- ✅ `src/dashboard/routes/user_settings.py` (para configuración)
- ✅ Cualquier otro archivo en `routes/`

---

## 📝 CHECKLIST DE ACTUALIZACIÓN

- [ ] **1. Auth Routes** - Actualizar `ingresoportal.html` → `auth/login.html`
- [ ] **2. Auth Routes** - Actualizar `registroportal.html` → `auth/register.html`
- [ ] **3. Main Routes** - Actualizar `index.html` → `main/dashboard.html`
- [ ] **4. Settings Routes** - Actualizar `configuracion.html` → `main/configuracion.html`
- [ ] **5. Formularios Routes** - Actualizar `formularios.html` → `formularios/index.html`
- [ ] **6. Unificación Routes** - Actualizar `unificacion.html` → `unificacion/index.html`
- [ ] **7. Probar** - Verificar que todas las rutas funcionen correctamente
- [ ] **8. Git Commit** - Hacer commit de los cambios

---

## ⚙️ COMANDOS ÚTILES PARA ACTUALIZACIÓN MASIVA

Si tienes muchas referencias, puedes usar `sed` o buscar/reemplazar en VS Code:

### VS Code (Buscar y Reemplazar en Archivos):
1. Presiona `Ctrl + Shift + H` (Windows/Linux) o `Cmd + Shift + H` (Mac)
2. Busca: `render_template\('ingresoportal\.html'\)`
3. Reemplaza: `render_template('auth/login.html')`
4. Haz clic en "Reemplazar Todo"

Repite para cada archivo movido.

---

## 🚨 IMPORTANTE: PRUEBA DESPUÉS DE CADA CAMBIO

Después de actualizar las rutas, prueba cada módulo:

```bash
# Iniciar el servidor
python src/dashboard/app.py

# Probar las rutas:
http://localhost:5000/login           # Debe cargar auth/login.html
http://localhost:5000/register        # Debe cargar auth/register.html
http://localhost:5000/dashboard       # Debe cargar main/dashboard.html
http://localhost:5000/configuracion   # Debe cargar main/configuracion.html
http://localhost:5000/formularios     # Debe cargar formularios/index.html
http://localhost:5000/unificacion     # Debe cargar unificacion/index.html
```

---

## 📌 NOTAS ADICIONALES

- **Archivos parciales** como `_sidebar.html`, `_header.html`, `_footer.html` se mantienen en la raíz de `templates/` (esto es correcto para Flask).
- **Archivos de error** (`errors/404.html`, `errors/500.html`) ya están organizados correctamente.
- **Carpetas existentes** como `marketing/`, `pagos/`, `copiloto/` ya tenían archivos organizados.

---

¿Necesitas ayuda con alguna actualización específica? ¡Déjame saber! 🚀
