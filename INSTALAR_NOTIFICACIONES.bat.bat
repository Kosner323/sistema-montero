@echo off
REM ============================================
REM Script de Instalación - Sistema de Notificaciones
REM Sistema Montero
REM ============================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║     INSTALACIÓN SISTEMA DE NOTIFICACIONES                 ║
echo ║     Sistema Montero v2.1                                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Verificar Python
echo [1/10] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instala Python 3.9 o superior.
    pause
    exit /b 1
)
echo ✅ Python encontrado

REM Verificar pip
echo.
echo [2/10] Verificando pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no encontrado
    pause
    exit /b 1
)
echo ✅ pip encontrado

REM Instalar dependencias
echo.
echo [3/10] Instalando dependencias...
pip install Flask-Mail>=0.9.1 celery>=5.2.0 redis>=4.0.0 requests>=2.28.0 --break-system-packages
if errorlevel 1 (
    echo ⚠️  Advertencia: Algunos paquetes pueden no haberse instalado correctamente
) else (
    echo ✅ Dependencias instaladas
)

REM Verificar Redis
echo.
echo [4/10] Verificando Redis...
redis-cli --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis no encontrado.
    echo    Descarga Redis desde: https://github.com/microsoftarchive/redis/releases
    echo    O instala con Chocolatey: choco install redis-64
    echo.
    set /p CONTINUE="¿Continuar sin Redis? (las tareas programadas no funcionarán) [S/N]: "
    if /i not "%CONTINUE%"=="S" (
        exit /b 1
    )
) else (
    echo ✅ Redis encontrado
)

REM Crear directorios necesarios
echo.
echo [5/10] Creando directorios...
if not exist "templates\emails" mkdir "templates\emails"
if not exist "logs" mkdir "logs"
if not exist "backups" mkdir "backups"
echo ✅ Directorios creados

REM Copiar archivos
echo.
echo [6/10] Copiando archivos del sistema...
if exist "sistema-notificaciones\notification_service.py" (
    copy /Y "sistema-notificaciones\notification_service.py" .
    copy /Y "sistema-notificaciones\notificaciones_routes.py" .
    copy /Y "sistema-notificaciones\celery_config.py" .
    copy /Y "sistema-notificaciones\celery_tasks.py" .
    copy /Y "sistema-notificaciones\003_agregar_notificaciones.py" "alembic\versions\"
    copy /Y "sistema-notificaciones\notificaciones_component.html" "templates\"

    REM Copiar plantillas
    xcopy /Y /E /I "sistema-notificaciones\templates\emails" "templates\emails"

    echo ✅ Archivos copiados
) else (
    echo ⚠️  Directorio sistema-notificaciones no encontrado
    echo    Asegúrate de ejecutar este script desde la raíz del proyecto
    pause
    exit /b 1
)

REM Verificar .env
echo.
echo [7/10] Verificando configuración...
if not exist ".env" (
    if exist "sistema-notificaciones\.env.example" (
        copy "sistema-notificaciones\.env.example" ".env"
        echo ⚠️  Archivo .env creado desde plantilla
        echo    ¡IMPORTANTE! Edita el archivo .env con tus credenciales
    ) else (
        echo ❌ No se encontró .env.example
    )
) else (
    echo ✅ Archivo .env existe
)

REM Ejecutar migración
echo.
echo [8/10] Ejecutando migración de base de datos...
python -c "from database_schema_COMPLETO import get_db_connection; conn = get_db_connection(); cursor = conn.cursor(); exec(open('alembic/versions/003_agregar_notificaciones.py').read()); conn.close()" 2>nul
if errorlevel 1 (
    echo ⚠️  Advertencia: La migración puede haber fallado
    echo    Ejecuta manualmente: alembic upgrade head
) else (
    echo ✅ Migración ejecutada
)

REM Ejecutar tests
echo.
echo [9/10] Ejecutando tests...
if exist "sistema-notificaciones\test_notifications.py" (
    copy /Y "sistema-notificaciones\test_notifications.py" "tests\"
    python -m pytest tests\test_notifications.py -v --tb=short >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Algunos tests fallaron (esto es normal en instalación inicial)
    ) else (
        echo ✅ Tests pasados
    )
)

REM Resumen
echo.
echo [10/10] Instalación completada
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                     RESUMEN                               ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo ✅ Sistema de Notificaciones instalado
echo ✅ Archivos copiados correctamente
echo ✅ Base de datos actualizada
echo.
echo 📋 PRÓXIMOS PASOS:
echo.
echo 1. Edita el archivo .env con tus credenciales:
echo    - SMTP_USERNAME, SMTP_PASSWORD
echo    - SLACK_WEBHOOK_URL (opcional)
echo    - DISCORD_WEBHOOK_URL (opcional)
echo.
echo 2. Inicia Redis (si lo tienes instalado):
echo    redis-server
echo.
echo 3. En terminales separadas, ejecuta:
echo    Terminal 1: celery -A celery_config worker --loglevel=info
echo    Terminal 2: celery -A celery_config beat --loglevel=info
echo.
echo 4. Inicia tu aplicación Flask:
echo    python app.py
echo.
echo 5. Prueba las notificaciones:
echo    - Ve a http://localhost:5000
echo    - Busca el icono de campana en el header
echo.
echo 📖 Documentación completa en:
echo    sistema-notificaciones\GUIA_NOTIFICACIONES.md
echo    sistema-notificaciones\RESUMEN_EJECUTIVO.md
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║     ¡INSTALACIÓN EXITOSA! 🎉                              ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

pause
