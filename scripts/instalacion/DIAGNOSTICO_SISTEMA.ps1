# ==========================================
#   DIAGNÓSTICO DE SISTEMA
#   Sistema Montero - Backups Automáticos
# ==========================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  DIAGNÓSTICO DEL SISTEMA" -ForegroundColor Yellow
Write-Host "  Sistema Montero v1.0" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$errores = 0
$advertencias = 0

# --- 1. Verificar permisos de administrador ---
Write-Host "[1/7] Verificando permisos de administrador..." -ForegroundColor White
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Host "  ✓ Ejecutando como administrador" -ForegroundColor Green
} else {
    Write-Host "  ✗ NO se está ejecutando como administrador" -ForegroundColor Red
    Write-Host "    Solución: Haz clic derecho > Ejecutar como administrador" -ForegroundColor Yellow
    $errores++
}
Write-Host ""

# --- 2. Verificar Python ---
Write-Host "[2/7] Verificando instalación de Python..." -ForegroundColor White

$pythonPaths = @("python", "py", "C:\Python311\python.exe", "C:\Python312\python.exe")
$pythonExe = $null
$pythonVersion = $null

foreach ($path in $pythonPaths) {
    try {
        $version = & $path --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $path
            $pythonVersion = $version
            break
        }
    } catch {}
}

if ($pythonExe) {
    Write-Host "  ✓ Python encontrado: $pythonExe" -ForegroundColor Green
    Write-Host "    Versión: $pythonVersion" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Python NO encontrado" -ForegroundColor Red
    Write-Host "    Solución: Instalar desde https://www.python.org/downloads/" -ForegroundColor Yellow
    $errores++
}
Write-Host ""

# --- 3. Verificar archivos necesarios ---
Write-Host "[3/7] Verificando archivos del sistema..." -ForegroundColor White

$scriptDir = Split-Path -Parent $PSCommandPath
$archivosNecesarios = @(
    "sistema_backup.py",
    "instalar_backups.ps1"
)

foreach ($archivo in $archivosNecesarios) {
    $rutaCompleta = Join-Path $scriptDir $archivo
    if (Test-Path $rutaCompleta) {
        Write-Host "  ✓ $archivo" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $archivo NO encontrado" -ForegroundColor Red
        $errores++
    }
}
Write-Host ""

# --- 4. Verificar servicio Programador de Tareas ---
Write-Host "[4/7] Verificando Programador de Tareas de Windows..." -ForegroundColor White

try {
    $servicio = Get-Service -Name "Schedule" -ErrorAction Stop
    if ($servicio.Status -eq "Running") {
        Write-Host "  ✓ Servicio 'Programador de Tareas' activo" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Servicio 'Programador de Tareas' detenido" -ForegroundColor Yellow
        Write-Host "    Solución: Iniciar el servicio desde services.msc" -ForegroundColor Yellow
        $advertencias++
    }
} catch {
    Write-Host "  ✗ Error al verificar el servicio" -ForegroundColor Red
    $errores++
}
Write-Host ""

# --- 5. Verificar permisos en carpeta de destino ---
Write-Host "[5/7] Verificando permisos de escritura..." -ForegroundColor White

$backupFolder = "D:\Mi-App-React\src\dashboard\backups"
$testFile = Join-Path $backupFolder "_test_permisos.tmp"

try {
    # Crear carpeta si no existe
    if (!(Test-Path $backupFolder)) {
        New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null
    }
    
    # Intentar crear archivo de prueba
    "test" | Out-File -FilePath $testFile -Force
    Remove-Item $testFile -Force
    
    Write-Host "  ✓ Permisos de escritura correctos" -ForegroundColor Green
    Write-Host "    Carpeta: $backupFolder" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ Sin permisos de escritura en: $backupFolder" -ForegroundColor Red
    Write-Host "    Error: $_" -ForegroundColor Yellow
    $errores++
}
Write-Host ""

# --- 6. Verificar espacio en disco ---
Write-Host "[6/7] Verificando espacio en disco..." -ForegroundColor White

try {
    $drive = Get-PSDrive -Name D -ErrorAction Stop
    $espacioLibreGB = [math]::Round($drive.Free / 1GB, 2)
    
    if ($espacioLibreGB -gt 1) {
        Write-Host "  ✓ Espacio disponible: $espacioLibreGB GB" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Poco espacio disponible: $espacioLibreGB GB" -ForegroundColor Yellow
        Write-Host "    Recomendado: Al menos 1 GB libre" -ForegroundColor Yellow
        $advertencias++
    }
} catch {
    Write-Host "  ⚠ No se pudo verificar espacio en disco D:" -ForegroundColor Yellow
    $advertencias++
}
Write-Host ""

# --- 7. Verificar tareas programadas existentes ---
Write-Host "[7/7] Verificando tareas programadas existentes..." -ForegroundColor White

try {
    $tarea = Get-ScheduledTask -TaskName "BackupAutomaticoMontero" -ErrorAction SilentlyContinue
    if ($tarea) {
        Write-Host "  ⚠ Ya existe una tarea programada con este nombre" -ForegroundColor Yellow
        Write-Host "    Estado: $($tarea.State)" -ForegroundColor Gray
        Write-Host "    Nota: Se reemplazará durante la instalación" -ForegroundColor Gray
        $advertencias++
    } else {
        Write-Host "  ✓ No hay conflictos de tareas programadas" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ No se pudo verificar tareas programadas" -ForegroundColor Yellow
    $advertencias++
}
Write-Host ""

# --- Resumen ---
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN DEL DIAGNÓSTICO" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($errores -eq 0 -and $advertencias -eq 0) {
    Write-Host "✓ TODO CORRECTO" -ForegroundColor Green
    Write-Host ""
    Write-Host "El sistema está listo para instalar backups automáticos" -ForegroundColor White
    Write-Host "Ejecuta: INSTALAR_BACKUPS_ADMIN.bat" -ForegroundColor Cyan
} elseif ($errores -eq 0) {
    Write-Host "⚠ SISTEMA FUNCIONAL CON ADVERTENCIAS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Advertencias encontradas: $advertencias" -ForegroundColor Yellow
    Write-Host "Puedes continuar, pero revisa las advertencias arriba" -ForegroundColor White
} else {
    Write-Host "✗ ERRORES ENCONTRADOS" -ForegroundColor Red
    Write-Host ""
    Write-Host "Errores críticos: $errores" -ForegroundColor Red
    Write-Host "Advertencias: $advertencias" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Debes corregir los errores antes de instalar" -ForegroundColor White
}

Write-Host ""
Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
