#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Migración de Rutas de Archivos - Sistema Montero
============================================================

Propósito:
    Actualizar las rutas de archivos existentes en la BD a la nueva estructura
    dinámica basada en MONTERO_TOTAL, asumiendo que los archivos físicos ya han
    sido movidos a sus ubicaciones correctas.

Tablas afectadas:
    1. pago_impuestos (columna: ruta_archivo)
       - Organización: EMPRESAS/[NIT]/PAGO DE IMPUESTOS/[TIPO_IMPUESTO]/[archivo]
    
    2. formularios_importados (columna: ruta_archivo)
       - Organización: FORMULARIOS/[archivo]
    
    3. documentos_gestor (columna: ruta)
       - Organización: GESTOR_ARCHIVOS/[categoria]/[archivo]
    
    4. tutelas (columna: documento_soporte)
       - Organización: USUARIOS/[ID_USUARIO]/TUTELAS/[archivo]

Nota: Si la tabla 'tutelas' no tiene la columna 'documento_soporte', 
      ejecutar primero: python patch_tutelas.py

Convención:
    - Rutas RELATIVAS a MONTERO_TOTAL (sin 'D:\' ni 'C:\')
    - Estructura dinámica por NIT de empresa
    - Sin barras invertidas (usar '/')

Autor: Sistema Montero
Fecha: 17 de noviembre de 2025
"""

import os
import sys
import json
from datetime import datetime
import shutil
import sqlite3

# Agregar el directorio dashboard al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import logger


# ==================== CONFIGURACIÓN INICIAL ====================

def get_db_path():
    """
    Retorna la ruta a la base de datos SQLite.
    
    Returns:
        str: Ruta absoluta al archivo de base de datos
    """
    return os.path.join(os.path.dirname(__file__), "data", "mi_sistema.db")


def get_db_connection():
    """
    Crea una conexión directa a SQLite para uso fuera de contexto Flask.
    
    Returns:
        sqlite3.Connection: Conexión a la base de datos
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    return conn


# ==================== CONFIGURACIÓN INICIAL ====================

def get_base_path():
    """
    Retorna la ruta base donde el código espera encontrar los documentos.
    
    Returns:
        str: Ruta base relativa a MONTERO_TOTAL
    """
    # La nueva estructura es relativa a MONTERO_TOTAL
    # El código espera rutas como: "EMPRESAS/900123456/PAGO DE IMPUESTOS/ICA/comprobante.pdf"
    return "MONTERO_TOTAL"


def create_backup():
    """
    Crea una copia de seguridad de la base de datos antes de la migración.
    
    Returns:
        str: Ruta del archivo de backup creado
    """
    db_path = get_db_path()
    backup_filename = f"mi_sistema_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(os.path.dirname(__file__), "data", backup_filename)
    
    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"✅ Backup creado: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"❌ Error al crear backup: {e}")
        raise


# ==================== MIGRACIÓN 1: PAGO DE IMPUESTOS ====================

def migrate_pago_impuestos():
    """
    Migra rutas de archivos en la tabla pago_impuestos.
    
    Nueva estructura:
        EMPRESAS/[NIT]/PAGO DE IMPUESTOS/[TIPO_IMPUESTO]/[nombre_archivo]
    
    Ejemplo:
        EMPRESAS/900123456/PAGO DE IMPUESTOS/ICA/comprobante_2024.pdf
    """
    logger.info("=" * 80)
    logger.info("💰 MIGRACIÓN 1: PAGO DE IMPUESTOS")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener todos los registros con ruta_archivo
        cursor.execute("""
            SELECT id, empresa_nit, empresa_nombre, tipo_impuesto, ruta_archivo, periodo
            FROM pago_impuestos 
            WHERE ruta_archivo IS NOT NULL AND ruta_archivo != ''
        """)
        registros = cursor.fetchall()
        
        if not registros:
            logger.info("ℹ️  No hay registros en pago_impuestos para migrar")
            return 0
        
        logger.info(f"📊 Encontrados {len(registros)} registros para procesar")
        
        migrados = 0
        errores = 0
        
        for registro in registros:
            registro_id = registro['id']
            empresa_nit = registro['empresa_nit']
            empresa_nombre = registro['empresa_nombre']
            tipo_impuesto = registro['tipo_impuesto']
            ruta_antigua = registro['ruta_archivo']
            periodo = registro['periodo']
            
            try:
                # Extraer nombre del archivo (sin ruta absoluta)
                nombre_archivo = os.path.basename(ruta_antigua)
                
                # Sanitizar nombres para rutas (reemplazar espacios y caracteres especiales)
                tipo_impuesto_sanitizado = tipo_impuesto.replace(" ", "_").replace("/", "-")
                
                # Construir nueva ruta relativa según especificación
                # Formato: EMPRESAS/[NIT]/PAGO DE IMPUESTOS/[TIPO_IMPUESTO]/[archivo]
                nueva_ruta = os.path.join(
                    "EMPRESAS",
                    str(empresa_nit),
                    "PAGO DE IMPUESTOS",
                    tipo_impuesto_sanitizado,
                    nombre_archivo
                )
                
                # Normalizar separadores a forward slash
                nueva_ruta = nueva_ruta.replace("\\", "/")
                
                # Ejecutar UPDATE
                cursor.execute(
                    "UPDATE pago_impuestos SET ruta_archivo = ?, updated_at = ? WHERE id = ?",
                    (nueva_ruta, datetime.now().isoformat(), registro_id)
                )
                
                logger.info(f"  ✅ ID {registro_id}: {empresa_nombre} - {tipo_impuesto}")
                logger.debug(f"     Antes: {ruta_antigua}")
                logger.debug(f"     Ahora: {nueva_ruta}")
                
                migrados += 1
                
            except Exception as e:
                logger.error(f"  ❌ Error en registro ID {registro_id}: {e}")
                errores += 1
        
        # Confirmar cambios
        conn.commit()
        
        logger.info(f"\n✅ Migración completada: {migrados} actualizados, {errores} errores")
        return migrados
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error crítico en migración de pago_impuestos: {e}")
        raise
    finally:
        cursor.close()


# ==================== MIGRACIÓN 2: FORMULARIOS IMPORTADOS ====================

def migrate_formularios_importados():
    """
    Migra rutas de archivos en la tabla formularios_importados.
    
    Nueva estructura:
        FORMULARIOS/[nombre_archivo]
    
    Ejemplo:
        FORMULARIOS/formulario_arl_2024.pdf
    """
    logger.info("=" * 80)
    logger.info("📋 MIGRACIÓN 2: FORMULARIOS IMPORTADOS")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, nombre, ruta_archivo FROM formularios_importados WHERE ruta_archivo IS NOT NULL")
        registros = cursor.fetchall()
        
        if not registros:
            logger.info("ℹ️  No hay registros en formularios_importados para migrar")
            return 0
        
        logger.info(f"📊 Encontrados {len(registros)} registros para procesar")
        
        migrados = 0
        errores = 0
        
        for registro in registros:
            registro_id = registro['id']
            nombre = registro['nombre']
            ruta_antigua = registro['ruta_archivo']
            
            try:
                # Extraer nombre del archivo
                nombre_archivo = os.path.basename(ruta_antigua)
                
                # Construir nueva ruta relativa
                nueva_ruta = os.path.join("FORMULARIOS", nombre_archivo)
                nueva_ruta = nueva_ruta.replace("\\", "/")
                
                # Ejecutar UPDATE
                cursor.execute(
                    "UPDATE formularios_importados SET ruta_archivo = ?, updated_at = ? WHERE id = ?",
                    (nueva_ruta, datetime.now().isoformat(), registro_id)
                )
                
                logger.info(f"  ✅ ID {registro_id}: {nombre}")
                logger.debug(f"     Antes: {ruta_antigua}")
                logger.debug(f"     Ahora: {nueva_ruta}")
                
                migrados += 1
                
            except Exception as e:
                logger.error(f"  ❌ Error en registro ID {registro_id}: {e}")
                errores += 1
        
        conn.commit()
        logger.info(f"\n✅ Migración completada: {migrados} actualizados, {errores} errores")
        return migrados
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error crítico en migración de formularios_importados: {e}")
        raise
    finally:
        cursor.close()


# ==================== MIGRACIÓN 3: DOCUMENTOS GESTOR ====================

def migrate_documentos_gestor():
    """
    Migra rutas de archivos en la tabla documentos_gestor.
    
    Nueva estructura:
        GESTOR_ARCHIVOS/[categoria]/[nombre_interno]
    
    Ejemplo:
        GESTOR_ARCHIVOS/Legal/abc123_contrato.pdf
    """
    logger.info("=" * 80)
    logger.info("📁 MIGRACIÓN 3: DOCUMENTOS GESTOR")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, nombre_archivo, nombre_interno, ruta, categoria
            FROM documentos_gestor 
            WHERE ruta IS NOT NULL
        """)
        registros = cursor.fetchall()
        
        if not registros:
            logger.info("ℹ️  No hay registros en documentos_gestor para migrar")
            return 0
        
        logger.info(f"📊 Encontrados {len(registros)} registros para procesar")
        
        migrados = 0
        errores = 0
        
        for registro in registros:
            registro_id = registro['id']
            nombre_archivo = registro['nombre_archivo']
            nombre_interno = registro['nombre_interno']
            ruta_antigua = registro['ruta']
            categoria = registro['categoria']
            
            try:
                # Usar nombre_interno para evitar duplicados
                archivo = nombre_interno if nombre_interno else os.path.basename(ruta_antigua)
                
                # Construir nueva ruta relativa
                nueva_ruta = os.path.join("GESTOR_ARCHIVOS", categoria, archivo)
                nueva_ruta = nueva_ruta.replace("\\", "/")
                
                # Ejecutar UPDATE
                cursor.execute(
                    "UPDATE documentos_gestor SET ruta = ?, updated_at = ? WHERE id = ?",
                    (nueva_ruta, datetime.now().isoformat(), registro_id)
                )
                
                logger.info(f"  ✅ ID {registro_id}: {nombre_archivo} ({categoria})")
                logger.debug(f"     Antes: {ruta_antigua}")
                logger.debug(f"     Ahora: {nueva_ruta}")
                
                migrados += 1
                
            except Exception as e:
                logger.error(f"  ❌ Error en registro ID {registro_id}: {e}")
                errores += 1
        
        conn.commit()
        logger.info(f"\n✅ Migración completada: {migrados} actualizados, {errores} errores")
        return migrados
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error crítico en migración de documentos_gestor: {e}")
        raise
    finally:
        cursor.close()


# ==================== MIGRACIÓN 4: TUTELAS ====================

def migrate_tutelas():
    """
    Migra rutas de documentos soporte en la tabla tutelas.
    
    Nueva estructura:
        USUARIOS/[ID_USUARIO]/TUTELAS/[nombre_archivo]
    
    Ejemplo:
        USUARIOS/123/TUTELAS/tutela_2024_001.pdf
    
    Nota: Requiere que la columna 'documento_soporte' exista en la tabla.
          Si no existe, ejecutar primero: python patch_tutelas.py
    """
    logger.info("=" * 80)
    logger.info("⚖️  MIGRACIÓN 4: TUTELAS")
    logger.info("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna documento_soporte existe
        cursor.execute("PRAGMA table_info(tutelas)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'documento_soporte' not in columns:
            logger.warning("⚠️  La columna 'documento_soporte' no existe en la tabla 'tutelas'")
            logger.warning("⚠️  Ejecute primero: python patch_tutelas.py")
            logger.info("ℹ️  Saltando migración de tutelas...")
            return 0
        
        cursor.execute("""
            SELECT id, usuario_id, numero_tutela, documento_soporte
            FROM tutelas 
            WHERE documento_soporte IS NOT NULL AND documento_soporte != ''
        """)
        registros = cursor.fetchall()
        
        if not registros:
            logger.info("ℹ️  No hay registros en tutelas para migrar")
            return 0
        
        logger.info(f"📊 Encontrados {len(registros)} registros para procesar")
        
        migrados = 0
        errores = 0
        
        for registro in registros:
            registro_id = registro['id']
            usuario_id = registro['usuario_id']
            numero_tutela = registro['numero_tutela']
            ruta_antigua = registro['documento_soporte']
            
            try:
                # Extraer nombre del archivo
                nombre_archivo = os.path.basename(ruta_antigua)
                
                # Construir nueva ruta relativa basada en usuario_id
                # Formato: USUARIOS/[ID_USUARIO]/TUTELAS/[archivo]
                nueva_ruta = os.path.join(
                    "USUARIOS",
                    str(usuario_id),
                    "TUTELAS",
                    nombre_archivo
                )
                
                # Normalizar separadores a forward slash
                nueva_ruta = nueva_ruta.replace("\\", "/")
                
                # Ejecutar UPDATE
                cursor.execute(
                    "UPDATE tutelas SET documento_soporte = ?, updated_at = ? WHERE id = ?",
                    (nueva_ruta, datetime.now().isoformat(), registro_id)
                )
                
                logger.info(f"  ✅ ID {registro_id}: Tutela {numero_tutela} (Usuario {usuario_id})")
                logger.debug(f"     Antes: {ruta_antigua}")
                logger.debug(f"     Ahora: {nueva_ruta}")
                
                migrados += 1
                
            except Exception as e:
                logger.error(f"  ❌ Error en registro ID {registro_id}: {e}")
                errores += 1
        
        conn.commit()
        logger.info(f"\n✅ Migración completada: {migrados} actualizados, {errores} errores")
        return migrados
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error crítico en migración de tutelas: {e}")
        raise
    finally:
        cursor.close()


# ==================== FUNCIÓN PRINCIPAL ====================

def migrate_paths():
    """
    Función principal de migración.
    
    Ejecuta la migración de rutas en las siguientes tablas:
    1. pago_impuestos (ruta_archivo)
    2. formularios_importados (ruta_archivo)
    3. documentos_gestor (ruta)
    4. tutelas (documento_soporte) - si la columna existe
    
    Returns:
        int: Total de registros migrados
    """
    logger.info("=" * 80)
    logger.info("🚀 INICIO DE MIGRACIÓN DE RUTAS - SISTEMA MONTERO")
    logger.info("=" * 80)
    logger.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📂 Ruta base: {get_base_path()}")
    logger.info("=" * 80)
    
    try:
        # Paso 1: Crear backup
        logger.info("\n📦 Paso 1: Creando backup de seguridad...")
        backup_path = create_backup()
        
        # Paso 2: Migrar pago_impuestos
        logger.info("\n💰 Paso 2: Migrando pago_impuestos...")
        migrados_impuestos = migrate_pago_impuestos()
        
        # Paso 3: Migrar formularios_importados
        logger.info("\n📋 Paso 3: Migrando formularios_importados...")
        migrados_formularios = migrate_formularios_importados()
        
        # Paso 4: Migrar documentos_gestor
        logger.info("\n📁 Paso 4: Migrando documentos_gestor...")
        migrados_documentos = migrate_documentos_gestor()
        
        # Paso 5: Migrar tutelas
        logger.info("\n⚖️  Paso 5: Migrando tutelas...")
        migrados_tutelas = migrate_tutelas()
        
        # Resumen final
        total_migrados = migrados_impuestos + migrados_formularios + migrados_documentos + migrados_tutelas
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 RESUMEN DE MIGRACIÓN")
        logger.info("=" * 80)
        logger.info(f"✅ Impuestos migrados:         {migrados_impuestos}")
        logger.info(f"✅ Formularios migrados:       {migrados_formularios}")
        logger.info(f"✅ Documentos gestor migrados: {migrados_documentos}")
        logger.info(f"✅ Tutelas migradas:           {migrados_tutelas}")
        logger.info(f"✅ TOTAL MIGRADOS:             {total_migrados}")
        logger.info("=" * 80)
        logger.info(f"💾 Backup disponible en: {backup_path}")
        logger.info("=" * 80)
        logger.info("✅ Migración de rutas completada en la BD.")
        logger.info("=" * 80)
        
        return total_migrados
        
    except Exception as e:
        logger.error("\n" + "=" * 80)
        logger.error("❌ ERROR CRÍTICO EN MIGRACIÓN")
        logger.error("=" * 80)
        logger.error(f"Detalles: {e}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()
        raise


# ==================== PUNTO DE ENTRADA ====================

if __name__ == '__main__':
    """
    Punto de entrada del script.
    Ejecutar con: python migration_paths.py
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migración de rutas de archivos en Base de Datos Montero'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simula la migración sin modificar la base de datos'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Muestra información detallada de cada operación'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logger.setLevel(logging.DEBUG)
    
    if args.dry_run:
        logger.warning("⚠️  MODO DRY-RUN ACTIVADO - No se realizarán cambios en la BD")
        print("\nEste es un modo de prueba. Para ejecutar la migración real, ejecute:")
        print("  python migration_paths.py")
        sys.exit(0)
    
    try:
        # Confirmar antes de ejecutar
        print("\n⚠️  ADVERTENCIA: Este script modificará las rutas en la base de datos.")
        print("Se creará un backup automático antes de proceder.")
        print("\n¿Desea continuar? (s/n): ", end='')
        
        confirmacion = input().strip().lower()
        
        if confirmacion not in ['s', 'si', 'yes', 'y']:
            print("\n❌ Migración cancelada por el usuario")
            sys.exit(0)
        
        # Ejecutar migración
        total_migrados = migrate_paths()
        
        print(f"\n✅ Migración completada exitosamente: {total_migrados} registros actualizados")
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n❌ Migración interrumpida por el usuario (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)
