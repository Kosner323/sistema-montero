@echo off
REM ================================================================
REM SCRIPT: Actualizar tabla empresas con columnas de rutas
REM ================================================================
echo.
echo ====================================================================
echo   ACTUALIZACION DE BASE DE DATOS - TABLA EMPRESAS
echo ====================================================================
echo.
echo Este script agregara las siguientes columnas a la tabla empresas:
echo   - ruta_carpeta
echo   - ruta_firma
echo   - ruta_logo
echo   - ruta_rut
echo   - ruta_camara_comercio
echo   - ruta_cedula_representante
echo   - ruta_arl
echo   - ruta_cuenta_bancaria
echo   - ruta_carta_autorizacion
echo.

REM Verificar si existe la base de datos
if not exist "data\montero.db" (
    echo [ERROR] No se encontro la base de datos en: data\montero.db
    echo Por favor, ejecute este script desde: src\dashboard\
    pause
    exit /b 1
)

REM Verificar si existe el archivo SQL
if not exist "sql\add_empresas_rutas.sql" (
    echo [ERROR] No se encontro el archivo: sql\add_empresas_rutas.sql
    pause
    exit /b 1
)

echo [INFO] Base de datos encontrada: data\montero.db
echo [INFO] Script SQL encontrado: sql\add_empresas_rutas.sql
echo.

REM Crear backup de la base de datos
echo [BACKUP] Creando copia de seguridad...
set FECHA=%date:~-4%%date:~3,2%%date:~0,2%
set HORA=%time:~0,2%%time:~3,2%%time:~6,2%
set HORA=%HORA: =0%
copy data\montero.db "data\montero_backup_%FECHA%_%HORA%.db" >nul

if errorlevel 1 (
    echo [ERROR] No se pudo crear el backup
    pause
    exit /b 1
)

echo [OK] Backup creado: montero_backup_%FECHA%_%HORA%.db
echo.

REM Ejecutar el script SQL
echo [EJECUTANDO] Aplicando cambios a la base de datos...
echo.

sqlite3 data\montero.db < sql\add_empresas_rutas.sql

if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un error al ejecutar el script SQL
    echo [SOLUCION] Restaure el backup si es necesario:
    echo    copy data\montero_backup_%FECHA%_%HORA%.db data\montero.db
    pause
    exit /b 1
)

echo.
echo [OK] Script ejecutado exitosamente
echo.

REM Verificar cambios
echo [VERIFICANDO] Comprobando estructura de la tabla empresas...
echo.

echo PRAGMA table_info(empresas); | sqlite3 data\montero.db > temp_schema.txt

findstr /C:"ruta_carpeta" temp_schema.txt >nul
if errorlevel 1 (
    echo [ERROR] La columna ruta_carpeta NO fue creada
    del temp_schema.txt
    pause
    exit /b 1
)

echo [OK] Columnas agregadas correctamente:
echo      - ruta_carpeta
echo      - ruta_firma
echo      - ruta_logo
echo      - ruta_rut
echo      - ruta_camara_comercio
echo      - ruta_cedula_representante
echo      - ruta_arl
echo      - ruta_cuenta_bancaria
echo      - ruta_carta_autorizacion
echo.

del temp_schema.txt

echo ====================================================================
echo   ACTUALIZACION COMPLETADA EXITOSAMENTE
echo ====================================================================
echo.
echo [SIGUIENTE PASO] 
echo 1. Reinicie la aplicacion Flask
echo 2. Pruebe creando una empresa desde el formulario
echo 3. Verifique que se genere la carpeta en:
echo    D:\Mi-App-React\MONTERO_NEGOCIO\MONTERO_TOTAL\EMPRESAS\
echo.

pause
