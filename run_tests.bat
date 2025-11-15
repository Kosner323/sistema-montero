@echo off
REM =======================================================================
REM run_tests.bat - Script para ejecutar tests en Windows
REM Sistema Montero
REM =======================================================================

echo.
echo ========================================================================
echo   SISTEMA DE TESTS - MONTERO
echo ========================================================================
echo.

REM Verificar que Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)

REM Verificar que pytest está instalado
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pytest no esta instalado
    echo.
    echo Instalar con: pip install -r requirements-test.txt
    pause
    exit /b 1
)

REM Si no hay argumentos, ejecutar con coverage
if "%1"=="" (
    echo Ejecutando tests con coverage...
    echo.
    python run_tests.py --coverage
    goto :end
)

REM Si hay argumentos, pasarlos al script Python
python run_tests.py %*

:end
echo.
pause
