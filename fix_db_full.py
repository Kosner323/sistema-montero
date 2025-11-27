#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                   SCRIPT DE MIGRACIÓN COMPLETA DE BD                      ║
║                                                                           ║
║  Fecha: 25 de Noviembre de 2025                                          ║
║  Descripción: Agrega TODAS las columnas faltantes a empresas y usuarios ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import sqlite3
import os
from datetime import datetime

# Ruta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'mi_sistema.db')

def ejecutar_migracion():
    """
    Ejecuta la migración completa agregando columnas faltantes
    """
    print("="*80)
    print("🔧 INICIANDO MIGRACIÓN COMPLETA DE BASE DE DATOS")
    print("="*80)
    print(f"📂 Base de datos: {DB_PATH}")
    print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: No se encontró la base de datos en {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # ═══════════════════════════════════════════════════════════
        # PARTE A: TABLA EMPRESAS
        # ═══════════════════════════════════════════════════════════
        print("📋 TABLA: empresas")
        print("-" * 80)
        
        columnas_empresas = [
            # Financieros
            ("banco", "TEXT"),
            ("tipo_cuenta", "TEXT"),
            ("numero_cuenta", "TEXT"),
            
            # Operativos
            ("sector_economico", "TEXT"),
            ("num_empleados", "INTEGER"),
            ("fecha_constitucion", "TEXT"),
            ("tipo_empresa", "TEXT"),
            
            # Seguridad Social (si no existen)
            ("arl", "TEXT"),
            ("ccf", "TEXT"),
            
            # Representante Legal Detalle
            ("rep_legal_tipo_id", "TEXT"),
            ("rep_legal_numero_id", "TEXT"),
            ("rep_legal_telefono", "TEXT"),
            ("rep_legal_correo", "TEXT"),
        ]
        
        # Obtener columnas existentes en empresas
        cursor.execute("PRAGMA table_info(empresas)")
        columnas_existentes_empresas = {row[1] for row in cursor.fetchall()}
        
        contador_empresas = 0
        for columna, tipo in columnas_empresas:
            if columna not in columnas_existentes_empresas:
                try:
                    sql = f"ALTER TABLE empresas ADD COLUMN {columna} {tipo}"
                    cursor.execute(sql)
                    print(f"  ✅ Columna agregada: {columna} ({tipo})")
                    contador_empresas += 1
                except Exception as e:
                    print(f"  ⚠️ Error agregando {columna}: {e}")
            else:
                print(f"  ℹ️ Columna ya existe: {columna}")
        
        print(f"\n✅ Empresas: {contador_empresas} columnas nuevas agregadas\n")
        
        # ═══════════════════════════════════════════════════════════
        # PARTE B: TABLA USUARIOS
        # ═══════════════════════════════════════════════════════════
        print("📋 TABLA: usuarios")
        print("-" * 80)
        
        columnas_usuarios = [
            # Ubicación de Residencia (diferente a nacimiento)
            ("municipioResidencia", "TEXT"),
            ("departamentoResidencia", "TEXT"),
            ("paisResidencia", "TEXT"),
            
            # Datos Laborales
            ("cargo", "TEXT"),
            ("tipo_contrato", "TEXT"),
        ]
        
        # Obtener columnas existentes en usuarios
        cursor.execute("PRAGMA table_info(usuarios)")
        columnas_existentes_usuarios = {row[1] for row in cursor.fetchall()}
        
        contador_usuarios = 0
        for columna, tipo in columnas_usuarios:
            if columna not in columnas_existentes_usuarios:
                try:
                    sql = f"ALTER TABLE usuarios ADD COLUMN {columna} {tipo}"
                    cursor.execute(sql)
                    print(f"  ✅ Columna agregada: {columna} ({tipo})")
                    contador_usuarios += 1
                except Exception as e:
                    print(f"  ⚠️ Error agregando {columna}: {e}")
            else:
                print(f"  ℹ️ Columna ya existe: {columna}")
        
        print(f"\n✅ Usuarios: {contador_usuarios} columnas nuevas agregadas\n")
        
        # Guardar cambios
        conn.commit()
        
        # ═══════════════════════════════════════════════════════════
        # RESUMEN FINAL
        # ═══════════════════════════════════════════════════════════
        print("="*80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print(f"📊 Resumen:")
        print(f"   • Empresas: {contador_empresas} columnas agregadas")
        print(f"   • Usuarios: {contador_usuarios} columnas agregadas")
        print(f"   • Total: {contador_empresas + contador_usuarios} columnas nuevas")
        print("\n🎉 La base de datos está lista para recibir todos los datos completos")
        print("="*80)
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    exito = ejecutar_migracion()
    
    if exito:
        print("\n🚀 Próximos pasos:")
        print("   1. Actualiza el código backend (empresas.py y usuarios.py)")
        print("   2. Actualiza los formularios frontend (ingresar.html y gestion.html)")
        print("   3. Reinicia el servidor Flask")
        print("   4. Prueba creando/editando empresas y usuarios\n")
        exit(0)
    else:
        print("\n⚠️ La migración falló. Revisa los errores anteriores.\n")
        exit(1)
