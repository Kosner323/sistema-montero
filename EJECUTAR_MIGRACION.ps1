# ================================================================
# SCRIPT DE MIGRACIÓN DE BASE DE DATOS (PowerShell)
# ================================================================
# Agrega columnas faltantes a las tablas empresas y usuarios
# ================================================================

Write-Host ""
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host "         MIGRACIÓN DE BASE DE DATOS - FIX_DB.PY" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en la carpeta correcta
if (-not (Test-Path "fix_db.py")) {
    Write-Host "[ERROR] No se encontró fix_db.py en la carpeta actual" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, ejecuta este script desde: src\dashboard\" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar si existe Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[INFO] Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Instala Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""

# Verificar base de datos
if (Test-Path "data\mi_sistema.db") {
    Write-Host "[INFO] Base de datos encontrada: data\mi_sistema.db" -ForegroundColor Green
} else {
    Write-Host "[ADVERTENCIA] No se encontró data\mi_sistema.db" -ForegroundColor Yellow
    Write-Host "              El script buscará en ubicaciones alternativas..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[EJECUTANDO] Migración de base de datos..." -ForegroundColor Cyan
Write-Host ""

# Ejecutar el script de migración
try {
    python fix_db.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "====================================================================" -ForegroundColor Green
        Write-Host "         MIGRACIÓN COMPLETADA EXITOSAMENTE" -ForegroundColor Green
        Write-Host "====================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "[SIGUIENTE PASO] Reinicia la aplicación Flask:" -ForegroundColor Cyan
        Write-Host "   python app.py" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "[ERROR] La migración falló con código de salida: $LASTEXITCODE" -ForegroundColor Red
        Write-Host ""
    }
} catch {
    Write-Host ""
    Write-Host "[ERROR] Error al ejecutar fix_db.py: $_" -ForegroundColor Red
    Write-Host ""
}

Read-Host "Presiona Enter para salir"
