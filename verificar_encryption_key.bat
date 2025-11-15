@echo off
chcp 65001 >nul
cls
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║  VERIFICACION RAPIDA - ENCRYPTION_KEY                    ║
echo ║  Sistema Montero                                         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo 📋 Verificando archivo _env...
echo.

if not exist _env (
    echo ❌ ERROR: Archivo _env NO encontrado
    echo.
    echo    El archivo _env debe estar en la carpeta del proyecto
    echo.
    goto error
)

echo ✅ Archivo _env encontrado
echo.
echo 📄 Contenido de ENCRYPTION_KEY:
echo.

findstr /C:"ENCRYPTION_KEY=" _env
if %errorlevel% neq 0 (
    echo ❌ ERROR: ENCRYPTION_KEY no encontrada en _env
    goto error
)

echo.
echo ✅ ENCRYPTION_KEY encontrada y configurada
echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ TODO ESTÁ BIEN - ENCRYPTION_KEY CONFIGURADA
echo ═══════════════════════════════════════════════════════════
echo.
echo La clave de encriptación está correctamente configurada.
echo No necesitas hacer nada más en este paso.
echo.
echo Presiona cualquier tecla para continuar...
pause >nul
exit /b 0

:error
echo.
echo ═══════════════════════════════════════════════════════════
echo   ⚠️  ATENCION - SE REQUIERE ACCION
echo ═══════════════════════════════════════════════════════════
echo.
echo Por favor revisa que:
echo   1. El archivo _env esté en la carpeta correcta
echo   2. Contenga la línea ENCRYPTION_KEY=...
echo.
pause
exit /b 1
