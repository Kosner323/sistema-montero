@echo off
REM =========================================================
REM  INICIAR SISTEMA MONTERO
REM  Inicia el servidor Flask en http://localhost:5000
REM =========================================================

title Sistema Montero - Servidor Flask
color 0A

echo.
echo ========================================
echo   SISTEMA MONTERO - SERVIDOR FLASK
echo ========================================
echo.

REM Cambiar al directorio del proyecto
cd /d "D:\Mi-App-React"

REM Verificar entorno virtual
if exist ".venv\Scripts\python.exe" (
    echo [OK] Entorno virtual encontrado
    SET PYTHON=.venv\Scripts\python.exe
) else (
    echo [INFO] Usando Python del sistema
    SET PYTHON=python
)

echo.
echo [INFO] Iniciando servidor...
echo [INFO] URL: http://localhost:5000/login
echo [INFO] Para detener: Ctrl+C
echo.

REM Abrir navegador automaticamente (esperar 2 segundos)
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000/login"

REM Iniciar servidor
%PYTHON% app.py

echo.
echo [INFO] Servidor detenido
pause
