# 🏢 Sistema Montero

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.3+-37814A?style=flat-square&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?style=flat-square&logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-Private-gray?style=flat-square)

**Sistema web de gestión empresarial con procesamiento asíncrono de tareas.**

Plataforma integral para administración de empresas, empleados, nómina, tutelas, cotizaciones, y más. Incluye asistente de IA (Jordy IA), automatización RPA, y notificaciones programadas.

---

## 📋 Tabla de Contenidos

- [Requisitos Previos](#-requisitos-previos)
- [Instalación Rápida](#-instalación-rápida-quick-start)
- [Arquitectura](#-arquitectura)
- [Variables de Entorno](#-variables-de-entorno)
- [Comandos Útiles](#-comandos-útiles)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Mantenimiento](#-mantenimiento)

---

## 🔧 Requisitos Previos

Solo necesitas tener instalado:

| Herramienta | Versión | Descarga |
|-------------|---------|----------|
| **Docker** | 20.10+ | [docker.com](https://www.docker.com/get-started) |
| **Docker Compose** | 2.0+ | Incluido con Docker Desktop |

> 💡 **Nota**: No necesitas instalar Python, Redis ni ninguna otra dependencia. Docker maneja todo.

---

## 🚀 Instalación Rápida (Quick Start)

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/Kosner323/sistema-montero.git
cd sistema-montero
```

### Paso 2: Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales reales
nano .env  # o usa tu editor preferido
```

**Variables críticas a configurar:**

```env
SECRET_KEY=tu_clave_secreta_segura_aqui
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_password_de_aplicacion
GEMINI_API_KEY=tu_api_key_de_google  # Para Jordy IA
```

### Paso 3: Levantar el sistema

```bash
# Windows
DOCKER_UP.bat

# Linux/Mac
docker-compose up --build
```

### Paso 4: Acceder a la aplicación

Abre tu navegador en: **http://localhost:5000**

---

## 🏗️ Arquitectura

El sistema utiliza **4 contenedores Docker** trabajando en conjunto:

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA MONTERO                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────┐         ┌─────────────────┐          │
│   │   WEB (Flask)   │◄───────►│     REDIS       │          │
│   │    :5000        │         │     :6379       │          │
│   │   Gunicorn      │         │   Message       │          │
│   │   4 workers     │         │   Broker        │          │
│   └────────┬────────┘         └────────┬────────┘          │
│            │                           │                    │
│            │         ┌─────────────────┼─────────────────┐ │
│            │         │                 │                 │ │
│   ┌────────▼─────────▼──┐    ┌────────▼────────┐        │ │
│   │   CELERY WORKER     │    │  CELERY BEAT    │        │ │
│   │   Tareas Async      │    │   Scheduler     │        │ │
│   │   - Emails          │    │   - 8:00 AM     │        │ │
│   │   - Reportes        │    │   - Cron jobs   │        │ │
│   │   - Notificaciones  │    │                 │        │ │
│   └─────────────────────┘    └─────────────────┘        │ │
│                                                          │ │
├──────────────────────────────────────────────────────────┴─┤
│   Volúmenes Persistentes:                                  │
│   📁 ./data  → Base de datos SQLite                        │
│   📁 ./logs  → Logs de aplicación                          │
└────────────────────────────────────────────────────────────┘
```

### Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| `montero-backend` | 5000 | Aplicación Flask principal |
| `montero-redis` | 6379 | Broker de mensajes para Celery |
| `montero-celery-worker` | - | Procesador de tareas asíncronas |
| `montero-celery-beat` | - | Programador de tareas (cron) |

---

## 🔐 Variables de Entorno

El archivo `.env` contiene todas las configuraciones sensibles:

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `SECRET_KEY` | Clave secreta para sesiones Flask | ✅ |
| `ENCRYPTION_KEY` | Clave para encriptar datos sensibles | ✅ |
| `MAIL_USERNAME` | Email para envío de notificaciones | ⚠️ |
| `MAIL_PASSWORD` | Password de aplicación Gmail | ⚠️ |
| `GEMINI_API_KEY` | API Key de Google Gemini (Jordy IA) | ⚠️ |
| `SENTRY_DSN` | DSN de Sentry para monitoreo | Opcional |

> ⚠️ = Requerido para funcionalidad completa

---

## 💻 Comandos Útiles

### Docker

```bash
# Iniciar todos los servicios
docker-compose up --build

# Iniciar en segundo plano (detached)
docker-compose up -d --build

# Detener todos los servicios
docker-compose down

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f montero-backend

# Reconstruir solo un servicio
docker-compose up -d --build montero-backend

# Eliminar todo (incluyendo volúmenes)
docker-compose down -v
```

### Desarrollo Local (sin Docker)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar Flask
python app.py

# Iniciar Celery Worker (terminal separada)
celery -A celery_config:celery_app worker --loglevel=info --pool=solo

# Iniciar Celery Beat (terminal separada)
celery -A celery_config:celery_app beat --loglevel=info
```

---

## 📁 Estructura del Proyecto

```
sistema-montero/
├── 📄 app.py                    # Aplicación Flask principal
├── 📄 celery_config.py          # Configuración de Celery
├── 📄 celery_tasks.py           # Tareas asíncronas
├── 📄 docker-compose.yml        # Orquestación de contenedores
├── 📄 Dockerfile                # Imagen Docker
├── 📄 requirements.txt          # Dependencias Python
│
├── 📁 models/                   # Modelos ORM (SQLAlchemy)
│   └── orm_models.py
│
├── 📁 routes/                   # Blueprints Flask (rutas)
│   ├── auth.py
│   ├── empresas.py
│   ├── usuarios.py
│   └── ...
│
├── 📁 templates/                # Plantillas Jinja2
│   ├── _header.html
│   ├── _footer.html
│   └── ...
│
├── 📁 static/                   # Archivos estáticos (CSS, JS)
│
├── 📁 scripts/                  # Scripts de utilidad
│   ├── mantenimiento/           # Sincronización BD
│   ├── migraciones/             # Migraciones de datos
│   ├── diagnostico/             # Herramientas de debug
│   └── instalacion/             # Scripts .bat/.ps1
│
├── 📁 docs/                     # Documentación adicional
├── 📁 tests/                    # Tests unitarios
├── 📁 data/                     # Base de datos SQLite
└── 📁 logs/                     # Logs de aplicación
```

---

## 🛠️ Mantenimiento

### Sincronizar Base de Datos

Si modificas los modelos ORM, ejecuta:

```bash
# Dentro del contenedor
docker-compose exec montero-backend python scripts/mantenimiento/init_db_consolidado.py

# O localmente
python scripts/mantenimiento/init_db_consolidado.py
```

### Ver Estado de Tareas Celery

```bash
# Ver tareas activas
docker-compose exec montero-celery-worker celery -A celery_config:celery_app inspect active

# Ver tareas programadas
docker-compose exec montero-celery-worker celery -A celery_config:celery_app inspect scheduled
```

### Backup de Base de Datos

```bash
# Copiar archivo SQLite
cp data/mi_sistema.db backups/mi_sistema_$(date +%Y%m%d).db
```

---

## 📞 Soporte

**Desarrollado por:** Sistema Montero Team  
**Email:** kevinlomasd@gmail.com  
**Repositorio:** [github.com/Kosner323/sistema-montero](https://github.com/Kosner323/sistema-montero)

---

<div align="center">

**Hecho con ❤️ en Colombia**

*Sistema Montero v1.0 - Refactorizado Diciembre 2025*

</div>
