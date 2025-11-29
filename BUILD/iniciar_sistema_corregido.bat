@echo off
REM =========================================================
REM  INICIAR SISTEMA - VERSIÓN CORREGIDA
REM  Inicia el servidor Flask y abre el navegador en la página de Login.
REM =========================================================

title Sistema de Formularios PDF - Inicializador
color 0A

REM Definir rutas absolutas (AJUSTAR ESTAS RUTAS SI SON DIFERENTES)
SET PROJECT_ROOT=D:\Mi-App-React\src\dashboard
SET VENV_PYTHON=D:\Mi-App-React\BUILD\venv\Scripts\python.exe
SET VENV_PIP=D:\Mi-App-React\BUILD\venv\Scripts\pip.exe

echo.
echo ========================================
echo   SISTEMA DE FORMULARIOS PDF
echo ========================================
echo.

REM =========================================================
REM  PASO 1: Verificar Entorno Virtual
REM =========================================================
echo [1/5] Verificando entorno virtual...

if not exist "%VENV_PYTHON%" (
    echo [ERROR] No se encontrÃ³ el entorno virtual
    echo Esperado en: %VENV_PYTHON%
    echo.
    echo Solucion: Crea el VENV con: python -m venv D:\Mi-App-React\BUILD\venv
    pause
    exit /b 1
)

echo [OK] Entorno virtual encontrado
echo.

REM =========================================================
REM  PASO 2: Verificar Cryptography
REM =========================================================
echo [2/5] Verificando cryptography...

"%VENV_PYTHON%" -c "import cryptography" 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo [ADVERTENCIA] Cryptography no estÃ¡ instalado
    echo.
    echo Â¿Deseas instalarlo ahora? (S/N)
    set /p RESPUESTA=
    
    if /i "%RESPUESTA%"=="S" (
        echo.
        echo [INFO] Instalando cryptography...
        "%VENV_PYTHON%" -m pip install cryptography --quiet --disable-pip-version-check
      
        REM Verificar nuevamente
        "%VENV_PYTHON%" -c "import cryptography" 2>nul
        
        if %ERRORLEVEL% EQU 0 (
            echo [OK] Cryptography instalado correctamente
        ) else (
            echo [ERROR] No se pudo instalar cryptography
            echo Ejecuta manualmente: instalar_cryptography.bat
            pause
            exit /b 1
        )
    ) else (
        echo [ADVERTENCIA] Continuando sin cryptography (puede causar errores)
    )
) else (
    echo [OK] Cryptography estÃ¡ instalado
)

echo.
REM =========================================================
REM  PASO 3: Instalar/Actualizar Dependencias
REM =========================================================
echo [3/5] Verificando dependencias...

cd /d "%PROJECT_ROOT%"

if exist "requirements.txt" (
    echo [INFO] Instalando dependencias desde requirements.txt...
    "%VENV_PYTHON%" -m pip install -r requirements.txt --quiet --disable-pip-version-check
    echo [OK] Dependencias verificadas
) else (
    echo [ADVERTENCIA] No se encontrÃ³ requirements.txt
)

echo.
REM =========================================================
REM  PASO 4: Verificar Base de Datos
REM =========================================================
echo [4/5] Verificando base de datos...

if exist "mi_sistema.db" (
    echo [OK] Base de datos encontrada
) else (
    echo [INFO] Base de datos no encontrada, se crearÃ¡ al iniciar
)

REM Preguntar por datos de prueba (opcional)
if exist "DATOS_DE_PRUEBA.py" (
    echo.
    echo Â¿Deseas cargar datos de prueba? (S/N)
    set /p RESPUESTA_DATOS=
    
    if /i "%RESPUESTA_DATOS%"=="S" (
        echo [INFO] Cargando datos de prueba...
        "%VENV_PYTHON%" DATOS_DE_PRUEBA.py
        echo [OK] Datos cargados
    )
)

echo.
REM =========================================================
REM  PASO 5: Iniciar Servidor
REM =========================================================
echo [5/5] Iniciando servidor...
echo.
echo ========================================
echo   SERVIDOR FLASK BACKEND
echo ========================================
echo.
REM === CORRECCIÓN APLICADA AQUÍ ===
echo [INFO] URL: http://localhost:5000/ingresoportal.html
echo [INFO] Para detener: Ctrl+C
echo.

REM Abrir navegador automÃ¡ticamente (esperar 3 segundos)
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:5000/ingresoportal.html"

REM Iniciar servidor (usa el Python del VENV)
"%VENV_PYTHON%" app.py

REM Si el servidor se detiene
echo.
echo [INFO] Servidor detenido
pause