# 🔧 GUÍA DE INSTALACIÓN DE BACKUPS AUTOMÁTICOS
## Sistema Montero v1.0

---

## 📋 TABLA DE CONTENIDOS
1. [Problema Identificado](#problema-identificado)
2. [Soluciones Disponibles](#soluciones-disponibles)
3. [Instalación Paso a Paso](#instalación-paso-a-paso)
4. [Solución de Problemas](#solución-de-problemas)
5. [Verificación Post-Instalación](#verificación-post-instalación)

---

## 🔴 PROBLEMA IDENTIFICADO

### Error Principal
```
No se pudo crear la tarea programada. Ejecuta como administrador.
```

### Causas
1. **Falta de permisos de administrador**: El Programador de Tareas de Windows requiere privilegios elevados
2. **Codificación incorrecta**: Caracteres como "AUTOMÃTICOS" indican problema de UTF-8

---

## ✅ SOLUCIONES DISPONIBLES

Se han creado **3 archivos mejorados** para resolver ambos problemas:

### 1. `instalar_backups_MEJORADO.ps1`
**Características:**
- ✓ Auto-elevación de permisos (solicita automáticamente permisos de admin)
- ✓ Codificación UTF-8 correcta
- ✓ Validación completa de Python
- ✓ Verificación de archivos necesarios
- ✓ Opción de backup de prueba
- ✓ Mensajes informativos mejorados

### 2. `INSTALAR_BACKUPS_ADMIN.bat`
**Características:**
- ✓ Detección automática de permisos
- ✓ Solicitud de elevación si es necesario
- ✓ Codificación UTF-8 para la consola
- ✓ Manejo de errores mejorado

### 3. Esta guía (`GUIA_INSTALACION_BACKUPS.md`)
- ✓ Instrucciones paso a paso
- ✓ Solución de problemas comunes
- ✓ Procedimientos de verificación

---

## 📦 INSTALACIÓN PASO A PASO

### MÉTODO 1: Usando el archivo .BAT (Más fácil)

#### Paso 1: Copiar archivos
Copia estos archivos nuevos a tu carpeta del proyecto:
```
D:\Mi-App-React\src\dashboard\
├── INSTALAR_BACKUPS_ADMIN.bat  ← Nuevo archivo
├── instalar_backups.ps1         ← Reemplaza el existente con instalar_backups_MEJORADO.ps1
└── sistema_backup.py
```

#### Paso 2: Ejecutar instalador
1. Haz **doble clic** en `INSTALAR_BACKUPS_ADMIN.bat`
2. Windows te mostrará un cuadro de diálogo de Control de Cuentas de Usuario (UAC)
3. Haz clic en **"Sí"** para permitir la ejecución con permisos de administrador
4. El instalador se ejecutará automáticamente

#### Paso 3: Seguir instrucciones en pantalla
- El script verificará Python ✓
- Creará la carpeta de backups ✓
- Configurará la tarea programada ✓
- Te preguntará si quieres hacer un backup de prueba

---

### MÉTODO 2: Usando PowerShell directamente

#### Paso 1: Reemplazar archivo
1. Renombra `instalar_backups_MEJORADO.ps1` a `instalar_backups.ps1`
2. Reemplaza el archivo existente en tu proyecto

#### Paso 2: Ejecutar con permisos
1. Haz **clic derecho** en `instalar_backups.ps1`
2. Selecciona **"Ejecutar con PowerShell"**
3. El script solicitará automáticamente permisos de administrador
4. Haz clic en **"Sí"** cuando aparezca el UAC

---

### MÉTODO 3: Desde PowerShell como Administrador (Manual)

#### Paso 1: Abrir PowerShell como Admin
1. Presiona `Win + X`
2. Selecciona **"Windows PowerShell (Administrador)"** o **"Terminal (Admin)"**
3. Haz clic en **"Sí"** en el UAC

#### Paso 2: Navegar a la carpeta
```powershell
cd "D:\Mi-App-React\src\dashboard"
```

#### Paso 3: Ejecutar instalador
```powershell
.\instalar_backups.ps1
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Problema 1: "No se puede ejecutar scripts en este sistema"

**Error:**
```
No se puede cargar el archivo porque la ejecución de scripts está deshabilitada
```

**Solución:**
1. Abre PowerShell como administrador
2. Ejecuta:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
3. Confirma con `S` o `Y`

---

### Problema 2: Sigue apareciendo error de permisos

**Causas posibles:**
- El servicio "Programador de Tareas" está detenido
- Restricciones de políticas de grupo (en equipos corporativos)
- Antivirus bloqueando la acción

**Soluciones:**

#### A. Verificar servicio Programador de Tareas
1. Presiona `Win + R`
2. Escribe: `services.msc`
3. Busca **"Programador de tareas"** (Task Scheduler)
4. Verifica que esté **"Ejecutándose"**
5. Si está detenido, haz clic derecho → **Iniciar**

#### B. Crear la tarea manualmente
Si el script sigue fallando, crea la tarea manualmente:

1. Abre el **Programador de Tareas**:
   - `Win + R` → `taskschd.msc` → Enter

2. En el panel derecho, haz clic en **"Crear tarea básica"**

3. Completa el asistente:
   - **Nombre:** BackupAutomaticoMontero
   - **Descripción:** Backup automático del sistema Montero
   - **Desencadenador:** Diariamente
   - **Hora:** 9:00 AM
   - **Acción:** Iniciar un programa
   - **Programa:** Ruta de Python (ejemplo: `C:\Python311\python.exe`)
   - **Argumentos:** `"D:\Mi-App-React\src\dashboard\sistema_backup.py"`

4. Marca: **"Ejecutar con los privilegios más altos"**

5. Haz clic en **Finalizar**

---

### Problema 3: Caracteres raros en la consola

**Síntoma:**
```
INSTALADOR DE BACKUPS AUTOMÃTICOS
```

**Solución:**
Los archivos nuevos ya tienen la codificación UTF-8 correcta. Si sigues viendo problemas:

1. Abre PowerShell
2. Ejecuta:
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```
3. Vuelve a ejecutar el instalador

---

### Problema 4: Python no encontrado

**Error:**
```
Python no está instalado o no se encontró en el sistema
```

**Solución:**
1. Descarga Python desde: https://www.python.org/downloads/
2. Durante la instalación, marca: **"Add Python to PATH"**
3. Reinicia tu computadora
4. Vuelve a ejecutar el instalador

---

## ✓ VERIFICACIÓN POST-INSTALACIÓN

### 1. Verificar que la tarea se creó correctamente

#### Opción A: Desde PowerShell
```powershell
Get-ScheduledTask -TaskName "BackupAutomaticoMontero"
```

**Resultado esperado:**
```
TaskPath  TaskName                   State
--------  --------                   -----
\         BackupAutomaticoMontero    Ready
```

#### Opción B: Desde Programador de Tareas
1. Presiona `Win + R`
2. Escribe: `taskschd.msc`
3. En **"Biblioteca del Programador de tareas"**
4. Busca: **"BackupAutomaticoMontero"**

### 2. Ejecutar un backup de prueba manual

Opción 1 - Desde el instalador:
- Durante la instalación, responde **"S"** cuando pregunte si quieres ejecutar backup de prueba

Opción 2 - Manual:
```powershell
cd "D:\Mi-App-React\src\dashboard"
python sistema_backup.py
```

### 3. Verificar que se crearon los backups

Revisa la carpeta:
```
D:\Mi-App-React\src\dashboard\backups\
```

Deberías ver archivos como:
- `backup_YYYYMMDD_HHMMSS.zip`
- `mi_sistema_YYYYMMDD_HHMMSS.db`

---

## 📊 MEJORAS IMPLEMENTADAS

### Comparación: Antes vs Ahora

| Característica | Antes | Ahora |
|----------------|-------|-------|
| Solicitud de permisos | ❌ Manual | ✅ Automática |
| Codificación | ❌ ANSI/Latin1 | ✅ UTF-8 |
| Validación Python | ⚠️ Básica | ✅ Completa |
| Verificación archivos | ❌ No | ✅ Sí |
| Backup de prueba | ❌ No | ✅ Opcional |
| Manejo de errores | ⚠️ Básico | ✅ Completo |
| Mensajes informativos | ⚠️ Limitados | ✅ Detallados |

---

## 🎯 RESUMEN EJECUTIVO

### Para instalar los backups automáticos:

1. **Usa el archivo `INSTALAR_BACKUPS_ADMIN.bat`**
   - Doble clic
   - Acepta permisos de administrador
   - Sigue las instrucciones

2. **O usa `instalar_backups_MEJORADO.ps1`**
   - Renómbralo a `instalar_backups.ps1`
   - Doble clic o ejecuta desde PowerShell
   - Acepta permisos cuando se soliciten

3. **Verifica la instalación**
   - Abre el Programador de Tareas
   - Busca "BackupAutomaticoMontero"
   - Ejecuta un backup de prueba

### ¿Problemas?
- Revisa la sección [Solución de Problemas](#solución-de-problemas)
- Verifica que el servicio "Programador de Tareas" esté activo
- Crea la tarea manualmente si es necesario

---

## 📞 CONTACTO Y SOPORTE

Si continúas teniendo problemas después de seguir esta guía:

1. Verifica que tengas permisos de administrador en tu equipo
2. Si es un equipo corporativo, consulta con tu departamento de IT
3. Revisa los logs del sistema en el Visor de Eventos de Windows

---

**Fecha de creación:** 02/11/2025  
**Versión del sistema:** Montero v1.0  
**Autor:** Sistema de Backups Automáticos
