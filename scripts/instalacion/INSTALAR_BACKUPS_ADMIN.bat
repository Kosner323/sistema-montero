@echo off
chcp 65001 >nul
:: ==========================================
::   INSTALADOR DE BACKUPS AUTOMÁTICOS
::   Sistema Montero v1.0
:: ==========================================

echo.
echo ==========================================
echo   INSTALADOR DE BACKUPS AUTOMÁTICOS
echo   Sistema Montero v1.0
echo ==========================================
echo.

:: Verificar si se está ejecutando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Ejecutando con permisos de administrador
    echo.
    goto :ejecutar_instalador
) else (
    echo [!] Este instalador requiere permisos de administrador
    echo.
    echo Solicitando elevacion de permisos...
    echo.
    
    :: Solicitar permisos de administrador
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:ejecutar_instalador
:: Ejecutar el script PowerShell con permisos elevados
echo Iniciando instalador...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar_backups.ps1"

if %errorLevel% NEQ 0 (
    echo.
    echo [ERROR] Hubo un problema durante la instalacion
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Proceso completado
echo.
pause
exit /b 0
