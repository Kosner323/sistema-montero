# CI/CD Quick Start - Sistema Montero

## ¿Qué se implementó?

✅ **Pipeline de CI/CD con GitHub Actions**
- Formateo automático de código con Black
- Ejecución automática de tests
- Verificación de calidad de código

## Archivos Creados/Modificados

### Workflows de GitHub Actions
- ✅ `.github/workflows/format-and-test.yml` - Pipeline simplificado (NUEVO)
- ✅ `.github/workflows/ci.yml` - Pipeline completo (MODIFICADO)
- ✅ `.github/workflows/README.md` - Documentación de workflows (NUEVO)

### Configuración
- ✅ `pyproject.toml` - Configuración de Black, isort, pytest (ACTUALIZADO)
- ✅ `requirements.txt` - Agregado Black, Flake8, isort (MODIFICADO)

### Scripts de Ayuda
- ✅ `pre-commit-check.py` - Script para verificar antes de commit (NUEVO)

### Documentación
- ✅ `CICD_PIPELINE_DOCUMENTATION.md` - Documentación completa (NUEVO)
- ✅ `CICD_QUICK_START.md` - Esta guía rápida (NUEVO)

## Uso Diario

### Antes de hacer commit (LOCAL)

```bash
# Método 1: Script automático
cd D:\Mi-App-React\src\dashboard
python pre-commit-check.py

# Método 2: Manual
black .
isort .
pytest
```

### Hacer commit y push

```bash
git add .
git commit -m "Tu mensaje"
git push
```

### Ver resultados en GitHub

1. Ve a: https://github.com/tu-usuario/tu-repo/actions
2. Ve el status del pipeline
3. Si falla, lee los logs y corrige

## Comandos Importantes

### Formatear código con Black
```bash
# Verificar (sin cambiar)
black --check .

# Formatear
black .

# Formatear archivo específico
black routes/auth.py
```

### Ejecutar tests
```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=.

# Ver reporte HTML
pytest --cov=. --cov-report=html
# Abre: htmlcov/index.html
```

### Ordenar imports
```bash
# Verificar
isort --check-only .

# Ordenar
isort .
```

## ¿Qué hace el Pipeline?

### Job 1: Format Check
- ✅ Verifica que el código esté formateado con Black
- ✅ Falla si encuentra código mal formateado
- ✅ Muestra el diff de lo que hay que cambiar

### Job 2: Run Tests
- ✅ Ejecuta todos los tests con pytest
- ✅ Genera reporte de cobertura
- ✅ Prueba en Python 3.10, 3.11, 3.12

### Job 3: Summary
- ✅ Muestra resumen del pipeline
- ✅ Indica si pasó o falló

## Configuración de Black

```toml
[tool.black]
line-length = 120
target-version = ['py310', 'py311', 'py312']
```

## Solución Rápida de Problemas

### "Black check failed"
```bash
black .
git add .
git commit -m "Format code with Black"
git push
```

### "Tests failed"
```bash
pytest -v  # Ver qué test falla
# Arregla el código
pytest     # Verifica que pase
git add .
git commit -m "Fix failing tests"
git push
```

### "Import errors"
```bash
pip install -r requirements.txt
```

## Instalación de Herramientas

```bash
# Instalar todas las herramientas de desarrollo
pip install black flake8 isort pytest pytest-cov

# O instalar desde requirements.txt
pip install -r requirements.txt
```

## Flujo de Trabajo Recomendado

```
1. Escribir código
2. python pre-commit-check.py
3. git add .
4. git commit -m "mensaje"
5. git push
6. Ver GitHub Actions
7. Si falla, arreglar y repetir desde paso 2
```

## Hacer que los Checks sean Obligatorios

En GitHub:
1. Settings > Branches
2. Add rule para `main`
3. Require status checks to pass:
   - ☑ Format Check (Black)
   - ☑ Run Tests
4. Save

Ahora no se podrá hacer merge si el pipeline falla.

## Próximos Pasos

1. ✅ Instalar herramientas: `pip install -r requirements.txt`
2. ✅ Formatear código existente: `black .`
3. ✅ Ejecutar tests: `pytest`
4. ✅ Hacer commit y push
5. ✅ Ver el pipeline en acción en GitHub Actions

## Ayuda

- 📚 Documentación completa: `CICD_PIPELINE_DOCUMENTATION.md`
- 🔧 Configuración: `pyproject.toml`
- 🤖 Workflows: `.github/workflows/`

---

¡Listo! Ahora tienes un pipeline de CI/CD profesional. 🎉
