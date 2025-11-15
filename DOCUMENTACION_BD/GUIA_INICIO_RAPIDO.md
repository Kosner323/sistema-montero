# 🚀 GUÍA DE INICIO RÁPIDO - COVERAGE 80%

## 📋 RESUMEN EJECUTIVO

**Objetivo:** Aumentar coverage de 7% a 80%+
**Tiempo:** 10 días (40 horas @ 4h/día)
**Inicio:** 12 de noviembre de 2025
**Día 1 Focus:** Tests de auth.py (18+ tests, 80% coverage)

---

## ⚡ INICIO RÁPIDO (5 MINUTOS)

### Paso 1: Preparar Entorno
```bash
# Navegar al proyecto
cd /mnt/project

# Instalar dependencias (si aún no están)
pip install pytest pytest-cov pytest-mock --break-system-packages
```

### Paso 2: Copiar Archivos del Plan
```bash
# Copiar plan maestro
cp /home/claude/PLAN_COVERAGE_80_PERCENT.md .

# Copiar script de inicio
cp /home/claude/INICIAR_DIA_1.py .

# Crear directorio de tests
mkdir -p tests

# Copiar tests de auth.py
cp /home/claude/tests/test_auth_completo.py tests/test_auth.py
```

### Paso 3: Ejecutar Tests del Día 1
```bash
# Opción A: Usando el script de inicio
python INICIAR_DIA_1.py

# Opción B: Directo con pytest
pytest tests/test_auth.py -v --cov=auth --cov-report=html
```

### Paso 4: Ver Resultados
```bash
# Ver reporte en consola
pytest tests/test_auth.py --cov=auth --cov-report=term-missing

# Abrir reporte HTML
# Windows:
start htmlcov/index.html

# Linux:
xdg-open htmlcov/index.html

# Mac:
open htmlcov/index.html
```

---

## 📊 VALIDACIÓN DEL DÍA 1

### Métricas Esperadas:
- ✅ **Tests Ejecutados:** 18+ tests
- ✅ **Tests Pasando:** 100%
- ✅ **Coverage auth.py:** 80%+
- ✅ **Tiempo Ejecución:** < 5 segundos

### Comando de Validación:
```bash
pytest tests/test_auth.py -v --cov=auth --cov-report=term | grep -E "(passed|auth.py)"
```

### Salida Esperada:
```
test_auth.py::TestEmailValidation::test_email_valido_basico PASSED
test_auth.py::TestEmailValidation::test_email_valido_con_puntos PASSED
...
auth.py                              160    32    80%   51-52, 59-67, 76-89
===== 18 passed in 2.43s =====
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

Después de ejecutar los pasos, deberías tener:

```
/mnt/project/
├── PLAN_COVERAGE_80_PERCENT.md      ← Plan maestro completo
├── INICIAR_DIA_1.py                 ← Script de inicio rápido
├── auth.py                          ← Módulo a testear
├── tests/
│   ├── test_auth.py                 ← 18+ tests de auth.py
│   └── ...                          ← Más tests en días siguientes
├── conftest.py                      ← Fixtures compartidos
├── pytest.ini                       ← Configuración de pytest
└── htmlcov/                         ← Reporte HTML de coverage
    └── index.html
```

---

## 🎯 CHECKLIST DEL DÍA 1

### Pre-Trabajo (5 minutos):
- [ ] Entorno virtual activado
- [ ] Dependencias instaladas (pytest, pytest-cov)
- [ ] Plan maestro revisado
- [ ] Estructura de directorios creada

### Bloque de Mañana (2 horas):
- [ ] 09:00-10:30 - Tests de autenticación básica (6 tests)
- [ ] 10:30-12:00 - Tests de seguridad (6 tests)

### Bloque de Tarde (2 horas):
- [ ] 14:00-15:30 - Tests de validación (6 tests)
- [ ] 15:30-16:00 - Ejecutar suite completa y verificar coverage

### Post-Trabajo (10 minutos):
- [ ] Coverage auth.py >= 80%
- [ ] Todos los tests pasando
- [ ] Commit de cambios
- [ ] Actualizar tracking de progreso

---

## 🔧 TROUBLESHOOTING

### Problema 1: "ModuleNotFoundError: No module named 'pytest'"
**Solución:**
```bash
pip install pytest pytest-cov --break-system-packages
```

### Problema 2: "No module named 'auth'"
**Solución:**
- Asegúrate de estar en la raíz del proyecto
- Verifica que auth.py esté en la raíz (no en subcarpeta)

### Problema 3: Tests fallan por "No module named 'routes'"
**Solución:**
- Los módulos están en la raíz, no en carpeta 'routes'
- Actualiza los imports en test_auth.py si es necesario

### Problema 4: "fixture 'test_db' not found"
**Solución:**
- Verifica que conftest.py esté en la raíz del proyecto
- Asegúrate de que contiene la fixture test_db

### Problema 5: Tests muy lentos
**Solución:**
```bash
# Ejecutar solo tests rápidos
pytest -m "not slow" tests/test_auth.py
```

---

## 📈 TRACKING DE PROGRESO

### Template de Reporte Diario:

```markdown
## DÍA 1 - REPORTE

**Fecha:** [DD/MM/YYYY]
**Tiempo Invertido:** [X] horas

### Resultados:
- Tests Escritos: [X]
- Tests Pasando: [X]
- Coverage Logrado: [X]%

### Logros:
- [✅] Completado X
- [✅] Logrado Y
- [🟡] En progreso Z

### Bloqueadores:
- [❌] Problema A (Resuelto/Pendiente)

### Próximos Pasos:
- [ ] Acción 1
- [ ] Acción 2
```

---

## 💡 TIPS PARA MÁXIMA EFICIENCIA

### 1. Usa TDD (Test-Driven Development)
```python
# 1. Escribe el test primero
def test_login_exitoso():
    # Test implementation

# 2. Ejecuta y ve que falla
pytest tests/test_auth.py::test_login_exitoso

# 3. Implementa código para que pase
# (En este caso, ya está implementado)

# 4. Refactoriza si es necesario
```

### 2. Ejecuta Tests Frecuentemente
```bash
# Ejecutar un test específico mientras desarrollas
pytest tests/test_auth.py::TestLogin::test_login_exitoso -v

# Ejecutar una clase completa de tests
pytest tests/test_auth.py::TestLogin -v

# Modo watch (re-ejecuta al guardar)
pytest-watch tests/test_auth.py
```

### 3. Usa Coverage para Identificar Gaps
```bash
# Ver líneas específicas sin cubrir
pytest --cov=auth --cov-report=term-missing | grep "Missing"

# Enfocarte en un módulo
pytest --cov=auth --cov-report=html
# Luego abre htmlcov/auth_py.html
```

### 4. Documenta Casos de Borde
```python
def test_edge_case_descripcion_clara():
    """
    Test: Describe exactamente qué caso de borde estás testeando

    Context: Por qué este caso es importante
    Expected: Qué debería pasar
    """
    # Test implementation
```

---

## 🎓 RECURSOS DE APRENDIZAJE

### Documentación Oficial:
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Guide](https://coverage.readthedocs.io/)
- [pytest-cov Plugin](https://pytest-cov.readthedocs.io/)

### Mejores Prácticas:
- [Effective Python Testing](https://realpython.com/pytest-python-testing/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

### Comandos Útiles:
```bash
# Ver todos los tests sin ejecutarlos
pytest --collect-only tests/

# Ejecutar tests en paralelo (más rápido)
pytest -n auto tests/

# Salir al primer fallo
pytest -x tests/

# Modo verboso con traceback completo
pytest -vv --tb=long tests/

# Generar reporte XML (para CI/CD)
pytest --cov=. --cov-report=xml
```

---

## 📞 SOPORTE

### Si tienes problemas:
1. **Revisa el troubleshooting** arriba
2. **Ejecuta el script de validación** (próximo archivo)
3. **Revisa los logs** de pytest con -vv
4. **Verifica las fixtures** en conftest.py

### Contacto:
- Sistema: Sistema Montero v2.1
- Proyecto: Coverage 80% Initiative
- Fecha: 12 de noviembre de 2025

---

## 🎉 ¡ÉXITO!

Si llegaste aquí y todos los checks están ✅, ¡felicitaciones!

**Completaste el Día 1 del plan de coverage.**

### Próximos Pasos:
1. ✅ Commit tus cambios
2. ✅ Actualiza el tracking
3. ✅ Descansa y prepárate para el Día 2
4. ✅ Mañana: app.py y encryption.py

---

**¡VAMOS POR ESE 80% DE COVERAGE!** 🚀💯

---

*Última Actualización: 12 de noviembre de 2025*
*Versión: 1.0*
