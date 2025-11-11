@echo off
chcp 65001 >nul
echo ============================================
echo   VALIDACION DE ENCRYPTION_KEY
echo   Sistema Montero - Windows
echo ============================================
echo.

echo [1/4] Verificando archivo _env...
if exist _env (
    echo ✓ Archivo _env encontrado
) else (
    echo ✗ ERROR: Archivo _env no encontrado
    pause
    exit /b 1
)
echo.

echo [2/4] Verificando que Python esté instalado...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ ERROR: Python no está instalado o no está en PATH
    pause
    exit /b 1
)
python --version
echo ✓ Python encontrado
echo.

echo [3/4] Verificando dependencias...
python -c "import cryptography; print('✓ cryptography instalado - version:', cryptography.__version__)" 2>nul
if %errorlevel% neq 0 (
    echo ⚠ cryptography no está instalado
    echo   Instalando cryptography...
    pip install cryptography --break-system-packages
    if %errorlevel% neq 0 (
        echo ✗ ERROR: No se pudo instalar cryptography
        pause
        exit /b 1
    )
)
echo.

echo [4/4] Probando sistema de encriptación...
python validate_encryption_env.py
if %errorlevel% neq 0 (
    echo.
    echo ✗ ERROR: La validación de encriptación falló
    pause
    exit /b 1
)
echo.

echo ============================================
echo   ✓ VALIDACION COMPLETADA EXITOSAMENTE
echo ============================================
echo.
echo Todo está funcionando correctamente:
echo   ✓ Archivo _env configurado
echo   ✓ ENCRYPTION_KEY presente
echo   ✓ Sistema de encriptación operativo
echo.
pause
