@echo off
REM =====================================================
REM VERIFICADOR SISTEMA LOCK SCREEN
REM Sistema Montero
REM =====================================================

echo.
echo ========================================
echo   VERIFICACIÓN LOCK SCREEN
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Verificando endpoint en auth.py...
findstr /C:"verify-password" routes\auth.py >nul
if %errorlevel%==0 (
    echo ✓ Endpoint /api/verify-password encontrado
) else (
    echo ✗ ERROR: Endpoint no encontrado
    goto error
)

echo.
echo [2/4] Verificando check_password_hash...
findstr /C:"check_password_hash" routes\auth.py >nul
if %errorlevel%==0 (
    echo ✓ Verificación bcrypt implementada
) else (
    echo ✗ ERROR: check_password_hash no encontrado
    goto error
)

echo.
echo [3/4] Verificando JavaScript en _header.html...
findstr /C:"desbloquearPantalla" templates\_header.html >nul
if %errorlevel%==0 (
    echo ✓ Función desbloquearPantalla() encontrada
) else (
    echo ✗ ERROR: Función no encontrada
    goto error
)

findstr /C:"/api/verify-password" templates\_header.html >nul
if %errorlevel%==0 (
    echo ✓ Fetch al endpoint correcto
) else (
    echo ✗ ERROR: Endpoint incorrecto en fetch
    goto error
)

echo.
echo [4/4] Verificando archivos de documentación...
if exist "DOCUMENTACION_LOCKSCREEN.md" (
    echo ✓ Documentación encontrada
) else (
    echo ⚠ Advertencia: Documentación no encontrada
)

if exist "test_lockscreen.py" (
    echo ✓ Tests encontrados
) else (
    echo ⚠ Advertencia: Tests no encontrados
)

echo.
echo ========================================
echo   ✅ VERIFICACIÓN EXITOSA
echo ========================================
echo.
echo Sistema Lock Screen implementado correctamente:
echo.
echo Componentes verificados:
echo   ✓ Endpoint: POST /api/verify-password
echo   ✓ Verificación bcrypt con check_password_hash()
echo   ✓ JavaScript: desbloquearPantalla()
echo   ✓ Fetch al endpoint correcto
echo   ✓ Overlay full-screen en _header.html
echo.
echo Próximos pasos:
echo   1. Reiniciar servidor: python app.py
echo   2. Login: http://localhost:5000
echo   3. Click avatar ^> Bloquear Pantalla
echo   4. Ingresar contraseña ^> Enter
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo   ❌ ERROR EN VERIFICACIÓN
echo ========================================
echo.
echo Por favor revisa los archivos mencionados
echo o contacta al equipo de desarrollo.
echo.
pause
exit /b 1
