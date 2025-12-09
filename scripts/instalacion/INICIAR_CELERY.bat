@echo off
REM =====================================================================
REM INICIAR_CELERY.bat - Iniciar Worker de Celery para desarrollo local
REM =====================================================================
REM REQUISITOS:
REM   1. Redis corriendo en localhost:6379
REM   2. Variables CELERY_BROKER_URL y CELERY_RESULT_BACKEND en .env
REM   3. pip install celery redis
REM =====================================================================

echo.
echo ===============================================
echo  SISTEMA MONTERO - Celery Worker
echo ===============================================
echo.

REM Verificar si Redis está corriendo
echo [1/3] Verificando conexion a Redis...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Redis no esta corriendo en localhost:6379
    echo         Instalar Redis: https://redis.io/docs/install/
    echo         O usar Docker: docker run -d -p 6379:6379 redis:7-alpine
    pause
    exit /b 1
)
echo [OK] Redis conectado

REM Cargar variables de entorno
echo [2/3] Cargando variables de entorno...
if exist .env (
    for /f "tokens=1,2 delims==" %%a in ('type .env ^| findstr /v "^#"') do (
        set "%%a=%%b"
    )
    echo [OK] Variables cargadas desde .env
) else (
    echo [WARN] Archivo .env no encontrado, usando valores por defecto
)

REM Iniciar Celery Worker
echo [3/3] Iniciando Celery Worker...
echo.
echo Comando: celery -A celery_config:celery_app worker --loglevel=info --pool=solo
echo.
echo Presiona Ctrl+C para detener el worker
echo -----------------------------------------------

cd /d "%~dp0..\.."
celery -A celery_config:celery_app worker --loglevel=info --pool=solo

pause
