# Sistema Montero 🏢

![CI Status](https://github.com/Kosner323/sistema-montero/workflows/CI%20-%20Tests%20%26%20Quality/badge.svg)
![Security](https://github.com/Kosner323/sistema-montero/workflows/Security%20Scans/badge.svg)
![Deploy](https://github.com/Kosner323/sistema-montero/workflows/Deploy/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

Sistema integral de gestión empresarial con CI/CD Pipeline completo.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Uso](#-uso)
- [Testing](#-testing)
- [Despliegue](#-despliegue)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## ✨ Características

- 🔐 **Autenticación segura** con encriptación de credenciales
- 👥 **Gestión de usuarios** y empresas
- 📊 **Dashboard** con métricas y reportes
- 📁 **Gestión de formularios** (incapacidades, tutelas, novedades)
- 💰 **Pago de impuestos y planillas**
- 📄 **Generación de PDF** automatizada
- 🔒 **Encriptación** de datos sensibles
- 🚀 **CI/CD Pipeline** completo
- 🧪 **Testing automatizado** con cobertura
- 🔍 **Escaneo de seguridad** automatizado

---

## 🔧 Requisitos

### Software Requerido

- **Python** 3.10 o 3.11
- **pip** 23.0+
- **Git** 2.30+

### Dependencias Principales

- Flask 3.0.0
- SQLAlchemy (con Alembic para migraciones)
- Cryptography 42.0.5+
- Pydantic (validación de datos)
- Pytest (testing)

---

## 📥 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Kosner323/sistema-montero.git
cd sistema-montero
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
# Dependencias principales
pip install -r requirements.txt

# Dependencias de desarrollo (opcional)
pip install -r requirements-dev.txt
```

### 4. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
nano .env
```

**Variables requeridas en `.env`:**

```bash
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
ENCRYPTION_KEY=tu-clave-de-encriptacion-base64
FLASK_ENV=development
DATABASE_PATH=data/mi_sistema.db
LOG_LEVEL=INFO
```

### 5. Inicializar Base de Datos

```bash
# Ejecutar migraciones
alembic upgrade head

# O crear base de datos manualmente
python -c "from app import init_db; init_db()"
```

---

## ⚙️ Configuración

### Configuración de Desarrollo

```bash
# Archivo .env para desarrollo
FLASK_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG
```

### Configuración de Producción

```bash
# Archivo .env para producción
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=WARNING
```

---

## 🚀 CI/CD Pipeline

Este proyecto implementa un **pipeline de CI/CD completo** con GitHub Actions.

### 📊 Workflows Activos

#### 1. **CI - Tests & Quality**
- ✅ Ejecuta tests en Python 3.10 y 3.11
- ✅ Genera reportes de cobertura
- ✅ Ejecuta linters (Black, Flake8, isort, Pylint)
- ✅ Verifica formato de código
- ✅ Build check

#### 2. **Security Scans**
- 🔒 Escaneo con Bandit
- 🔍 Detección de vulnerabilidades (Safety, pip-audit)
- 🔐 Detección de secretos (TruffleHog)
- 📊 Dependency Review
- ⏰ Escaneos programados semanalmente

#### 3. **Deploy**
- 🚀 Despliegue automático a producción
- 🐳 Build de imagen Docker (tags)
- 📧 Notificaciones de despliegue

### 🔧 Configurar CI/CD Localmente

#### Linux/Mac:
```bash
./setup_cicd.sh
```

#### Windows:
```cmd
setup_cicd.bat
```

### 🎯 Pre-commit Hooks

El proyecto usa **pre-commit hooks** para validar código antes de cada commit:

```bash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

**Hooks configurados:**
- 🎨 Black (formato de código)
- 📦 isort (ordenar imports)
- 📏 Flake8 (linting)
- 🔒 Bandit (seguridad)
- 📚 pydocstyle (docstrings)
- 🕵️ detect-secrets (secretos)

### 📈 Verificar Estado Antes de Push

```bash
# Script de validación completa
python validar_pre_ci.py
```

**Este script verifica:**
- ✅ Tests pasando
- ✅ Cobertura >= 20%
- ✅ Sin errores de linting
- ✅ Sin vulnerabilidades críticas
- ✅ Variables de entorno configuradas

---

## 💻 Uso

### Iniciar el Servidor

```bash
# Modo desarrollo
python app.py

# O con Flask CLI
flask run
```

El servidor estará disponible en: `http://localhost:5000`

### Acceder al Sistema

1. Abre tu navegador en `http://localhost:5000`
2. Inicia sesión con credenciales (o regístrate)
3. Navega por los módulos disponibles

---

## 🧪 Testing

### Ejecutar Todos los Tests

```bash
pytest
```

### Tests con Cobertura

```bash
# Con reporte en terminal
pytest --cov=. --cov-report=term-missing

# Con reporte HTML
pytest --cov=. --cov-report=html

# Abrir reporte
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

### Ejecutar Tests Específicos

```bash
# Por archivo
pytest tests/test_auth.py

# Por función
pytest tests/test_auth.py::test_login

# Por marker
pytest -m unit  # Solo tests unitarios
pytest -m integration  # Solo tests de integración
```

### Tests en Modo Verbose

```bash
pytest -v  # Verbose
pytest -vv  # Muy verbose
pytest -vv -s  # Con print statements
```

---

## 📦 Despliegue

### Opción 1: Despliegue Manual

```bash
# 1. Configurar variables de entorno de producción
export FLASK_ENV=production

# 2. Ejecutar migraciones
alembic upgrade head

# 3. Iniciar con Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Opción 2: Docker

```bash
# Build
docker build -t sistema-montero .

# Run
docker run -p 5000:5000 --env-file .env sistema-montero
```

### Opción 3: GitHub Actions (Automático)

Los push a `main` disparan automáticamente el workflow de deploy.

```bash
git push origin main
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Sigue estos pasos:

### 1. Fork el Proyecto

```bash
# Click en "Fork" en GitHub
```

### 2. Crear Rama de Feature

```bash
git checkout -b feature/nueva-funcionalidad
```

### 3. Hacer Cambios

```bash
# Escribe código
# Asegúrate de que los tests pasen
pytest

# Asegúrate de que el linting pase
pre-commit run --all-files
```

### 4. Commit

```bash
git add .
git commit -m "feat: agregar nueva funcionalidad"
```

**Formato de commits (Conventional Commits):**
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Documentación
- `style:` - Formato de código
- `refactor:` - Refactorización
- `test:` - Tests
- `chore:` - Tareas de mantenimiento

### 5. Push y Pull Request

```bash
git push origin feature/nueva-funcionalidad
```

Luego crea un Pull Request en GitHub.

### 🔍 Checklist de PR

- [ ] Tests pasan localmente
- [ ] Pre-commit hooks pasan
- [ ] Cobertura >= 20%
- [ ] Documentación actualizada
- [ ] Sin errores de linting
- [ ] Commit messages siguen convención

---

## 📚 Documentación Adicional

- [Guía de CI/CD](docs/CICD.md)
- [Guía de Migraciones](DOCUMENTACION_BD/GUIA_MIGRACIONES_ALEMBIC.md)
- [Documentación de Base de Datos](DOCUMENTACION_BD/)
- [Guía de Seguridad](docs/SECURITY.md)

---

## 🐛 Reporte de Bugs

Reporta bugs creando un [Issue en GitHub](https://github.com/Kosner323/sistema-montero/issues) con:

- Descripción del problema
- Pasos para reproducir
- Comportamiento esperado
- Screenshots (si aplica)
- Versión de Python y dependencias

---

## 📊 Estado del Proyecto

### Cobertura de Tests
- **Objetivo:** 80%
- **Actual:** ~55%
- **En progreso:** Aumentando cobertura gradualmente

### Roadmap

- [x] Autenticación y encriptación
- [x] Gestión de usuarios y empresas
- [x] Módulos de formularios
- [x] CI/CD Pipeline
- [x] Testing automatizado
- [ ] API REST completa
- [ ] Dashboard con métricas en tiempo real
- [ ] Notificaciones por email
- [ ] Mobile responsive
- [ ] Dockerización completa

---

## 👥 Equipo

- **Desarrollador Principal:** Kosner323

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- Flask y su comunidad
- GitHub Actions
- Todos los contribuidores

---

## 📞 Contacto

- **GitHub:** [@Kosner323](https://github.com/Kosner323)
- **Issues:** [GitHub Issues](https://github.com/Kosner323/sistema-montero/issues)

---

## 🌟 Si te gusta este proyecto

¡Dale una ⭐ en GitHub!

---

<div align="center">

**Made with ❤️ by Kosner323**

[⬆ Volver arriba](#sistema-montero-)

</div>
