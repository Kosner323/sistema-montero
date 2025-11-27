#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicialización de Módulos Nuevos
===========================================
Crea las tablas necesarias para los nuevos módulos del sistema:
- Marketing (Prospectos, Campañas, Redes)
- Cartera (Cuentas por Cobrar, Obligaciones SS)
- Documentos y Auditoría
- Automatización (Copiloto ARL)
- Impuestos

Autor: Portal Montero
Fecha: 2025
"""

import sqlite3
import os
import sys
from pathlib import Path

# Configurar encoding UTF-8 para la consola de Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ========================================================================
# CONFIGURACIÓN
# ========================================================================

# Ruta a la base de datos
DB_PATH = Path(__file__).parent / "src" / "dashboard" / "data" / "mi_sistema.db"

print("="*70)
print("🔧 INICIALIZADOR DE MÓDULOS NUEVOS - Portal Montero")
print("="*70)
print(f"📂 Ruta de BD: {DB_PATH}")
print()

# ========================================================================
# SQL - DEFINICIONES DE TABLAS
# ========================================================================

SQL_STATEMENTS = [
    # ====================================================================
    # MÓDULO: MARKETING
    # ====================================================================
    """
    CREATE TABLE IF NOT EXISTS marketing_redes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plataforma TEXT NOT NULL,
        url TEXT NOT NULL,
        seguidores INTEGER DEFAULT 0,
        estado TEXT DEFAULT 'Activo',
        descripcion TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS marketing_campanas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_campana TEXT NOT NULL,
        descripcion TEXT,
        fecha_inicio TEXT NOT NULL,
        fecha_fin TEXT NOT NULL,
        presupuesto REAL DEFAULT 0.0,
        estado TEXT DEFAULT 'Activa',
        objetivo TEXT,
        canal TEXT,
        metricas_alcance INTEGER DEFAULT 0,
        metricas_conversiones INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS marketing_prospectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        telefono TEXT,
        correo TEXT,
        origen TEXT DEFAULT 'Web',
        interes TEXT,
        estado TEXT DEFAULT 'Nuevo',
        notas TEXT,
        fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
        fecha_contacto TEXT,
        fecha_cierre TEXT,
        valor_estimado REAL DEFAULT 0.0,
        asignado_a TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,

    # ====================================================================
    # MÓDULO: CARTERA (Gestión Financiera)
    # ====================================================================
    """
    CREATE TABLE IF NOT EXISTS cartera_cobrar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_nit TEXT NOT NULL,
        concepto TEXT NOT NULL,
        monto REAL NOT NULL DEFAULT 0.0,
        fecha_emision TEXT DEFAULT CURRENT_TIMESTAMP,
        fecha_vencimiento TEXT NOT NULL,
        estado TEXT DEFAULT 'Pendiente',
        monto_pagado REAL DEFAULT 0.0,
        fecha_pago TEXT,
        notas TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS cartera_pagar_ss (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_nit TEXT NOT NULL,
        tipo_entidad TEXT NOT NULL,
        nombre_entidad TEXT NOT NULL,
        periodo TEXT NOT NULL,
        monto REAL NOT NULL DEFAULT 0.0,
        fecha_limite TEXT NOT NULL,
        estado TEXT DEFAULT 'Pendiente',
        fecha_pago TEXT,
        numero_planilla TEXT,
        notas TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (empresa_nit) REFERENCES empresas(nit)
    )
    """,

    # ====================================================================
    # MÓDULO: IMPUESTOS
    # ====================================================================
    """
    CREATE TABLE IF NOT EXISTS pago_impuestos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_nit TEXT NOT NULL,
        empresa_nombre TEXT NOT NULL,
        tipo_impuesto TEXT NOT NULL,
        periodo TEXT NOT NULL,
        fecha_limite TEXT NOT NULL,
        estado TEXT DEFAULT 'Pendiente de Pago' CHECK(estado IN ('Pendiente de Pago', 'Pagado', 'Vencido')),
        ruta_archivo TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (empresa_nit) REFERENCES empresas(nit) ON DELETE CASCADE
    )
    """,

    # ====================================================================
    # MÓDULO: DOCUMENTOS Y ARCHIVOS
    # ====================================================================
    """
    CREATE TABLE IF NOT EXISTS documentos_gestor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_archivo TEXT NOT NULL,
        nombre_interno TEXT NOT NULL UNIQUE,
        ruta TEXT NOT NULL,
        categoria TEXT NOT NULL CHECK(categoria IN ('Legal', 'Contable', 'RRHH', 'Operativo', 'Otro')),
        tipo_mime TEXT,
        tamano_bytes INTEGER,
        fecha_subida TEXT DEFAULT CURRENT_TIMESTAMP,
        subido_por INTEGER NOT NULL,
        subido_por_nombre TEXT,
        descripcion TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (subido_por) REFERENCES usuarios(id) ON DELETE CASCADE
    )
    """,

    # ====================================================================
    # MÓDULO: AUDITORÍA Y LOGS
    # ====================================================================
    """
    CREATE TABLE IF NOT EXISTS auditoria_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        usuario_nombre TEXT NOT NULL,
        accion TEXT NOT NULL,
        detalle TEXT,
        resultado TEXT CHECK(resultado IN ('exito', 'error', 'advertencia')),
        ip_address TEXT,
        user_agent TEXT,
        metodo_http TEXT,
        ruta TEXT,
        fecha_hora TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )
    """,

    # ====================================================================
    # MÓDULO: AUTOMATIZACIÓN (Copiloto ARL)
    # ====================================================================
    """
    CREATE TABLE IF NOT EXISTS copiloto_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id TEXT NOT NULL UNIQUE,
        accion TEXT NOT NULL,
        empresa_nit TEXT NOT NULL,
        empresa_nombre TEXT,
        empleado_id TEXT,
        empleado_nombre TEXT,
        estado TEXT DEFAULT 'iniciado' CHECK(estado IN ('iniciado', 'ejecutando', 'completado', 'error')),
        progreso INTEGER DEFAULT 0,
        mensaje TEXT,
        resultado_json TEXT,
        usuario_id INTEGER,
        fecha_inicio TEXT DEFAULT CURRENT_TIMESTAMP,
        fecha_fin TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (empresa_nit) REFERENCES empresas(nit),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )
    """,
]

# ========================================================================
# ÍNDICES PARA OPTIMIZACIÓN
# ========================================================================

SQL_INDEXES = [
    # Marketing
    "CREATE INDEX IF NOT EXISTS idx_marketing_redes_plataforma ON marketing_redes(plataforma)",
    "CREATE INDEX IF NOT EXISTS idx_marketing_campanas_estado ON marketing_campanas(estado)",
    "CREATE INDEX IF NOT EXISTS idx_marketing_campanas_fechas ON marketing_campanas(fecha_inicio, fecha_fin)",
    "CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_estado ON marketing_prospectos(estado)",
    "CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_origen ON marketing_prospectos(origen)",
    "CREATE INDEX IF NOT EXISTS idx_marketing_prospectos_fecha ON marketing_prospectos(fecha_registro)",

    # Cartera
    "CREATE INDEX IF NOT EXISTS idx_cartera_cobrar_empresa ON cartera_cobrar(empresa_nit)",
    "CREATE INDEX IF NOT EXISTS idx_cartera_cobrar_estado ON cartera_cobrar(estado)",
    "CREATE INDEX IF NOT EXISTS idx_cartera_cobrar_vencimiento ON cartera_cobrar(fecha_vencimiento)",
    "CREATE INDEX IF NOT EXISTS idx_cartera_pagar_empresa ON cartera_pagar_ss(empresa_nit)",
    "CREATE INDEX IF NOT EXISTS idx_cartera_pagar_tipo ON cartera_pagar_ss(tipo_entidad)",
    "CREATE INDEX IF NOT EXISTS idx_cartera_pagar_periodo ON cartera_pagar_ss(periodo)",
    "CREATE INDEX IF NOT EXISTS idx_cartera_pagar_estado ON cartera_pagar_ss(estado)",

    # Impuestos
    "CREATE INDEX IF NOT EXISTS idx_impuestos_empresa ON pago_impuestos(empresa_nit)",
    "CREATE INDEX IF NOT EXISTS idx_impuestos_tipo ON pago_impuestos(tipo_impuesto)",
    "CREATE INDEX IF NOT EXISTS idx_impuestos_estado ON pago_impuestos(estado)",
    "CREATE INDEX IF NOT EXISTS idx_impuestos_fecha_limite ON pago_impuestos(fecha_limite)",

    # Documentos
    "CREATE INDEX IF NOT EXISTS idx_documentos_categoria ON documentos_gestor(categoria)",
    "CREATE INDEX IF NOT EXISTS idx_documentos_subido_por ON documentos_gestor(subido_por)",
    "CREATE INDEX IF NOT EXISTS idx_documentos_fecha ON documentos_gestor(fecha_subida)",

    # Auditoría
    "CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria_logs(usuario_id)",
    "CREATE INDEX IF NOT EXISTS idx_auditoria_accion ON auditoria_logs(accion)",
    "CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria_logs(fecha_hora DESC)",
    "CREATE INDEX IF NOT EXISTS idx_auditoria_resultado ON auditoria_logs(resultado)",

    # Copiloto
    "CREATE INDEX IF NOT EXISTS idx_copiloto_jobs_job_id ON copiloto_jobs(job_id)",
    "CREATE INDEX IF NOT EXISTS idx_copiloto_jobs_empresa ON copiloto_jobs(empresa_nit)",
    "CREATE INDEX IF NOT EXISTS idx_copiloto_jobs_estado ON copiloto_jobs(estado)",
    "CREATE INDEX IF NOT EXISTS idx_copiloto_jobs_fecha ON copiloto_jobs(fecha_inicio DESC)",
]

# ========================================================================
# FUNCIONES PRINCIPALES
# ========================================================================

def initialize_database():
    """
    Conecta a la base de datos y crea todas las tablas necesarias.
    """
    try:
        # Verificar que la base de datos existe
        if not DB_PATH.exists():
            print(f"❌ ERROR: La base de datos no existe en {DB_PATH}")
            print("💡 Sugerencia: Primero ejecuta el script principal del sistema.")
            return False

        # Conectar a la base de datos
        print("📡 Conectando a la base de datos...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Activar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        print("✅ Conexión exitosa\n")

        # Crear tablas
        print("📋 Creando tablas nuevas...")
        print("-" * 70)

        table_names = [
            "marketing_redes",
            "marketing_campanas",
            "marketing_prospectos",
            "cartera_cobrar",
            "cartera_pagar_ss",
            "pago_impuestos",
            "documentos_gestor",
            "auditoria_logs",
            "copiloto_jobs"
        ]

        for i, sql in enumerate(SQL_STATEMENTS):
            table_name = table_names[i]
            try:
                cursor.execute(sql)
                print(f"  ✅ Tabla creada/verificada: {table_name}")
            except Exception as e:
                print(f"  ⚠️  Error en tabla {table_name}: {e}")

        print()

        # Crear índices
        print("🔍 Creando índices para optimización...")
        print("-" * 70)

        indices_creados = 0
        for sql_index in SQL_INDEXES:
            try:
                cursor.execute(sql_index)
                indices_creados += 1
            except Exception as e:
                print(f"  ⚠️  Error creando índice: {e}")

        print(f"  ✅ {indices_creados} índices creados/verificados")
        print()

        # Commit cambios
        conn.commit()

        # Verificar tablas creadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tablas_totales = cursor.fetchall()

        print("="*70)
        print(f"✅ BASE DE DATOS LISTA CON TODAS LAS TABLAS NUEVAS")
        print(f"📊 Total de tablas en la BD: {len(tablas_totales)}")
        print("="*70)
        print()
        print("🚀 Módulos disponibles:")
        print("   • Marketing (Prospectos, Campañas, Redes Sociales)")
        print("   • Cartera (Cuentas por Cobrar, Obligaciones SS)")
        print("   • Impuestos (Formularios y Pagos)")
        print("   • Documentos (Gestor de Archivos)")
        print("   • Auditoría (Logs del Sistema)")
        print("   • Copiloto ARL (Automatización RPA)")
        print()
        print("✅ El sistema está listo para ejecutar el módulo Copiloto ARL")
        print()

        # Cerrar conexión
        conn.close()
        return True

    except sqlite3.Error as e:
        print(f"❌ ERROR DE BASE DE DATOS: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        return False

# ========================================================================
# PUNTO DE ENTRADA
# ========================================================================

if __name__ == "__main__":
    try:
        success = initialize_database()

        if success:
            print("🎉 Proceso completado exitosamente")
            print("💡 Ahora puedes ejecutar el módulo Copiloto ARL sin errores")
        else:
            print("⚠️  El proceso finalizó con advertencias")
            print("💡 Revisa los mensajes anteriores para más detalles")

    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
