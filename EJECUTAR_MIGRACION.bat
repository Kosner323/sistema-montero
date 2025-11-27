@echo off
REM ================================================================
REM SCRIPT DE MIGRACION DE BASE DE DATOS
REM ================================================================
REM Agrega columnas faltantes a las tablas empresas y usuarios
REM ================================================================

echo.
echo ====================================================================
echo            MIGRACION DE BASE DE DATOS - FIX_DB.PY
echo ====================================================================
echo.

REM Verificar que estamos en la carpeta correcta
if not exist "fix_db.py" (
    echo [ERROR] No se encontro fix_db.py en la carpeta actual
    echo.
    echo Por favor, ejecuta este script desde: src\dashboard\
    echo.
    pause
    exit /b 1
)

REM Verificar si existe Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    echo Instala Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [INFO] Python encontrado:
python --version
echo.

REM Ejecutar el script de migracion
echo [EJECUTANDO] Migracion de base de datos...
echo.

python fix_db.py

if errorlevel 1 (
    echo.
    echo [ERROR] La migracion fallo
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================================================
echo            MIGRACION COMPLETADA EXITOSAMENTE
echo ====================================================================
echo.
echo [SIGUIENTE PASO] Reinicia la aplicacion Flask:
echo    python app.py
echo.

pause
