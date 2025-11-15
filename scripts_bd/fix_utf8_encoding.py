#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_utf8_encoding.py
====================================================
Script para detectar y corregir problemas de
encoding UTF-8 en archivos Python del sistema Montero.
====================================================
"""

import os
import re
import sys
from pathlib import Path

# Mapeo de caracteres corruptos a caracteres correctos
# (Tu gran lista de ENCODING_FIXES va aquí... la omito por brevedad)
ENCODING_FIXES = {
    "\u00c3\u00a9": "é",  # Ã©
    "\u00c3\u00a1": "á",  # Ã¡
    "\u00c3\u00ad": "í",  # Ã­
    "\u00c3\u00b3": "ó",  # Ã³
    "\u00c3\u00ba": "ú",  # Ãº
    "\u00c3\u00b1": "ñ",  # Ã±
    "\u00c3\u0089": "É",  # Ã‰
    "\u00c3\u201a": "Á",  # Ã (with special char)
    "\u00c3\u201c": "Ó",  # Ã"
    "Gesti\u00c3\u00b3n": "Gestión",
    "Autenticaci\u00c3\u00b3n": "Autenticación",
    "Configuraci\u00c3\u00b3n": "Configuración",
    "Informaci\u00c3\u00b3n": "Información",
    "Validaci\u00c3\u00b3n": "Validación",
    "Operaci\u00c3\u00b3n": "Operación",
    "m\u00c3\u00b3dulo": "módulo",
    "m\u00c3\u00a9todo": "método",
    "n\u00c3\u00bamero": "número",
    "c\u00c3\u00b3digo": "código",
    "l\u00c3\u00adnea": "línea",
    "m\u00c3\u00a1s": "más",
    "d\u00c3\u00ada": "día",
}


class UTF8Fixer:
    """Clase para detectar y corregir problemas de encoding UTF-8"""

    def __init__(self, project_path, dry_run=True):
        self.project_path = Path(project_path)
        self.dry_run = dry_run
        self.stats = {
            "files_analyzed": 0,
            "files_with_issues": 0,
            "issues_found": 0,
            "issues_fixed": 0,
        }

    def find_python_files(self):
        """Encuentra todos los archivos Python en el proyecto"""
        python_files = []
        # Busca en la carpeta del proyecto y sus subdirectorios
        search_paths = [self.project_path] + [d for d in self.project_path.iterdir() if d.is_dir()]

        for path in search_paths:
            for file_path in path.rglob("*.py"):
                # Excluir carpetas conocidas
                if any(x in str(file_path) for x in ["__pycache__", ".venv", "venv", ".git", "scripts_bd"]):
                    continue
                if file_path not in python_files:
                    python_files.append(file_path)

        # Asegurarse de incluir archivos .py en la raíz (dashboard)
        for file_path in self.project_path.glob("*.py"):
            if file_path not in python_files and "scripts_bd" not in str(file_path):
                python_files.append(file_path)

        return list(set(python_files))  # Devolver lista única

    def detect_encoding_issues(self, content):
        """Detecta problemas de encoding en el contenido"""
        issues = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for corrupted, correct in ENCODING_FIXES.items():
                if corrupted in line:
                    issues.append(
                        {
                            "line": line_num,
                            "corrupted": corrupted,
                            "correct": correct,
                            "original_line": line,
                        }
                    )

        return issues

    def fix_content(self, content):
        """Corrige el contenido del archivo"""
        fixed_content = content

        # Usar un orden específico: de más largo a más corto
        sorted_fixes = sorted(ENCODING_FIXES.items(), key=lambda item: len(item[0]), reverse=True)

        for corrupted, correct in sorted_fixes:
            fixed_content = fixed_content.replace(corrupted, correct)

        return fixed_content

    def process_file(self, file_path):
        """Procesa un archivo individual"""
        try:
            # Intentar leer con utf-8, si falla, usar latin-1 como fallback
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
                print(f"   (Leyendo {file_path.name} como latin-1)")

            issues = self.detect_encoding_issues(content)

            if not issues:
                return None

            fixed_content = self.fix_content(content)

            result = {
                "file": str(file_path.relative_to(self.project_path)),
                "issues": issues,
                "fixed": False,
            }

            if not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                result["fixed"] = True

            return result

        except Exception as e:
            print(f"Error procesando {file_path}: {e}")
            return None

    def run(self):
        """Ejecuta el proceso de corrección"""
        print("=" * 70)
        print("🔧 CORRECTOR DE ENCODING UTF-8 - SISTEMA MONTERO")
        print("=" * 70)
        print()

        if self.dry_run:
            print("⚠️  MODO DRY-RUN: Solo se mostrarán los problemas")
        else:
            print("✅ MODO CORRECCIÓN: Los cambios se aplicarán")

        print(f"Buscando archivos .py en: {self.project_path}")
        print()

        python_files = self.find_python_files()
        print(f"📁 Archivos Python encontrados: {len(python_files)}")
        print()

        files_with_issues = []

        for file_path in python_files:
            self.stats["files_analyzed"] += 1
            result = self.process_file(file_path)

            if result:
                files_with_issues.append(result)
                self.stats["files_with_issues"] += 1
                self.stats["issues_found"] += len(result["issues"])
                if result["fixed"]:
                    self.stats["issues_fixed"] += len(result["issues"])

        self.print_results(files_with_issues)

    def print_results(self, files_with_issues):
        """Imprime los resultados del análisis"""
        print("=" * 70)
        print("📊 RESULTADOS DEL ANÁLISIS")
        print("=" * 70)
        print()

        if not files_with_issues:
            print("✅ ¡Excelente! No se encontraron problemas de encoding UTF-8")
            print()
            return

        print(f"⚠️  Archivos con problemas: {len(files_with_issues)}")
        print()

        for file_info in files_with_issues:
            print(f"📄 {file_info['file']}")
            print(f"   Problemas: {len(file_info['issues'])}")

            for issue in file_info["issues"][:3]:
                print(f"   Línea {issue['line']}: problemas detectados")

            if len(file_info["issues"]) > 3:
                print(f"   ... y {len(file_info['issues']) - 3} más")

            if file_info["fixed"]:
                print("   ✅ CORREGIDO")
            else:
                print("   ⚠️  PENDIENTE")

            print()

        print("=" * 70)
        print("📈 ESTADÍSTICAS")
        print("=" * 70)
        print(f"Archivos analizados:     {self.stats['files_analyzed']}")
        print(f"Archivos con problemas:  {self.stats['files_with_issues']}")
        print(f"Problemas encontrados:   {self.stats['issues_found']}")
        print(f"Problemas corregidos:    {self.stats['issues_fixed']}")
        print()

        if self.dry_run:
            print("⚠️  Para aplicar correcciones:")
            print(f"   python {os.path.basename(__file__)} --fix")
        else:
            print("✅ ¡Correcciones aplicadas!")


def main():
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        dry_run = False

    # --- RUTA CORREGIDA PARA WINDOWS ---
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # ------------------------------------

    fixer = UTF8Fixer(project_path=project_root, dry_run=dry_run)
    fixer.run()


if __name__ == "__main__":
    main()
