# 🚀 Documentación CI/CD Pipeline - Sistema Montero

> Pipeline completo de Integración y Despliegue Continuo

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura del Pipeline](#arquitectura-del-pipeline)
3. [Workflows de GitHub Actions](#workflows-de-github-actions)
4. [Pre-commit Hooks](#pre-commit-hooks)
5. [Configuración Local](#configuración-local)
6. [Uso Diario](#uso-diario)
7. [Troubleshooting](#troubleshooting)
8. [Mejores Prácticas](#mejores-prácticas)
9. [FAQ](#faq)

---

## 🎯 Introducción

El Sistema Montero implementa un **pipeline de CI/CD completo** que automatiza:

- ✅ Testing automatizado en múltiples versiones de Python
- ✅ Code quality checks (linting, formatting)
- ✅ Security scanning
- ✅ Deployment automation
- ✅ Pre-commit hooks locales
- ✅ Branch protection

### Beneficios

- 🚀 **Despliegues confiables:** Cada cambio es testeado automáticamente
- 🔒 **Seguridad:** Escaneo automático de vulnerabilidades
- 📊 **Calidad:** Código formateado y validado consistentemente
- ⚡ **Velocidad:** Feedback inmediato en cada PR
- 🛡️ **Protección:** Evita que código roto llegue a producción

---

## 🏗️ Arquitectura del Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    DESARROLLO LOCAL                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Escribir código                                          │
│  2. git add .                                                │
│  3. git commit  ──► Pre-commit Hooks ──► Validación Local   │
│     │                  - Black                                │
│     │                  - isort                                │
│     │                  - Flake8                               │
│     │                  - Bandit                               │
│     │                  - detect-secrets                       │
│     ▼                                                         │
│  4. git push                                                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                            │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  CI Workflow     │  │ Security Workflow│                │
│  ├──────────────────┤  ├──────────────────┤                │
│  │ • Tests (3.10)   │  │ • Bandit         │                │
│  │ • Tests (3.11)   │  │ • Safety         │                │
│  │ • Linting        │  │ • pip-audit      │                │
│  │ • Build Check    │  │ • TruffleHog     │                │
│  │ • Coverage       │  │ • Dependency Rev.│                │
│  └──────────────────┘  └──────────────────┘                │
│           │                      │                            │
│           └──────────┬───────────┘                           │
│                      ▼                                        │
│              ┌──────────────────┐                            │
│              │  All Checks Pass │                            │
│              └──────────────────┘                            │
│                      │                                        │
│                      ▼                                        │
│              ┌──────────────────┐                            │
│              │   Merge to main  │                            │
│              └──────────────────┘                            │
│                      │                                        │
│                      ▼                                        │
│              ┌──────────────────┐                            │
│              │ Deploy Workflow  │                            │
│              ├──────────────────┤                            │
│              │ • Build          │                            │
│              │ • Deploy         │                            │
│              │ • Notify         │                            │
│              └──────────────────┘                            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflows de GitHub Actions

### 1. CI - Tests & Quality

**Archivo:** `.github/workflows/ci.yml`

**Trigger:**
- Push a `main` o `develop`
- Pull requests a `main` o `develop`

**Jobs:**

#### 1.1 Test Job
```yaml
- Python versions: 3.10, 3.11
- Crea estructura de directorios
- Instala dependencias
- Ejecuta tests con pytest
- Genera reportes de coverage
- Sube artifacts (reportes HTML, XML)
```

**Comandos ejecutados:**
```bash
pytest --cov=. --cov-report=xml --cov-report=html -v
coverage report --fail-under=20
```

#### 1.2 Lint Job
```yaml
- Black (formato de código)
- Flake8 (linting)
- Pylint (análisis estático)
- isort (ordenar imports)
```

**Comandos ejecutados:**
```bash
black --check --diff .
flake8 . --count --show-source
pylint **/*.py --exit-zero
isort --check-only --diff .
```

#### 1.3 Build Job
```yaml
- Verifica imports
- Valida estructura del proyecto
- Prueba inicialización de módulos
```

**Comandos ejecutados:**
```bash
python -c "import app; print('✅ Application imports successfully')"
python -c "from routes import auth; print('✅ Auth module OK')"
python -c "import encryption; print('✅ Encryption module OK')"
```

---

### 2. Security Scans

**Archivo:** `.github/workflows/security.yml`

**Trigger:**
- Push a `main` o `develop`
- Pull requests a `main` o `develop`
- Cron: Lunes a las 9 AM

**Jobs:**

#### 2.1 Security Scan Job
```yaml
- Bandit (análisis de código)
- Safety (vulnerabilidades en dependencias)
- pip-audit (auditoría de dependencias)
```

**Comandos ejecutados:**
```bash
bandit -r . -f json -o bandit-report.json
safety check --json > safety-report.json
pip-audit --desc
```

#### 2.2 Dependency Review
```yaml
- Revisa cambios en dependencias (solo PRs)
- Detecta vulnerabilidades conocidas
- Comenta en PR si encuentra issues
```

#### 2.3 Secret Scanning
```yaml
- TruffleHog (detección de secretos)
- Escanea commits buscando credenciales
- Verifica solo secretos verificados
```

---

### 3. Deploy

**Archivo:** `.github/workflows/deploy.yml`

**Trigger:**
- Push a `main`
- Tags: `v*.*.*`
- Manual (workflow_dispatch)

**Jobs:**

#### 3.1 Deploy Job
```yaml
- Ejecuta tests rápidos
- Build de aplicación
- Deploy a ambiente
- Genera reporte de deployment
```

#### 3.2 Docker Build (solo para tags)
```yaml
- Build de imagen Docker
- Push a Docker Hub (si está configurado)
- Tagging semántico
```

#### 3.3 Notify
```yaml
- Envía notificaciones de deployment
- Status: success/failure
```

---

## 🪝 Pre-commit Hooks

Los **pre-commit hooks** se ejecutan **antes de cada commit** para validar el código localmente.

### Configuración

**Archivo:** `.pre-commit-config.yaml`

### Hooks Activos

| Hook | Descripción | Acción |
|------|-------------|--------|
| `trailing-whitespace` | Elimina espacios al final de líneas | Auto-fix |
| `end-of-file-fixer` | Asegura newline al final de archivo | Auto-fix |
| `check-yaml` | Valida sintaxis YAML | Check |
| `check-json` | Valida sintaxis JSON | Check |
| `check-large-files` | Previene archivos > 1MB | Check |
| `check-merge-conflict` | Detecta marcadores de merge | Check |
| `detect-private-key` | Detecta llaves privadas | Check |
| `black` | Formatea código Python | Auto-fix |
| `isort` | Ordena imports | Auto-fix |
| `flake8` | Linting de código | Check |
| `bandit` | Escaneo de seguridad | Check |
| `pydocstyle` | Valida docstrings | Check |
| `detect-secrets` | Detecta secretos hardcodeados | Check |

### Configuración de Hooks

**Black:**
```yaml
args: ['--line-length=127']
```

**isort:**
```yaml
args: ['--profile', 'black', '--line-length', '127']
```

**Flake8:**
```yaml
args: ['--max-line-length=127', '--extend-ignore=E203,W503']
```

**Bandit:**
```yaml
args: ['-ll', '-r', '.']
exclude: ^tests/
```

---

## ⚙️ Configuración Local

### Instalación Automática

#### Linux/Mac:
```bash
chmod +x setup_cicd.sh
./setup_cicd.sh
```

#### Windows:
```cmd
setup_cicd.bat
```

### Instalación Manual

#### 1. Instalar Pre-commit
```bash
pip install pre-commit
```

#### 2. Instalar Hooks
```bash
pre-commit install
```

#### 3. Instalar Herramientas de Desarrollo
```bash
pip install -r requirements-dev.txt
```

#### 4. Ejecutar Primera Vez
```bash
pre-commit run --all-files
```

### Verificar Instalación

```bash
# Ver hooks instalados
pre-commit --version
ls -la .git/hooks/

# Ver configuración
pre-commit sample-config
```

---

## 💼 Uso Diario

### Workflow de Desarrollo

#### 1. Crear Rama de Feature

```bash
git checkout -b feature/nueva-funcionalidad
```

#### 2. Hacer Cambios

```bash
# Editar archivos
# ...

# Ver cambios
git status
git diff
```

#### 3. Ejecutar Tests Localmente (Opcional)

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=. --cov-report=term-missing

# Solo tests modificados
pytest -k test_nueva_funcionalidad
```

#### 4. Commit (Pre-commit se ejecuta automáticamente)

```bash
git add .
git commit -m "feat: agregar nueva funcionalidad"
```

**Salida esperada:**
```
🧹 Remove trailing whitespace.......................Passed
📝 Fix end of files.................................Passed
✅ Check YAML syntax................................Passed
✅ Check JSON syntax................................Passed
🚫 Check for large files............................Passed
⚠️  Check for merge conflicts.......................Passed
🔐 Detect private keys..............................Passed
📄 Check line endings...............................Passed
🎨 Format code with Black...........................Passed
📦 Sort imports with isort..........................Passed
📏 Lint with Flake8.................................Passed
🔒 Security scan with Bandit........................Passed
📚 Check docstrings.................................Passed
🕵️ Detect secrets...................................Passed

[feature/nueva-funcionalidad abc1234] feat: agregar nueva funcionalidad
 2 files changed, 45 insertions(+), 3 deletions(-)
```

#### 5. Si Pre-commit Falla

**Escenario 1: Auto-fix (Black, isort)**
```bash
# Los hooks auto-corrigen
# Simplemente commit de nuevo
git add .
git commit -m "feat: agregar nueva funcionalidad"
```

**Escenario 2: Errores de Linting**
```bash
# Corregir errores manualmente
# Ver detalles del error
flake8 archivo.py

# Corregir y commit de nuevo
git add .
git commit -m "feat: agregar nueva funcionalidad"
```

#### 6. Push a GitHub

```bash
git push origin feature/nueva-funcionalidad
```

#### 7. Crear Pull Request

1. Ve a GitHub
2. Click en "Compare & pull request"
3. Completa descripción:

```markdown
## Descripción
Breve descripción de los cambios

## Tipo de cambio
- [ ] Bug fix
- [x] Nueva funcionalidad
- [ ] Breaking change
- [ ] Documentación

## Checklist
- [x] Tests pasan localmente
- [x] Pre-commit hooks pasan
- [x] Documentación actualizada
- [x] Sin errores de linting
```

4. Esperar a que pasen los checks de GitHub Actions
5. Pedir code review
6. Merge cuando esté aprobado

---

### Validación Pre-Push

Antes de hacer push, ejecuta el script de validación:

```bash
python validar_pre_ci.py
```

**Verifica:**
- ✅ Tests pasando
- ✅ Coverage >= 20%
- ✅ Sin errores de linting
- ✅ Sin vulnerabilidades críticas
- ✅ Variables de entorno configuradas
- ✅ Base de datos accesible

---

## 🔧 Troubleshooting

### Problema 1: Pre-commit Muy Lento

**Síntoma:**
```
Pre-commit tarda varios minutos en ejecutarse
```

**Solución:**
```bash
# Limpiar cache
pre-commit clean
pre-commit gc

# Reinstalar
pre-commit uninstall
pre-commit install
```

---

### Problema 2: Tests Fallan en GitHub pero Pasan Localmente

**Síntoma:**
```
pytest local: ✅ PASSED
pytest GitHub: ❌ FAILED
```

**Soluciones:**

**A. Verificar variables de entorno**
```bash
# GitHub Actions usa .env diferente
# Verificar en .github/workflows/ci.yml
cat .github/workflows/ci.yml | grep -A 10 "env:"
```

**B. Verificar base de datos**
```bash
# GitHub Actions usa :memory:
# Verificar que tests usen fixtures correctos
cat conftest.py
```

**C. Verificar dependencias**
```bash
# Asegurar que requirements.txt esté actualizado
pip freeze > requirements-check.txt
diff requirements.txt requirements-check.txt
```

---

### Problema 3: Pre-commit Hook Específico Falla

**Síntoma:**
```
🔒 Security scan with Bandit........................Failed
```

**Solución:**

**A. Ver detalles del error**
```bash
pre-commit run bandit --all-files --verbose
```

**B. Skip temporalmente (NO RECOMENDADO)**
```bash
git commit -m "mensaje" --no-verify
```

**C. Corregir el issue**
```bash
# Ver reporte detallado de Bandit
bandit -r . -f txt

# Corregir código
# Commit de nuevo
```

---

### Problema 4: Workflow No Se Ejecuta

**Síntoma:**
```
Push a GitHub pero workflow no aparece en Actions
```

**Soluciones:**

**A. Verificar que GitHub Actions esté habilitado**
```
Settings → Actions → General
☑️ Allow all actions
```

**B. Verificar sintaxis de workflow**
```bash
# Instalar yamllint
pip install yamllint

# Validar archivo
yamllint .github/workflows/ci.yml
```

**C. Verificar triggers**
```yaml
# En .github/workflows/ci.yml
on:
  push:
    branches: [ main, develop ]  # ← Verifica que tu branch esté aquí
```

---

### Problema 5: Coverage Muy Bajo

**Síntoma:**
```
Coverage: 15% (fail-under=20%)
```

**Solución:**

**A. Ver qué archivos tienen baja coverage**
```bash
pytest --cov=. --cov-report=term-missing
```

**B. Escribir tests para archivos sin coverage**
```bash
# Ver archivos sin coverage
coverage report --show-missing | grep "0%"
```

**C. Ajustar umbral temporalmente (NO RECOMENDADO)**
```yaml
# En .github/workflows/ci.yml
coverage report --fail-under=15  # ← Reducir temporalmente
```

---

### Problema 6: Merge Bloqueado por Branch Protection

**Síntoma:**
```
❌ Merging is blocked
Required status checks must pass
```

**Solución:**

**A. Esperar a que pasen todos los checks**
```
✅ CI - Tests & Quality / test (Python 3.10)
✅ CI - Tests & Quality / test (Python 3.11)
✅ CI - Tests & Quality / lint
✅ CI - Tests & Quality / build
✅ Security Scans / security-scan
```

**B. Si un check falla constantemente**
```bash
# Reproducir localmente
python validar_pre_ci.py

# Corregir errores
# Push de nuevo
git push
```

**C. Si necesitas bypass temporal (SOLO ADMIN)**
```
Settings → Branches → Edit Rule
☐ Include administrators (desmarcar temporalmente)
```

---

## ✅ Mejores Prácticas

### 1. Commits

**✅ BUENO:**
```bash
git commit -m "feat: agregar autenticación OAuth"
git commit -m "fix: corregir bug en login"
git commit -m "docs: actualizar README con instrucciones"
```

**❌ MALO:**
```bash
git commit -m "cambios"
git commit -m "fix stuff"
git commit -m "asdfasdf"
```

**Formato:** [Conventional Commits](https://www.conventionalcommits.org/)
```
<tipo>(<scope>): <descripción>

Tipos:
- feat: Nueva funcionalidad
- fix: Bug fix
- docs: Documentación
- style: Formato (no afecta código)
- refactor: Refactorización
- test: Tests
- chore: Mantenimiento
```

---

### 2. Pull Requests

**✅ BUENO:**
- Título descriptivo
- Descripción detallada
- Screenshots si aplica
- Referencia a issues
- Checklist completo
- Tamaño razonable (< 500 líneas)

**❌ MALO:**
- Título genérico: "Update code"
- Sin descripción
- PR gigante (1000+ líneas)
- Mezcla múltiples features

---

### 3. Testing

**✅ BUENO:**
```python
def test_login_success():
    """Test successful login with valid credentials."""
    # Arrange
    user = create_test_user()

    # Act
    result = login(user.username, "password")

    # Assert
    assert result.success is True
    assert result.user_id == user.id
```

**❌ MALO:**
```python
def test_stuff():
    # No docstring
    # Sin estructura AAA
    # Assert ambiguo
    assert login("user", "pass")
```

---

### 4. Code Review

**Para Reviewers:**
- ✅ Revisar en máximo 24 horas
- ✅ Ser específico en comentarios
- ✅ Aprobar si pasan checks y código es bueno
- ❌ No hacer "rubber stamp" reviews

**Para Authors:**
- ✅ Responder a todos los comentarios
- ✅ Hacer cambios solicitados
- ✅ Marcar conversaciones como resueltas
- ❌ No hacer force push después de review

---

### 5. Secrets y Variables de Entorno

**✅ BUENO:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
```

**❌ MALO:**
```python
SECRET_KEY = "mi-clave-secreta-12345"  # ❌ Hardcoded
```

**Verificar:**
```bash
# Pre-commit detecta secretos
detect-secrets scan

# Verificar .gitignore
cat .gitignore | grep ".env"
```

---

## ❓ FAQ

### ¿Cuánto tarda el pipeline completo?

**Promedio:** 5-8 minutos
- CI Workflow: 3-5 minutos
- Security Workflow: 2-3 minutos
- Deploy Workflow: 5-8 minutos (si aplica)

---

### ¿Puedo saltarme los pre-commit hooks?

**Técnicamente sí:**
```bash
git commit --no-verify
```

**Pero NO SE RECOMIENDA porque:**
- Código sin formato llegará al repo
- GitHub Actions puede fallar
- Reduce calidad de código

---

### ¿Qué hacer si tengo prisa?

**Opción 1: Fix & Fast Forward**
```bash
# Ejecutar pre-commit y corregir rápido
pre-commit run --all-files
git add .
git commit -m "fix: quick fix"
git push
```

**Opción 2: Draft PR**
```bash
# Crear Draft PR para ejecutar CI
git push origin feature/branch
# En GitHub: Create Pull Request → Create draft pull request
```

---

### ¿Cómo actualizo los hooks?

```bash
pre-commit autoupdate
```

Esto actualizará las versiones en `.pre-commit-config.yaml`.

---

### ¿Cómo desactivo un hook temporalmente?

Editar `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/psf/black
  rev: 23.12.1
  hooks:
    - id: black
      # stages: [manual]  # ← Desactivar automático, solo manual
```

---

### ¿Cómo veo los logs de GitHub Actions?

1. Ve a repositorio en GitHub
2. Click en pestaña "Actions"
3. Click en workflow run
4. Click en job
5. Ver logs detallados

---

### ¿Puedo ejecutar workflows manualmente?

Sí, si el workflow tiene `workflow_dispatch`:

```yaml
on:
  workflow_dispatch:  # ← Permite ejecución manual
```

**Ejecutar:**
1. Actions tab
2. Seleccionar workflow
3. "Run workflow"
4. Elegir branch
5. "Run workflow"

---

## 📚 Referencias

### Documentación Oficial
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Pre-commit Docs](https://pre-commit.com/)
- [Pytest Docs](https://docs.pytest.org/)
- [Black Docs](https://black.readthedocs.io/)

### Herramientas
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

### Recursos Internos
- [README.md](../README.md)
- [Guía de Migraciones](../DOCUMENTACION_BD/GUIA_MIGRACIONES_ALEMBIC.md)
- [Tutorial CI/CD](../tutorial_cicd.md)

---

## 📞 Soporte

¿Problemas con CI/CD?

1. Revisar esta documentación
2. Revisar troubleshooting
3. Verificar GitHub Actions logs
4. Crear issue en GitHub

---

<div align="center">

**Sistema Montero CI/CD Pipeline**

Última actualización: Noviembre 2024

[⬆ Volver arriba](#-documentación-cicd-pipeline---sistema-montero)

</div>
