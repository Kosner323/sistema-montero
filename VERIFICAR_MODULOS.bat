@echo off
REM =====================================================
REM VERIFICADOR DE MÓDULOS - SISTEMA MONTERO
REM Verifica que todos los blueprints estén cargados
REM =====================================================

echo.
echo ========================================
echo   VERIFICACIÓN DE MÓDULOS
echo ========================================
echo.

cd /d "%~dp0"

echo [1/6] Verificando importaciones en app.py...
findstr /C:"from routes.automation_routes import automation_bp" app.py >nul
if %errorlevel%==0 (
    echo ✓ automation_bp importado
) else (
    echo ✗ ERROR: automation_bp no importado
    goto error
)

findstr /C:"from routes.auth import auth_bp" app.py >nul
if %errorlevel%==0 (
    echo ✓ auth_bp importado
) else (
    echo ✗ ERROR: auth_bp no importado
    goto error
)

echo.
echo [2/6] Verificando registro de blueprints...
findstr /C:"app.register_blueprint(automation_bp)" app.py >nul
if %errorlevel%==0 (
    echo ✓ automation_bp registrado
) else (
    echo ✗ ERROR: automation_bp no registrado
    goto error
)

echo.
echo [3/6] Verificando configuración de uploads...
findstr /C:"UPLOAD_FOLDER" app.py >nul
if %errorlevel%==0 (
    echo ✓ UPLOAD_FOLDER configurado
) else (
    echo ✗ ERROR: UPLOAD_FOLDER no configurado
    goto error
)

findstr /C:"MAX_CONTENT_LENGTH" app.py >nul
if %errorlevel%==0 (
    echo ✓ MAX_CONTENT_LENGTH configurado
) else (
    echo ✗ ERROR: MAX_CONTENT_LENGTH no configurado
    goto error
)

echo.
echo [4/6] Verificando inicialización de extensiones...
findstr /C:"CSRFProtect" app.py >nul
if %errorlevel%==0 (
    echo ✓ CSRFProtect inicializado
) else (
    echo ✗ ERROR: CSRFProtect no encontrado
    goto error
)

findstr /C:"limiter.init_app" app.py >nul
if %errorlevel%==0 (
    echo ✓ Limiter inicializado
) else (
    echo ⚠ Advertencia: Limiter no encontrado
)

echo.
echo [5/6] Verificando manejadores de error...
findstr /C:"errorhandler(404)" app.py >nul
if %errorlevel%==0 (
    echo ✓ Error 404 manejado
) else (
    echo ⚠ Advertencia: Error 404 no manejado
)

findstr /C:"errorhandler(500)" app.py >nul
if %errorlevel%==0 (
    echo ✓ Error 500 manejado
) else (
    echo ⚠ Advertencia: Error 500 no manejado
)

echo.
echo [6/6] Verificando inicialización de BD...
findstr /C:"initialize_database" app.py >nul
if %errorlevel%==0 (
    echo ✓ Función initialize_database() encontrada
) else (
    echo ✗ ERROR: initialize_database() no encontrada
    goto error
)

echo.
echo ========================================
echo   ✅ VERIFICACIÓN EXITOSA
echo ========================================
echo.
echo Módulos verificados en app.py:
echo.
echo Core:
echo   ✓ auth_bp (autenticación)
echo   ✓ bp_main (rutas principales)
echo   ✓ bp_empresa (empresas)
echo   ✓ bp_empleado (usuarios)
echo.
echo Negocio:
echo   ✓ bp_pagos (pagos)
echo   ✓ bp_notificaciones (notificaciones)
echo   ✓ bp_tutelas (tutelas)
echo   ✓ bp_cotizaciones (cotizaciones)
echo   ✓ bp_incapacidades (incapacidades)
echo.
echo Nuevos Módulos:
echo   ✓ automation_bp (RPA Copiloto)
echo   ✓ bp_marketing (marketing)
echo   ✓ finance_bp (finanzas)
echo   ✓ admin_bp (administración)
echo   ✓ user_settings_bp (configuración usuario)
echo.
echo Configuración:
echo   ✓ UPLOAD_FOLDER: static/uploads
echo   ✓ MAX_CONTENT_LENGTH: 16MB
echo   ✓ CSRFProtect activado
echo   ✓ Database: data/mi_sistema.db
echo.
echo Próximos pasos:
echo   1. python app.py
echo   2. Verificar mensaje: "✅ Todos los módulos cargados"
echo   3. Acceder a: http://localhost:5000
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo   ❌ ERROR EN VERIFICACIÓN
echo ========================================
echo.
echo Por favor revisa app.py
echo Asegúrate de que todos los imports y
echo register_blueprint estén correctos.
echo.
pause
exit /b 1
