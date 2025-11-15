@echo off
REM ========================================
REM Script de Corrección del Sistema Montero
REM Ejecutar desde: D:\Mi-App-React\src\dashboard
REM ========================================

echo.
echo ========================================
echo   CORRECCION DEL SISTEMA MONTERO
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "app.py" (
    echo [ERROR] No se encuentra app.py
    echo Este script debe ejecutarse desde la carpeta 'dashboard'
    echo.
    pause
    exit /b 1
)

echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    pause
    exit /b 1
)
echo [OK] Python encontrado

echo.
echo [2/4] Creando estructura de assets...
if not exist "assets" mkdir "assets"
if not exist "assets\css" mkdir "assets\css"
if not exist "assets\js" mkdir "assets\js"
if not exist "assets\images" mkdir "assets\images"
if not exist "assets\fonts" mkdir "assets\fonts"
echo [OK] Estructura de assets creada

echo.
echo [3/4] Corrigiendo rutas en archivos HTML...
python corregir_rutas_assets.py
if errorlevel 1 (
    echo [ERROR] No se pudo ejecutar el script de correccion
    echo Verifica que el archivo corregir_rutas_assets.py este en este directorio
    pause
    exit /b 1
)

echo.
echo [4/4] Ejecutando verificacion del sistema...
python verificar_sistema_montero.py
if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] Se encontraron problemas
    echo Revisa los mensajes anteriores para mas detalles
    echo.
) else (
    echo.
    echo [OK] Sistema verificado correctamente
    echo.
)

echo ========================================
echo   PROCESO COMPLETADO
echo ========================================
echo.
echo Siguiente paso: Copiar archivos reales de assets
echo.
echo   Desde: D:\Mi-App-React\src\assets\
echo   Hacia: D:\Mi-App-React\src\dashboard\assets\
echo.
echo   O usar el siguiente comando:
echo   xcopy /E /I /Y "D:\Mi-App-React\src\assets" "D:\Mi-App-React\src\dashboard\assets"
echo.
echo Para iniciar el servidor:
echo   python app.py
echo   o
echo   iniciar_sistema_corregido.bat
echo.
pause
