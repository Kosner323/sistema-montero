# 📋 GUÍA DE EJECUCIÓN - DÍA 3: MIGRAR CREDENCIALES EXISTENTES

**Fecha:** 31 de octubre de 2025  
**Objetivo:** Migrar todas las credenciales de texto plano a formato encriptado  
**Tiempo estimado:** 15-30 minutos

---

## 🎯 OBJETIVO DEL DÍA 3

Convertir todas las credenciales almacenadas en texto plano en la base de datos a formato encriptado, utilizando el sistema de encriptación implementado en los días anteriores.

---

## ✅ PRE-REQUISITOS

Antes de ejecutar la migración, verifica que:

- [x] **Día 1 completado:** ENCRYPTION_KEY generada en archivo `_env`
- [x] **Día 2 completado:** Archivos Python con encoding UTF-8 correcto
- [x] **Sistema funcionando:** El servidor Flask arranca sin errores
- [x] **Módulos disponibles:** `encryption.py` y `logger.py` funcionando

### Verificar pre-requisitos:

```bash
# 1. Verificar que existe el archivo _env con ENCRYPTION_KEY
cat _env | grep ENCRYPTION_KEY

# 2. Verificar que existe la base de datos
ls -lh mi_sistema.db

# 3. Verificar módulos Python
python -c "from encryption import encrypt_text; print('✅ encryption.py OK')"
python -c "from logger import get_logger; print('✅ logger.py OK')"
```

---

## 📦 ARCHIVOS DEL DÍA 3

Se han creado **2 scripts nuevos**:

### 1. `dia3_migrar_credenciales.py` (Principal)
- **Función:** Ejecuta la migración completa
- **Características:**
  - ✅ Crea respaldo automático de la BD
  - ✅ Analiza estado actual de credenciales
  - ✅ Migra credenciales de texto plano a encriptado
  - ✅ Verifica resultado de la migración
  - ✅ Genera reporte detallado

### 2. `validar_dia3.py` (Validador)
- **Función:** Valida que la migración fue exitosa
- **Características:**
  - ✅ Verifica ENCRYPTION_KEY
  - ✅ Prueba sistema de encriptación
  - ✅ Valida todas las credenciales en BD
  - ✅ Muestra tabla con resultados

---

## 🚀 PASO A PASO - EJECUCIÓN

### **PASO 1: Preparación**

```bash
# Ir al directorio del proyecto
cd /ruta/a/tu/proyecto

# Copiar los scripts al directorio principal
cp dia3_migrar_credenciales.py ./
cp validar_dia3.py ./

# Dar permisos de ejecución (Linux/Mac)
chmod +x dia3_migrar_credenciales.py validar_dia3.py
```

---

### **PASO 2: Ejecutar la Migración**

```bash
# Ejecutar el script de migración
python dia3_migrar_credenciales.py
```

**¿Qué hace el script?**

1. **Análisis inicial** (5 seg)
   - Busca la base de datos
   - Cuenta las credenciales
   - Identifica cuáles están en texto plano
   - Muestra tabla con el estado actual

2. **Respaldo de seguridad** (2 seg)
   - Crea carpeta `backups/` si no existe
   - Copia `mi_sistema.db` a `mi_sistema_backup_YYYYMMDD_HHMMSS.db`
   - Verifica el tamaño del respaldo

3. **Confirmación del usuario**
   - Pregunta: `¿Desea proceder con la migración? (s/n):`
   - Escribe `s` y presiona Enter

4. **Ejecución de la migración** (10-30 seg)
   - Procesa cada credencial
   - Encripta usuario y contraseña
   - Actualiza la base de datos
   - Muestra progreso en tiempo real

5. **Verificación automática** (5 seg)
   - Lee cada credencial encriptada
   - Intenta desencriptarla
   - Confirma que funciona correctamente

6. **Reporte final**
   - Muestra estadísticas completas
   - Indica ubicación del respaldo
   - Confirma éxito o errores

---

### **PASO 3: Validar el Resultado**

```bash
# Ejecutar el script de validación
python validar_dia3.py
```

**¿Qué hace el validador?**

1. **Verifica ENCRYPTION_KEY**
   - Confirma que existe en `_env`
   - Muestra su longitud
   - Preview de los primeros caracteres

2. **Prueba de encriptación**
   - Ejecuta 5 tests de roundtrip
   - Encripta → Desencripta → Compara
   - Verifica que el texto original se recupera

3. **Valida credenciales**
   - Lee todas las credenciales de la BD
   - Intenta desencriptarlas
   - Muestra tabla con resultados
   - Calcula tasa de éxito

4. **Resumen final**
   - ✅ o ❌ para cada componente
   - Recomendaciones si hay errores

---

## 📊 EJEMPLO DE SALIDA EXITOSA

```
╔═══════════════════════════════════════════════════════════════════╗
║       DÍA 3: MIGRACIÓN DE CREDENCIALES A ENCRIPTACIÓN            ║
╚═══════════════════════════════════════════════════════════════════╝

🔐 Verificando sistema de encriptación...
✅ Sistema de encriptación disponible

======================================================================
📊 ANÁLISIS DE CREDENCIALES EN BASE DE DATOS
======================================================================

📌 Total de credenciales: 25

----------------------------------------------------------------------
ID   1 | DIAN                           | 🔓 TEXTO PLANO
ID   2 | Seguridad Social               | 🔓 TEXTO PLANO
ID   3 | Parafiscales                   | 🔓 TEXTO PLANO
...
----------------------------------------------------------------------

📊 Resumen:
   🔒 Ya encriptadas: 0
   🔓 En texto plano: 25

💾 Creando respaldo de seguridad...
✅ Respaldo creado: backups/mi_sistema_backup_20251031_153022.db (245.50 KB)

======================================================================
¿Desea proceder con la migración? (s/n): s

======================================================================
🔐 INICIANDO MIGRACIÓN DE CREDENCIALES
======================================================================

📝 Procesando 25 credenciales...

  ✅ ID   1 | DIAN                           | Encriptada correctamente
  ✅ ID   2 | Seguridad Social               | Encriptada correctamente
  ✅ ID   3 | Parafiscales                   | Encriptada correctamente
  ...

✅ Cambios guardados en la base de datos

======================================================================
🔍 VERIFICANDO RESULTADO DE LA MIGRACIÓN
======================================================================

🔎 Verificando 25 credenciales...

  ✅ ID   1 | DIAN                           | Verificada OK
  ✅ ID   2 | Seguridad Social               | Verificada OK
  ✅ ID   3 | Parafiscales                   | Verificada OK
  ...

----------------------------------------------------------------------
✅ Verificadas correctamente: 25
⚠️  Con advertencias: 0
----------------------------------------------------------------------

======================================================================
📊 RESUMEN DE LA MIGRACIÓN
======================================================================

📈 Estadísticas:
   • Total procesadas:      25
   • Migradas exitosamente: 25
   • Ya encriptadas:        0
   • Errores:               0

💾 Respaldo guardado en: backups/mi_sistema_backup_20251031_153022.db

✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!
======================================================================

======================================================================
🎉 ¡DÍA 3 COMPLETADO EXITOSAMENTE!
======================================================================

✅ Logros del Día 3:
   • Credenciales migradas a formato encriptado
   • Respaldo de seguridad creado
   • Verificación de integridad completada
   • Sistema listo para uso seguro

📋 Próximo paso:
   DÍA 4: Implementar tests unitarios básicos
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "No se encontró la base de datos"

**Causa:** El script no encuentra `mi_sistema.db`

**Solución:**
```bash
# Buscar manualmente la base de datos
find . -name "mi_sistema.db"

# Si está en otro directorio, crear symlink o mover el script
```

---

### ❌ Error: "ModuleNotFoundError: No module named 'encryption'"

**Causa:** El script no puede importar el módulo de encriptación

**Solución:**
```bash
# Verificar que encryption.py existe
ls -l encryption.py

# Ejecutar desde el directorio correcto
cd /ruta/donde/está/encryption.py
python dia3_migrar_credenciales.py
```

---

### ❌ Error: "ENCRYPTION_KEY no definida"

**Causa:** La clave de encriptación no está en el archivo `_env`

**Solución:**
```bash
# Ejecutar el sistema una vez para generar la clave
python app.py

# O ejecutar el día 1 nuevamente
python fix_encryption_key.py
```

---

### ⚠️ Advertencia: "Ya encriptadas: 25"

**Causa:** Las credenciales ya fueron migradas anteriormente

**Solución:**
```
✅ No hacer nada - esto es normal si ejecutas el script múltiples veces
El script detecta automáticamente credenciales ya encriptadas
```

---

### ❌ Error: "Error migrando credencial X"

**Causa:** Problema específico con una credencial

**Solución:**
1. Revisar el log en `montero_errors.log`
2. Verificar que la credencial tenga datos válidos
3. Revisar manualmente en la BD:
```sql
SELECT * FROM credenciales_plataforma WHERE id = X;
```

---

## 📝 CHECKLIST POST-MIGRACIÓN

Después de completar el Día 3, verifica:

- [ ] El script de migración se ejecutó sin errores
- [ ] Existe un respaldo en la carpeta `backups/`
- [ ] El validador muestra "✅ VALIDACIÓN COMPLETA EXITOSA"
- [ ] Todas las credenciales tienen estado "✅ OK"
- [ ] El archivo `montero_app.log` tiene entradas de migración exitosa
- [ ] El sistema Flask sigue funcionando normalmente
- [ ] Puedes hacer login en el sistema
- [ ] Las plataformas muestran credenciales correctamente

---

## 🎯 CRITERIOS DE ÉXITO

El **Día 3 está completado** cuando:

1. ✅ **Migración exitosa:** 
   - 0 errores en la migración
   - Todas las credenciales encriptadas

2. ✅ **Respaldo creado:**
   - Archivo `backups/mi_sistema_backup_*.db` existe
   - Tamaño del respaldo > 0 KB

3. ✅ **Validación exitosa:**
   - Validador muestra 100% de éxito
   - Todas las credenciales se pueden desencriptar

4. ✅ **Sistema funcional:**
   - Flask arranca sin errores
   - Login funciona correctamente
   - Credenciales se muestran en el sistema

---

## 📚 RECURSOS ADICIONALES

### Archivos importantes:
- `encryption.py` - Sistema de encriptación
- `logger.py` - Sistema de logging
- `_env` - Variables de entorno (contiene ENCRYPTION_KEY)
- `mi_sistema.db` - Base de datos principal

### Logs para revisar:
- `montero_app.log` - Log general de la aplicación
- `montero_errors.log` - Log de errores

### Comando útiles:

```bash
# Ver últimas 20 líneas del log
tail -n 20 montero_app.log

# Buscar errores en el log
grep ERROR montero_errors.log

# Verificar tamaño de la BD
ls -lh mi_sistema.db

# Ver respaldos creados
ls -lh backups/

# Contar credenciales en BD
sqlite3 mi_sistema.db "SELECT COUNT(*) FROM credenciales_plataforma;"
```

---

## 🎉 ¡FELICITACIONES!

Si completaste todos los pasos y el validador muestra éxito, **¡has completado el Día 3!**

### Logros desbloqueados:
- 🔐 Credenciales 100% encriptadas
- 💾 Sistema de respaldos automático
- ✅ Validación de integridad
- 🛡️ Seguridad mejorada significativamente

### Siguiente paso:
**DÍA 4: Implementar Tests Unitarios Básicos**
- Instalar pytest
- Crear tests para auth.py
- Crear tests para encryption.py
- Lograr coverage > 70%

---

## 📞 SOPORTE

Si encuentras problemas:

1. **Revisa los logs:**
   - `montero_app.log`
   - `montero_errors.log`

2. **Ejecuta el validador:**
   ```bash
   python validar_dia3.py
   ```

3. **Verifica el respaldo:**
   ```bash
   ls -lh backups/
   ```

4. **Consulta el dictamen:**
   - `DICTAMEN_AVANCE_OCTUBRE_31_2025.md`

---

**¡Buena suerte con la migración!** 🚀
