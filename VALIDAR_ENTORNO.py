#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrapper para scripts/validadores/VALIDAR_ENTORNO.py
Mantiene compatibilidad con referencias antiguas
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

# Importar y ejecutar el script real
if __name__ == "__main__":
    # Cambiar al directorio raíz
    import os
    os.chdir(ROOT_DIR)

    # Ejecutar el script
    exec(open(ROOT_DIR / "scripts" / "validadores" / "VALIDAR_ENTORNO.py", encoding="utf-8").read())
