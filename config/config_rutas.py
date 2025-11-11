import os
from pathlib import Path

# ========================================================
# ARCHIVO DE CONFIGURACIÓN DE RUTAS ABSOLUTAS
# Define todas las rutas críticas del proyecto
# ========================================================

# 1. Ubicación de este archivo (config/config_rutas.py)
BASE_DIR_OF_CONFIG = Path(os.path.dirname(os.path.abspath(__file__)))

# 2. Raíz del proyecto (D:\Mi-App-React)
# Subimos tres niveles: config -> dashboard -> src -> Mi-App-React
RUTA_RAIZ_PROYECTO = BASE_DIR_OF_CONFIG.parent.parent.parent.resolve()

# 3. Rutas principales del proyecto
RUTA_MONTERO_NEGOCIO = RUTA_RAIZ_PROYECTO.joinpath("MONTERO_NEGOCIO")
RUTA_SRC = RUTA_RAIZ_PROYECTO.joinpath("src")
RUTA_ASSETS = RUTA_SRC.joinpath(
    "assets"
)  # Carpeta donde guardas tus PDFs o formularios

# ===================== RUTAS CRÍTICAS DEL SISTEMA =====================

# 4. Ruta de la base de datos
RUTA_BASE_DE_DATOS = RUTA_MONTERO_NEGOCIO.joinpath("BASE_DE_DATOS")

# 5. Ruta para archivos subidos por el usuario
# ✅ CORRECCIÓN FINAL: Variable renombrada a RUTA_UPLOADS_FORMULARIOS
RUTA_UPLOADS_FORMULARIOS = RUTA_MONTERO_NEGOCIO.joinpath("UPLOADS_FORMULARIOS")

# ======================================================================
# TODAS LAS RUTAS SON ABSOLUTAS Y NORMALIZADAS.
# Los archivos como 'formularios.db' y los PDFs se buscarán correctamente.
# ======================================================================

# 🧩 Depuración opcional: imprime las rutas detectadas
if __name__ == "__main__":
    print(f"Ruta raíz del proyecto: {RUTA_RAIZ_PROYECTO}")
    print(f"Ruta de la base de datos: {RUTA_BASE_DE_DATOS}")
    print(f"Ruta de assets: {RUTA_ASSETS}")
    print(f"Ruta de uploads formularios: {RUTA_UPLOADS_FORMULARIOS}")
