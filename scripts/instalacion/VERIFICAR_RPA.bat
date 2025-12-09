@echo off
REM =====================================================
REM VERIFICADOR DE INSTALACIÓN RPA
REM Sistema Montero
REM =====================================================

echo.
echo ========================================
echo   VERIFICACIÓN MOTOR RPA
echo ========================================
echo.

cd /d "%~dp0"

echo [1/5] Verificando estructura de archivos...
if exist "rpa\arl_bot.py" (
    echo ✓ Motor RPA encontrado: rpa\arl_bot.py
) else (
    echo ✗ ERROR: No se encuentra rpa\arl_bot.py
    goto error
)

if exist "rpa\__init__.py" (
    echo ✓ Módulo RPA inicializado
) else (
    echo ✗ ERROR: No se encuentra rpa\__init__.py
    goto error
)

echo.
echo [2/5] Verificando requirements.txt...
findstr /C:"selenium" requirements.txt >nul
if %errorlevel%==0 (
    echo ✓ selenium agregado a requirements.txt
) else (
    echo ✗ ERROR: selenium no encontrado en requirements.txt
    goto error
)

findstr /C:"webdriver-manager" requirements.txt >nul
if %errorlevel%==0 (
    echo ✓ webdriver-manager agregado a requirements.txt
) else (
    echo ✗ ERROR: webdriver-manager no encontrado en requirements.txt
    goto error
)

echo.
echo [3/5] Verificando instalación de Selenium...
python -c "import selenium; print('✓ Selenium instalado:', selenium.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ⚠ Selenium NO instalado - Ejecuta: .\INSTALAR_RPA.bat
) else (
    echo ✓ Selenium instalado correctamente
)

echo.
echo [4/5] Verificando automation_routes.py...
findstr /C:"import threading" routes\automation_routes.py >nul
if %errorlevel%==0 (
    echo ✓ Threading importado
) else (
    echo ✗ ERROR: Threading no importado en automation_routes.py
    goto error
)

findstr /C:"ARLBot" routes\automation_routes.py >nul
if %errorlevel%==0 (
    echo ✓ ARLBot importado
) else (
    echo ✗ ERROR: ARLBot no importado en automation_routes.py
    goto error
)

echo.
echo [5/5] Probando importación del bot...
python -c "try:
    from rpa.arl_bot import ARLBot
    print('✓ ARLBot importado correctamente')
    print('✓ VERIFICACIÓN EXITOSA')
except ImportError as e:
    print('⚠ ARLBot no se puede importar:', e)
    print('  Esto es normal si Selenium no está instalado')
    print('  Ejecuta: .\\INSTALAR_RPA.bat')" 2>nul

if %errorlevel% neq 0 (
    echo ⚠ No se pudo importar ARLBot
    echo   Ejecuta: .\INSTALAR_RPA.bat para instalar dependencias
)

echo.
echo ========================================
echo   VERIFICACIÓN COMPLETADA
echo ========================================
echo.
echo Archivos creados:
echo   ✓ src\dashboard\rpa\arl_bot.py
echo   ✓ src\dashboard\rpa\__init__.py
echo   ✓ src\dashboard\DOCUMENTACION_RPA.md
echo   ✓ src\dashboard\INSTALAR_RPA.bat
echo.
echo Próximos pasos:
echo   1. Instalar dependencias: .\INSTALAR_RPA.bat
echo   2. Reiniciar servidor: python app.py
echo   3. Probar: http://localhost:5000/copiloto/arl
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo   ERROR EN VERIFICACIÓN
echo ========================================
echo.
echo Por favor revisa los archivos mencionados
echo o contacta al equipo de desarrollo.
echo.
pause
exit /b 1
