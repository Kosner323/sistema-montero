# 🚀 GUÍA RÁPIDA DE INICIO - POST DÍA 1

## ✅ Estado Actual
El problema de `ENCRYPTION_KEY` ha sido **RESUELTO**.

---

## 🎯 PARA INICIAR EL SISTEMA AHORA

### Opción 1: Inicio Rápido
```bash
cd /mnt/project
python3 app.py
```

### Opción 2: Con validación previa
```bash
# 1. Validar que todo está OK
cd /home/claude
python3 validate_day1.py

# 2. Si todo está verde, iniciar sistema
cd /mnt/project
python3 app.py
```

---

## 🔍 VERIFICAR QUE TODO FUNCIONA

### 1. Verificar logs al iniciar
Deberías ver algo como:
```
2025-10-31 XX:XX:XX | INFO | encryption | _initialize_fernet | Sistema de encriptación inicializado correctamente
```

### 2. Probar módulo de credenciales
1. Acceder a: http://localhost:5000/credenciales
2. Agregar una credencial de prueba
3. Verificar que se guarda correctamente
4. Verificar que se puede recuperar

### 3. Verificar encriptación en base de datos
```bash
cd /mnt/project
sqlite3 mi_sistema.db

# Ver las credenciales (deberían estar encriptadas)
SELECT * FROM credenciales_plataforma;

# Salir
.quit
```

Las contraseñas deberían verse como:
```
gAAAAABpBL5S9kNve_e24ZGFkRiWYS...
```

---

## 📁 ARCHIVOS IMPORTANTES GENERADOS

En `/mnt/user-data/outputs/`:
- 📄 `DIA_1_COMPLETADO.md` - Documentación completa
- 📄 `DIA_1_RESUMEN_EJECUTIVO.md` - Resumen visual
- 🐍 `fix_encryption_key.py` - Script generador de clave
- 🐍 `validate_day1.py` - Script de validación

---

## 🔐 CLAVE DE ENCRIPTACIÓN

### Ubicación
```
/mnt/project/_env (línea 19)
```

### Valor actual
```
ENCRYPTION_KEY=PtD_PO0CPR2ofUAtUcVEgAGPK4r1fLX8tuqjH-BjRvQ=
```

### ⚠️ IMPORTANTE
- **Guarda una copia de seguridad de esta clave**
- Sin ella, no podrás desencriptar las credenciales
- NO la compartas ni la subas a Git

### Cómo hacer backup
```bash
# Copiar a un lugar seguro
cp /mnt/project/_env ~/backup_env_$(date +%Y%m%d).txt

# O extraer solo la clave
grep ENCRYPTION_KEY /mnt/project/_env > ~/encryption_key_backup.txt
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Problema: "ENCRYPTION_KEY no encontrada"
**Solución:**
```bash
cd /home/claude
python3 fix_encryption_key.py
```

### Problema: "Error al desencriptar credenciales"
**Causa:** La clave cambió después de guardar credenciales

**Solución:**
1. Si tienes backup de la clave antigua, restáurala
2. Si no, las credenciales antiguas no se pueden recuperar
3. Elimina las credenciales antiguas y créalas nuevamente

### Problema: "El módulo encryption no funciona"
**Solución:**
```bash
cd /mnt/project
python3 test_encryption.py
```

Si todas las pruebas pasan, el problema está en otro lado.

---

## 📋 CHECKLIST PRE-PRODUCCIÓN

Antes de usar en producción, verifica:

- [ ] ✅ ENCRYPTION_KEY está en _env y no está vacía
- [ ] ✅ Backup de ENCRYPTION_KEY guardado en lugar seguro
- [ ] ✅ Archivo _env NO está en control de versiones (.gitignore)
- [ ] ✅ Pruebas de encriptación pasan (test_encryption.py)
- [ ] ✅ Validación del sistema pasa (validate_day1.py)
- [ ] ✅ Sistema Flask inicia sin errores
- [ ] ✅ Módulo de credenciales funciona correctamente
- [ ] ⚠️  Problemas de encoding UTF-8 pendientes (Día 2)
- [ ] ⚠️  SECRET_KEY por defecto (Día 4)

---

## 🎯 PRÓXIMOS PASOS (DÍAS SIGUIENTES)

### Día 2: Encoding UTF-8
Corregir caracteres corruptos en:
- app.py
- auth.py
- empresas.py
- Y otros archivos .py

### Día 3: Migrar Credenciales
Si ya tienes credenciales guardadas en texto plano:
```bash
cd /mnt/project
python3 migrate_encrypt_credentials.py
```

### Día 4: SECRET_KEY Segura
Cambiar la SECRET_KEY por defecto:
```python
# No usar esto en producción:
SECRET_KEY = 'default-secret-key-change-me'

# Usar esto:
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no definida")
```

---

## 📊 COMANDOS ÚTILES

### Ver estado actual
```bash
# Ver ENCRYPTION_KEY
grep ENCRYPTION_KEY /mnt/project/_env

# Validar sistema
python3 /home/claude/validate_day1.py

# Probar encriptación
cd /mnt/project && python3 test_encryption.py
```

### Logs del sistema
```bash
# Ver logs recientes
tail -f /mnt/project/logs/montero_app.log

# Ver solo errores
tail -f /mnt/project/logs/montero_errors.log
```

### Base de datos
```bash
# Conectar a la base de datos
sqlite3 /mnt/project/mi_sistema.db

# Ver todas las tablas
.tables

# Ver credenciales (encriptadas)
SELECT * FROM credenciales_plataforma;
```

---

## 💡 TIPS

1. **Siempre haz backup antes de cambios importantes**
   ```bash
   cp /mnt/project/_env /mnt/project/_env.backup.$(date +%Y%m%d)
   ```

2. **Verifica logs después de cada cambio**
   ```bash
   tail -n 50 /mnt/project/logs/montero_app.log
   ```

3. **Usa el script de validación frecuentemente**
   ```bash
   python3 /home/claude/validate_day1.py
   ```

---

## 🎉 ¡TODO LISTO!

El sistema está **listo para usar** con encriptación funcional.

**Siguiente paso:** Día 2 - Resolver problemas de encoding UTF-8

---

**Actualizado:** 31 de octubre de 2025  
**Sistema:** Montero v1.0  
**Estado:** ✅ Día 1 Completado
