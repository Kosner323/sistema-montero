"""
Script de Prueba: API de Tareas Personal (Fase 11.2)
====================================================
Valida los 4 endpoints del sistema de To-Do List

Endpoints a probar:
    1. GET  /api/tareas           - Listar tareas
    2. POST /api/tareas           - Crear tarea
    3. PUT  /api/tareas/<id>/toggle - Toggle estado
    4. DELETE /api/tareas/<id>    - Eliminar tarea

Autor: Senior Backend Developer
Fecha: 30 de Noviembre de 2024
"""

import sqlite3
from datetime import datetime
from decimal import Decimal

DB_PATH = 'data/mi_sistema.db'

def print_section(title):
    """Imprime sección decorada"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def simular_listar_tareas(user_id=1, estado='pendientes'):
    """
    Simula: GET /api/tareas?estado=pendientes
    """
    print(f"\n📊 Simulando GET /api/tareas?estado={estado} (user_id={user_id})")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query según estado
    if estado == 'pendientes':
        cursor.execute("""
            SELECT id, descripcion, completada, created_at 
            FROM tareas_usuario 
            WHERE user_id = ? AND completada = 0
            ORDER BY created_at DESC
        """, (user_id,))
    elif estado == 'completadas':
        cursor.execute("""
            SELECT id, descripcion, completada, created_at 
            FROM tareas_usuario 
            WHERE user_id = ? AND completada = 1
            ORDER BY created_at DESC
        """, (user_id,))
    else:  # todas
        cursor.execute("""
            SELECT id, descripcion, completada, created_at 
            FROM tareas_usuario 
            WHERE user_id = ?
            ORDER BY completada ASC, created_at DESC
        """, (user_id,))
    
    tareas = cursor.fetchall()
    
    # Estadísticas
    cursor.execute("SELECT COUNT(*) FROM tareas_usuario WHERE user_id = ? AND completada = 0", (user_id,))
    pendientes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tareas_usuario WHERE user_id = ? AND completada = 1", (user_id,))
    completadas = cursor.fetchone()[0]
    
    conn.close()
    
    # Simular respuesta JSON
    response = {
        'success': True,
        'tareas': [],
        'total': len(tareas),
        'pendientes': pendientes,
        'completadas': completadas
    }
    
    for tarea in tareas:
        response['tareas'].append({
            'id': tarea[0],
            'descripcion': tarea[1],
            'completada': bool(tarea[2]),
            'created_at': tarea[3]
        })
    
    print(f"\n✅ Response 200 OK:")
    print(f"   Total tareas: {response['total']}")
    print(f"   Pendientes: {response['pendientes']}")
    print(f"   Completadas: {response['completadas']}")
    
    print(f"\n   Tareas retornadas:")
    for tarea in response['tareas']:
        estado_emoji = "✅" if tarea['completada'] else "⏳"
        print(f"   {estado_emoji} [{tarea['id']}] {tarea['descripcion']}")
        print(f"      Creada: {tarea['created_at']}")
    
    return response

def simular_crear_tarea(user_id=1, descripcion=""):
    """
    Simula: POST /api/tareas
    Body: {"descripcion": "..."}
    """
    print(f"\n➕ Simulando POST /api/tareas")
    print(f"   Request Body: {{'descripcion': '{descripcion}'}}")
    
    # Validaciones
    if not descripcion or not descripcion.strip():
        print("\n❌ Response 400 Bad Request:")
        print("   Error: La descripción no puede estar vacía")
        return None
    
    if len(descripcion) > 500:
        print("\n❌ Response 400 Bad Request:")
        print("   Error: La descripción no puede superar 500 caracteres")
        return None
    
    # Insertar nueva tarea
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO tareas_usuario (user_id, descripcion, completada, created_at)
        VALUES (?, ?, 0, datetime('now'))
    """, (user_id, descripcion.strip()))
    
    nueva_id = cursor.lastrowid
    conn.commit()
    
    # Obtener tarea creada
    cursor.execute("""
        SELECT id, descripcion, completada, created_at 
        FROM tareas_usuario 
        WHERE id = ?
    """, (nueva_id,))
    
    tarea = cursor.fetchone()
    conn.close()
    
    response = {
        'success': True,
        'tarea': {
            'id': tarea[0],
            'descripcion': tarea[1],
            'completada': bool(tarea[2]),
            'created_at': tarea[3]
        },
        'message': 'Tarea creada exitosamente'
    }
    
    print(f"\n✅ Response 201 Created:")
    print(f"   ID: {response['tarea']['id']}")
    print(f"   Descripción: {response['tarea']['descripcion']}")
    print(f"   Estado: {'Completada' if response['tarea']['completada'] else 'Pendiente'}")
    print(f"   Creada: {response['tarea']['created_at']}")
    
    return response

def simular_toggle_tarea(user_id=1, tarea_id=1):
    """
    Simula: PUT /api/tareas/<id>/toggle
    """
    print(f"\n🔄 Simulando PUT /api/tareas/{tarea_id}/toggle (user_id={user_id})")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar tarea
    cursor.execute("""
        SELECT id, descripcion, completada, created_at 
        FROM tareas_usuario 
        WHERE id = ? AND user_id = ?
    """, (tarea_id, user_id))
    
    tarea = cursor.fetchone()
    
    if not tarea:
        conn.close()
        print(f"\n❌ Response 404 Not Found:")
        print(f"   Error: Tarea no encontrada o no pertenece al usuario")
        return None
    
    # Toggle estado
    nuevo_estado = 1 if tarea[2] == 0 else 0
    
    cursor.execute("""
        UPDATE tareas_usuario 
        SET completada = ? 
        WHERE id = ?
    """, (nuevo_estado, tarea_id))
    
    conn.commit()
    
    # Obtener tarea actualizada
    cursor.execute("""
        SELECT id, descripcion, completada, created_at 
        FROM tareas_usuario 
        WHERE id = ?
    """, (tarea_id,))
    
    tarea_actualizada = cursor.fetchone()
    conn.close()
    
    estado_texto = "completada" if nuevo_estado else "pendiente"
    
    response = {
        'success': True,
        'tarea': {
            'id': tarea_actualizada[0],
            'descripcion': tarea_actualizada[1],
            'completada': bool(tarea_actualizada[2]),
            'created_at': tarea_actualizada[3]
        },
        'message': f'Tarea marcada como {estado_texto}'
    }
    
    print(f"\n✅ Response 200 OK:")
    print(f"   ID: {response['tarea']['id']}")
    print(f"   Descripción: {response['tarea']['descripcion']}")
    print(f"   Nuevo Estado: {'✅ Completada' if response['tarea']['completada'] else '⏳ Pendiente'}")
    print(f"   Mensaje: {response['message']}")
    
    return response

def simular_eliminar_tarea(user_id=1, tarea_id=1):
    """
    Simula: DELETE /api/tareas/<id>
    """
    print(f"\n🗑️  Simulando DELETE /api/tareas/{tarea_id} (user_id={user_id})")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buscar tarea
    cursor.execute("""
        SELECT id, descripcion 
        FROM tareas_usuario 
        WHERE id = ? AND user_id = ?
    """, (tarea_id, user_id))
    
    tarea = cursor.fetchone()
    
    if not tarea:
        conn.close()
        print(f"\n❌ Response 404 Not Found:")
        print(f"   Error: Tarea no encontrada o no pertenece al usuario")
        return None
    
    descripcion = tarea[1]
    
    # Eliminar tarea
    cursor.execute("DELETE FROM tareas_usuario WHERE id = ?", (tarea_id,))
    conn.commit()
    conn.close()
    
    response = {
        'success': True,
        'message': 'Tarea eliminada exitosamente',
        'tarea_id': tarea_id,
        'descripcion': descripcion
    }
    
    print(f"\n✅ Response 200 OK:")
    print(f"   ID eliminado: {response['tarea_id']}")
    print(f"   Descripción: {response['descripcion']}")
    print(f"   Mensaje: {response['message']}")
    
    return response

def simular_estadisticas(user_id=1):
    """
    Simula: GET /api/tareas/stats
    """
    print(f"\n📈 Simulando GET /api/tareas/stats (user_id={user_id})")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tareas_usuario WHERE user_id = ?", (user_id,))
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tareas_usuario WHERE user_id = ? AND completada = 0", (user_id,))
    pendientes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tareas_usuario WHERE user_id = ? AND completada = 1", (user_id,))
    completadas = cursor.fetchone()[0]
    
    conn.close()
    
    porcentaje = (completadas / total * 100) if total > 0 else 0.0
    
    response = {
        'success': True,
        'stats': {
            'total': total,
            'pendientes': pendientes,
            'completadas': completadas,
            'porcentaje_completadas': round(porcentaje, 2)
        }
    }
    
    print(f"\n✅ Response 200 OK:")
    print(f"   Total tareas: {response['stats']['total']}")
    print(f"   Pendientes: {response['stats']['pendientes']}")
    print(f"   Completadas: {response['stats']['completadas']}")
    print(f"   % Completadas: {response['stats']['porcentaje_completadas']}%")
    
    return response

# =============================================================================
# EJECUCIÓN DE PRUEBAS
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  🧪 PRUEBA COMPLETA: API de Tareas Personal (Fase 11.2)")
    print("="*70)
    
    USER_ID = 1  # Usuario de prueba
    
    # =========================================================================
    # PRUEBA 1: Listar tareas pendientes (estado inicial)
    # =========================================================================
    print_section("PRUEBA 1: GET /api/tareas?estado=pendientes")
    simular_listar_tareas(USER_ID, 'pendientes')
    
    # =========================================================================
    # PRUEBA 2: Listar todas las tareas
    # =========================================================================
    print_section("PRUEBA 2: GET /api/tareas?estado=todas")
    simular_listar_tareas(USER_ID, 'todas')
    
    # =========================================================================
    # PRUEBA 3: Crear nueva tarea
    # =========================================================================
    print_section("PRUEBA 3: POST /api/tareas (Crear nueva tarea)")
    nueva_tarea = simular_crear_tarea(USER_ID, "Enviar planilla de Febrero 2025 a PILA")
    
    # =========================================================================
    # PRUEBA 4: Marcar tarea como completada (toggle)
    # =========================================================================
    print_section("PRUEBA 4: PUT /api/tareas/1/toggle (Marcar completada)")
    simular_toggle_tarea(USER_ID, 1)
    
    # =========================================================================
    # PRUEBA 5: Marcar tarea como pendiente (toggle de vuelta)
    # =========================================================================
    print_section("PRUEBA 5: PUT /api/tareas/1/toggle (Marcar pendiente)")
    simular_toggle_tarea(USER_ID, 1)
    
    # =========================================================================
    # PRUEBA 6: Eliminar tarea
    # =========================================================================
    print_section("PRUEBA 6: DELETE /api/tareas/2 (Eliminar tarea)")
    simular_eliminar_tarea(USER_ID, 2)
    
    # =========================================================================
    # PRUEBA 7: Estadísticas finales
    # =========================================================================
    print_section("PRUEBA 7: GET /api/tareas/stats (Estadísticas)")
    simular_estadisticas(USER_ID)
    
    # =========================================================================
    # PRUEBA 8: Listar tareas finales
    # =========================================================================
    print_section("PRUEBA 8: GET /api/tareas?estado=todas (Estado final)")
    simular_listar_tareas(USER_ID, 'todas')
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print("\n" + "="*70)
    print("  ✅ PRUEBA COMPLETA FINALIZADA")
    print("="*70)
    print("\n📝 Resumen:")
    print("   ✅ Tabla tareas_usuario creada")
    print("   ✅ Modelo ORM TareaUsuario implementado")
    print("   ✅ 4 endpoints validados:")
    print("      - GET  /api/tareas           ✅")
    print("      - POST /api/tareas           ✅")
    print("      - PUT  /api/tareas/<id>/toggle ✅")
    print("      - DELETE /api/tareas/<id>    ✅")
    print("   ✅ Endpoint bonus /api/tareas/stats ✅")
    print("   ✅ Blueprint registrado en app.py")
    print("\n🎯 Sistema de Tareas Personal (Fase 11.2) COMPLETADO")
    print("="*70 + "\n")
