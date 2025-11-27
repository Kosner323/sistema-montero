# Documentación del Pipeline CI/CD - Sistema Montero

## Resumen
Se ha implementado un pipeline de CI/CD completo usando **GitHub Actions** para automatizar la verificación de calidad de código y tests en cada push o pull request.

## Archivos del Pipeline

### 1. Workflow Principal: `ci.yml`
**Ubicación:** `.github/workflows/ci.yml`

**Características:**
- ✅ Ejecuta tests con cobertura de código
- ✅ Verifica formateo con Black (OBLIGATORIO)
- ✅ Análisis de código con Flake8, Pylint, isort
- ✅ Verificación de build
- ✅ Matriz de versiones de Python (3.10, 3.11)
- ✅ Upload de reportes de cobertura

### 2. Workflow Simplificado: `format-and-test.yml`
**Ubicación:** `.github/workflows/format-and-test.yml`

**Características:**
- ✅ Job 1: Verificación de formateo con Black
- ✅ Job 2: Ejecución de tests unitarios
- ✅ Job 3: Resumen del pipeline
- ✅ Matriz de versiones de Python (3.10, 3.11, 3.12)

## Configuración

### Archivo de Configuración: `pyproject.toml`

```toml
[tool.black]
line-length = 120
target-version = ['py310', 'py311', 'py312']
```

### Dependencias Agregadas: `requirements.txt`

```txt
# Code Quality & Formatting
black>=24.0.0
flake8>=7.0.0
isort>=5.13.0
```

## Triggers (Disparadores)

Los pipelines se ejecutan automáticamente en:

### Push a ramas principales
```yaml
on:
  push:
    branches: [ main, master, develop ]
```

### Pull Requests
```yaml
on:
  pull_request:
    branches: [ main, master, develop ]
```

## Jobs del Pipeline

### Job 1: Format Check (Black)

**Propósito:** Verificar que todo el código Python cumpla con el estilo de Black

**Pasos:**
1. Checkout del código
2. Configurar Python 3.10
3. Instalar Black
4. Ejecutar `black --check --diff .`

**Si falla:**
```bash
❌ Codigo no cumple con el formato de Black
Ejecuta 'black .' localmente para formatear
```

**Cómo arreglarlo:**
```bash
cd D:\Mi-App-React\src\dashboard
pip install black
black .
git add .
git commit -m "Format code with Black"
git push
```

### Job 2: Run Tests

**Propósito:** Ejecutar todos los tests unitarios con cobertura de código

**Matriz de versiones:**
- Python 3.10
- Python 3.11
- Python 3.12

**Pasos:**
1. Checkout del código
2. Configurar Python (versión de la matriz)
3. Crear directorios necesarios (data, logs, etc.)
4. Crear archivo `.env` de prueba
5. Instalar dependencias (`pip install -r requirements.txt`)
6. Inicializar base de datos de prueba
7. Ejecutar tests con pytest
8. Upload de resultados (coverage.xml, htmlcov)

**Comando de tests:**
```bash
pytest --cov=. --cov-report=xml --cov-report=term-missing -v
```

### Job 3: Summary

**Propósito:** Mostrar un resumen del resultado del pipeline

**Salida exitosa:**
```
✅ Formateo: PASSED
✅ Tests: PASSED
🎉 PIPELINE EXITOSO
```

**Salida con errores:**
```
❌ Formateo: FAILED
✅ Tests: PASSED
💥 PIPELINE FALLÓ
```

## Uso Local

### Formatear código con Black

```bash
cd D:\Mi-App-React\src\dashboard

# Instalar Black
pip install black

# Verificar formato (sin cambiar archivos)
black --check .

# Formatear todos los archivos
black .

# Formatear archivo específico
black routes/auth.py
```

### Ejecutar tests localmente

```bash
cd D:\Mi-App-React\src\dashboard

# Instalar dependencias de testing
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=. --cov-report=html

# Ver reporte de cobertura
# Abre: htmlcov/index.html en tu navegador
```

### Verificar isort (ordenamiento de imports)

```bash
# Instalar isort
pip install isort

# Verificar ordenamiento
isort --check-only --diff .

# Ordenar imports automáticamente
isort .
```

## Flujo de Trabajo Recomendado

### Antes de hacer commit:

```bash
# 1. Formatear código
black .

# 2. Ordenar imports
isort .

# 3. Ejecutar tests
pytest

# 4. Verificar que todo está correcto
black --check .
isort --check-only .
pytest --cov=.

# 5. Hacer commit
git add .
git commit -m "Tu mensaje de commit"
git push
```

### Después del push:

1. **GitHub Actions se ejecutará automáticamente**
2. **Verás el progreso en la pestaña "Actions" del repositorio**
3. **Si falla:**
   - Lee el log del job que falló
   - Arregla el problema localmente
   - Vuelve a hacer commit y push

## Configuración de Badges (Opcional)

Puedes agregar badges al README.md para mostrar el estado del pipeline:

```markdown
![CI Status](https://github.com/tu-usuario/tu-repo/workflows/Format%20&%20Test%20Pipeline/badge.svg)
![CI Tests](https://github.com/tu-usuario/tu-repo/workflows/CI%20-%20Tests%20&%20Quality/badge.svg)
```

## Estructura de Archivos

```
src/dashboard/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Pipeline completo
│       ├── format-and-test.yml       # Pipeline simplificado
│       ├── security.yml              # (existente)
│       └── deploy.yml                # (existente)
├── pyproject.toml                    # Configuración de Black, isort, pytest
├── requirements.txt                  # Dependencias (incluye black, flake8, isort)
├── tests/                            # Tests unitarios
│   ├── test_*.py
│   └── ...
└── ...
```

## Configuración del Repositorio GitHub

### Protección de Rama Main

Para hacer que el pipeline sea obligatorio antes de hacer merge:

1. Ve a **Settings** > **Branches** en tu repositorio
2. Agrega una regla para la rama `main`
3. Marca:
   - ☑ **Require status checks to pass before merging**
   - ☑ **Require branches to be up to date before merging**
4. Selecciona los checks requeridos:
   - `Format Check (Black)`
   - `Run Tests`
   - `summary`

### Pull Requests

Ahora cuando crees un Pull Request:
1. ✅ GitHub Actions ejecutará el pipeline automáticamente
2. ✅ No se podrá hacer merge si el pipeline falla
3. ✅ Verás el estado de cada job en el PR

## Troubleshooting

### Error: "black not found"
**Solución:**
```bash
pip install black
```

### Error: "tests failed"
**Solución:**
1. Ejecuta los tests localmente: `pytest -v`
2. Ve qué test falla
3. Arregla el código
4. Vuelve a ejecutar `pytest`

### Error: "black --check failed"
**Solución:**
```bash
# Formatear todo el código
black .

# Verificar
black --check .

# Commit
git add .
git commit -m "Format code with Black"
git push
```

### Error: "import could not be resolved"
**Solución:**
```bash
# Asegúrate de que todas las dependencias estén instaladas
pip install -r requirements.txt
```

## Mejoras Futuras

### 1. Agregar Tests de Integración
```yaml
- name: Run integration tests
  run: pytest tests/integration/ -v
```

### 2. Deploy Automático
```yaml
deploy:
  name: Deploy to Production
  needs: [format-check, run-tests]
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - name: Deploy
      run: # comandos de deploy
```

### 3. Notificaciones
- Configurar notificaciones por email cuando falle el pipeline
- Integrar con Slack o Discord

### 4. Cache de Dependencias
```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## Comandos Útiles

### Ver logs del pipeline en GitHub

```bash
# URL: https://github.com/tu-usuario/tu-repo/actions
```

### Ejecutar solo tests específicos

```bash
pytest tests/test_auth.py -v
```

### Ver cobertura de un archivo específico

```bash
pytest --cov=routes/auth.py --cov-report=term-missing
```

### Formatear solo archivos modificados

```bash
git diff --name-only | grep '\.py$' | xargs black
```

## Referencias

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Black Documentation](https://black.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [isort Documentation](https://pycqa.github.io/isort/)

---

**Implementado el:** 2025-11-15
**Versiones soportadas:** Python 3.10, 3.11, 3.12
