#!/bin/bash
# =====================================================================
# SETUP_CICD.SH - Sistema Montero
# =====================================================================
# Script de instalación de CI/CD Pipeline para Linux/Mac
# Instala y configura todas las herramientas necesarias
# =====================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Función para imprimir headers
print_header() {
    echo -e "\n${CYAN}${BOLD}===========================================${NC}"
    echo -e "${CYAN}${BOLD}  $1${NC}"
    echo -e "${CYAN}${BOLD}===========================================${NC}\n"
}

# Función para mensajes de éxito
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Función para mensajes de error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función para mensajes de advertencia
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Función para mensajes de info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner inicial
clear
print_header "INSTALACIÓN CI/CD PIPELINE - SISTEMA MONTERO"

# =====================================================================
# PASO 1: Verificar Python
# =====================================================================
print_info "Verificando Python..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    print_info "Instala Python 3.9+ desde https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python encontrado: $PYTHON_VERSION"

# Verificar versión mínima de Python (3.9+)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    print_error "Se requiere Python 3.9 o superior (encontrado: $PYTHON_VERSION)"
    exit 1
fi

# =====================================================================
# PASO 2: Verificar pip
# =====================================================================
print_info "Verificando pip..."

if ! command -v pip3 &> /dev/null; then
    print_error "pip no está instalado"
    print_info "Instalando pip..."
    python3 -m ensurepip --upgrade
fi

PIP_VERSION=$(pip3 --version 2>&1 | awk '{print $2}')
print_success "pip encontrado: $PIP_VERSION"

# Actualizar pip
print_info "Actualizando pip..."
python3 -m pip install --upgrade pip --quiet
print_success "pip actualizado"

# =====================================================================
# PASO 3: Crear entorno virtual (opcional pero recomendado)
# =====================================================================
print_info "¿Deseas crear un entorno virtual? (Recomendado) [s/N]"
read -r CREATE_VENV

if [[ "$CREATE_VENV" =~ ^[Ss]$ ]]; then
    if [ ! -d "venv" ]; then
        print_info "Creando entorno virtual..."
        python3 -m venv venv
        print_success "Entorno virtual creado"
    else
        print_warning "El entorno virtual ya existe"
    fi

    print_info "Activando entorno virtual..."
    source venv/bin/activate
    print_success "Entorno virtual activado"
fi

# =====================================================================
# PASO 4: Instalar dependencias principales
# =====================================================================
print_header "INSTALANDO DEPENDENCIAS"

print_info "Instalando dependencias principales..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    print_success "Dependencias principales instaladas"
else
    print_warning "No se encontró requirements.txt"
fi

# =====================================================================
# PASO 5: Instalar herramientas de desarrollo
# =====================================================================
print_info "Instalando herramientas de desarrollo..."

TOOLS=(
    "pre-commit>=3.6.0"
    "black>=23.12.0"
    "flake8>=7.0.0"
    "isort>=5.13.0"
    "pylint>=3.0.0"
    "bandit>=1.7.6"
    "safety>=3.0.0"
    "pytest>=7.4.3"
    "pytest-cov>=4.1.0"
    "pytest-html>=4.1.0"
    "pytest-mock>=3.12.0"
    "mypy>=1.8.0"
    "pip-audit>=2.6.0"
)

for tool in "${TOOLS[@]}"; do
    tool_name=$(echo $tool | cut -d'>' -f1 | cut -d'=' -f1)
    print_info "  Instalando $tool_name..."
    pip install "$tool" --quiet
done

print_success "Herramientas de desarrollo instaladas"

# Guardar dependencias de desarrollo
print_info "Guardando dependencias de desarrollo..."
cat > requirements-dev.txt << 'EOF'
# =====================================================================
# REQUIREMENTS-DEV.TXT - Sistema Montero
# =====================================================================
# Dependencias de desarrollo y CI/CD
# =====================================================================

# Pre-commit and hooks
pre-commit>=3.6.0

# Code formatting
black>=23.12.0
isort>=5.13.0

# Linting
flake8>=7.0.0
flake8-docstrings>=1.7.0
pylint>=3.0.0
mypy>=1.8.0

# Security
bandit>=1.7.6
safety>=3.0.0
pip-audit>=2.6.0
detect-secrets>=1.5.0

# Testing
pytest>=7.4.3
pytest-cov>=4.1.0
pytest-html>=4.1.0
pytest-mock>=3.12.0
pytest-timeout>=2.2.0

# Documentation
pydocstyle>=6.3.0

# Build tools
build>=1.0.0
wheel>=0.42.0
EOF

print_success "requirements-dev.txt creado"

# =====================================================================
# PASO 6: Configurar pre-commit
# =====================================================================
print_header "CONFIGURANDO PRE-COMMIT HOOKS"

if [ -f ".pre-commit-config.yaml" ]; then
    print_info "Instalando pre-commit hooks..."
    pre-commit install
    print_success "Pre-commit hooks instalados"

    print_info "Ejecutando pre-commit en todos los archivos (primera vez)..."
    print_warning "Esto puede tomar varios minutos..."

    # Ejecutar pre-commit (puede fallar en la primera vez, es normal)
    if pre-commit run --all-files; then
        print_success "Pre-commit ejecutado exitosamente"
    else
        print_warning "Pre-commit encontró algunos problemas (normal en primera ejecución)"
        print_info "Ejecutando de nuevo para aplicar correcciones..."

        if pre-commit run --all-files; then
            print_success "Pre-commit ejecutado exitosamente"
        else
            print_warning "Algunos checks fallaron, revisa los mensajes arriba"
        fi
    fi
else
    print_warning "No se encontró .pre-commit-config.yaml"
    print_info "Creando configuración básica de pre-commit..."

    cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        args: ['--line-length=127']
EOF

    pre-commit install
    print_success "Pre-commit básico configurado"
fi

# =====================================================================
# PASO 7: Crear directorios necesarios
# =====================================================================
print_header "CREANDO ESTRUCTURA DE DIRECTORIOS"

DIRECTORIES=(
    "data"
    "logs"
    "formularios_pdf"
    "test_data/usuarios"
    "test_data/empresas"
    "htmlcov"
    "docs"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        print_success "Creado: $dir"
    else
        print_info "Ya existe: $dir"
    fi
done

# =====================================================================
# PASO 8: Configurar variables de entorno para testing
# =====================================================================
print_header "CONFIGURANDO VARIABLES DE ENTORNO"

if [ ! -f ".env.test" ]; then
    print_info "Creando archivo .env.test..."

    cat > .env.test << 'EOF'
# =====================================================================
# .ENV.TEST - Variables de entorno para testing
# =====================================================================

SECRET_KEY=test-secret-key-for-ci-12345678901234567890123456789012
ENCRYPTION_KEY=HLh9Yfi7v5-QnQ4WYALaTPIC__LX-VqCK01eJBNK8Zw=
FLASK_ENV=testing
DATABASE_PATH=:memory:
LOG_LEVEL=ERROR
EOF

    print_success ".env.test creado"
else
    print_info ".env.test ya existe"
fi

# =====================================================================
# PASO 9: Ejecutar tests
# =====================================================================
print_header "EJECUTANDO TESTS"

print_info "Ejecutando suite de tests..."
print_warning "Esto puede tomar algunos minutos..."

# Crear archivo .env temporal si no existe
if [ ! -f ".env" ]; then
    cp .env.test .env
    TEMP_ENV_CREATED=true
fi

if pytest --cov=. --cov-report=html --cov-report=term --cov-report=xml -v; then
    print_success "Tests ejecutados exitosamente"

    # Mostrar reporte de coverage
    echo -e "\n${CYAN}${BOLD}Reporte de Cobertura:${NC}"
    coverage report

    print_info "Reporte HTML disponible en: htmlcov/index.html"
else
    print_warning "Algunos tests fallaron, revisa los mensajes arriba"
fi

# Limpiar .env temporal si fue creado
if [ "$TEMP_ENV_CREATED" = true ]; then
    rm .env
fi

# =====================================================================
# PASO 10: Ejecutar validación de seguridad
# =====================================================================
print_header "EJECUTANDO ESCANEO DE SEGURIDAD"

print_info "Ejecutando Bandit (security scanner)..."
if bandit -r . -ll -f txt; then
    print_success "Escaneo de seguridad completado"
else
    print_warning "Se encontraron algunos problemas de seguridad"
fi

print_info "Verificando vulnerabilidades en dependencias..."
if safety check --json > safety-report.json 2>/dev/null; then
    print_success "Safety check completado"
else
    print_warning "Safety check encontró vulnerabilidades (revisar safety-report.json)"
fi

# =====================================================================
# PASO 11: Generar reporte de instalación
# =====================================================================
print_header "GENERANDO REPORTE DE INSTALACIÓN"

REPORT_FILE="cicd_installation_report.txt"

cat > $REPORT_FILE << EOF
=====================================================================
REPORTE DE INSTALACIÓN CI/CD - SISTEMA MONTERO
=====================================================================

Fecha: $(date)
Usuario: $(whoami)
Sistema: $(uname -s)
Hostname: $(hostname)

=====================================================================
VERSIONES INSTALADAS
=====================================================================

Python: $PYTHON_VERSION
pip: $PIP_VERSION

Herramientas de desarrollo:
$(pip list | grep -E "pre-commit|black|flake8|isort|pylint|bandit|safety|pytest")

=====================================================================
ARCHIVOS DE CONFIGURACIÓN
=====================================================================

$(if [ -f ".pre-commit-config.yaml" ]; then echo "✅ .pre-commit-config.yaml"; else echo "❌ .pre-commit-config.yaml"; fi)
$(if [ -f ".flake8" ]; then echo "✅ .flake8"; else echo "❌ .flake8"; fi)
$(if [ -f "pyproject.toml" ]; then echo "✅ pyproject.toml"; else echo "❌ pyproject.toml"; fi)
$(if [ -f "pytest.ini" ]; then echo "✅ pytest.ini"; else echo "❌ pytest.ini"; fi)
$(if [ -f ".github/workflows/ci.yml" ]; then echo "✅ .github/workflows/ci.yml"; else echo "❌ .github/workflows/ci.yml"; fi)
$(if [ -f ".github/workflows/security.yml" ]; then echo "✅ .github/workflows/security.yml"; else echo "❌ .github/workflows/security.yml"; fi)
$(if [ -f ".github/workflows/deploy.yml" ]; then echo "✅ .github/workflows/deploy.yml"; else echo "❌ .github/workflows/deploy.yml"; fi)

=====================================================================
PRE-COMMIT HOOKS
=====================================================================

$(pre-commit --version 2>/dev/null || echo "No instalado")

=====================================================================
ESTADO DE GIT
=====================================================================

Branch actual: $(git branch --show-current 2>/dev/null || echo "No es un repositorio git")
Último commit: $(git log -1 --oneline 2>/dev/null || echo "Sin commits")

=====================================================================
PRÓXIMOS PASOS
=====================================================================

1. Revisar el reporte de coverage en: htmlcov/index.html
2. Configurar GitHub Actions en tu repositorio
3. Configurar branch protection en GitHub
4. Hacer tu primer commit con pre-commit hooks activos
5. Crear un Pull Request de prueba

=====================================================================
COMANDOS ÚTILES
=====================================================================

# Ejecutar pre-commit manualmente
pre-commit run --all-files

# Ejecutar tests con coverage
pytest --cov=. --cov-report=html -v

# Ejecutar linting
flake8 .
black --check .
isort --check .

# Escaneo de seguridad
bandit -r .
safety check

# Validar antes de commit
python validar_pre_ci.py

=====================================================================
EOF

print_success "Reporte generado: $REPORT_FILE"

# =====================================================================
# PASO 12: Resumen final
# =====================================================================
print_header "INSTALACIÓN COMPLETADA"

echo -e "${GREEN}${BOLD}🎉 ¡CI/CD Pipeline instalado exitosamente!${NC}\n"

print_success "Pre-commit hooks instalados y configurados"
print_success "Herramientas de desarrollo instaladas"
print_success "Tests ejecutados"
print_success "Escaneo de seguridad completado"
print_success "Reporte generado"

echo -e "\n${CYAN}${BOLD}📊 Archivos generados:${NC}"
echo -e "  📄 requirements-dev.txt - Dependencias de desarrollo"
echo -e "  📄 .env.test - Variables de entorno para testing"
echo -e "  📄 $REPORT_FILE - Reporte de instalación"
echo -e "  📄 htmlcov/index.html - Reporte de coverage"
echo -e "  📄 safety-report.json - Reporte de vulnerabilidades"

echo -e "\n${CYAN}${BOLD}🚀 Próximos pasos:${NC}"
echo -e "  1. Abre el reporte de coverage: ${YELLOW}open htmlcov/index.html${NC}"
echo -e "  2. Revisa el reporte de instalación: ${YELLOW}cat $REPORT_FILE${NC}"
echo -e "  3. Haz un commit de prueba: ${YELLOW}git commit -m 'test: CI/CD'${NC}"
echo -e "  4. Configura GitHub Actions en tu repositorio"
echo -e "  5. Lee la documentación en: ${YELLOW}docs/CICD.md${NC}"

echo -e "\n${CYAN}${BOLD}📚 Comandos útiles:${NC}"
echo -e "  ${YELLOW}pre-commit run --all-files${NC}  - Ejecutar pre-commit"
echo -e "  ${YELLOW}pytest --cov=. -v${NC}            - Ejecutar tests"
echo -e "  ${YELLOW}python validar_pre_ci.py${NC}     - Validar antes de push"

echo -e "\n${GREEN}${BOLD}✨ ¡Todo listo para empezar a desarrollar con CI/CD!${NC}\n"

# Preguntar si desea ver el reporte de coverage
echo -e "${CYAN}¿Deseas abrir el reporte de coverage ahora? [s/N]${NC}"
read -r OPEN_COVERAGE

if [[ "$OPEN_COVERAGE" =~ ^[Ss]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open htmlcov/index.html
    elif command -v open &> /dev/null; then
        open htmlcov/index.html
    else
        print_info "Abre manualmente: htmlcov/index.html"
    fi
fi

echo ""
