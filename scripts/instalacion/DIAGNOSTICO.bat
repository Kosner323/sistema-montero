@echo off
REM Script de Diagnóstico del Sistema de Backups
REM Sistema Montero - Windows
REM ==========================================

title Diagnóstico del Sistema de Backups

echo.
echo ==========================================
echo   DIAGNOSTICO DEL SISTEMA DE BACKUPS
echo   Sistema Montero v1.0
echo ==========================================
echo.
echo Este script verificara que el sistema de
echo backups este correctamente instalado.
echo.
pause

REM Ejecutar el diagnóstico
python diagnostico_backup.py

REM Verificar si Python existe
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo.
    echo Por favor:
    echo 1. Instale Python desde: https://www.python.org/
    echo 2. Durante la instalacion, marque "Add Python to PATH"
    echo 3. Ejecute este script nuevamente
    echo.
    pause
)
