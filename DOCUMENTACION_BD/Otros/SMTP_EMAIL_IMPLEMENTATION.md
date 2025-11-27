# Implementación de Servidor SMTP con Flask-Mail

## Resumen
Se ha implementado exitosamente **Flask-Mail** para el envío de correos electrónicos reales a través de servidores SMTP (Gmail, SendGrid, Mailgun, etc.).

## Cambios Realizados

### 1. Dependencias Agregadas
**Archivo:** `requirements.txt`
- Agregado: `Flask-Mail>=0.9.1`

### 2. Configuración de Variables de Entorno
**Archivo:** `.env`

```bash
# --- Email (SMTP) ---
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_de_aplicacion_aqui
MAIL_DEFAULT_SENDER=Sistema Montero <tu_email@gmail.com>
MAIL_MAX_EMAILS=None
MAIL_ASCII_ATTACHMENTS=False
```

### 3. Extensión Flask-Mail Agregada
**Archivo:** `extensions.py`

```python
from flask_mail import Mail

mail = Mail()
```

### 4. Inicialización en app.py
**Archivo:** `app.py`

```python
from extensions import limiter, mail

# Configuración
app.config.from_mapping(
    # ... otras configuraciones
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS", "True").lower() == "true",
    # ... más configuraciones
)

# Inicialización
mail.init_app(app)
```

### 5. Módulo de Utilidades de Email
**Archivo:** `email_utils.py` (NUEVO)

Funciones disponibles:
- `send_notification_email(recipient, subject, body_html)` - Envío genérico
- `send_welcome_email(recipient, nombre, fecha_registro, url_login)` - Email de bienvenida
- `send_password_reset_email(recipient, nombre, reset_token, reset_url)` - Restablecimiento de contraseña
- `send_test_email(recipient)` - Email de prueba

### 6. Integración en Registro de Usuario
**Archivo:** `routes/auth.py`

```python
from email_utils import send_welcome_email

# En el endpoint de registro, después de crear el usuario:
email_sent = send_welcome_email(
    recipient=data.email,
    nombre=data.nombre,
    fecha_registro=datetime.now().strftime("%d/%m/%Y"),
    url_login=request.host_url + "login"
)
```

## Configuración de Gmail (Recomendado para Desarrollo)

### Paso 1: Activar Verificación en 2 Pasos
1. Ve a: https://myaccount.google.com/security
2. En "Cómo accedes a Google", selecciona "Verificación en dos pasos"
3. Sigue los pasos para activarla

### Paso 2: Generar Contraseña de Aplicación
1. Ve a: https://myaccount.google.com/apppasswords
2. En "Seleccionar app", elige "Correo"
3. En "Seleccionar dispositivo", elige "Otro (nombre personalizado)"
4. Escribe "Sistema Montero" y haz clic en "Generar"
5. Copia la contraseña de 16 caracteres generada

### Paso 3: Configurar .env
Edita el archivo `.env` con tus credenciales:

```bash
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=xxxx xxxx xxxx xxxx  # La contraseña de aplicación generada
MAIL_DEFAULT_SENDER=Sistema Montero <tu_email@gmail.com>
```

**⚠️ IMPORTANTE:**
- NO uses tu contraseña normal de Gmail
- USA la contraseña de aplicación de 16 caracteres
- NO compartas este archivo .env

## Otras Opciones de Servidor SMTP

### SendGrid (Recomendado para Producción)
```bash
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=tu_api_key_de_sendgrid
MAIL_DEFAULT_SENDER=noreply@tudominio.com
```

### Mailgun
```bash
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=postmaster@tudominio.mailgun.org
MAIL_PASSWORD=tu_password_de_mailgun
MAIL_DEFAULT_SENDER=noreply@tudominio.com
```

### Outlook/Hotmail
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@outlook.com
MAIL_PASSWORD=tu_password
MAIL_DEFAULT_SENDER=Sistema Montero <tu_email@outlook.com>
```

### Servidor SMTP Propio
```bash
MAIL_SERVER=smtp.tudominio.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@tudominio.com
MAIL_PASSWORD=tu_password
MAIL_DEFAULT_SENDER=Sistema Montero <noreply@tudominio.com>
```

## Pruebas

### Método 1: Script de Prueba Automatizado

1. **Configura tus credenciales** en el archivo `.env`

2. **Ejecuta el script de verificación:**
```bash
cd D:\Mi-App-React\src\dashboard
python test_smtp_config.py
```

El script:
- Verifica que todas las variables estén configuradas
- Inicializa la aplicación Flask
- Te pide un correo de destino
- Envía un correo de prueba
- Muestra el resultado

### Método 2: Prueba con Registro de Usuario

1. **Inicia el servidor Flask:**
```bash
cd D:\Mi-App-React\src\dashboard
python app.py
```

2. **Registra un nuevo usuario** vía API:
```bash
curl -X POST http://127.0.0.1:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Test User",
    "email": "tu_email_de_prueba@gmail.com",
    "password": "Test1234!",
    "telefono": "1234567890",
    "fecha_nacimiento": "1990-01-01"
  }'
```

3. **Verifica** que llegó el correo de bienvenida

### Método 3: Prueba Manual desde Python

```python
from app import create_app
from email_utils import send_test_email

app = create_app()

with app.app_context():
    send_test_email("tu_email@gmail.com")
```

## Plantillas de Email Disponibles

### 1. Email de Bienvenida
- Diseño profesional con estilo HTML/CSS
- Incluye nombre del usuario
- Botón de "Iniciar Sesión"
- Fecha de registro
- Responsive

### 2. Email de Restablecimiento de Contraseña
- Diseño con advertencias de seguridad
- Link con token de restablecimiento
- Expiración del token (1 hora)
- Instrucciones claras

### 3. Email de Prueba
- Simple y directo
- Verifica configuración SMTP
- Mensaje de éxito

## Uso Programático

### Envío de Email Genérico
```python
from email_utils import send_notification_email

html_content = """
<html>
<body>
    <h1>Hola Usuario</h1>
    <p>Este es un correo personalizado.</p>
</body>
</html>
"""

send_notification_email(
    recipient="usuario@ejemplo.com",
    subject="Asunto del Correo",
    body_html=html_content
)
```

### Envío de Email de Bienvenida
```python
from email_utils import send_welcome_email

send_welcome_email(
    recipient="nuevo_usuario@ejemplo.com",
    nombre="Juan Pérez",
    fecha_registro="15/11/2025",
    url_login="http://localhost:5000/login"
)
```

### Envío de Email de Restablecimiento
```python
from email_utils import send_password_reset_email

send_password_reset_email(
    recipient="usuario@ejemplo.com",
    nombre="Juan Pérez",
    reset_token="abc123def456",
    reset_url="http://localhost:5000/reset-password"
)
```

## Solución de Problemas

### Error: "Username and Password not accepted"
**Causa:** Contraseña incorrecta o no usar contraseña de aplicación
**Solución:**
1. Verifica que uses la contraseña de aplicación, NO tu contraseña normal
2. Asegúrate de haber activado la verificación en 2 pasos
3. Genera una nueva contraseña de aplicación

### Error: "Connection timeout"
**Causa:** Puerto bloqueado o servidor SMTP incorrecto
**Solución:**
1. Verifica que el puerto 587 no esté bloqueado por tu firewall
2. Prueba con `MAIL_PORT=465` y `MAIL_USE_SSL=True`
3. Verifica que `MAIL_SERVER` sea correcto

### Error: "SMTPAuthenticationError"
**Causa:** Credenciales inválidas
**Solución:**
1. Verifica MAIL_USERNAME y MAIL_PASSWORD en .env
2. Para Gmail, asegúrate de usar contraseña de aplicación
3. Verifica que no haya espacios extra en las credenciales

### El correo no llega
**Posibles causas:**
1. Revisa la carpeta de spam/correo no deseado
2. Verifica que el email de destino sea válido
3. Revisa los logs de la aplicación para errores
4. Algunos proveedores tienen límites de envío

### Error: "ModuleNotFoundError: No module named 'flask_mail'"
**Solución:**
```bash
pip install Flask-Mail
```

## Límites de Envío

### Gmail (Desarrollo)
- **Límite:** ~500 correos/día
- **Recomendación:** Solo para desarrollo/pruebas

### SendGrid (Producción)
- **Plan Gratuito:** 100 correos/día
- **Plan Básico:** 40,000 correos/mes desde $19.95/mes

### Mailgun (Producción)
- **Plan Gratuito:** 5,000 correos/mes (primeros 3 meses)
- **Plan Flex:** Pay-as-you-go desde $0.80/1000 emails

## Seguridad

### Buenas Prácticas
1. ✅ **NUNCA** subas el archivo `.env` a Git
2. ✅ Usa contraseñas de aplicación, no contraseñas reales
3. ✅ Valida direcciones de correo antes de enviar
4. ✅ Implementa rate limiting para prevenir spam
5. ✅ Usa plantillas para evitar inyección de HTML
6. ✅ Registra todos los envíos en logs
7. ✅ Usa HTTPS en producción

### .gitignore
Asegúrate de que `.env` esté en `.gitignore`:
```
.env
*.env
.env.local
```

## Monitoreo

Los envíos de correo se registran automáticamente en los logs:
```python
# Éxito
logger.info(f"Correo enviado exitosamente a {recipient}: {subject}")

# Error
logger.error(f"Error al enviar correo a {recipient}: {e}")
```

Para ver los logs:
```bash
tail -f logs/app.log
```

## Mejoras Futuras

1. **Envío asíncrono** con Celery para no bloquear las peticiones
2. **Sistema de cola** para reintentos automáticos
3. **Plantillas con Jinja2** desde archivos externos
4. **Tracking de apertura** de correos
5. **Estadísticas de envío** (tasa de apertura, clicks, etc.)
6. **Soporte para adjuntos** (PDFs, imágenes, etc.)
7. **Emails transaccionales** (confirmación de pedido, facturas, etc.)

## Archivos Creados/Modificados

### Archivos Nuevos
- ✅ `email_utils.py` - Funciones de envío de correo
- ✅ `test_smtp_config.py` - Script de prueba
- ✅ `SMTP_EMAIL_IMPLEMENTATION.md` - Esta documentación

### Archivos Modificados
- ✅ `requirements.txt` - Agregado Flask-Mail
- ✅ `.env` - Configuración SMTP
- ✅ `extensions.py` - Objeto Mail
- ✅ `app.py` - Configuración e inicialización
- ✅ `routes/auth.py` - Integración en registro

## Referencias

- [Documentación oficial de Flask-Mail](https://pythonhosted.org/Flask-Mail/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [SendGrid Python Quickstart](https://docs.sendgrid.com/for-developers/sending-email/quickstart-python)
- [Mailgun Documentation](https://documentation.mailgun.com/en/latest/)

---

**Implementado el:** 2025-11-15
**Versión de Flask-Mail:** 0.10.0+
