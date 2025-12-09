# -*- coding: utf-8 -*-
"""
Test de Carga Masiva de Deudas de Cartera
==========================================
Prueba el endpoint POST /api/cartera/carga-masiva con datos simulados
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models.orm_models import Usuario, Empresa, DeudaCartera
from datetime import datetime

def crear_datos_prueba():
    """Crea usuarios y empresas de prueba si no existen"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("📋 PREPARANDO DATOS DE PRUEBA")
        print("=" * 80)
        
        # Crear empresa de prueba si no existe
        empresa = db.session.query(Empresa).filter_by(nit="900123456").first()
        if not empresa:
            empresa = Empresa(
                nit="900123456",
                nombre_empresa="Empresa ABC S.A.S",
                razon_social="Empresa ABC S.A.S",
                tipo_documento="NIT",
                estado="Activo"
            )
            db.session.add(empresa)
            print("✅ Empresa de prueba creada: 900123456 - Empresa ABC S.A.S")
        else:
            print("ℹ️  Empresa de prueba ya existe: 900123456")
        
        # Crear usuarios de prueba si no existen
        usuarios_prueba = [
            {
                "numeroId": "1234567890",
                "primerNombre": "Juan",
                "primerApellido": "Pérez",
                "empresa_nit": "900123456"
            },
            {
                "numeroId": "9876543210",
                "primerNombre": "María",
                "primerApellido": "García",
                "empresa_nit": "900123456"
            },
            {
                "numeroId": "1111222233",
                "primerNombre": "Pedro",
                "primerApellido": "López",
                "empresa_nit": "900123456"
            }
        ]
        
        for user_data in usuarios_prueba:
            usuario = db.session.query(Usuario).filter_by(numeroId=user_data["numeroId"]).first()
            if not usuario:
                usuario = Usuario(**user_data)
                db.session.add(usuario)
                print(f"✅ Usuario de prueba creado: {user_data['numeroId']} - {user_data['primerNombre']} {user_data['primerApellido']}")
            else:
                print(f"ℹ️  Usuario de prueba ya existe: {user_data['numeroId']}")
        
        db.session.commit()
        print("=" * 80)
        print()

def test_carga_masiva():
    """Prueba la carga masiva de deudas"""
    app = create_app()
    
    print("=" * 80)
    print("🧪 TEST: CARGA MASIVA DE DEUDAS DE CARTERA")
    print("=" * 80)
    print(f"🕐 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    with app.test_client() as client:
        # Simular login (si es necesario)
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['logged_in'] = True
        
        # Datos de prueba para carga masiva
        datos_carga = {
            "deudas": [
                {
                    "usuario_id": "1234567890",
                    "nombre_usuario": "Juan Pérez",
                    "empresa_nit": "900123456",
                    "nombre_empresa": "Empresa ABC S.A.S",
                    "entidad": "EPS",
                    "monto": 500000,
                    "dias_mora": 15
                },
                {
                    "usuario_id": "9876543210",
                    "nombre_usuario": "María García",
                    "empresa_nit": "900123456",
                    "nombre_empresa": "Empresa ABC S.A.S",
                    "entidad": "ARL",
                    "monto": 750000,
                    "dias_mora": 0
                },
                {
                    "usuario_id": "1111222233",
                    "nombre_usuario": "Pedro López",
                    "empresa_nit": "900123456",
                    "nombre_empresa": "Empresa ABC S.A.S",
                    "entidad": "AFP",
                    "monto": 1200000,
                    "dias_mora": 30
                },
                {
                    "usuario_id": "1234567890",
                    "nombre_usuario": "Juan Pérez",
                    "empresa_nit": "900123456",
                    "nombre_empresa": "Empresa ABC S.A.S",
                    "entidad": "CCF",
                    "monto": 300000,
                    "dias_mora": 5
                },
                {
                    "usuario_id": "9876543210",
                    "nombre_usuario": "María García",
                    "empresa_nit": "900123456",
                    "nombre_empresa": "Empresa ABC S.A.S",
                    "entidad": "ICBF",
                    "monto": 450000,
                    "dias_mora": 0
                }
            ]
        }
        
        print(f"📊 Datos de prueba preparados:")
        print(f"   - Total de deudas a cargar: {len(datos_carga['deudas'])}")
        print(f"   - Usuarios involucrados: 3")
        print(f"   - Empresa: 900123456 - Empresa ABC S.A.S")
        print(f"   - Entidades: EPS, ARL, AFP, CCF, ICBF")
        print()
        
        # Estado antes de la carga
        with app.app_context():
            total_antes = db.session.query(DeudaCartera).count()
            print(f"📈 Estado ANTES de la carga:")
            print(f"   - Total de deudas en BD: {total_antes}")
            print()
        
        # Realizar la petición POST
        print("🚀 Enviando petición POST /api/cartera/carga-masiva...")
        response = client.post(
            '/api/cartera/carga-masiva',
            json=datos_carga,
            content_type='application/json'
        )
        
        print(f"📡 Respuesta del servidor:")
        print(f"   - Status Code: {response.status_code}")
        print(f"   - Content-Type: {response.content_type}")
        print()
        
        # Analizar respuesta
        if response.status_code == 201:
            data = response.get_json()
            print("✅ CARGA MASIVA EXITOSA")
            print("=" * 80)
            print(f"📊 RESULTADOS:")
            print(f"   - Deudas guardadas: {data.get('guardadas', 0)}")
            print(f"   - Deudas con errores: {data.get('errores', 0)}")
            print(f"   - Total procesadas: {data.get('total_procesadas', 0)}")
            print(f"   - Mensaje: {data.get('mensaje', '')}")
            print()
            
            if 'deudas_creadas' in data:
                print("📋 DEUDAS CREADAS:")
                for deuda in data['deudas_creadas']:
                    print(f"   ✅ Usuario: {deuda['usuario_id']}, Entidad: {deuda['entidad']}, Monto: ${deuda['monto']:,.0f}")
            
            if 'detalles_errores' in data and data['detalles_errores']:
                print("\n⚠️  ERRORES ENCONTRADOS:")
                for error in data['detalles_errores']:
                    print(f"   ❌ Índice {error['indice']}: {error['error']}")
        else:
            print("❌ ERROR EN LA CARGA MASIVA")
            print("=" * 80)
            print(f"   - Status Code: {response.status_code}")
            data = response.get_json()
            if data:
                print(f"   - Error: {data.get('error', 'Desconocido')}")
                if 'detalles_errores' in data:
                    print("\n   Detalles de errores:")
                    for error in data['detalles_errores']:
                        print(f"      - {error}")
        
        print()
        
        # Estado después de la carga
        with app.app_context():
            total_despues = db.session.query(DeudaCartera).count()
            print(f"📈 Estado DESPUÉS de la carga:")
            print(f"   - Total de deudas en BD: {total_despues}")
            print(f"   - Deudas nuevas agregadas: {total_despues - total_antes}")
            print()
            
            # Mostrar deudas por estado
            from sqlalchemy import func
            stats = db.session.query(
                DeudaCartera.estado,
                func.count(DeudaCartera.id),
                func.sum(DeudaCartera.monto)
            ).group_by(DeudaCartera.estado).all()
            
            print("📊 ESTADÍSTICAS POR ESTADO:")
            for estado, cantidad, monto_total in stats:
                print(f"   - {estado}: {cantidad} deuda(s), Total: ${monto_total:,.0f}")
            print()
            
            # Mostrar últimas deudas creadas
            ultimas_deudas = db.session.query(DeudaCartera).order_by(
                DeudaCartera.id.desc()
            ).limit(5).all()
            
            print("📋 ÚLTIMAS 5 DEUDAS REGISTRADAS:")
            for deuda in ultimas_deudas:
                print(f"   ID {deuda.id}: {deuda.nombre_usuario} - {deuda.entidad} - ${deuda.monto:,.0f} - {deuda.estado}")
        
        print()
        print("=" * 80)
        print("✅ TEST COMPLETADO")
        print("=" * 80)
        
        return response.status_code == 201

def test_estadisticas():
    """Prueba el endpoint de estadísticas"""
    app = create_app()
    
    print("\n" + "=" * 80)
    print("🧪 TEST: ENDPOINT DE ESTADÍSTICAS")
    print("=" * 80)
    
    with app.test_client() as client:
        # Simular login
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'admin'
            sess['logged_in'] = True
        
        print("🚀 Enviando petición GET /api/cartera/estadisticas...")
        response = client.get('/api/cartera/estadisticas')
        
        if response.status_code == 200:
            data = response.get_json()
            print("\n✅ ESTADÍSTICAS OBTENIDAS:")
            print("=" * 80)
            print(f"   📊 Total de deudas: {data.get('total_deudas', 0)}")
            print(f"   💰 Monto total: ${data.get('monto_total', 0):,.0f}")
            print(f"   📈 Cartera total: ${data.get('cartera_total', 0):,.0f}")
            print(f"\n   📋 Por estado:")
            print(f"      - Pendientes: {data.get('deudas_pendientes', 0)} (${data.get('monto_pendiente', 0):,.0f})")
            print(f"      - Vencidas: {data.get('deudas_vencidas', 0)} (${data.get('monto_vencido', 0):,.0f})")
            print(f"      - Pagadas: {data.get('deudas_pagadas', 0)}")
        else:
            print(f"\n❌ ERROR: Status Code {response.status_code}")
        
        print("=" * 80)

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 INICIANDO SUITE DE PRUEBAS - CARTERA")
    print("=" * 80)
    print()
    
    # Paso 1: Crear datos de prueba
    crear_datos_prueba()
    
    # Paso 2: Probar carga masiva
    exitoso = test_carga_masiva()
    
    # Paso 3: Probar estadísticas
    test_estadisticas()
    
    print("\n" + "=" * 80)
    print("🎉 SUITE DE PRUEBAS FINALIZADA")
    print("=" * 80)
    
    exit(0 if exitoso else 1)
