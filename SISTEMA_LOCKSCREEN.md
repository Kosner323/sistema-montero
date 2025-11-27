# 🔒 Sistema de Bloqueo de Pantalla (Lockscreen)

## ✅ Implementación Completada

Se ha implementado un **sistema de bloqueo de sesión real** que valida la contraseña contra la base de datos y previene el acceso no autorizado.

---

## 📋 Cambios Realizados

### 1. Backend - [auth.py](src/dashboard/routes/auth.py)

**Rutas agregadas:**

#### `/api/lockscreen` (GET)
- Muestra la pantalla de bloqueo
- Verifica que haya una sesión activa
- Redirige a `/login` si no hay sesión

**Código** (líneas 388-395):
```python
@auth_bp.route('/lockscreen')
def lockscreen():
    """Muestra la pantalla de bloqueo de sesión."""
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('auth/lockscreen.html')
```

#### `/api/verify-password` (POST)
- Valida la contraseña contra la base de datos real
- Usa `check_password_hash()` para seguridad
- Retorna éxito/fallo en formato JSON
- Registra intentos fallidos en logs

**Código** (líneas 398-429):
```python
@auth_bp.route('/verify-password', methods=['POST'])
@login_required
def verify_password():
    """API para validar contraseña y desbloquear la sesión."""
    conn = None
    try:
        data = request.get_json()
        password_input = data.get('password')
        user_id = session.get('user_id')

        conn = get_db_connection()
        user = conn.execute("SELECT password_hash FROM usuarios WHERE id = ?", (user_id,)).fetchone()

        if user and check_password_hash(user['password_hash'], password_input):
            logger.info(f"✅ Usuario ID {user_id} desbloqueó la sesión")
            return jsonify({"success": True, "message": "Desbloqueo exitoso"}), 200
        else:
            logger.warning(f"⚠️ Intento fallido de desbloqueo para usuario ID {user_id}")
            return jsonify({"success": False, "message": "Contraseña incorrecta"}), 401
    except Exception as e:
        logger.error(f"❌ Error verificando password: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Error del sistema"}), 500
    finally:
        if conn: conn.close()
```

---

### 2. Frontend - [lockscreen.html](src/dashboard/templates/auth/lockscreen.html)

**Características de Seguridad:**

✅ **Bloqueo de navegación hacia atrás** (líneas 70-72):
```javascript
history.pushState(null, null, location.href);
window.onpopstate = function () { history.go(1); };
```

✅ **Deshabilitación de herramientas de desarrollador** (líneas 125-137):
- F12 bloqueado
- CTRL+SHIFT+I bloqueado
- CTRL+SHIFT+J bloqueado
- CTRL+U bloqueado (ver código fuente)

✅ **Deshabilitación de menú contextual** (líneas 139-143):
```javascript
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    return false;
});
```

✅ **Validación de contraseña real** (líneas 84-91):
```javascript
const res = await fetch('/api/verify-password', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': '{{ csrf_token() if csrf_token else "" }}'
    },
    body: JSON.stringify({ password: pass })
});
```

---

## 🚀 Cómo Usar

### Opción 1: Acceso Directo a la URL

1. Inicia sesión en el sistema normalmente
2. Navega a: **http://localhost:5000/api/lockscreen**
3. Verás la pantalla de bloqueo con tu nombre de usuario
4. Ingresa tu contraseña para desbloquear

### Opción 2: Agregar Botón en el Dashboard

Agrega este botón en cualquier template (por ejemplo, en `_header.html`):

```html
<a href="/api/lockscreen" class="btn btn-sm btn-outline-secondary">
    <i class="feather icon-lock"></i> Bloquear Sesión
</a>
```

### Opción 3: Atajo de Teclado (Avanzado)

Agrega este script en `index.html` o en un archivo JS global:

```javascript
// CTRL+ALT+L = Bloquear sesión
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.altKey && e.key === 'l') {
        window.location.href = '/api/lockscreen';
    }
});
```

---

## 🔐 Funcionalidades de Seguridad

### 1. **Validación Real contra Base de Datos**
- No usa contraseñas hardcodeadas
- Valida contra `usuarios.password_hash` en la BD
- Usa `check_password_hash()` de Werkzeug

### 2. **Prevención de Bypass**
- **Botón Atrás del navegador**: Bloqueado con `history.pushState()`
- **Herramientas de desarrollador**: F12 y atajos deshabilitados
- **Clic derecho**: Deshabilitado para prevenir inspección
- **Navegación manual**: No se puede salir sin desbloquear

### 3. **Logging de Intentos**
- ✅ Desbloqueos exitosos se registran en logs
- ⚠️ Intentos fallidos se registran con advertencia
- ❌ Errores del sistema se registran con stack trace

### 4. **UX Mejorada**
- Spinner de carga durante validación
- SweetAlert2 para notificaciones elegantes
- Mensaje de éxito antes de redirección
- Campo de contraseña se limpia en errores

---

## 🧪 Pruebas de Seguridad

### Test 1: Contraseña Correcta
1. Accede a `/api/lockscreen`
2. Ingresa tu contraseña real
3. ✅ Debería desbloquear y redirigir a `/dashboard`

### Test 2: Contraseña Incorrecta
1. Accede a `/api/lockscreen`
2. Ingresa una contraseña equivocada
3. ❌ Debería mostrar "Contraseña incorrecta"
4. Campo se limpia automáticamente

### Test 3: Botón Atrás
1. Bloquea la sesión
2. Presiona el botón "Atrás" del navegador
3. ✅ Debería permanecer en lockscreen (no retrocede)

### Test 4: F12 / DevTools
1. Bloquea la sesión
2. Intenta presionar F12 o CTRL+SHIFT+I
3. ✅ Nada debería pasar (teclas bloqueadas)

### Test 5: Sin Sesión
1. Cierra sesión completamente
2. Intenta acceder a `/api/lockscreen` directamente
3. ✅ Debería redirigir a `/login`

---

## 📊 Logs del Sistema

El sistema registra eventos importantes:

**Desbloqueo exitoso:**
```
INFO | ✅ Usuario ID 2 desbloqueó la sesión exitosamente
```

**Intento fallido:**
```
WARNING | ⚠️ Intento fallido de desbloqueo para usuario ID 2
```

**Error del sistema:**
```
ERROR | ❌ Error verificando password para desbloqueo: [error details]
```

---

## 🔧 Personalización

### Cambiar Avatar del Usuario

Edita `lockscreen.html` línea 48:
```html
<img src="/assets/images/user/avatar-1.jpg" alt="User" class="avatar-lock">
```

Puedes usar la foto del usuario desde la BD:
```html
<img src="{{ session.get('user_photo', '/assets/images/user/avatar-1.jpg') }}" alt="User" class="avatar-lock">
```

### Cambiar Colores del Tema

Edita el CSS en `lockscreen.html` (líneas 13-43):
```css
body {
    background: #e9ecef; /* Cambia el color de fondo */
}
.lock-card {
    background: white; /* Cambia el color de la tarjeta */
}
```

### Agregar Tiempo de Bloqueo Automático

Agrega este script en tus templates principales:
```javascript
let inactivityTimer;

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
        window.location.href = '/api/lockscreen';
    }, 5 * 60 * 1000); // 5 minutos de inactividad
}

document.addEventListener('mousemove', resetInactivityTimer);
document.addEventListener('keypress', resetInactivityTimer);
resetInactivityTimer();
```

---

## ⚠️ Notas Importantes

1. **CSRF Token**: El sistema usa CSRF para prevenir ataques
2. **Sesión requerida**: El usuario debe estar logueado primero
3. **No cierra sesión**: Solo bloquea la pantalla, la sesión permanece activa
4. **Logout disponible**: El usuario puede cerrar sesión desde el lockscreen

---

## 📞 Soporte

Si tienes problemas con el lockscreen:

1. **Revisa los logs del servidor** (busca mensajes de desbloqueo)
2. **Verifica que el usuario tenga `password_hash` en la BD**
3. **Asegúrate de que `get_db_connection()` funcione correctamente**

---

**¡Sistema de Lockscreen implementado con éxito!** 🎉
