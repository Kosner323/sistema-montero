# 🚀 Inicio Rápido - Sistema de Backups Automáticos

## Sistema Montero v1.0

---

## ⚡ Instalación en 3 Pasos

### 1️⃣ Copiar Archivos
Copie todos los archivos a su proyecto:
```
sistema_backup.py
backup_config.ini
instalar_backups.ps1
INSTALAR_BACKUPS.bat
MANUAL_BACKUPS.md
diagnostico_backup.py
DIAGNOSTICO.bat
```

### 2️⃣ Ejecutar Instalador
- Click derecho en **INSTALAR_BACKUPS.bat**
- Seleccionar **"Ejecutar como administrador"**
- Seguir el asistente

### 3️⃣ ¡Listo!
El sistema está configurado y funcionando automáticamente.

---

## 📋 Verificación

### Probar el Sistema
```bash
# Opción 1: Ejecutar el diagnóstico
DIAGNOSTICO.bat

# Opción 2: Ejecutar backup de prueba
test_backup.bat
```

---

## 🎯 Uso Diario

### Backup Manual
```bash
# Doble click en:
ejecutar_backup.bat
```

### Ver Backups
```bash
python sistema_backup.py --list
```

### Restaurar
```bash
# Doble click en:
restaurar_backup.bat
```

---

## 📖 Documentación Completa

Para más detalles, consulte:
- **MANUAL_BACKUPS.md** - Documentación completa

---

## 🔧 Configuración

Editar **backup_config.ini** para cambiar:
- Hora del backup
- Días de retención
- Tipo de backup (estándar/completo)
- Archivos adicionales

---

## ✅ ¿Está Funcionando?

Verificar en:
1. **Directorio backups/** - Deben aparecer archivos .zip
2. **backups/backup.log** - Log de operaciones
3. **Programador de tareas** - Buscar "SistemaMonterBackup"

---

## 🆘 Problemas

### Python no encontrado
```bash
# Instalar desde:
https://www.python.org/downloads/

# Durante instalación, marcar:
☑ Add Python to PATH
```

### Tarea no se ejecuta
```bash
# 1. Abrir "Programador de tareas"
# 2. Buscar "SistemaMonterBackup"
# 3. Ejecutar manualmente para probar
```

### Más ayuda
Consulte **MANUAL_BACKUPS.md** sección "Solución de Problemas"

---

## 📞 Comandos Útiles

```bash
# Ayuda
python sistema_backup.py --help

# Backup completo
python sistema_backup.py --full

# Listar backups
python sistema_backup.py --list

# Limpiar antiguos
python sistema_backup.py --clean

# Restaurar último
python sistema_backup.py --restore latest

# Diagnóstico
python diagnostico_backup.py
```

---

## 🎉 ¡Sistema Listo!

Su Sistema Montero ahora tiene:
- ✅ Backups automáticos diarios
- ✅ Rotación automática de backups
- ✅ Sistema de recuperación
- ✅ Logging completo
- ✅ Production-ready

---

**¡Tus datos están protegidos!** 🔒

Sistema desarrollado para Sistema Montero  
Versión 1.0 - Noviembre 2025
