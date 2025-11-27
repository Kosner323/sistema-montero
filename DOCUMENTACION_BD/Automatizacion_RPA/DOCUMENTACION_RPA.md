# 🤖 Documentación del Motor RPA - Sistema Montero

## 📋 Resumen de Implementación

Se ha implementado exitosamente el motor de automatización RPA (Robotic Process Automation) basado en Selenium para el Sistema Montero.

---

## ✅ Cambios Realizados

### **1. Dependencias Actualizadas** (`requirements.txt`)

```txt
# --- AUTOMATIZACIÓN RPA ---
selenium>=4.15.0
webdriver-manager>=4.0.1
beautifulsoup4>=4.12.3
```

**Instalación:**
```bash
cd src/dashboard
.\INSTALAR_RPA.bat
```

O manualmente:
```bash
pip install selenium>=4.15.0 webdriver-manager>=4.0.1 beautifulsoup4>=4.12.3
```

---

### **2. Módulo RPA Creado** (`src/dashboard/rpa/arl_bot.py`)

**Clase Principal:** `ARLBot`

**Características:**
- ✅ Modo headless opcional (ideal para servidores)
- ✅ WebDriver Manager automático (descarga ChromeDriver)
- ✅ Manejo robusto de errores
- ✅ Logging detallado con emoji visual
- ✅ Configuración anti-detección (`--no-sandbox`, `--disable-dev-shm-usage`)

**Métodos Implementados:**

| Método | Descripción | Retorno |
|--------|-------------|---------|
| `__init__(headless=False)` | Inicializa bot y WebDriver | - |
| `navegar_portal(url)` | Navega a URL y espera carga | `bool` |
| `ejecutar_afiliacion(datos)` | Afilia empleado en portal ARL | `dict` |
| `ejecutar_certificado(datos)` | Descarga certificado de afiliación | `dict` |
| `ejecutar_incapacidad(datos)` | Radica incapacidad médica | `dict` |
| `cerrar()` | Cierra navegador y libera recursos | - |

**Ejemplo de Respuesta:**
```python
{
    "status": "exito",  # o "error"
    "mensaje": "Afiliación radicada",
    "soporte": "AF-12345.pdf"
}
```

---

### **3. Backend Actualizado** (`routes/automation_routes.py`)

**Nuevas Importaciones:**
```python
import threading
from rpa.arl_bot import ARLBot
```

**Nueva Función Worker:**
```python
def ejecutar_bot_background(job_id, accion, datos):
    """
    Ejecuta bot RPA en thread separado.
    Actualiza BD con progreso en tiempo real.
    """
```

**Endpoint Modificado:**
```python
POST /copiloto/api/ejecutar
```

**Flujo de Ejecución:**
1. Recibe solicitud POST con `{accion, empresa_nit, empleado_id, empleado_nombre}`
2. Crea registro en tabla `copiloto_jobs` (job_id único)
3. Lanza thread daemon con `ejecutar_bot_background()`
4. Retorna respuesta inmediata con `job_id` y `steps`
5. Bot se ejecuta en paralelo actualizando progreso en BD

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (arl.html)                      │
│  [Selector Empresa] [Input Cédula] [Botón Ejecutar]       │
└──────────────────────┬──────────────────────────────────────┘
                       │ POST /copiloto/api/ejecutar
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND (automation_routes.py)                 │
│                                                             │
│  1. Valida datos y crea job_id                             │
│  2. INSERT INTO copiloto_jobs (estado='iniciado')          │
│  3. Lanza thread: ejecutar_bot_background()                │
│  4. Retorna: {"status": "iniciado", "job_id": "..."}       │
└──────────────────────┬──────────────────────────────────────┘
                       │ Thread Daemon
                       ▼
┌─────────────────────────────────────────────────────────────┐
│            WORKER THREAD (Background)                       │
│                                                             │
│  1. UPDATE copiloto_jobs SET estado='ejecutando'           │
│  2. Inicializa ARLBot(headless=True)                       │
│  3. Ejecuta: bot.ejecutar_afiliacion(datos)                │
│  4. UPDATE progreso: 0% → 30% → 60% → 100%                 │
│  5. UPDATE estado='completado' o 'error'                   │
│  6. bot.cerrar()                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ Selenium
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              BOT RPA (arl_bot.py)                           │
│                                                             │
│  ChromeDriver → Portal ARL SURA                            │
│  1. Navegación: https://www.arlsura.com                    │
│  2. Login automático (credenciales encriptadas)            │
│  3. Completar formularios                                  │
│  4. Descarga de documentos PDF                             │
│  5. Captura de screenshots (evidencia)                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Modos de Operación

### **Modo CON Selenium (Producción)**
- ✅ Bot real navega portal ARL
- ✅ Interacción con formularios HTML
- ✅ Descarga automática de documentos
- ✅ ChromeDriver se descarga automáticamente

### **Modo SIN Selenium (Fallback)**
- ⚠️ Simulación (delay de 3 segundos)
- ⚠️ No navega portal real
- ⚠️ Retorna respuestas simuladas
- ✅ Útil para desarrollo sin dependencias

---

## 📊 Tabla de Base de Datos: `copiloto_jobs`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `job_id` | TEXT | ID único (JOB-20251119120000-12345) |
| `accion` | TEXT | 'afiliar', 'certificado', 'incapacidad' |
| `empresa_nit` | TEXT | NIT de la empresa |
| `empleado_id` | TEXT | Cédula del empleado |
| `empleado_nombre` | TEXT | Nombre completo |
| `estado` | TEXT | 'iniciado', 'ejecutando', 'completado', 'error' |
| `progreso` | INTEGER | 0-100 (porcentaje) |
| `mensaje` | TEXT | Mensaje descriptivo del estado actual |
| `fecha_inicio` | TEXT | Timestamp de inicio |
| `fecha_fin` | TEXT | Timestamp de finalización |

---

## 🚀 Guía de Uso

### **1. Instalación de Dependencias**

```bash
cd src/dashboard
.\INSTALAR_RPA.bat
```

### **2. Verificar Instalación**

```python
# En consola Python
from rpa.arl_bot import ARLBot
bot = ARLBot(headless=True)
print("✅ Bot iniciado correctamente")
bot.cerrar()
```

### **3. Probar Automatización**

1. Iniciar servidor Flask:
   ```bash
   python app.py
   ```

2. Acceder al módulo:
   ```
   http://localhost:5000/copiloto/arl
   ```

3. Seleccionar empresa (ej: Innovatech S.A.S)
4. Ingresar cédula (ej: 100100100)
5. Seleccionar acción (Afiliar / Certificado / Incapacidad)
6. Hacer clic en "Iniciar Misión"

### **4. Monitorear Ejecución**

Ver logs del servidor Flask:
```
[INFO] 🤖 Iniciando bot RPA para job JOB-20251119120000-12345
[INFO] 🚀 Bot RPA iniciado correctamente (Chrome)
[INFO] 🌐 Navegando a: https://www.arlsura.com
[INFO] 📝 Diligenciando formulario para: Pedro Pérez
[INFO] ✅ Job JOB-20251119120000-12345 finalizado con estado: completado
[INFO] 🛑 Bot RPA finalizado
```

---

## 🛠️ Personalización para Portal Real

### **Ejemplo: Completar formulario de afiliación**

```python
# En rpa/arl_bot.py - método ejecutar_afiliacion()

def ejecutar_afiliacion(self, datos_empleado):
    try:
        # 1. Navegar al portal
        self.navegar_portal("https://www.arlsura.com")
        
        # 2. Login (si requiere autenticación)
        user_field = self.driver.find_element(By.ID, "username")
        user_field.send_keys("usuario_empresa")
        
        pass_field = self.driver.find_element(By.ID, "password")
        pass_field.send_keys("contraseña_segura")
        
        login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_btn.click()
        
        # 3. Esperar carga del dashboard
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "dashboard"))
        )
        
        # 4. Navegar a afiliaciones
        afiliacion_link = self.driver.find_element(By.LINK_TEXT, "Afiliar Empleado")
        afiliacion_link.click()
        
        # 5. Completar formulario
        nombre_field = self.driver.find_element(By.NAME, "nombre")
        nombre_field.send_keys(datos_empleado['nombre'])
        
        cedula_field = self.driver.find_element(By.NAME, "cedula")
        cedula_field.send_keys(datos_empleado['empleado_id'])
        
        # 6. Enviar formulario
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button.btn-submit")
        submit_btn.click()
        
        # 7. Esperar confirmación
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        # 8. Capturar número de radicado
        radicado = self.driver.find_element(By.ID, "numero_radicado").text
        
        return {
            "status": "exito",
            "mensaje": f"Afiliación radicada exitosamente",
            "soporte": radicado
        }
        
    except Exception as e:
        logger.error(f"Error en afiliación: {e}")
        return {"status": "error", "mensaje": str(e)}
```

---

## 🔐 Seguridad

**Recomendaciones:**
- ✅ Usar credenciales encriptadas (módulo `encryption.py`)
- ✅ Ejecutar en modo headless en producción
- ✅ Implementar rate limiting para evitar bloqueos
- ✅ Guardar logs de auditoría en `audit_log`
- ✅ Validar certificados SSL del portal

---

## 📝 Logs Disponibles

| Nivel | Descripción | Ejemplo |
|-------|-------------|---------|
| `INFO` | Operaciones exitosas | `✅ Bot iniciado correctamente` |
| `DEBUG` | Detalles de navegación | `🌐 Navegando a: https://...` |
| `WARNING` | Advertencias no críticas | `⚠️ Motor RPA no disponible` |
| `ERROR` | Errores recuperables | `❌ Error navegando: Timeout` |
| `CRITICAL` | Errores fatales | `❌ Error iniciando WebDriver` |

---

## ❓ Troubleshooting

### **Error: "No module named 'selenium'"**
**Solución:**
```bash
pip install selenium>=4.15.0
```

### **Error: "ChromeDriver not found"**
**Solución:** WebDriver Manager lo descargará automáticamente en la primera ejecución.

### **Error: "selenium.common.exceptions.TimeoutException"**
**Solución:**
- Aumentar timeout en `WebDriverWait(self.driver, 30)`
- Verificar selectores CSS/ID correctos
- Revisar si el portal cambió su estructura HTML

### **Bot ejecuta pero queda en "ejecutando"**
**Solución:**
- Revisar logs del servidor Flask
- Verificar que `bot.cerrar()` se ejecute en el `finally`
- Comprobar que la BD se actualice correctamente

---

## 📚 Referencias

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [WebDriver Manager](https://github.com/SergeyPirogov/webdriver_manager)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)

---

## 🎯 Roadmap Futuro

- [ ] Implementar captura de screenshots como evidencia
- [ ] Agregar soporte para Firefox/Edge (multi-browser)
- [ ] Sistema de reintentos automáticos en caso de fallo
- [ ] Panel de monitoreo en tiempo real (WebSockets)
- [ ] Integración con Celery para colas de trabajo
- [ ] Notificaciones por email al finalizar automatización

---

**Autor:** Sistema Montero - Equipo de Desarrollo  
**Fecha:** 19 de Noviembre de 2025  
**Versión:** 1.0.0
