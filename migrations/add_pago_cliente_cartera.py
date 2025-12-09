# -*- coding: utf-8 -*-
"""
Migración: Agregar campos de pago a cliente en incapacidades y crear tabla deudas_cartera
========================================================================================
Fecha: 2024-11-29
Descripción: 
    1. Agrega campos para flujo de pago a cliente en tabla incapacidades
    2. Crea nueva tabla deudas_cartera para gestión de cartera
"""
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "data", "mi_sistema.db")

def run_migration():
    """Ejecuta la migración de base de datos"""
    
    print("=" * 80)
    print("🔄 INICIANDO MIGRACIÓN DE BASE DE DATOS")
    print("=" * 80)
    print(f"📁 Base de datos: {DATABASE_PATH}")
    print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not os.path.exists(DATABASE_PATH):
        print(f"❌ ERROR: La base de datos no existe en {DATABASE_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # ========== PASO 1: Verificar tabla incapacidades ==========
        print("📋 PASO 1: Verificando tabla 'incapacidades'...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incapacidades'")
        if not cursor.fetchone():
            print("❌ ERROR: La tabla 'incapacidades' no existe")
            return False
        print("✅ Tabla 'incapacidades' encontrada")
        
        # ========== PASO 2: Agregar columnas a incapacidades ==========
        print("\n📋 PASO 2: Agregando columnas de pago a cliente en 'incapacidades'...")
        
        nuevas_columnas = [
            ("monto_pagado_cliente", "DECIMAL(15, 2)"),
            ("fecha_pago_cliente", "TEXT"),
            ("observaciones_pago", "TEXT"),
            ("comprobante_pago", "TEXT"),
            ("fecha_cierre", "TEXT")
        ]
        
        # Obtener columnas existentes
        cursor.execute("PRAGMA table_info(incapacidades)")
        columnas_existentes = [row[1] for row in cursor.fetchall()]
        
        columnas_agregadas = 0
        for columna, tipo in nuevas_columnas:
            if columna not in columnas_existentes:
                try:
                    sql = f"ALTER TABLE incapacidades ADD COLUMN {columna} {tipo}"
                    cursor.execute(sql)
                    print(f"   ✅ Columna '{columna}' agregada")
                    columnas_agregadas += 1
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️  Columna '{columna}' ya existe o error: {e}")
            else:
                print(f"   ℹ️  Columna '{columna}' ya existe")
        
        print(f"✅ {columnas_agregadas} columna(s) nueva(s) agregada(s) a 'incapacidades'")
        
        # ========== PASO 3: Crear tabla deudas_cartera ==========
        print("\n📋 PASO 3: Creando tabla 'deudas_cartera'...")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='deudas_cartera'")
        if cursor.fetchone():
            print("   ℹ️  Tabla 'deudas_cartera' ya existe")
        else:
            sql_create_deudas_cartera = """
            CREATE TABLE deudas_cartera (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id TEXT NOT NULL,
                nombre_usuario TEXT,
                empresa_nit TEXT NOT NULL,
                nombre_empresa TEXT,
                entidad TEXT NOT NULL,
                monto DECIMAL(15, 2) NOT NULL,
                dias_mora INTEGER DEFAULT 0,
                estado TEXT DEFAULT 'Pendiente',
                tipo TEXT DEFAULT 'Manual',
                fecha_creacion TEXT,
                fecha_vencimiento TEXT,
                usuario_registro TEXT,
                FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)
            )
            """
            cursor.execute(sql_create_deudas_cartera)
            print("   ✅ Tabla 'deudas_cartera' creada exitosamente")
            
            # Crear índices para mejor performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deudas_usuario ON deudas_cartera(usuario_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deudas_empresa ON deudas_cartera(empresa_nit)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_deudas_estado ON deudas_cartera(estado)")
            print("   ✅ Índices creados en 'deudas_cartera'")
        
        # ========== PASO 4: Commit y verificación ==========
        conn.commit()
        
        print("\n📋 PASO 4: Verificando estructura final...")
        
        # Verificar incapacidades
        cursor.execute("PRAGMA table_info(incapacidades)")
        campos_incapacidades = cursor.fetchall()
        print(f"\n   📊 Tabla 'incapacidades': {len(campos_incapacidades)} columnas")
        for campo in campos_incapacidades:
            if campo[1] in ['monto_pagado_cliente', 'fecha_pago_cliente', 'comprobante_pago', 'fecha_cierre']:
                print(f"      ✅ {campo[1]} ({campo[2]})")
        
        # Verificar deudas_cartera
        cursor.execute("PRAGMA table_info(deudas_cartera)")
        campos_deudas = cursor.fetchall()
        print(f"\n   📊 Tabla 'deudas_cartera': {len(campos_deudas)} columnas")
        for campo in campos_deudas:
            print(f"      - {campo[1]} ({campo[2]})")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM incapacidades")
        total_incapacidades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM deudas_cartera")
        total_deudas = cursor.fetchone()[0]
        
        print(f"\n📊 RESUMEN DE DATOS:")
        print(f"   - Incapacidades existentes: {total_incapacidades}")
        print(f"   - Deudas en cartera: {total_deudas}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 80)
        print("\n📝 Cambios aplicados:")
        print("   1. ✅ Agregadas columnas de pago a cliente en 'incapacidades'")
        print("   2. ✅ Creada tabla 'deudas_cartera' con índices")
        print("   3. ✅ Estructura de BD actualizada y verificada")
        print("\n🚀 Sistema listo para:")
        print("   - Endpoint: PUT /api/incapacidades/<id>/transferir-cliente")
        print("   - Endpoint: POST /api/cartera/carga-masiva")
        print("=" * 80)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ ERROR DE BASE DE DATOS: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    exitoso = run_migration()
    exit(0 if exitoso else 1)
