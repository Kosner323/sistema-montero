#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_utf8_fix.py
====================================================
Script para validar que las correcciones de UTF-8
se aplicaron correctamente.
====================================================
"""

import os
import sys
from pathlib import Path


class UTF8Validator:
    """Valida que no haya problemas de encoding UTF-8"""

    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.stats = {
            "files_checked": 0,
            "files_ok": 0,
            "files_with_issues": 0,
            "issues_found": 0,
        }

        # Patrones problemáticos que NO deberían existir
        self.bad_patterns = [
            "Ã©",
            "Ã¡",
            "Ã­",
            "Ã³",
            "Ãº",
            "Ã±",
            "Ã‰",
            "Ã",
            'Ã"',
            "Ãš",
            "ÃƒÂ©",
            "ÃƒÂ¡",
            "ÃƒÂ­",
            "ÃƒÂ³",
            "ÃƒÂº",
            "ÃƒÂ±",
            "GestiÃ³n",
            "AutenticaciÃ³n",
            "ConfiguraciÃ³n",
            "InformaciÃ³n",
            "ValidaciÃ³n",
            "OperaciÃ³n",
        ]

        # Patrones correctos que SÍ deberían existir
        self.good_patterns = [
            "Gestión",
            "Autenticación",
            "Configuración",
            "Información",
            "Validación",
            "Operación",
            "función",
            "módulo",
            "método",
        ]

    def find_python_files(self):
        """Encuentra archivos Python"""
        python_files = []
        # Busca en la carpeta del proyecto y sus subdirectorios
        search_paths = [self.project_path] + [
            d for d in self.project_path.iterdir() if d.is_dir()
        ]

        for path in search_paths:
            for file_path in path.rglob("*.py"):
                # Excluir carpetas conocidas
                if any(
                    x in str(file_path)
                    for x in ["__pycache__", ".venv", "venv", ".git", "scripts_bd"]
                ):
                    continue
                if file_path not in python_files:
                    python_files.append(file_path)

        # Asegurarse de incluir archivos .py en la raíz (dashboard)
        for file_path in self.project_path.glob("*.py"):
            if file_path not in python_files and "scripts_bd" not in str(file_path):
                python_files.append(file_path)

        return list(set(python_files))  # Devolver lista única

    def check_file(self, file_path):
        """Verifica un archivo"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            issues = []
            for pattern in self.bad_patterns:
                if pattern in content:
                    count = content.count(pattern)
                    issues.append(f"'{pattern}' aparece {count} veces")

            return issues

        except Exception as e:
            return [f"Error: {e}"]

    def run(self):
        """Ejecuta la validación"""
        print("=" * 70)
        print("✅ VALIDADOR DE CORRECCIONES UTF-8")
        print("=" * 70)
        print(f"Buscando archivos .py en: {self.project_path}")
        print()

        python_files = self.find_python_files()
        print(f"📁 Archivos Python a verificar: {len(python_files)}")
        print()

        files_with_issues = []

        for file_path in python_files:
            self.stats["files_checked"] += 1
            issues = self.check_file(file_path)

            if issues:
                files_with_issues.append(
                    {
                        "file": str(file_path.relative_to(self.project_path)),
                        "issues": issues,
                    }
                )
                self.stats["files_with_issues"] += 1
                self.stats["issues_found"] += len(issues)
            else:
                self.stats["files_ok"] += 1

        self.print_results(files_with_issues)

    def print_results(self, files_with_issues):
        """Imprime resultados"""
        print("=" * 70)
        print("📊 RESULTADOS DE LA VALIDACIÓN")
        print("=" * 70)
        print()

        if not files_with_issues:
            print("✅ ¡PERFECTO! Todos los archivos están correctamente codificados")
            print()
            print("🎉 Características encontradas:")
            print("   ✅ Acentos correctos (é, á, í, ó, ú)")
            print("   ✅ Eñes correctas (ñ, Ñ)")
            print("   ✅ Sin caracteres corruptos")
            print("   ✅ Encoding UTF-8 válido")
            print()
        else:
            print(f"⚠️  Archivos con problemas restantes: {len(files_with_issues)}")
            print()

            for file_info in files_with_issues:
                print(f"📄 {file_info['file']}")
                for issue in file_info["issues"]:
                    print(f"   ⚠️  {issue}")
                print()

        print("=" * 70)
        print("📈 ESTADÍSTICAS")
        print("=" * 70)
        print(f"Archivos verificados:      {self.stats['files_checked']}")
        print(f"Archivos OK:               {self.stats['files_ok']}")
        print(f"Archivos con problemas:    {self.stats['files_with_issues']}")
        print(f"Problemas encontrados:     {self.stats['issues_found']}")
        print()

        if not files_with_issues:
            print("✅ VALIDACIÓN EXITOSA - Día 2 completado")
            return True
        else:
            print("⚠️  VALIDACIÓN PARCIAL - Requiere revisión manual")
            return False


def main():
    # --- RUTA CORREGIDA PARA WINDOWS ---
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # ------------------------------------

    validator = UTF8Validator(project_path=project_root)
    success = validator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
