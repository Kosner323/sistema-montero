@echo off
REM =====================================================================
REM DOCKER_DOWN.bat - Detener Sistema Montero
REM =====================================================================

echo.
echo Deteniendo todos los contenedores...
docker-compose down

echo.
echo [OK] Servicios detenidos
echo.
echo Para eliminar volumenes (datos de Redis):
echo   docker-compose down -v
echo.
pause
