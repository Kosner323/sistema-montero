# -*- coding: utf-8 -*-
import unittest
import json
from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models.orm_models import Incapacidad, Tutela, Empresa, Usuario

class TestLegalOrm(unittest.TestCase):

    def setUp(self):
        """Configuración para las pruebas."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self._create_test_data()

    def tearDown(self):
        """Limpieza después de las pruebas."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_test_data(self):
        """Crea una empresa y un usuario de prueba."""
        empresa = Empresa(nit='900000000-1', nombre_empresa='Empresa Test')
        usuario = Usuario(numeroId='123456789', primerNombre='Juan', primerApellido='Perez', empresa_nit=empresa.nit)
        db.session.add(empresa)
        db.session.add(usuario)
        db.session.commit()

    def test_create_and_read_incapacidad(self):
        """Prueba la creación y lectura de una incapacidad."""
        # Crear incapacidad
        fecha_inicio = datetime.utcnow().date()
        fecha_fin = fecha_inicio + timedelta(days=5)
        
        incapacidad_data = {
            'empresa_nit': '900000000-1',
            'usuario_id': '123456789',
            'diagnostico': 'Gripe Común',
            'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
            'archivos_info': 'path/to/fake.pdf'
        }
        
        # Simulamos un post con los datos, sin subir archivo real
        nueva_incapacidad = Incapacidad(**incapacidad_data)
        db.session.add(nueva_incapacidad)
        db.session.commit()

        # Verificar
        incapacidad = Incapacidad.query.filter_by(usuario_id='123456789').first()
        self.assertIsNotNone(incapacidad)
        self.assertEqual(incapacidad.diagnostico, 'Gripe Común')

    def test_create_and_read_tutela(self):
        """Prueba la creación y lectura de una tutela."""
        # Crear tutela
        fecha_radicacion = datetime.utcnow().date()
        
        tutela_data = {
            'empresa_nit': '900000000-1',
            'usuario_id': '123456789',
            'motivo': 'Reclamo de pago',
            'fecha_radicacion': fecha_radicacion,
            'archivos_info': 'path/to/fake_tutela.pdf'
        }
        
        nueva_tutela = Tutela(**tutela_data)
        db.session.add(nueva_tutela)
        db.session.commit()

        # Verificar
        tutela = Tutela.query.filter_by(usuario_id='123456789').first()
        self.assertIsNotNone(tutela)
        self.assertEqual(tutela.motivo, 'Reclamo de pago')

if __name__ == '__main__':
    unittest.main()
