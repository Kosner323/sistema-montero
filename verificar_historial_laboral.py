# -*- coding: utf-8 -*-
"""
Script de Verificación del Módulo de Unificación
Valida que la tabla historial_laboral esté correctamente creada
y muestra registros de ejemplo.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mi_sistema.db')

def verificar_tabla_historial():
    """Verifica que la tabla historial_laboral existe y tiene la estructura correcta."""
    print("=" * 80)
    print("🔍 VERIFICACIÓN DE TABLA HISTORIAL_LABORAL")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 1. Verificar existencia de tabla
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='historial_laboral'
        """)
        
        if cursor.fetchone():
            print("✅ Tabla 'historial_laboral' existe")
        else:
            print("❌ Tabla 'historial_laboral' NO existe")
            print("\n💡 Ejecuta: python -c \"import sqlite3; conn = sqlite3.connect('data/mi_sistema.db'); conn.executescript(open('sql/crear_historial_laboral.sql', 'r', encoding='utf-8').read()); conn.commit(); conn.close()\"")
            return False
        
        # 2. Obtener esquema
        cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'historial_laboral'")
        schema = cursor.fetchone()['sql']
        print("\n📋 ESQUEMA DE LA TABLA:")
        print("-" * 80)
        print(schema)
        
        # 3. Verificar columnas
        cursor.execute("PRAGMA table_info(historial_laboral)")
        columnas = cursor.fetchall()
        
        print("\n📊 COLUMNAS:")
        print("-" * 80)
        for col in columnas:
            print(f"  - {col['name']:30} | Tipo: {col['type']:15} | NOT NULL: {bool(col['notnull'])}")
        
        # 4. Verificar índices
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='historial_laboral'
        """)
        indices = cursor.fetchall()
        
        print("\n🔗 ÍNDICES:")
        print("-" * 80)
        if indices:
            for idx in indices:
                print(f"  - {idx['name']}")
        else:
            print("  ⚠️ No hay índices creados")
        
        # 5. Contar registros
        cursor.execute("SELECT COUNT(*) as total FROM historial_laboral")
        total = cursor.fetchone()['total']
        
        print(f"\n📈 TOTAL DE REGISTROS: {total}")
        
        # 6. Mostrar últimos 5 registros
        if total > 0:
            cursor.execute("""
                SELECT 
                    h.id,
                    h.usuario_id,
                    h.fecha_cambio,
                    h.tipo_operacion,
                    h.empresa_anterior_nit,
                    h.empresa_nueva_nit,
                    h.responsable_nombre,
                    h.motivo
                FROM historial_laboral h
                ORDER BY h.fecha_cambio DESC
                LIMIT 5
            """)
            
            registros = cursor.fetchall()
            print("\n📜 ÚLTIMOS 5 REGISTROS:")
            print("-" * 80)
            for reg in registros:
                print(f"\nID: {reg['id']} | Usuario: {reg['usuario_id']} | Fecha: {reg['fecha_cambio']}")
                print(f"  Operación: {reg['tipo_operacion']}")
                print(f"  Empresa Anterior: {reg['empresa_anterior_nit'] or 'N/A'}")
                print(f"  Empresa Nueva: {reg['empresa_nueva_nit'] or 'N/A'}")
                print(f"  Responsable: {reg['responsable_nombre']}")
                print(f"  Motivo: {reg['motivo']}")
        
        # 7. Verificar vista
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name='vista_historial_laboral_completo'
        """)
        
        if cursor.fetchone():
            print("\n✅ Vista 'vista_historial_laboral_completo' existe")
            
            # Contar registros en vista
            cursor.execute("SELECT COUNT(*) as total FROM vista_historial_laboral_completo")
            total_vista = cursor.fetchone()['total']
            print(f"   Total en vista: {total_vista}")
        else:
            print("\n⚠️ Vista 'vista_historial_laboral_completo' NO existe")
        
        print("\n" + "=" * 80)
        print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ ERROR DE BASE DE DATOS: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def insertar_registro_prueba():
    """Inserta un registro de prueba en historial_laboral."""
    print("\n" + "=" * 80)
    print("🧪 INSERTAR REGISTRO DE PRUEBA")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener un usuario de prueba
        cursor.execute("SELECT id FROM usuarios LIMIT 1")
        usuario = cursor.fetchone()
        
        if not usuario:
            print("❌ No hay usuarios en la base de datos para crear registro de prueba")
            return False
        
        usuario_id = usuario[0]
        
        # Obtener una empresa de prueba
        cursor.execute("SELECT nit FROM empresas LIMIT 1")
        empresa = cursor.fetchone()
        
        if not empresa:
            print("❌ No hay empresas en la base de datos para crear registro de prueba")
            return False
        
        empresa_nit = empresa[0]
        
        # Insertar registro de prueba
        cursor.execute("""
            INSERT INTO historial_laboral (
                usuario_id,
                empresa_anterior_nit,
                empresa_nueva_nit,
                motivo,
                responsable_nombre,
                tipo_operacion,
                observaciones
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            usuario_id,
            None,
            empresa_nit,
            "Registro de prueba automático",
            "Sistema de Verificación",
            "VINCULACION",
            f"Registro creado automáticamente para testing - {datetime.now()}"
        ))
        
        conn.commit()
        
        print(f"✅ Registro de prueba insertado:")
        print(f"   Usuario ID: {usuario_id}")
        print(f"   Empresa NIT: {empresa_nit}")
        print(f"   Tipo: VINCULACION")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ ERROR AL INSERTAR: {e}")
        return False


def menu_principal():
    """Menú interactivo para verificar el módulo."""
    while True:
        print("\n" + "=" * 80)
        print("🔧 HERRAMIENTA DE VERIFICACIÓN - MÓDULO DE UNIFICACIÓN")
        print("=" * 80)
        print("\n1. Verificar estructura de tabla historial_laboral")
        print("2. Insertar registro de prueba")
        print("3. Ver últimos 10 registros")
        print("4. Contar registros por tipo de operación")
        print("5. Salir")
        print("\n" + "-" * 80)
        
        opcion = input("\nSeleccione una opción (1-5): ").strip()
        
        if opcion == "1":
            verificar_tabla_historial()
        
        elif opcion == "2":
            insertar_registro_prueba()
        
        elif opcion == "3":
            ver_ultimos_registros()
        
        elif opcion == "4":
            contar_por_tipo()
        
        elif opcion == "5":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("\n❌ Opción inválida. Intente nuevamente.")


def ver_ultimos_registros():
    """Muestra los últimos 10 registros del historial."""
    print("\n" + "=" * 80)
    print("📜 ÚLTIMOS 10 REGISTROS")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                usuario_id,
                fecha_cambio,
                tipo_operacion,
                empresa_anterior_nit,
                empresa_nueva_nit,
                responsable_nombre,
                motivo
            FROM historial_laboral
            ORDER BY fecha_cambio DESC
            LIMIT 10
        """)
        
        registros = cursor.fetchall()
        
        if not registros:
            print("\n⚠️ No hay registros en historial_laboral")
        else:
            for i, reg in enumerate(registros, 1):
                print(f"\n{i}. ID: {reg['id']} | Usuario: {reg['usuario_id']} | Fecha: {reg['fecha_cambio']}")
                print(f"   Operación: {reg['tipo_operacion']}")
                print(f"   Empresa Anterior: {reg['empresa_anterior_nit'] or 'N/A'}")
                print(f"   Empresa Nueva: {reg['empresa_nueva_nit'] or 'N/A'}")
                print(f"   Responsable: {reg['responsable_nombre']}")
                print(f"   Motivo: {reg['motivo']}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n❌ ERROR: {e}")


def contar_por_tipo():
    """Cuenta registros agrupados por tipo de operación."""
    print("\n" + "=" * 80)
    print("📊 ESTADÍSTICAS POR TIPO DE OPERACIÓN")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                tipo_operacion,
                COUNT(*) as total
            FROM historial_laboral
            GROUP BY tipo_operacion
            ORDER BY total DESC
        """)
        
        resultados = cursor.fetchall()
        
        if not resultados:
            print("\n⚠️ No hay registros en historial_laboral")
        else:
            print("\n")
            for res in resultados:
                print(f"  {res['tipo_operacion']:20} → {res['total']:5} registros")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    print("\n🚀 Iniciando verificación del módulo de Unificación...")
    
    if os.path.exists(DB_PATH):
        print(f"✅ Base de datos encontrada: {DB_PATH}")
        menu_principal()
    else:
        print(f"❌ Base de datos no encontrada en: {DB_PATH}")
        print("💡 Verifica la ruta de la base de datos")
