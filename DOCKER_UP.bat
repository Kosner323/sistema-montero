@echo off
REM =====================================================================
REM DOCKER_UP.bat - Iniciar Sistema Montero completo con Docker
REM =====================================================================
REM Comando unico para levantar: App + Redis + Celery Worker + Celery Beat
REM =====================================================================

echo.
echo ===============================================
echo  SISTEMA MONTERO - Docker Compose
echo ===============================================
echo.

REM Verificar que Docker esté corriendo
echo [1/3] Verificando Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo
    echo         Por favor inicia Docker Desktop
    pause
    exit /b 1
)
echo [OK] Docker disponible

REM Verificar que exista .env
echo [2/3] Verificando archivo .env...
if not exist ".env" (
    echo [ERROR] Archivo .env no encontrado
    echo         Copia .env.example a .env y configura las variables
    pause
    exit /b 1
)
echo [OK] Archivo .env encontrado

REM Iniciar servicios
echo [3/3] Iniciando servicios...
echo.
echo Servicios a levantar:
echo   - montero-backend (Flask App) -> http://localhost:5000
echo   - montero-redis (Broker)      -> localhost:6379
echo   - montero-celery-worker       -> Tareas asincronas
echo   - montero-celery-beat         -> Tareas programadas
echo.
echo Presiona Ctrl+C para detener todos los servicios
echo -----------------------------------------------
echo.

docker-compose up --build

pause
