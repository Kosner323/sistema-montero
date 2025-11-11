# Directorio de Migraciones de Alembic

Esta carpeta es administrada por Alembic y contiene todo el historial de cambios
de la base de datos del Sistema Montero.

## Contenido

* `env.py`: Script de configuración de entorno de Alembic. Se conecta a la base de datos y define los modelos.
* `script.py.mako`: Plantilla para generar nuevos archivos de migración.
* `versions/`: Esta carpeta contiene todos los scripts de migración (los "cambios").

**IMPORTANTE:** No modifiques los archivos en `versions/` que ya hayan sido aplicados en producción.