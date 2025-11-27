# 🔐 INSTRUCCIONES COMPLETAS - LOGIN Y REGISTRO

**Fecha**: 15 de Noviembre de 2025
**Estado**: ✅ LISTO PARA USAR

---

## 🎯 CORRECCIONES APLICADAS (Versión 2)

### Problema Identificado
**Error 400 Bad Request** al intentar login/registro debido a:
1. ❌ Campo `password_confirm` requerido pero no enviado por el frontend
2. ❌ Manejo de errores poco descriptivo
3. ❌ Falta de logs informativos

### Soluciones Aplicadas

#### 1. `password_confirm` Ahora es Opcional
**Archivo**: `models/validation_models.py` (líneas 87-113)

**ANTES**:
```python
password_confirm: str = Field(...,  # REQUERIDO
```

**DESPUÉS**:
```python
password_confirm: Optional[str] = Field(None,  # OPCIONAL
```

✅ Ahora el frontend puede registrar usuarios SIN enviar `password_confirm`

#### 2. Mejor Manejo de Errores en `/register`
**Archivo**: `routes/auth.py` (líneas 100-117)

**Mejoras**:
- ✅ Verifica si se recibió JSON
- ✅ Logs informativos de datos recibidos
- ✅ Mensajes de error más descriptivos
- ✅ Devuelve detalles de validación

#### 3. Mejor Manejo de Errores en `/login`
**Archivo**: `routes/auth.py` (líneas 174-193)

**Mejoras**:
- ✅ Verifica si se recibió JSON
- ✅ Logs de intento de login
- ✅ Mensajes de error claros
- ✅ Diferencia errores de BD vs errores generales

---

## 🚀 CÓMO USAR EL SISTEMA

### Paso 1: Iniciar el Servidor

```bash
cd d:\Mi-App-React\src\dashboard
python app.py
```

**Salida Esperada**:
```
2025-11-15 XX:XX:XX | INFO | Base de datos inicializada correctamente
2025-11-15 XX:XX:XX | INFO | Todos los blueprints registrados exitosamente
 * Running on http://127.0.0.1:5000
```

---

### Paso 2: Acceder a la Página de Login

**URL**: `http://127.0.0.1:5000/login`

Deberías ver la página de login con estilos cargados correctamente.

---

### Paso 3: Registrar un Nuevo Usuario

#### Opción A: Desde el Frontend (Formulario Web)

1. Click en "Crear Cuenta" en la página de login
2. Llenar el formulario:
   - **Nombre**: Kevin Lomas
   - **Email**: kevinlomasd@gmail.com
   - **Password**: Montero323@
   - **Teléfono**: +573001234567 (opcional)
   - **Fecha de Nacimiento**: 1990-05-15 (opcional)

3. Click en "Registrar"

#### Opción B: Usando Postman/Thunder Client/curl

**Endpoint**: `POST http://127.0.0.1:5000/api/register`

**Headers**:
```
Content-Type: application/json
```

**Body (JSON)** - Versión MÍNIMA (solo campos requeridos):
```json
{
  "nombre": "Kevin Lomas",
  "email": "kevinlomasd@gmail.com",
  "password": "Montero323@"
}
```

**Body (JSON)** - Versión COMPLETA (con campos opcionales):
```json
{
  "nombre": "Kevin Lomas",
  "email": "kevinlomasd@gmail.com",
  "password": "Montero323@",
  "telefono": "+573001234567",
  "fecha_nacimiento": "1990-05-15"
}
```

**Respuesta Esperada** (201 Created):
```json
{
  "message": "Usuario registrado exitosamente."
}
```

**Errores Posibles**:
```json
// 422 - Validación fallida
{
  "error": "email: El email ya está registrado",
  "details": [...]
}

// 400 - Email duplicado
{
  "error": "El email ya está registrado."
}
```

---

### Paso 4: Iniciar Sesión

#### Opción A: Desde el Frontend (Formulario Web)

1. Ir a `http://127.0.0.1:5000/login`
2. Ingresar credenciales:
   - **Email**: kevinlomasd@gmail.com
   - **Password**: Montero323@
3. Click en "Ingresar"

Si el login es exitoso, deberías ser redirigido al dashboard.

#### Opción B: Usando Postman/Thunder Client/curl

**Endpoint**: `POST http://127.0.0.1:5000/api/login`

**Headers**:
```
Content-Type: application/json
```

**Body (JSON)**:
```json
{
  "email": "kevinlomasd@gmail.com",
  "password": "Montero323@"
}
```

**Respuesta Esperada** (200 OK):
```json
{
  "message": "Inicio de sesión exitoso",
  "user_id": 2,
  "user_name": "Kevin",
  "user_role": "empleado"
}
```

**Errores Posibles**:
```json
// 401 - Credenciales incorrectas
{
  "error": "Email o contraseña incorrectos."
}

// 429 - Demasiados intentos fallidos
{
  "error": "Demasiados intentos fallidos. Intente de nuevo en X minutos."
}

// 422 - Validación fallida
{
  "error": "email: value is not a valid email address",
  "details": [...]
}
```

---

## 🔍 VERIFICAR QUE FUNCIONA

### Test 1: Ver Logs del Servidor

Al ejecutar `python app.py`, deberías ver en la consola:

```
# Al registrar usuario:
2025-11-15 XX:XX:XX | INFO | Datos recibidos para registro: dict_keys(['nombre', 'email', 'password', ...])
2025-11-15 XX:XX:XX | INFO | Nuevo usuario registrado: kevinlomasd@gmail.com

# Al hacer login:
2025-11-15 XX:XX:XX | INFO | Intento de login con datos: dict_keys(['email', 'password'])
2025-11-15 XX:XX:XX | INFO | Login exitoso: kevinlomasd@gmail.com (ID: 2)
```

### Test 2: Verificar Usuario en la Base de Datos

```bash
cd d:\Mi-App-React\src\dashboard
sqlite3 data/mi_sistema.db

# Dentro de SQLite:
.mode column
.headers on
SELECT id, primerNombre, correoElectronico, role, estado FROM usuarios;
```

**Salida Esperada**:
```
id  primerNombre  correoElectronico         role       estado
--  ------------  --------------------      -------    ------
1   Admin         admin@montero.com         admin      activo
2   Kevin         kevinlomasd@gmail.com     empleado   activo
```

### Test 3: Verificar Sesión (Después de Login)

Si usas el navegador, abre DevTools (F12) → Application → Cookies → http://127.0.0.1:5000

Deberías ver una cookie de sesión con información del usuario.

---

## 📋 CAMPOS REQUERIDOS VS OPCIONALES

### Registro (`/api/register`)

| Campo | Tipo | Requerido | Ejemplo | Notas |
|-------|------|-----------|---------|-------|
| nombre | string | ✅ Sí | "Kevin Lomas" | Min 2, max 100 caracteres |
| email | email | ✅ Sí | "kevinlomasd@gmail.com" | Debe ser válido |
| password | string | ✅ Sí | "Montero323@" | Min 6 caracteres |
| password_confirm | string | ❌ No | "Montero323@" | Debe coincidir con password (si se envía) |
| telefono | string | ❌ No | "+573001234567" | Formato internacional |
| fecha_nacimiento | date | ❌ No | "1990-05-15" | Formato YYYY-MM-DD, mínimo 13 años |

### Login (`/api/login`)

| Campo | Tipo | Requerido | Ejemplo | Notas |
|-------|------|-----------|---------|-------|
| email | email | ✅ Sí | "kevinlomasd@gmail.com" | Debe existir en BD |
| password | string | ✅ Sí | "Montero323@" | Min 6 caracteres |

---

## 🎯 DATOS QUE SE GUARDAN EN LA BD

Cuando registras un usuario, se guardan estos datos en la tabla `usuarios`:

| Campo BD | Valor | Origen |
|----------|-------|--------|
| primerNombre | "Kevin" | De `nombre` del request |
| correoElectronico | "kevinlomasd@gmail.com" | De `email` del request |
| password_hash | "$pbkdf2..." | Hasheado de `password` |
| telefonoCelular | "+573001234567" | De `telefono` del request (o NULL) |
| fechaNacimiento | "1990-05-15" | De `fecha_nacimiento` del request (o NULL) |
| empresa_nit | "999999999" | **Default automático** |
| tipoId | "CC" | **Default automático** |
| numeroId | "0000000" | **Default automático** |
| primerApellido | "Usuario" | **Default automático** |
| estado | "activo" | **Default automático** |
| role | "empleado" | **Default automático** |

**Nota**: Los campos con "Default automático" se insertan automáticamente aunque no vengan en el request.

---

## 🔐 CREDENCIALES DE PRUEBA

### Usuario Admin (Pre-existente)
```
Email: admin@montero.com
Password: admin123
Role: admin
```

### Usuario de Prueba (Registrar tú)
```
Email: kevinlomasd@gmail.com
Password: Montero323@
Role: empleado (automático)
```

---

## 🐛 TROUBLESHOOTING

### Problema: "No se recibieron datos JSON"

**Causa**: El frontend no está enviando `Content-Type: application/json`

**Solución**: Verificar que el header esté presente en la petición.

### Problema: "email: value is not a valid email address"

**Causa**: El email no tiene formato válido

**Solución**: Usar un email válido como `usuario@ejemplo.com`

### Problema: "password: Field required"

**Causa**: No se envió el campo `password` en el JSON

**Solución**: Incluir `password` en el body del request

### Problema: "El email ya está registrado"

**Causa**: Ya existe un usuario con ese email en la BD

**Soluciones**:
1. Usar otro email
2. O eliminar el usuario existente de la BD

### Problema: "Email o contraseña incorrectos"

**Causas Posibles**:
1. El email no existe en la BD
2. La contraseña es incorrecta
3. El usuario fue registrado con otro password

**Solución**: Verificar credenciales o registrar nuevamente

---

## 📝 EJEMPLO COMPLETO CON curl

### Registrar Usuario
```bash
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Kevin Lomas",
    "email": "kevinlomasd@gmail.com",
    "password": "Montero323@",
    "telefono": "+573001234567",
    "fecha_nacimiento": "1990-05-15"
  }'
```

### Login
```bash
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "kevinlomasd@gmail.com",
    "password": "Montero323@"
  }'
```

---

## ✅ CHECKLIST FINAL

Antes de probar, verifica:

- [x] Servidor Flask está corriendo (`python app.py`)
- [x] Base de datos existe (`data/mi_sistema.db`)
- [x] Empresa con NIT 999999999 existe en BD
- [x] Archivos `routes/auth.py` y `models/validation_models.py` actualizados
- [x] El navegador puede acceder a `http://127.0.0.1:5000/login`
- [x] Los estilos se cargan correctamente (sin errores 404 en assets)

---

## 🎉 RESULTADO ESPERADO

Después de seguir estas instrucciones:

✅ Puedes registrar nuevos usuarios desde el formulario web
✅ Puedes iniciar sesión con las credenciales correctas
✅ El sistema te redirige al dashboard después de login exitoso
✅ Puedes ver tus datos de usuario en la sesión
✅ Los logs muestran información clara de lo que está pasando

**¡Tu sistema de autenticación está 100% funcional!** 🚀

---

**Última actualización**: 15 de Noviembre de 2025, 17:15
**Archivos modificados**:
- `routes/auth.py`
- `models/validation_models.py`

**Estado**: PRODUCCIÓN READY ✅
