# -*- coding: utf-8 -*-
"""
tests/conftest.py - Fixtures específicas para tests unitarios
==============================================================
Este archivo complementa el conftest.py de la raíz con fixtures
adicionales específicas para la carpeta tests/.
"""

import os
import pytest

# Asegurar variables de entorno para tests
os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-32chars")
os.environ.setdefault("ENCRYPTION_KEY", "tZNEUELUZ7lMMN8g4WW1nxpu67mALsZOCBdV5bniow4=")
os.environ.setdefault("DATABASE_PATH", ":memory:")


@pytest.fixture(scope="function")
def db_session(app):
    """
    Proporciona una sesión de base de datos limpia para cada test.
    Usa el contexto de la aplicación Flask.
    """
    from extensions import db
    
    with app.app_context():
        db.create_all()
        yield db.session
        db.session.rollback()
        db.drop_all()


@pytest.fixture(scope="function")
def sample_usuario(db_session):
    """
    Crea un usuario de prueba en la base de datos.
    """
    from models.orm_models import Usuario
    
    usuario = Usuario(
        numeroId="123456789",
        primerNombre="Test",
        primerApellido="Usuario",
        correoElectronico="test@example.com",
        estado="Activo"
    )
    db_session.add(usuario)
    db_session.commit()
    
    yield usuario
    
    # Cleanup
    try:
        db_session.delete(usuario)
        db_session.commit()
    except:
        db_session.rollback()


@pytest.fixture(scope="function")
def sample_empresa(db_session):
    """
    Crea una empresa de prueba en la base de datos.
    """
    from models.orm_models import Empresa
    
    empresa = Empresa(
        nit="900123456",
        nombre_empresa="Empresa Test S.A.S.",
        rep_legal="Representante Test",
        estado="Activa"
    )
    db_session.add(empresa)
    db_session.commit()
    
    yield empresa
    
    # Cleanup
    try:
        db_session.delete(empresa)
        db_session.commit()
    except:
        db_session.rollback()


@pytest.fixture(scope="function")
def auth_headers(client):
    """
    Proporciona headers de autenticación para tests que requieren login.
    Simula una sesión autenticada.
    """
    # Simular login (ajustar según tu sistema de auth)
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['logged_in'] = True
        sess['user_role'] = 'admin'
    
    return {'Content-Type': 'application/json'}
