# ==========================================
#   INSTALADOR DE BACKUPS AUTOMÁTICOS
#   Sistema Montero v1.0
# ==========================================

# Configurar codificación UTF-8 para la consola
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Verificar si se está ejecutando como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "===========================================" -ForegroundColor Red
    Write-Host "  ATENCIÓN: Se requieren permisos de administrador" -ForegroundColor Yellow
    Write-Host "===========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Este instalador necesita permisos de administrador para:" -ForegroundColor White
    Write-Host "  • Crear tareas programadas en Windows" -ForegroundColor Cyan
    Write-Host "  • Configurar backups automáticos" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Solicitando elevación de permisos..." -ForegroundColor Yellow
    Write-Host ""
    
    # Reiniciar el script con permisos de administrador
    Start-Process powershell.exe -Verb RunAs -ArgumentList ("-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"") -Wait
    exit
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  INSTALADOR DE BACKUPS AUTOMÁTICOS" -ForegroundColor Yellow
Write-Host "  Sistema Montero v1.0" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Ejecutando con permisos de administrador" -ForegroundColor Green
Write-Host ""

# --- Verificar Python ---
Write-Host "Verificando instalación de Python..." -ForegroundColor White

$pythonPaths = @("python", "py", "C:\Python311\python.exe", "C:\Python312\python.exe")
$pythonExe = $null

foreach ($path in $pythonPaths) {
    try {
        $version = & $path --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $path
            Write-Host "✓ Python encontrado en: $pythonExe" -ForegroundColor Green
            Write-Host "  Versión: $version" -ForegroundColor Gray
            break
        }
    } catch {}
}

if (-not $pythonExe) {
    Write-Host "✗ Python no está instalado o no se encontró en el sistema." -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor instala Python 3.11 o superior desde:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host ""
    Pause
    exit
}

Write-Host ""

# --- Verificar script de backup ---
$scriptDir = Split-Path -Parent $PSCommandPath
$pythonScript = Join-Path $scriptDir "sistema_backup.py"

if (!(Test-Path $pythonScript)) {
    Write-Host "✗ No se encontró el archivo sistema_backup.py" -ForegroundColor Red
    Write-Host "  Ruta esperada: $pythonScript" -ForegroundColor Yellow
    Write-Host ""
    Pause
    exit
}

Write-Host "✓ Script de backup encontrado" -ForegroundColor Green
Write-Host ""

# --- Crear carpeta de backups ---
$backupFolder = "D:\Mi-App-React\src\dashboard\backups"

Write-Host "Verificando carpeta de backups..." -ForegroundColor White

if (!(Test-Path $backupFolder)) {
    try {
        New-Item -ItemType Directory -Path $backupFolder -Force | Out-Null
        Write-Host "✓ Carpeta de backups creada en: $backupFolder" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error al crear carpeta de backups: $_" -ForegroundColor Red
        Write-Host ""
        Pause
        exit
    }
} else {
    Write-Host "✓ Carpeta de backups ya existe: $backupFolder" -ForegroundColor Green
}
Write-Host ""

# --- Programar tarea en Windows ---
$taskName = "BackupAutomaticoMontero"

Write-Host "Configurando tarea programada..." -ForegroundColor White
Write-Host "  Nombre: $taskName" -ForegroundColor Gray
Write-Host "  Frecuencia: Diaria a las 09:00 AM" -ForegroundColor Gray
Write-Host ""

try {
    # Eliminar tarea existente si la hay
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "  Eliminando tarea anterior..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }
    
    # Crear nueva tarea programada
    $action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$pythonScript`"" -WorkingDirectory $scriptDir
    $trigger = New-ScheduledTaskTrigger -Daily -At 9am
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U
    
    Register-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Principal $principal -TaskName $taskName -Description "Backup automático del sistema Montero - Base de datos y archivos" -Force | Out-Null
    
    Write-Host "✓ Tarea programada creada exitosamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "La tarea se ejecutará:" -ForegroundColor Cyan
    Write-Host "  • Todos los días a las 09:00 AM" -ForegroundColor White
    Write-Host "  • Incluso si el equipo está desconectado (se ejecutará al reconectar)" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "✗ Error al crear la tarea programada: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Posibles soluciones:" -ForegroundColor Yellow
    Write-Host "  1. Ejecuta este script como administrador" -ForegroundColor White
    Write-Host "  2. Verifica que el servicio 'Programador de tareas' esté activo" -ForegroundColor White
    Write-Host ""
}

# --- Probar backup manual ---
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ¿Deseas ejecutar un backup de prueba?" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona 'S' para ejecutar backup ahora, o cualquier otra tecla para salir" -ForegroundColor White

$respuesta = Read-Host

if ($respuesta -eq 'S' -or $respuesta -eq 's') {
    Write-Host ""
    Write-Host "Ejecutando backup de prueba..." -ForegroundColor Cyan
    Write-Host ""
    
    try {
        & $pythonExe $pythonScript
        Write-Host ""
        Write-Host "✓ Backup de prueba completado" -ForegroundColor Green
    } catch {
        Write-Host "✗ Error durante el backup de prueba: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Instalación completada" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para verificar la tarea programada, abre:" -ForegroundColor White
Write-Host "  Programador de tareas > Biblioteca del programador de tareas" -ForegroundColor Cyan
Write-Host ""
Write-Host "Gracias por usar el Sistema de Backups Automáticos!" -ForegroundColor Yellow
Write-Host ""
Pause
