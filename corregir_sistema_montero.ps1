# ========================================
# Script de Corrección del Sistema Montero
# Ejecutar desde: D:\Mi-App-React\src\dashboard
# Uso: .\corregir_sistema_montero.ps1
# ========================================

Write-Host ""
Write-Host "========================================"
Write-Host "  CORRECCIÓN DEL SISTEMA MONTERO"
Write-Host "========================================"
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "app.py")) {
    Write-Host "[ERROR] No se encuentra app.py" -ForegroundColor Red
    Write-Host "Este script debe ejecutarse desde la carpeta 'dashboard'" -ForegroundColor Red
    Write-Host ""
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host "[1/5] Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no está instalado o no está en el PATH" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "[2/5] Creando estructura de assets..." -ForegroundColor Cyan
$assetsPaths = @(
    "assets",
    "assets\css",
    "assets\js",
    "assets\images",
    "assets\fonts"
)

foreach ($path in $assetsPaths) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}
Write-Host "[OK] Estructura de assets creada" -ForegroundColor Green

Write-Host ""
Write-Host "[3/5] Verificando archivos de scripts..." -ForegroundColor Cyan
$scriptsRequeridos = @(
    "corregir_rutas_assets.py",
    "verificar_sistema_montero.py"
)

$scriptsFaltantes = @()
foreach ($script in $scriptsRequeridos) {
    if (-not (Test-Path $script)) {
        $scriptsFaltantes += $script
    }
}

if ($scriptsFaltantes.Count -gt 0) {
    Write-Host "[ADVERTENCIA] Faltan algunos scripts:" -ForegroundColor Yellow
    foreach ($script in $scriptsFaltantes) {
        Write-Host "  - $script" -ForegroundColor Yellow
    }
    Write-Host "Descárgalos de los archivos que te compartí" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Todos los scripts disponibles" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/5] Copiando archivos de assets..." -ForegroundColor Cyan
$origenAssets = "..\assets"
$destinoAssets = "assets"

if (Test-Path $origenAssets) {
    Write-Host "Copiando desde: $origenAssets" -ForegroundColor White
    try {
        Copy-Item -Path "$origenAssets\*" -Destination $destinoAssets -Recurse -Force
        Write-Host "[OK] Assets copiados correctamente" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] No se pudieron copiar los assets: $_" -ForegroundColor Red
    }
} else {
    Write-Host "[ADVERTENCIA] No se encontró la carpeta: $origenAssets" -ForegroundColor Yellow
    Write-Host "Deberás copiar manualmente los assets" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/5] Ejecutando verificación del sistema..." -ForegroundColor Cyan
if (Test-Path "verificar_sistema_montero.py") {
    python verificar_sistema_montero.py
} else {
    Write-Host "[ADVERTENCIA] No se encontró verificar_sistema_montero.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================"
Write-Host "  PROCESO COMPLETADO"
Write-Host "========================================"
Write-Host ""
Write-Host "Archivos de assets:" -ForegroundColor Cyan
if (Test-Path "assets\css\style.css") {
    Write-Host "  [OK] CSS principal encontrado" -ForegroundColor Green
} else {
    Write-Host "  [!] CSS principal NO encontrado" -ForegroundColor Yellow
}

if (Test-Path "assets\fonts") {
    $fontCount = (Get-ChildItem "assets\fonts" -Recurse -File).Count
    Write-Host "  [OK] Fuentes: $fontCount archivos" -ForegroundColor Green
} else {
    Write-Host "  [!] Carpeta de fuentes vacía" -ForegroundColor Yellow
}

if (Test-Path "assets\images") {
    $imgCount = (Get-ChildItem "assets\images" -File).Count
    Write-Host "  [OK] Imágenes: $imgCount archivos" -ForegroundColor Green
} else {
    Write-Host "  [!] Carpeta de imágenes vacía" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Para iniciar el servidor:" -ForegroundColor Cyan
Write-Host "  python app.py" -ForegroundColor White
Write-Host "  o" -ForegroundColor White
Write-Host "  .\iniciar_sistema_corregido.bat" -ForegroundColor White
Write-Host ""
Write-Host "URL: http://127.0.0.1:5000/ingresoportal.html" -ForegroundColor White
Write-Host ""

Read-Host "Presiona Enter para salir"
