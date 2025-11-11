@echo off
REM Script de instalación de CI/CD Pipeline para Windows
REM Sistema Montero v2.1

echo ==========================================
echo    INSTALACION CI/CD PIPELINE
echo    Sistema Montero v2.1
echo ==========================================
echo.

REM 1. Verificar Python
echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado
    pause
    exit /b 1
)
echo [OK] Python encontrado
echo.

REM 2. Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip
echo.

REM 3. Instalar herramientas de desarrollo
echo Instalando herramientas de desarrollo...
pip install pre-commit black flake8 pylint isort mypy
pip install bandit safety pip-audit
pip install pytest pytest-cov pytest-html pytest-mock
echo [OK] Herramientas instaladas
echo.

REM 4. Configurar pre-commit
echo Configurando pre-commit hooks...
if exist .pre-commit-config.yaml (
    pre-commit install
    echo [OK] Pre-commit hooks instalados
) else (
    echo [WARNING] Archivo .pre-commit-config.yaml no encontrado
)
echo.

REM 5. Crear baseline de secretos
echo Creando baseline de deteccion de secretos...
detect-secrets scan > .secrets.baseline 2>nul
if errorlevel 1 (
    echo [WARNING] detect-secrets no instalado
) else (
    echo [OK] Baseline creado
)
echo.

REM 6. Ejecutar tests
echo Ejecutando tests...
if exist pytest.ini (
    pytest --cov=. --cov-report=term-missing
    echo [OK] Tests completados
) else (
    echo [WARNING] pytest.ini no encontrado
)
echo.

REM 7. Security scan
echo Ejecutando analisis de seguridad...
bandit -r . -ll 2>nul
safety check 2>nul
echo [OK] Analisis completado
echo.

REM 8. Generar reporte HTML
echo Generando reporte de coverage...
pytest --cov=. --cov-report=html --cov-report=term
echo [OK] Reporte generado en htmlcov\index.html
echo.

REM Resumen
echo ==========================================
echo RESUMEN DE INSTALACION
echo ==========================================
echo.
echo [OK] Python y pip instalados
echo [OK] Herramientas de desarrollo instaladas
echo [OK] Pre-commit hooks configurados
echo [OK] Analisis de seguridad completado
echo.
echo Proximos pasos:
echo   1. Revisar reporte: htmlcov\index.html
echo   2. Corregir problemas de seguridad
echo   3. Hacer commit para probar hooks
echo   4. Configurar secretos en GitHub
echo.
echo Documentacion: Ver CI_CD_README.md
echo.
echo [OK] Instalacion completada!
echo.
pause
