@echo off
REM =========================================================
REM  INSTALACION DIRECTA DE CRYPTOGRAPHY EN VENV
REM  Sin activacion manual - Uso directo del ejecutable
REM =========================================================

title Instalacion de Cryptography en VENV

echo.
echo ========================================
echo   INSTALACION DE CRYPTOGRAPHY
echo ========================================
echo.

REM Definir rutas absolutas
SET VENV_PYTHON=D:\Mi-App-React\BUILD\venv\Scripts\python.exe
SET VENV_PIP=D:\Mi-App-React\BUILD\venv\Scripts\pip.exe

REM Verificar que el VENV existe
if not exist "%VENV_PYTHON%" (
    echo [ERROR] No se encontro el entorno virtual en:
    echo %VENV_PYTHON%
    echo.
    echo Por favor verifica que el VENV este creado en D:\Mi-App-React\BUILD\venv
    pause
    exit /b 1
)

echo [OK] Entorno virtual encontrado
echo.

REM Mostrar version de Python del VENV
echo [INFO] Version de Python del VENV:
"%VENV_PYTHON%" --version
echo.

REM Actualizar pip primero
echo [INFO] Actualizando pip...
"%VENV_PYTHON%" -m pip install --upgrade pip
echo.

REM Instalar cryptography directamente
echo [INFO] Instalando cryptography...
echo.
"%VENV_PYTHON%" -m pip install cryptography
SET INSTALL_ERROR=%ERRORLEVEL%

echo.

REM Verificar instalacion
if %INSTALL_ERROR% EQU 0 (
    echo [OK] Instalacion completada
    echo.
    echo [INFO] Verificando instalacion...
    "%VENV_PYTHON%" -m pip show cryptography
    echo.
    
    REM Probar importacion
    echo [INFO] Probando importacion...
    "%VENV_PYTHON%" -c "from cryptography.fernet import Fernet; print('[OK] Cryptography funciona correctamente')"
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ========================================
        echo   INSTALACION EXITOSA
        echo ========================================
        echo.
        echo Cryptography esta instalado y funcional en el VENV
        echo Ruta: D:\Mi-App-React\BUILD\venv\Scripts\python.exe
        echo.
    ) else (
        echo.
        echo [ERROR] La importacion de cryptography fallo
        echo Verifica los errores anteriores
        echo.
    )
) else (
    echo [ERROR] La instalacion de cryptography fallo
    echo Codigo de error: %INSTALL_ERROR%
    echo.
    echo Posibles soluciones:
    echo 1. Verifica tu conexion a internet
    echo 2. Ejecuta este script como Administrador
    echo 3. Verifica que no haya antivirus bloqueando la instalacion
    echo.
)

pause
