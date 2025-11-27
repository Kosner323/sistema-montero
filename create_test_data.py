#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para insertar datos de prueba en la base de datos.

Crea:
- Empresa: Innovatech S.A.S (NIT: 900111222)
- Usuario: Pedro Pérez (Cédula: 100100100, Role: empleado)

Uso:
    python create_test_data.py
"""

import os
import sqlite3
import sys
from datetime import datetime

from werkzeug.security import generate_password_hash

# ==================== CONFIGURACIÓN ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "mi_sistema.db")

# ==================== DATOS DE PRUEBA ====================

# Empresa de prueba
EMPRESA_TEST = {
    'nit': '900111222',
    'nombre_empresa': 'Innovatech S.A.S',
    'tipo_identificacion_empresa': 'NIT',
    'direccion_empresa': 'Calle 100 # 20-30',
    'telefono_empresa': '6012345678',
    'correo_empresa': 'info@innovatech.com.co',
    'departamento_empresa': 'Cundinamarca',
    'ciudad_empresa': 'Bogotá',
    'ibc_empresa': 5000000.0,
    'afp_empresa': 'Porvenir',
    'arl_empresa': 'Sura',
    'rep_legal_nombre': 'Carlos Alberto Gómez',
    'rep_legal_tipo_id': 'CC',
    'rep_legal_numero_id': '80123456'
}

# Usuario de prueba (empleado)
USUARIO_TEST = {
    'empresa_nit': '900111222',  # ✅ Vinculado a Innovatech
    'tipoId': 'CC',
    'numeroId': '100100100',
    'primerNombre': 'Pedro',
    'segundoNombre': 'Antonio',
    'primerApellido': 'Pérez',
    'segundoApellido': 'Rodríguez',
    'sexoBiologico': 'Masculino',
    'sexoIdentificacion': 'Masculino',
    'nacionalidad': 'Colombiana',
    'fechaNacimiento': '1990-05-15',
    'paisNacimiento': 'Colombia',
    'departamentoNacimiento': 'Cundinamarca',
    'municipioNacimiento': 'Bogotá',
    'direccion': 'Carrera 50 # 80-20',
    'telefonoCelular': '3101234567',
    'correoElectronico': 'pedro.perez@innovatech.com.co',
    'comunaBarrio': 'Suba',
    'afpNombre': 'Porvenir',
    'afpCosto': 48000.0,
    'epsNombre': 'Sura',
    'epsCosto': 128000.0,
    'arlNombre': 'Sura',
    'arlCosto': 5220.0,
    'ccfNombre': 'Compensar',
    'ccfCosto': 40000.0,
    'administracion': 'Innovatech S.A.S',
    'ibc': 1200000.0,
    'claseRiesgoARL': 'I',
    'fechaIngreso': '2023-01-15',
    'password_hash': generate_password_hash('test1234'),  # ✅ Contraseña hasheada
    'estado': 'activo',
    'role': 'empleado'
}


# ==================== FUNCIÓN PRINCIPAL ====================

def get_db_connection():
    """Establece conexión con la base de datos SQLite."""
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Base de datos no encontrada en {DB_PATH}")
        print("   Por favor, ejecuta primero el script de inicialización.")
        sys.exit(1)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def insert_test_data():
    """Inserta empresa y usuario de prueba en la base de datos."""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("=" * 70)
    print("🚀 INSERCIÓN DE DATOS DE PRUEBA")
    print("=" * 70)
    
    try:
        # ==================== INSERTAR EMPRESA ====================
        print("\n📦 Insertando empresa de prueba...")
        
        cursor.execute("""
            INSERT OR IGNORE INTO empresas (
                nit, nombre_empresa, tipo_identificacion_empresa,
                direccion_empresa, telefono_empresa, correo_empresa,
                departamento_empresa, ciudad_empresa, ibc_empresa,
                afp_empresa, arl_empresa, rep_legal_nombre,
                rep_legal_tipo_id, rep_legal_numero_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            EMPRESA_TEST['nit'],
            EMPRESA_TEST['nombre_empresa'],
            EMPRESA_TEST['tipo_identificacion_empresa'],
            EMPRESA_TEST['direccion_empresa'],
            EMPRESA_TEST['telefono_empresa'],
            EMPRESA_TEST['correo_empresa'],
            EMPRESA_TEST['departamento_empresa'],
            EMPRESA_TEST['ciudad_empresa'],
            EMPRESA_TEST['ibc_empresa'],
            EMPRESA_TEST['afp_empresa'],
            EMPRESA_TEST['arl_empresa'],
            EMPRESA_TEST['rep_legal_nombre'],
            EMPRESA_TEST['rep_legal_tipo_id'],
            EMPRESA_TEST['rep_legal_numero_id']
        ))
        
        if cursor.rowcount > 0:
            print(f"   ✅ Empresa creada: {EMPRESA_TEST['nombre_empresa']} (NIT: {EMPRESA_TEST['nit']})")
        else:
            print(f"   ℹ️  Empresa ya existe: {EMPRESA_TEST['nombre_empresa']} (NIT: {EMPRESA_TEST['nit']})")
        
        
        # ==================== INSERTAR USUARIO ====================
        print("\n👤 Insertando usuario de prueba...")
        
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (
                empresa_nit, tipoId, numeroId,
                primerNombre, segundoNombre, primerApellido, segundoApellido,
                sexoBiologico, sexoIdentificacion, nacionalidad,
                fechaNacimiento, paisNacimiento, departamentoNacimiento, municipioNacimiento,
                direccion, telefonoCelular, correoElectronico, comunaBarrio,
                afpNombre, afpCosto, epsNombre, epsCosto, arlNombre, arlCosto, ccfNombre, ccfCosto,
                administracion, ibc, claseRiesgoARL, fechaIngreso,
                password_hash, estado, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            USUARIO_TEST['empresa_nit'],
            USUARIO_TEST['tipoId'],
            USUARIO_TEST['numeroId'],
            USUARIO_TEST['primerNombre'],
            USUARIO_TEST['segundoNombre'],
            USUARIO_TEST['primerApellido'],
            USUARIO_TEST['segundoApellido'],
            USUARIO_TEST['sexoBiologico'],
            USUARIO_TEST['sexoIdentificacion'],
            USUARIO_TEST['nacionalidad'],
            USUARIO_TEST['fechaNacimiento'],
            USUARIO_TEST['paisNacimiento'],
            USUARIO_TEST['departamentoNacimiento'],
            USUARIO_TEST['municipioNacimiento'],
            USUARIO_TEST['direccion'],
            USUARIO_TEST['telefonoCelular'],
            USUARIO_TEST['correoElectronico'],
            USUARIO_TEST['comunaBarrio'],
            USUARIO_TEST['afpNombre'],
            USUARIO_TEST['afpCosto'],
            USUARIO_TEST['epsNombre'],
            USUARIO_TEST['epsCosto'],
            USUARIO_TEST['arlNombre'],
            USUARIO_TEST['arlCosto'],
            USUARIO_TEST['ccfNombre'],
            USUARIO_TEST['ccfCosto'],
            USUARIO_TEST['administracion'],
            USUARIO_TEST['ibc'],
            USUARIO_TEST['claseRiesgoARL'],
            USUARIO_TEST['fechaIngreso'],
            USUARIO_TEST['password_hash'],
            USUARIO_TEST['estado'],
            USUARIO_TEST['role']
        ))
        
        if cursor.rowcount > 0:
            print(f"   ✅ Usuario creado: {USUARIO_TEST['primerNombre']} {USUARIO_TEST['primerApellido']} (CC: {USUARIO_TEST['numeroId']})")
            print(f"      🔑 Cédula: {USUARIO_TEST['numeroId']}")
            print(f"      🔒 Password: test1234")
            print(f"      🏢 Empresa: {EMPRESA_TEST['nombre_empresa']}")
            print(f"      🎭 Rol: {USUARIO_TEST['role']}")
        else:
            print(f"   ℹ️  Usuario ya existe: {USUARIO_TEST['primerNombre']} {USUARIO_TEST['primerApellido']} (CC: {USUARIO_TEST['numeroId']})")
        
        
        # ==================== CONFIRMAR CAMBIOS ====================
        conn.commit()
        
        
        # ==================== VERIFICACIÓN FINAL ====================
        print("\n" + "=" * 70)
        print("🔍 VERIFICACIÓN DE DATOS")
        print("=" * 70)
        
        # Verificar empresa
        cursor.execute("SELECT nit, nombre_empresa FROM empresas WHERE nit = ?", (EMPRESA_TEST['nit'],))
        empresa = cursor.fetchone()
        if empresa:
            print(f"\n✅ Empresa encontrada:")
            print(f"   NIT: {empresa['nit']}")
            print(f"   Nombre: {empresa['nombre_empresa']}")
        
        # Verificar usuario
        cursor.execute("""
            SELECT u.numeroId, u.primerNombre, u.primerApellido, u.role, u.empresa_nit, e.nombre_empresa
            FROM usuarios u
            LEFT JOIN empresas e ON u.empresa_nit = e.nit
            WHERE u.numeroId = ?
        """, (USUARIO_TEST['numeroId'],))
        usuario = cursor.fetchone()
        if usuario:
            print(f"\n✅ Usuario encontrado:")
            print(f"   Cédula: {usuario['numeroId']}")
            print(f"   Nombre: {usuario['primerNombre']} {usuario['primerApellido']}")
            print(f"   Rol: {usuario['role']}")
            print(f"   Empresa NIT: {usuario['empresa_nit']}")
            print(f"   Empresa Nombre: {usuario['nombre_empresa']}")
        
        
        # ==================== RESUMEN ====================
        print("\n" + "=" * 70)
        print("✅ DATOS DE PRUEBA INSERTADOS CORRECTAMENTE")
        print("=" * 70)
        print("\n📋 Resumen:")
        print(f"   🏢 Empresa: {EMPRESA_TEST['nombre_empresa']} (NIT: {EMPRESA_TEST['nit']})")
        print(f"   👤 Usuario: {USUARIO_TEST['primerNombre']} {USUARIO_TEST['primerApellido']} (CC: {USUARIO_TEST['numeroId']})")
        print(f"   🔐 Credenciales: {USUARIO_TEST['numeroId']} / test1234")
        print(f"   🎯 Rol: {USUARIO_TEST['role']}")
        print("\n💡 Puedes usar estos datos para probar el Copiloto ARL.")
        print("=" * 70 + "\n")
        
    except sqlite3.IntegrityError as e:
        print(f"\n⚠️  Error de integridad: {e}")
        print("   Los datos pueden ya existir en la base de datos.")
        conn.rollback()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


# ==================== EJECUCIÓN ====================

if __name__ == '__main__':
    insert_test_data()
