#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERIFICADOR DE ESQUEMA DE BASE DE DATOS
=========================================

Este script verifica el estado actual de la base de datos y lo compara
con la documentación del esquema esperado.

Uso:
    python verificar_esquema.py [ruta_a_database.db]

Si no se proporciona ruta, busca en las ubicaciones estándar.
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Colores para terminal
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text: str):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")


def print_success(text: str):
    """Imprime texto de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text: str):
    """Imprime texto de advertencia"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text: str):
    """Imprime texto de error"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Imprime texto informativo"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def find_database() -> Path:
    """
    Busca la base de datos en ubicaciones estándar.

    Returns:
        Path: Ruta a la base de datos
    """
    # Ubicaciones posibles
    possible_locations = [
        Path.cwd() / "database.db",
        Path.cwd() / "data" / "database.db",
        Path.cwd() / "MONTERO_NEGOCIO" / "BASE_DE_DATOS" / "database.db",
        Path.cwd().parent / "MONTERO_NEGOCIO" / "BASE_DE_DATOS" / "database.db",
    ]

    for location in possible_locations:
        if location.exists():
            return location

    return None


def get_table_structure(conn: sqlite3.Connection, table_name: str) -> Dict:
    """
    Obtiene la estructura de una tabla.

    Args:
        conn: Conexión a la base de datos
        table_name: Nombre de la tabla

    Returns:
        dict: Estructura de la tabla
    """
    cursor = conn.cursor()

    # Obtener columnas
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    # Obtener foreign keys
    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
    foreign_keys = cursor.fetchall()

    # Obtener índices
    cursor.execute(f"PRAGMA index_list({table_name});")
    indexes = cursor.fetchall()

    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cursor.fetchone()[0]

    return {
        "columns": columns,
        "foreign_keys": foreign_keys,
        "indexes": indexes,
        "row_count": row_count,
    }


def verify_unique_constraints(conn: sqlite3.Connection) -> List[Tuple[str, str, bool]]:
    """
    Verifica constraints UNIQUE críticos.

    Returns:
        list: Lista de (tabla, campo, existe)
    """
    cursor = conn.cursor()
    results = []

    # Verificar empresas.nit
    cursor.execute(
        """
        SELECT COUNT(*) FROM sqlite_master
        WHERE type='index'
        AND tbl_name='empresas'
        AND sql LIKE '%nit%'
        AND sql LIKE '%UNIQUE%';
    """
    )
    nit_unique = cursor.fetchone()[0] > 0
    results.append(("empresas", "nit", nit_unique))

    # Verificar usuarios(tipoId, numeroId)
    cursor.execute(
        """
        SELECT COUNT(*) FROM sqlite_master
        WHERE type='index'
        AND tbl_name='usuarios'
        AND (sql LIKE '%tipoId%' AND sql LIKE '%numeroId%')
        AND sql LIKE '%UNIQUE%';
    """
    )
    documento_unique = cursor.fetchone()[0] > 0
    results.append(("usuarios", "tipoId+numeroId", documento_unique))

    # Verificar formularios_importados.nombre_archivo
    cursor.execute(
        """
        SELECT COUNT(*) FROM sqlite_master
        WHERE type='index'
        AND tbl_name='formularios_importados'
        AND sql LIKE '%nombre_archivo%'
        AND sql LIKE '%UNIQUE%';
    """
    )
    archivo_unique = cursor.fetchone()[0] > 0
    results.append(("formularios_importados", "nombre_archivo", archivo_unique))

    return results


def verify_indexes(conn: sqlite3.Connection) -> List[Tuple[str, str, bool]]:
    """
    Verifica índices recomendados.

    Returns:
        list: Lista de (tabla, campo, existe)
    """
    cursor = conn.cursor()
    results = []

    # Índices recomendados
    recommended_indexes = [
        ("usuarios", "empresa_nit", "idx_usuarios_empresa"),
        ("usuarios", "correoElectronico", "idx_usuarios_email"),
        ("empresas", "nombre_empresa", "idx_empresas_nombre"),
        ("formularios_importados", "nombre", "idx_formularios_nombre"),
    ]

    for table, field, index_name in recommended_indexes:
        cursor.execute(
            f"""
            SELECT COUNT(*) FROM sqlite_master
            WHERE type='index'
            AND name='{index_name}';
        """
        )
        exists = cursor.fetchone()[0] > 0
        results.append((table, field, exists))

    return results


def check_data_integrity(conn: sqlite3.Connection) -> Dict:
    """
    Verifica integridad de datos.

    Returns:
        dict: Resultados de verificación
    """
    cursor = conn.cursor()
    issues = {
        "empleados_huerfanos": [],
        "nits_duplicados": [],
        "documentos_duplicados": [],
        "emails_duplicados": [],
    }

    # Buscar empleados sin empresa (huérfanos)
    try:
        cursor.execute(
            """
            SELECT u.id, u.numeroId, u.primerNombre, u.primerApellido, u.empresa_nit
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE e.nit IS NULL;
        """
        )
        issues["empleados_huerfanos"] = cursor.fetchall()
    except Exception as e:
        print_warning(f"No se pudo verificar empleados huérfanos: {e}")

    # Buscar NITs duplicados
    try:
        cursor.execute(
            """
            SELECT nit, COUNT(*) as count
            FROM empresas
            WHERE nit IS NOT NULL
            GROUP BY nit
            HAVING count > 1;
        """
        )
        issues["nits_duplicados"] = cursor.fetchall()
    except Exception as e:
        print_warning(f"No se pudo verificar NITs duplicados: {e}")

    # Buscar documentos duplicados en usuarios
    try:
        cursor.execute(
            """
            SELECT tipoId, numeroId, COUNT(*) as count
            FROM usuarios
            WHERE tipoId IS NOT NULL AND numeroId IS NOT NULL
            GROUP BY tipoId, numeroId
            HAVING count > 1;
        """
        )
        issues["documentos_duplicados"] = cursor.fetchall()
    except Exception as e:
        print_warning(f"No se pudo verificar documentos duplicados: {e}")

    # Buscar emails duplicados
    try:
        cursor.execute(
            """
            SELECT correoElectronico, COUNT(*) as count
            FROM usuarios
            WHERE correoElectronico IS NOT NULL
            GROUP BY correoElectronico
            HAVING count > 1;
        """
        )
        issues["emails_duplicados"] = cursor.fetchall()
    except Exception as e:
        print_warning(f"No se pudo verificar emails duplicados: {e}")

    return issues


def generate_report(db_path: Path):
    """
    Genera reporte completo de verificación.

    Args:
        db_path: Ruta a la base de datos
    """
    print_header("VERIFICACIÓN DE ESQUEMA - SISTEMA MONTERO")
    print_info(f"Base de datos: {db_path}")
    print_info(f"Tamaño: {db_path.stat().st_size / 1024:.2f} KB")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Verificar tablas existentes
        print_header("1. TABLAS EXISTENTES")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()

        expected_tables = ["empresas", "usuarios", "formularios_importados"]
        for table in expected_tables:
            if (table,) in tables:
                print_success(f"Tabla '{table}' existe")
            else:
                print_error(f"Tabla '{table}' NO existe")

        # 2. Estructura de cada tabla
        print_header("2. ESTRUCTURA DE TABLAS")
        for (table_name,) in tables:
            if table_name == "sqlite_sequence":
                continue

            structure = get_table_structure(conn, table_name)
            print(f"\n{Colors.BOLD}📋 {table_name}{Colors.END}")
            print(f"   Columnas: {len(structure['columns'])}")
            print(f"   Foreign Keys: {len(structure['foreign_keys'])}")
            print(f"   Índices: {len(structure['indexes'])}")
            print(f"   Registros: {structure['row_count']}")

            if structure["foreign_keys"]:
                for fk in structure["foreign_keys"]:
                    print_success(f"   FK: {fk[3]} → {fk[2]}.{fk[4]}")

        # 3. Verificar constraints UNIQUE críticos
        print_header("3. CONSTRAINTS UNIQUE (CRÍTICOS)")
        unique_constraints = verify_unique_constraints(conn)

        for table, field, exists in unique_constraints:
            if exists:
                print_success(f"{table}.{field} tiene constraint UNIQUE")
            else:
                print_error(f"{table}.{field} NO tiene constraint UNIQUE ⚠️ CRÍTICO")

        # 4. Verificar índices recomendados
        print_header("4. ÍNDICES DE BÚSQUEDA")
        indexes = verify_indexes(conn)

        for table, field, exists in indexes:
            if exists:
                print_success(f"Índice en {table}.{field}")
            else:
                print_warning(f"Falta índice en {table}.{field} (recomendado)")

        # 5. Verificar integridad de datos
        print_header("5. INTEGRIDAD DE DATOS")
        issues = check_data_integrity(conn)

        if not any(issues.values()):
            print_success("No se encontraron problemas de integridad")
        else:
            if issues["empleados_huerfanos"]:
                print_error(f"Empleados huérfanos: {len(issues['empleados_huerfanos'])}")
                for emp in issues["empleados_huerfanos"][:3]:  # Mostrar solo 3
                    print(f"   - ID {emp[0]}: {emp[2]} {emp[3]} (NIT: {emp[4]})")

            if issues["nits_duplicados"]:
                print_error(f"NITs duplicados: {len(issues['nits_duplicados'])}")
                for nit, count in issues["nits_duplicados"]:
                    print(f"   - NIT {nit} aparece {count} veces")

            if issues["documentos_duplicados"]:
                print_error(f"Documentos duplicados: {len(issues['documentos_duplicados'])}")
                for tipo, num, count in issues["documentos_duplicados"]:
                    print(f"   - {tipo} {num} aparece {count} veces")

            if issues["emails_duplicados"]:
                print_warning(f"Emails duplicados: {len(issues['emails_duplicados'])}")
                for email, count in issues["emails_duplicados"][:3]:
                    print(f"   - {email} aparece {count} veces")

        # 6. Resumen y recomendaciones
        print_header("6. RESUMEN Y RECOMENDACIONES")

        critical_issues = sum(1 for _, _, exists in unique_constraints if not exists)
        warnings = sum(1 for _, _, exists in indexes if not exists)
        data_issues = sum(len(v) for v in issues.values())

        print(f"\n{Colors.BOLD}Puntuación:{Colors.END}")
        if critical_issues == 0 and data_issues == 0:
            print_success(f"✅ EXCELENTE - Base de datos bien configurada")
        elif critical_issues > 0:
            print_error(f"⚠️ CRÍTICO - {critical_issues} problemas de seguridad encontrados")
        else:
            print_warning(f"⚠️ MEJORABLE - {warnings} optimizaciones recomendadas")

        print(f"\n{Colors.BOLD}Próximos pasos:{Colors.END}")
        if critical_issues > 0:
            print_error("1. Aplicar constraints UNIQUE (ver create_database.sql)")
            print_error("2. Hacer backup antes de cualquier cambio")
        if warnings > 0:
            print_warning("3. Crear índices de búsqueda (mejorar performance)")
        if data_issues > 0:
            print_error("4. Corregir problemas de integridad de datos")

        if critical_issues == 0 and data_issues == 0:
            print_success("5. Continuar con Semana 2 - Día 4: Implementar Alembic")

        conn.close()

    except sqlite3.Error as e:
        print_error(f"Error al conectar con la base de datos: {e}")
        sys.exit(1)


def main():
    """Función principal"""
    # Buscar base de datos
    if len(sys.argv) > 1:
        db_path = Path(sys.argv[1])
    else:
        db_path = find_database()

    if not db_path or not db_path.exists():
        print_error("No se encontró la base de datos")
        print_info("Uso: python verificar_esquema.py [ruta_a_database.db]")
        print_info("\nUbicaciones buscadas:")
        print("  - ./database.db")
        print("  - ./data/database.db")
        print("  - ./MONTERO_NEGOCIO/BASE_DE_DATOS/database.db")
        sys.exit(1)

    # Generar reporte
    generate_report(db_path)

    print_header("VERIFICACIÓN COMPLETADA")
    print_info("Revisar 'database_schema.py' para documentación completa")
    print_info("Ejecutar 'create_database.sql' para aplicar mejoras")
    print()


if __name__ == "__main__":
    main()
