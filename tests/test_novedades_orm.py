# -*- coding: utf-8 -*-
import json
import unittest
from unittest.mock import patch
from app import create_app
from extensions import db
from models.orm_models import Novedad

class TestNovedadesORM(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Limpieza después de cada prueba."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_update_and_verify_history(self):
        """
        Prueba la creación y actualización de una novedad, 
        y verifica que el historial se guarde correctamente.
        """
        # 1. Crear una novedad de prueba
        with patch('flask.session', {'user_name': 'test_user'}):
            new_novedad_data = {
                "client": "Cliente de Prueba",
                "subject": "Asunto de Prueba",
                "priority": 1,
                "status": "Nuevo",
                "description": "Descripción de prueba."
            }
            response = self.client.post('/api/novedades', 
                                        data=json.dumps(new_novedad_data),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 201)
            created_novedad = json.loads(response.data)
            self.assertIn('id', created_novedad)
            novedad_id = created_novedad['id']

            # Verificar historial inicial
            self.assertEqual(len(created_novedad['history']), 1)
            self.assertEqual(created_novedad['history'][0]['action'], "Creó el caso.")

        # 2. Actualizar la novedad
        with patch('flask.session', {'user_name': 'update_user'}):
            update_data = {
                "status": "En Proceso",
                "newComment": "Actualizando estado."
            }
            response = self.client.put(f'/api/novedades/{novedad_id}',
                                       data=json.dumps(update_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 200)
            updated_novedad = json.loads(response.data)

            # 3. Verificar que el historial se guardó correctamente
            self.assertEqual(len(updated_novedad['history']), 2)
            self.assertEqual(updated_novedad['history'][1]['user'], "update_user")
            self.assertIn("Cambió estado a 'En Proceso'", updated_novedad['history'][1]['action'])
            self.assertEqual(updated_novedad['history'][1]['comment'], "Actualizando estado.")

if __name__ == '__main__':
    unittest.main()
