# -*- coding: utf-8 -*-
"""
Tests para el Sistema de Lock Screen
Sistema Montero
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
import json

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLockScreenEndpoint(unittest.TestCase):
    """Suite de pruebas para el endpoint de verificación de contraseña"""

    def setUp(self):
        """Configuración antes de cada test"""
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    @patch('routes.auth.get_db_connection')
    @patch('routes.auth.session', {'user_id': 1})
    def test_verify_password_success(self, mock_db):
        """Test: Contraseña correcta retorna success=true"""
        # Arrange
        mock_conn = Mock()
        mock_user = {
            'id': 1,
            'password_hash': 'pbkdf2:sha256:600000$abcd1234$hash_valido',
            'primerNombre': 'Pedro',
            'primerApellido': 'Pérez'
        }
        
        mock_conn.execute.return_value.fetchone.return_value = mock_user
        mock_db.return_value = mock_conn
        
        # Mock check_password_hash para retornar True
        with patch('routes.auth.check_password_hash', return_value=True):
            # Act
            response = self.client.post(
                '/api/verify-password',
                json={'password': 'test1234'},
                content_type='application/json'
            )
            
            # Assert
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Desbloqueo exitoso')

    @patch('routes.auth.get_db_connection')
    @patch('routes.auth.session', {'user_id': 1})
    def test_verify_password_incorrect(self, mock_db):
        """Test: Contraseña incorrecta retorna success=false"""
        # Arrange
        mock_conn = Mock()
        mock_user = {
            'id': 1,
            'password_hash': 'pbkdf2:sha256:600000$abcd1234$hash_valido',
            'primerNombre': 'Pedro',
            'primerApellido': 'Pérez'
        }
        
        mock_conn.execute.return_value.fetchone.return_value = mock_user
        mock_db.return_value = mock_conn
        
        # Mock check_password_hash para retornar False
        with patch('routes.auth.check_password_hash', return_value=False):
            # Act
            response = self.client.post(
                '/api/verify-password',
                json={'password': 'wrong_password'},
                content_type='application/json'
            )
            
            # Assert
            self.assertEqual(response.status_code, 401)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('incorrecta', data['message'].lower())

    def test_verify_password_no_data(self):
        """Test: Request sin datos retorna error 400"""
        # Act
        response = self.client.post(
            '/api/verify-password',
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

    @patch('routes.auth.session', {'user_id': 1})
    def test_verify_password_empty_password(self):
        """Test: Contraseña vacía retorna error 400"""
        # Act
        response = self.client.post(
            '/api/verify-password',
            json={'password': ''},
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('requerida', data['message'].lower())

    @patch('routes.auth.get_db_connection')
    @patch('routes.auth.session', {'user_id': 999})
    def test_verify_password_user_not_found(self, mock_db):
        """Test: Usuario no encontrado retorna error 404"""
        # Arrange
        mock_conn = Mock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_db.return_value = mock_conn
        
        # Act
        response = self.client.post(
            '/api/verify-password',
            json={'password': 'test1234'},
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])


class TestLockScreenFrontend(unittest.TestCase):
    """Suite de pruebas para el frontend del lock screen"""

    def test_lockscreen_html_elements_exist(self):
        """Test: Verifica que los elementos HTML existan en _header.html"""
        # Arrange
        header_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            '_header.html'
        )
        
        if not os.path.exists(header_path):
            self.skipTest("Archivo _header.html no encontrado")
        
        with open(header_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Assert
        self.assertIn('lockScreenOverlay', content)
        self.assertIn('lockscreen-password', content)
        self.assertIn('lockscreenError', content)
        self.assertIn('unlockButton', content)
        self.assertIn('desbloquearPantalla', content)
        self.assertIn('lockScreen()', content)

    def test_lockscreen_fetch_endpoint(self):
        """Test: Verifica que el fetch use el endpoint correcto"""
        # Arrange
        header_path = os.path.join(
            os.path.dirname(__file__),
            'templates',
            '_header.html'
        )
        
        if not os.path.exists(header_path):
            self.skipTest("Archivo _header.html no encontrado")
        
        with open(header_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Assert
        self.assertIn('/api/verify-password', content)
        self.assertIn("method: 'POST'", content)
        self.assertIn('JSON.stringify', content)


class TestLockScreenIntegration(unittest.TestCase):
    """Tests de integración para el sistema completo"""

    def setUp(self):
        """Configuración antes de cada test"""
        from app import create_app
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def test_lockscreen_full_flow(self):
        """Test: Flujo completo de bloqueo y desbloqueo"""
        # Este test requiere una BD real con usuarios
        # Se ejecuta solo si existe la BD
        
        db_path = os.path.join(
            os.path.dirname(__file__),
            'data',
            'mi_sistema.db'
        )
        
        if not os.path.exists(db_path):
            self.skipTest("Base de datos no encontrada")
        
        # 1. Login
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin Sistema'
        
        # 2. Verificar contraseña correcta
        response = self.client.post(
            '/api/verify-password',
            json={'password': 'admin123'},  # Contraseña de prueba
            content_type='application/json'
        )
        
        # La verificación real depende de la BD
        self.assertIn(response.status_code, [200, 401])


def run_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*70)
    print("  EJECUTANDO TESTS DEL SISTEMA LOCK SCREEN")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLockScreenEndpoint))
    suite.addTests(loader.loadTestsFromTestCase(TestLockScreenFrontend))
    suite.addTests(loader.loadTestsFromTestCase(TestLockScreenIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    if result.wasSuccessful():
        print("  ✅ TODOS LOS TESTS PASARON")
    else:
        print("  ❌ ALGUNOS TESTS FALLARON")
        if result.failures:
            print(f"\n  Fallos: {len(result.failures)}")
        if result.errors:
            print(f"  Errores: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
