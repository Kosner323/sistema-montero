# Implementación de Rate Limiting con Flask-Limiter

## Resumen
Se ha implementado exitosamente **Flask-Limiter** para proteger los endpoints de autenticación contra ataques de fuerza bruta.

## Cambios Realizados

### 1. Dependencias Agregadas
**Archivo:** `requirements.txt`
- Agregado: `Flask-Limiter>=3.5.0`

### 2. Nuevo Archivo de Extensiones
**Archivo:** `extensions.py` (nuevo)

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,  # Identifica al cliente por su IP
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # Almacenamiento en memoria
    strategy="fixed-window",
)
```

**Características:**
- `key_func=get_remote_address`: Identifica usuarios por su dirección IP
- `default_limits`: Límites globales para toda la aplicación
- `storage_uri="memory://"`: Almacena límites en memoria (cambiar a Redis en producción)
- `strategy="fixed-window"`: Ventana de tiempo fija para contar solicitudes

### 3. Inicialización en app.py
**Archivo:** `app.py`

```python
from extensions import limiter

# En create_app():
limiter.init_app(app)
```

### 4. Decoradores Aplicados en routes/auth.py
**Archivo:** `routes/auth.py`

#### Endpoint de Login
```python
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # ... código existente
```

**Límite:** 5 solicitudes por minuto por IP

#### Endpoint de Register
```python
@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per hour")
def register():
    # ... código existente
```

**Límite:** 10 solicitudes por hora por IP

## Instalación

### Paso 1: Instalar la dependencia
```bash
cd D:\Mi-App-React\src\dashboard
pip install Flask-Limiter
```

### Paso 2: Verificar la instalación
```bash
pip show Flask-Limiter
```

## Pruebas

### Método 1: Script de Prueba Automatizado

1. **Iniciar el servidor Flask:**
```bash
cd D:\Mi-App-React\src\dashboard
python app.py
```

2. **En otra terminal, ejecutar el script de prueba:**
```bash
cd D:\Mi-App-React\src\dashboard
python test_rate_limiting.py
```

El script probará automáticamente:
- Login: Intentará 7 solicitudes (debería bloquear después de la 5ª)
- Register: Intentará 12 solicitudes (debería bloquear después de la 10ª)

### Método 2: Prueba Manual con curl

#### Probar Login (5 por minuto)
```bash
# Ejecutar este comando 6 veces rápidamente
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test123"}'
```

**Resultado esperado:**
- Solicitudes 1-5: `401 Unauthorized` o `422 Validation Error`
- Solicitud 6: `429 Too Many Requests`

#### Probar Register (10 por hora)
```bash
# Ejecutar este comando 11 veces
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test User",
    "email": "test1@test.com",
    "password": "Test1234!",
    "telefono": "1234567890",
    "fecha_nacimiento": "1990-01-01"
  }'
```

**Resultado esperado:**
- Solicitudes 1-10: `201 Created`, `409 Conflict`, o `422 Validation Error`
- Solicitud 11: `429 Too Many Requests`

### Método 3: Prueba con Postman/Insomnia

1. Configurar una solicitud POST a `http://127.0.0.1:5000/api/login`
2. Headers: `Content-Type: application/json`
3. Body (JSON):
```json
{
  "email": "test@test.com",
  "password": "wrongpassword"
}
```
4. Enviar la solicitud 6 veces rápidamente
5. La 6ª solicitud debería devolver error 429

## Respuesta Esperada al Exceder el Límite

### HTTP Status Code
```
429 Too Many Requests
```

### Headers de Respuesta
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1699999999
Retry-After: 42
```

### Body de Respuesta
```json
{
  "error": "5 per 1 minute"
}
```

## Consideraciones de Producción

### 1. Cambiar a Redis para Almacenamiento
**Archivo:** `extensions.py`

```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379",  # Cambiar a Redis
    strategy="fixed-window",
)
```

**Razón:** El almacenamiento en memoria no funciona con múltiples workers o servidores.

### 2. Configurar Límites por Usuario Autenticado
```python
from flask import g

def get_user_id():
    """Identifica por user_id si está autenticado, sino por IP."""
    return g.get('user_id') or get_remote_address()

limiter = Limiter(
    key_func=get_user_id,
    # ... resto de la configuración
)
```

### 3. Personalizar Mensajes de Error
**Archivo:** `app.py`

```python
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Demasiadas solicitudes. Por favor, intente más tarde.",
        "retry_after": e.description
    }), 429
```

### 4. Whitelist de IPs (Opcional)
```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window",
    exempt_when=lambda: request.remote_addr in ['127.0.0.1', '192.168.1.100']
)
```

## Monitoreo y Logs

Flask-Limiter registra automáticamente eventos de rate limiting. Los logs incluyen:
- IP bloqueada
- Endpoint afectado
- Límite excedido

Para ver los logs:
```bash
tail -f logs/app.log
```

## Ventajas sobre el Rate Limiting Manual Anterior

| Característica | Sistema Anterior | Flask-Limiter |
|---------------|------------------|---------------|
| **Simplicidad** | Código manual complejo | Decorador simple |
| **Persistencia** | Diccionario en memoria | Redis/Memoria |
| **Granularidad** | Por email | Por IP o usuario |
| **Headers HTTP** | No | Sí (X-RateLimit-*) |
| **Testing** | Difícil | Fácil |
| **Escalabilidad** | No (un solo proceso) | Sí (con Redis) |
| **Mantenimiento** | Alto | Bajo |

## Verificación de la Implementación

Para verificar que todo está correcto:

1. ✅ `Flask-Limiter` está en `requirements.txt`
2. ✅ Archivo `extensions.py` creado con configuración de Limiter
3. ✅ `limiter.init_app(app)` en `app.py`
4. ✅ Decorador `@limiter.limit("5 per minute")` en `/api/login`
5. ✅ Decorador `@limiter.limit("10 per hour")` en `/api/register`

## Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'flask_limiter'"
**Solución:**
```bash
pip install Flask-Limiter
```

### Error: "limiter is not defined"
**Causa:** No se importó limiter en routes/auth.py
**Solución:** Agregar `from extensions import limiter`

### Los límites no se aplican
**Causa:** `limiter.init_app(app)` no se llamó
**Solución:** Verificar que está en `create_app()` en app.py

### Error 500 en lugar de 429
**Causa:** Configuración incorrecta de storage_uri
**Solución:** Usar `storage_uri="memory://"` para desarrollo

## Referencias

- [Documentación oficial de Flask-Limiter](https://flask-limiter.readthedocs.io/)
- [GitHub de Flask-Limiter](https://github.com/alisaifee/flask-limiter)
- [Estrategias de Rate Limiting](https://flask-limiter.readthedocs.io/en/stable/strategies.html)

---

**Implementado el:** 2025-11-15
**Versión de Flask-Limiter:** 4.0.0+
