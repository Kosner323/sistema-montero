@echo off
REM =========================================================
REM  VALIDACION COMPLETA DEL ENTORNO
REM  Verifica Python, VENV, dependencias y cryptography
REM =========================================================

title Validacion de Entorno

echo.
echo ========================================
echo   VALIDACION DE ENTORNO
echo ========================================
echo.

SET VENV_PYTHON=D:\Mi-App-React\BUILD\venv\Scripts\python.exe
SET PROJECT_ROOT=D:\Mi-App-React\src\dashboard

REM Variables para contar resultados
SET TESTS_PASSED=0
SET TESTS_FAILED=0

REM =========================================================
REM  TEST 1: Verificar Python Global
REM =========================================================
echo [TEST 1] Python global instalado...

python --version >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    python --version
    SET /A TESTS_PASSED+=1
    echo [OK] Python global encontrado
) else (
    SET /A TESTS_FAILED+=1
    echo [ERROR] Python global no encontrado
)

echo.

REM =========================================================
REM  TEST 2: Verificar VENV existe
REM =========================================================
echo [TEST 2] Entorno virtual existe...

if exist "%VENV_PYTHON%" (
    SET /A TESTS_PASSED+=1
    echo [OK] VENV encontrado en: %VENV_PYTHON%
) else (
    SET /A TESTS_FAILED+=1
    echo [ERROR] VENV no encontrado en: %VENV_PYTHON%
)

echo.

REM =========================================================
REM  TEST 3: Verificar Python del VENV funciona
REM =========================================================
echo [TEST 3] Python del VENV funcional...

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" --version
    
    if %ERRORLEVEL% EQU 0 (
        SET /A TESTS_PASSED+=1
        echo [OK] Python del VENV funciona
    ) else (
        SET /A TESTS_FAILED+=1
        echo [ERROR] Python del VENV no funciona
    )
) else (
    SET /A TESTS_FAILED+=1
    echo [ERROR] No se puede probar (VENV no existe)
)

echo.

REM =========================================================
REM  TEST 4: Verificar pip del VENV
REM =========================================================
echo [TEST 4] pip del VENV funcional...

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" -m pip --version
    
    if %ERRORLEVEL% EQU 0 (
        SET /A TESTS_PASSED+=1
        echo [OK] pip del VENV funciona
    ) else (
        SET /A TESTS_FAILED+=1
        echo [ERROR] pip del VENV no funciona
    )
) else (
    SET /A TESTS_FAILED+=1
    echo [ERROR] No se puede probar (VENV no existe)
)

echo.

REM =========================================================
REM  TEST 5: Verificar cryptography instalado
REM =========================================================
echo [TEST 5] Cryptography instalado...

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" -c "import cryptography; print('Version:', cryptography.__version__)" 2>nul
    
    if %ERRORLEVEL% EQU 0 (
        SET /A TESTS_PASSED+=1
        echo [OK] Cryptography instalado y funcional
    ) else (
        SET /A TESTS_FAILED+=1
        echo [ERROR] Cryptography no estÃ¡ instalado
        echo [INFO] Ejecuta: instalar_cryptography.bat
    )
) else (
    SET /A TESTS_FAILED+=1
    echo [ERROR] No se puede probar (VENV no existe)
)

echo.

REM =========================================================
REM  TEST 6: Verificar ubicaciÃ³n de cryptography
REM =========================================================
echo [TEST 6] UbicaciÃ³n de cryptography...

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" -m pip show cryptography 2>nul | findstr "Location"
    
    if %ERRORLEVEL% EQU 0 (
        REM Verificar que estÃ¡ en el VENV
        "%VENV_PYTHON%" -m pip show cryptography 2>nul | findstr "Location" | findstr "BUILD\\venv" >nul
        
        if %ERRORLEVEL% EQU 0 (
            SET /A TESTS_PASSED+=1
            echo [OK] Cryptography estÃ¡ en el VENV (no global)
        ) else (
            SET /A TESTS_FAILED+=1
            echo [ERROR] Cryptography estÃ¡ en ubicaciÃ³n global
            echo [INFO] Reinstala con: instalar_cryptography.bat
        )
    ) else (
        SET /A TESTS_FAILED+=1
        echo [ERROR] No se pudo verificar ubicaciÃ³n
    )
) else (
    SET /A TESTS_FAILED+=1
    echo [ERROR] No se puede probar (VENV no existe)
)

echo.

REM =========================================================
REM  TEST 7: Verificar imports crÃ­ticos
REM =========================================================
echo [TEST 7] Imports crÃ­ticos del proyecto...

if exist "%VENV_PYTHON%" (
    cd /d "%PROJECT_ROOT%"
    
    REM Probar imports uno por uno
    SET IMPORTS_OK=0
    
    "%VENV_PYTHON%" -c "from cryptography.fernet import Fernet" 2>nul
    if %ERRORLEVEL% EQU 0 SET /A IMPORTS_OK+=1
    
    "%VENV_PYTHON%" -c "import flask" 2>nul
    if %ERRORLEVEL% EQU 0 SET /A IMPORTS_OK+=1
    
    "%VENV_PYTHON%" -c "import sqlite3" 2>nul
    if %ERRORLEVEL% EQU 0 SET /A IMPORTS_OK+=1
    
    if %IMPORTS_OK% EQU 3 (
        SET /A TESTS_PASSED+=1
        echo [OK] Todos los imports crÃ­ticos funcionan
        echo     - cryptography.fernet.Fernet
        echo     - flask
        echo     - sqlite3
    ) else (
        SET /A TESTS_FAILED+=1
        echo [ERROR] Algunos imports fallaron
        echo [INFO] Instala dependencias con: pip install -r requirements.txt
    )
) else (
    SET /A TESTS_FAILED+=1
    echo [ERROR] No se puede probar (VENV no existe)
)

echo.

REM =========================================================
REM  TEST 8: Verificar estructura de proyecto
REM =========================================================
echo [TEST 8] Estructura de proyecto...

SET STRUCTURE_OK=0

if exist "%PROJECT_ROOT%\app.py" SET /A STRUCTURE_OK+=1
if exist "%PROJECT_ROOT%\_env" SET /A STRUCTURE_OK+=1
if exist "%PROJECT_ROOT%\encryption.py" SET /A STRUCTURE_OK+=1

if %STRUCTURE_OK% EQU 3 (
    SET /A TESTS_PASSED+=1
    echo [OK] Estructura de proyecto correcta
    echo     - app.py encontrado
    echo     - _env encontrado
    echo     - encryption.py encontrado
) else (
    SET /A TESTS_FAILED+=1
    echo [ERROR] Estructura de proyecto incompleta
    if not exist "%PROJECT_ROOT%\app.py" echo     - app.py NO encontrado
    if not exist "%PROJECT_ROOT%\_env" echo     - _env NO encontrado
    if not exist "%PROJECT_ROOT%\encryption.py" echo     - encryption.py NO encontrado
)

echo.

REM =========================================================
REM  RESUMEN FINAL
REM =========================================================
echo ========================================
echo   RESUMEN DE VALIDACION
echo ========================================
echo.

SET /A TOTAL_TESTS=%TESTS_PASSED% + %TESTS_FAILED%

echo Tests ejecutados: %TOTAL_TESTS%
echo Tests exitosos:   %TESTS_PASSED%
echo Tests fallidos:   %TESTS_FAILED%
echo.

if %TESTS_FAILED% EQU 0 (
    echo [RESULTADO] TODO OK - El entorno esta correctamente configurado
    echo.
    echo Puedes iniciar el sistema con: iniciar_sistema_corregido.bat
) else (
    echo [RESULTADO] HAY PROBLEMAS - Revisa los errores anteriores
    echo.
    echo Acciones recomendadas:
    echo 1. Si el VENV no existe: python -m venv D:\Mi-App-React\BUILD\venv
    echo 2. Si cryptography falta: instalar_cryptography.bat
    echo 3. Si hay imports faltantes: pip install -r requirements.txt
)

echo.
pause
