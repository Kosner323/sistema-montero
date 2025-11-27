# 🔒 Sistema de Bloqueo de Pantalla (Lock Screen)

## 📋 Resumen

Sistema de seguridad implementado para bloquear la pantalla del usuario sin cerrar sesión. Permite pausar el trabajo temporalmente manteniendo la sesión activa.

---

## ✅ Componentes Implementados

### **1. Backend - Endpoint de Verificación**

**Archivo:** `src/dashboard/routes/auth.py`

**Endpoint:** `POST /api/verify-password`

**Características:**
- ✅ Decorador `@login_required` (requiere sesión activa)
- ✅ Verificación con bcrypt (`check_password_hash`)
- ✅ Logging detallado (intentos exitosos y fallidos)
- ✅ Manejo robusto de errores (BD, sesión, etc.)
- ✅ Respuestas JSON estándar (`success`, `message`)

**Request:**
```json
{
    "password": "contraseña_usuario"
}
```

**Response (Éxito):**
```json
{
    "success": true,
    "message": "Desbloqueo exitoso"
}
```

**Response (Error):**
```json
{
    "success": false,
    "message": "Contraseña incorrecta"
}
```

---

### **2. Frontend - UI del Lock Screen**

**Archivo:** `templates/_header.html`

**Ubicación:** Modal overlay full-screen con z-index 2000

**Elementos HTML:**
```html
<div id="lockScreenOverlay">
    <div class="lock-screen-modal">
        <i data-feather="lock"></i>
        <h4>Sesión Bloqueada</h4>
        <p>Ingresa tu contraseña para volver</p>
        
        <div id="lockscreenError"></div>
        <input type="password" id="lockscreen-password" />
        <button id="unlockButton" onclick="desbloquearPantalla()">
            Desbloquear
        </button>
    </div>
</div>
```

**JavaScript Implementado:**

1. **lockScreen()** - Bloquea la pantalla
2. **desbloquearPantalla()** - Verifica contraseña y desbloquea
3. **mostrarErrorLockscreen()** - Muestra mensajes de error
4. **Persistencia con sessionStorage** - Mantiene bloqueo en recarga

---

## 🎯 Flujo de Funcionamiento

```
Usuario hace clic en "Bloquear Pantalla"
            ↓
    lockScreen() se ejecuta
            ↓
    Overlay se muestra (z-index 2000)
    sessionStorage.setItem('isLocked', 'true')
            ↓
    Usuario ingresa contraseña
            ↓
    desbloquearPantalla() se ejecuta
            ↓
    POST /api/verify-password
            ↓
    Backend verifica con check_password_hash()
            ↓
┌───────────┴───────────┐
│                       │
✅ Correcta           ❌ Incorrecta
│                       │
Overlay se oculta       Mensaje de error
sessionStorage.clear    Input se limpia
Console.log success     Focus en input
```

---

## 🔐 Seguridad Implementada

### **Backend:**
- ✅ `@login_required` - Solo usuarios autenticados
- ✅ Verificación con bcrypt (hash seguro)
- ✅ Logging de intentos fallidos
- ✅ Validación de sesión activa (`user_id` en session)
- ✅ Manejo de usuarios sin password_hash
- ✅ Protección contra SQLite injection (parametrización)

### **Frontend:**
- ✅ Overlay bloquea toda la interfaz (z-index 2000)
- ✅ Input de tipo `password` (oculta caracteres)
- ✅ Persistencia con `sessionStorage` (no `localStorage`)
- ✅ Auto-limpieza de input después de error
- ✅ Deshabilita botón mientras verifica
- ✅ Enter key para enviar formulario

---

## 🚀 Uso del Sistema

### **Bloquear Pantalla:**

**Opción 1: Menú del header**
```
Usuario → Click en avatar → "Bloquear Pantalla"
```

**Opción 2: JavaScript manual**
```javascript
lockScreen();
```

### **Desbloquear Pantalla:**

**Opción 1: Enter key**
```
1. Ingresar contraseña
2. Presionar Enter
```

**Opción 2: Click en botón**
```
1. Ingresar contraseña
2. Click en "Desbloquear"
```

---

## 📊 Estados del Sistema

| Estado | Descripción | sessionStorage | Overlay Visible |
|--------|-------------|----------------|-----------------|
| **Normal** | Pantalla desbloqueada | - | ❌ No |
| **Bloqueado** | Pantalla bloqueada | `isLocked: 'true'` | ✅ Sí |
| **Verificando** | Validando contraseña | `isLocked: 'true'` | ✅ Sí (botón disabled) |
| **Error** | Contraseña incorrecta | `isLocked: 'true'` | ✅ Sí (mensaje rojo) |

---

## 🧪 Pruebas de Funcionamiento

### **Test 1: Bloqueo básico**
```
1. Hacer login en el sistema
2. Click en avatar → "Bloquear Pantalla"
3. ✅ Verificar que overlay aparece
4. ✅ Verificar que input de contraseña tiene focus
5. ✅ Verificar que sessionStorage.isLocked = 'true'
```

### **Test 2: Desbloqueo exitoso**
```
1. Bloquear pantalla
2. Ingresar contraseña CORRECTA
3. Presionar Enter o Click en "Desbloquear"
4. ✅ Verificar que overlay desaparece
5. ✅ Verificar que sessionStorage.isLocked se eliminó
6. ✅ Verificar log en consola: "🔓 Pantalla desbloqueada"
```

### **Test 3: Contraseña incorrecta**
```
1. Bloquear pantalla
2. Ingresar contraseña INCORRECTA
3. Presionar Enter
4. ✅ Verificar mensaje de error rojo
5. ✅ Verificar que input se limpió
6. ✅ Verificar que overlay sigue visible
7. ✅ Verificar focus en input
```

### **Test 4: Persistencia en recarga**
```
1. Bloquear pantalla
2. Recargar página (F5)
3. ✅ Verificar que overlay aparece automáticamente
4. ✅ Verificar que sessionStorage mantiene 'isLocked'
```

### **Test 5: Validación de campo vacío**
```
1. Bloquear pantalla
2. Dejar input vacío
3. Presionar Enter
4. ✅ Verificar mensaje: "Por favor ingresa tu contraseña"
5. ✅ Verificar que NO se hace fetch al backend
```

### **Test 6: Error de conexión**
```
1. Bloquear pantalla
2. Detener servidor Flask
3. Ingresar contraseña
4. Presionar Enter
5. ✅ Verificar mensaje: "Error de conexión. Intenta de nuevo."
6. ✅ Verificar error en console.log
```

---

## 🛠️ Troubleshooting

### **Problema: Overlay no aparece**
**Solución:**
```javascript
// Verificar en consola del navegador:
document.getElementById('lockScreenOverlay')
// Debe retornar el elemento, no null

// Verificar clase hidden:
const overlay = document.getElementById('lockScreenOverlay');
overlay.classList.contains('hidden'); // Debe ser true cuando está oculto
```

### **Problema: Contraseña correcta pero no desbloquea**
**Solución:**
```bash
# 1. Verificar logs del servidor Flask:
grep "Desbloqueo exitoso" logs/app.log

# 2. Verificar respuesta del endpoint:
# En consola del navegador (Network tab):
# POST /api/verify-password
# Response: {"success": true, "message": "Desbloqueo exitoso"}

# 3. Verificar password_hash en BD:
sqlite3 data/mi_sistema.db
SELECT id, primerNombre, password_hash FROM usuarios WHERE id = 1;
# Debe retornar un hash bcrypt válido
```

### **Problema: sessionStorage no persiste**
**Solución:**
```javascript
// Navegador en modo incógnito no persiste sessionStorage
// Verificar en consola:
sessionStorage.getItem('isLocked'); // Debe retornar 'true' cuando bloqueado

// Limpiar manualmente si está corrupto:
sessionStorage.clear();
```

---

## 📝 Logs del Sistema

### **Logs de Éxito:**
```
2025-11-19 10:30:45 | INFO | auth.verify_password:xxx | ✅ Desbloqueo exitoso - User: 1 (Pedro Pérez)
```

### **Logs de Error:**
```
2025-11-19 10:31:12 | WARNING | auth.verify_password:xxx | ❌ Intento fallido de desbloqueo - User: 1
```

### **Logs de Sesión:**
```
2025-11-19 10:32:00 | ERROR | auth.verify_password:xxx | Intento de verificación sin user_id en sesión
```

---

## 🔄 Endpoints Disponibles

| Endpoint | Método | Descripción | Auth Requerido |
|----------|--------|-------------|----------------|
| `/api/verify-password` | POST | Verifica contraseña para lockscreen | ✅ Sí |
| `/api/user/verify_password` | POST | Alternativa en user_settings.py | ✅ Sí |

**Nota:** Ambos endpoints funcionan. `/api/verify-password` está en auth.py (recomendado para consistencia).

---

## 🎨 Personalización

### **Cambiar Tiempo de Auto-Ocultación del Error:**
```javascript
// En _header.html - función mostrarErrorLockscreen()
setTimeout(() => {
    errorDiv.style.display = 'none';
}, 5000); // Cambiar 5000 a los milisegundos deseados (5s = 5000ms)
```

### **Agregar Intentos Máximos:**
```javascript
// En _header.html - variable global
let intentosFallidos = 0;

// En desbloquearPantalla() - después de error
intentosFallidos++;
if (intentosFallidos >= 3) {
    mostrarErrorLockscreen('Demasiados intentos. Cerrando sesión...');
    setTimeout(() => {
        window.location.href = '/api/logout';
    }, 2000);
}
```

### **Agregar Bloqueo Automático por Inactividad:**
```javascript
// En _header.html - al final del script
let inactivityTimer;
const INACTIVITY_TIME = 5 * 60 * 1000; // 5 minutos

function resetInactivityTimer() {
    clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
        lockScreen();
    }, INACTIVITY_TIME);
}

// Eventos que resetean el timer
['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
    document.addEventListener(event, resetInactivityTimer, true);
});

// Iniciar timer
resetInactivityTimer();
```

---

## 📚 Compatibilidad

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile (iOS Safari, Chrome Android)

**Características usadas:**
- Fetch API
- Async/await
- sessionStorage
- CSS Flexbox
- Tailwind CSS classes

---

## 🔗 Referencias

- [Werkzeug Security](https://werkzeug.palletsprojects.com/en/2.3.x/utils/#module-werkzeug.security)
- [Flask Session Management](https://flask.palletsprojects.com/en/2.3.x/api/#sessions)
- [MDN - Fetch API](https://developer.mozilla.org/es/docs/Web/API/Fetch_API)
- [sessionStorage](https://developer.mozilla.org/es/docs/Web/API/Window/sessionStorage)

---

**Autor:** Sistema Montero - Equipo de Desarrollo  
**Fecha:** 19 de Noviembre de 2025  
**Versión:** 1.0.0  
**Estado:** ✅ Producción
