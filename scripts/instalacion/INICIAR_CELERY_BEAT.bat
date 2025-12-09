@echo off
REM =====================================================================
REM INICIAR_CELERY_BEAT.bat - Iniciar Scheduler de Celery para desarrollo
REM =====================================================================
REM IMPORTANTE: Ejecutar DESPUES de iniciar el Worker (INICIAR_CELERY.bat)
REM =====================================================================

echo.
echo ===============================================
echo  SISTEMA MONTERO - Celery Beat (Scheduler)
echo ===============================================
echo.

REM Verificar si Redis está corriendo
echo [1/2] Verificando conexion a Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Redis no esta corriendo en localhost:6379
    pause
    exit /b 1
)
echo [OK] Redis conectado

REM Iniciar Celery Beat
echo [2/2] Iniciando Celery Beat (Scheduler)...
echo.
echo Tareas programadas:
echo   - check_expiring_tutelas: Diaria 08:00 AM
echo   - send_monthly_report: Mensual dia 1, 09:00 AM
echo   - cleanup_old_notifications: Semanal Dom 02:00 AM
echo   - check_pending_payments: Diaria 10:00 AM
echo.
echo Presiona Ctrl+C para detener
echo -----------------------------------------------

cd /d "%~dp0..\.."
celery -A celery_config:celery_app beat --loglevel=info

pause
