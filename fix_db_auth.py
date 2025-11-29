#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fix_db_auth.py - Script de Reparación de Emergencia para Autenticación
======================================================================
Repara la tabla 'usuarios' agregando columnas faltantes (password_hash, role)
y resetea la contraseña del administrador.

La tabla 'usuarios' usa 'correoElectronico' como campo de email.

Autor: DBA Emergency Script
Fecha: 2025-11-28
"""

import sqlite3
import os
import sys

# Intentar importar werkzeug para hash de contraseñas
try:
    from werkzeug.security import generate_password_hash
except ImportError:
    print("ERROR: werkzeug no está instalado. Instalando...")
    os.system('pip install werkzeug')
    from werkzeug.security import generate_password_hash

# Configuración
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'mi_sistema.db')
ADMIN_EMAIL = 'admin@montero.com'
ADMIN_PASSWORD = 'admin123'

def print_header(msg):
    """Imprime encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"  {msg}")
    print("=" * 60)

def print_status(msg, success=True):
    """Imprime estado con indicador visual"""
    icon = "✅" if success else "❌"
    print(f"{icon} {msg}")

def get_table_columns(cursor, table_name):
    """Obtiene lista de columnas de una tabla"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return columns

def column_exists(cursor, table_name, column_name):
    """Verifica si una columna existe en una tabla"""
    columns = get_table_columns(cursor, table_name)
    return column_name.lower() in [c.lower() for c in columns]

def table_exists(cursor, table_name):
    """Verifica si una tabla existe"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """, (table_name,))
    return cursor.fetchone() is not None

def repair_database():
    """Función principal de reparación"""
    global DB_PATH
    
    print_header("SCRIPT DE REPARACIÓN DE BASE DE DATOS - AUTENTICACIÓN")
    
    # Verificar que el archivo de BD existe
    if not os.path.exists(DB_PATH):
        print_status(f"Base de datos no encontrada en: {DB_PATH}", False)
        print("  Verificando rutas alternativas...")
        
        # Buscar en rutas alternativas
        alt_paths = [
            'data/mi_sistema.db',
            '../data/mi_sistema.db',
            'mi_sistema.db'
        ]
        
        for alt in alt_paths:
            if os.path.exists(alt):
                print_status(f"Base de datos encontrada en: {alt}")
                DB_PATH = alt
                break
        else:
            print_status("No se pudo encontrar la base de datos", False)
            return False
    
    print_status(f"Base de datos encontrada: {DB_PATH}")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print_status("Conexión a base de datos establecida")
        
        # Verificar que la tabla usuarios existe
        if not table_exists(cursor, 'usuarios'):
            print_status("La tabla 'usuarios' NO existe", False)
            print("  Creando tabla usuarios...")
            cursor.execute("""
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255),
                    nombre VARCHAR(100),
                    role VARCHAR(50) DEFAULT 'user',
                    activo BOOLEAN DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print_status("Tabla 'usuarios' creada exitosamente")
        else:
            print_status("Tabla 'usuarios' existe")
        
        # Mostrar columnas actuales
        columns = get_table_columns(cursor, 'usuarios')
        print(f"\n  Columnas actuales: {', '.join(columns)}")
        
        # Verificar y agregar columna password_hash
        print_header("VERIFICACIÓN DE COLUMNA: password_hash")
        if column_exists(cursor, 'usuarios', 'password_hash'):
            print_status("Columna 'password_hash' ya existe")
        else:
            print_status("Columna 'password_hash' NO existe - Agregando...", False)
            cursor.execute("ALTER TABLE usuarios ADD COLUMN password_hash VARCHAR(255)")
            conn.commit()
            print_status("Columna 'password_hash' agregada exitosamente")
        
        # Verificar y agregar columna role
        print_header("VERIFICACIÓN DE COLUMNA: role")
        if column_exists(cursor, 'usuarios', 'role'):
            print_status("Columna 'role' ya existe")
        else:
            print_status("Columna 'role' NO existe - Agregando...", False)
            cursor.execute("ALTER TABLE usuarios ADD COLUMN role VARCHAR(50) DEFAULT 'user'")
            conn.commit()
            print_status("Columna 'role' agregada exitosamente")
        
        # Reset de contraseña del administrador
        print_header("RESET DE CONTRASEÑA ADMINISTRADOR")
        
        # La tabla usuarios usa 'correoElectronico' como campo de email
        cursor.execute("""
            SELECT id, correoElectronico, primerNombre, role FROM usuarios 
            WHERE id = 1 OR correoElectronico = ?
            LIMIT 1
        """, (ADMIN_EMAIL,))
        
        admin_user = cursor.fetchone()
        
        if admin_user:
            admin_id = admin_user[0]
            admin_email = admin_user[1]
            admin_nombre = admin_user[2] or 'Admin'
            
            print(f"  Usuario admin encontrado: ID={admin_id}, Email={admin_email}")
            
            # Generar nuevo hash de contraseña
            new_password_hash = generate_password_hash(ADMIN_PASSWORD)
            
            # Actualizar contraseña y role
            cursor.execute("""
                UPDATE usuarios 
                SET password_hash = ?, role = 'admin'
                WHERE id = ?
            """, (new_password_hash, admin_id))
            conn.commit()
            
            print_status(f"Contraseña actualizada para: {admin_email}")
            print(f"  Nueva contraseña: {ADMIN_PASSWORD}")
            print(f"  Role establecido: admin")
        else:
            print_status("No se encontró usuario administrador - Creando nuevo...", False)
            
            # Crear usuario administrador usando la estructura real de la tabla
            new_password_hash = generate_password_hash(ADMIN_PASSWORD)
            cursor.execute("""
                INSERT INTO usuarios (
                    correoElectronico, password_hash, primerNombre, primerApellido,
                    role, tipoId, numeroId, empresa_nit
                )
                VALUES (?, ?, 'Administrador', 'Sistema', 'admin', 'CC', '0000000', '999999999')
            """, (ADMIN_EMAIL, new_password_hash))
            conn.commit()
            
            print_status(f"Usuario administrador creado: {ADMIN_EMAIL}")
            print(f"  Contraseña: {ADMIN_PASSWORD}")
        
        # Verificación final
        print_header("VERIFICACIÓN FINAL")
        
        # Mostrar estructura actualizada
        columns = get_table_columns(cursor, 'usuarios')
        print(f"  Columnas finales: {', '.join(columns)}")
        
        # Verificar datos del admin
        cursor.execute("""
            SELECT id, correoElectronico, primerNombre, role, 
                   CASE WHEN password_hash IS NOT NULL AND password_hash != '' 
                        THEN 'Configurado' ELSE 'Sin configurar' END as pwd_status
            FROM usuarios 
            WHERE role = 'admin' OR id = 1
        """)
        
        admins = cursor.fetchall()
        if admins:
            print("\n  Usuarios administradores:")
            for admin in admins:
                print(f"    - ID: {admin[0]}, Email: {admin[1]}, Nombre: {admin[2]}, Role: {admin[3]}, Password: {admin[4]}")
        
        # Cerrar conexión
        conn.close()
        
        print_header("REPARACIÓN COMPLETADA EXITOSAMENTE")
        print(f"""
  CREDENCIALES DE ACCESO:
  ========================
  Email: {ADMIN_EMAIL}
  Contraseña: {ADMIN_PASSWORD}
  
  ¡El sistema debería funcionar correctamente ahora!
""")
        return True
        
    except sqlite3.Error as e:
        print_status(f"Error de SQLite: {e}", False)
        return False
    except Exception as e:
        print_status(f"Error inesperado: {e}", False)
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = repair_database()
    sys.exit(0 if success else 1)
