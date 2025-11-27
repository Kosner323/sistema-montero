# -*- coding: utf-8 -*-
"""
Tests unitarios para el Motor RPA
Sistema Montero - ARLBot
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestARLBot(unittest.TestCase):
    """Suite de pruebas para ARLBot"""

    @patch('rpa.arl_bot.webdriver.Chrome')
    @patch('rpa.arl_bot.ChromeDriverManager')
    def test_bot_inicializacion(self, mock_driver_manager, mock_chrome):
        """Test: Bot se inicializa correctamente"""
        # Arrange
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        # Act
        try:
            from rpa.arl_bot import ARLBot
            bot = ARLBot(headless=True)
            
            # Assert
            self.assertIsNotNone(bot.driver)
            mock_chrome.assert_called_once()
            
            bot.cerrar()
        except ImportError:
            self.skipTest("Selenium no instalado - test omitido")

    @patch('rpa.arl_bot.webdriver.Chrome')
    def test_navegar_portal_exitoso(self, mock_chrome):
        """Test: Navegación a portal exitosa"""
        try:
            from rpa.arl_bot import ARLBot
            
            # Arrange
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            bot = ARLBot(headless=True)
            
            # Mock WebDriverWait
            with patch('rpa.arl_bot.WebDriverWait') as mock_wait:
                mock_wait.return_value.until.return_value = True
                
                # Act
                resultado = bot.navegar_portal("https://www.arlsura.com")
                
                # Assert
                self.assertTrue(resultado)
                mock_driver.get.assert_called_with("https://www.arlsura.com")
            
            bot.cerrar()
        except ImportError:
            self.skipTest("Selenium no instalado - test omitido")

    @patch('rpa.arl_bot.webdriver.Chrome')
    def test_ejecutar_afiliacion(self, mock_chrome):
        """Test: Ejecución de afiliación retorna respuesta correcta"""
        try:
            from rpa.arl_bot import ARLBot
            
            # Arrange
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            bot = ARLBot(headless=True)
            
            datos_empleado = {
                "nombre": "Pedro Pérez",
                "empleado_id": "100100100",
                "nit": "900111222"
            }
            
            with patch('rpa.arl_bot.WebDriverWait'):
                # Act
                resultado = bot.ejecutar_afiliacion(datos_empleado)
                
                # Assert
                self.assertIn('status', resultado)
                self.assertIn('mensaje', resultado)
                self.assertEqual(resultado['status'], 'exito')
            
            bot.cerrar()
        except ImportError:
            self.skipTest("Selenium no instalado - test omitido")

    @patch('rpa.arl_bot.webdriver.Chrome')
    def test_bot_cerrar(self, mock_chrome):
        """Test: Bot se cierra correctamente"""
        try:
            from rpa.arl_bot import ARLBot
            
            # Arrange
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            bot = ARLBot(headless=True)
            
            # Act
            bot.cerrar()
            
            # Assert
            mock_driver.quit.assert_called_once()
        except ImportError:
            self.skipTest("Selenium no instalado - test omitido")

    def test_import_fallback(self):
        """Test: Sistema funciona sin Selenium instalado"""
        # Act & Assert
        # No debe levantar error al importar automation_routes
        try:
            from routes import automation_routes
            self.assertTrue(hasattr(automation_routes, 'automation_bp'))
            self.assertTrue(hasattr(automation_routes, 'ejecutar_bot_background'))
        except ImportError as e:
            self.fail(f"automation_routes no se puede importar: {e}")


class TestBackgroundWorker(unittest.TestCase):
    """Suite de pruebas para el worker background"""

    def test_ejecutar_bot_background_existe(self):
        """Test: Función worker está definida"""
        from routes.automation_routes import ejecutar_bot_background
        self.assertTrue(callable(ejecutar_bot_background))

    @patch('routes.automation_routes.get_db_connection')
    @patch('routes.automation_routes.ARLBot')
    def test_ejecutar_bot_background_simulacion(self, mock_bot, mock_db):
        """Test: Worker ejecuta en modo simulación"""
        from routes.automation_routes import ejecutar_bot_background, BOT_DISPONIBLE
        
        if BOT_DISPONIBLE:
            self.skipTest("Selenium instalado - test omitido")
        
        # Arrange
        mock_conn = Mock()
        mock_db.return_value = mock_conn
        
        job_id = "JOB-TEST-001"
        accion = "afiliar"
        datos = {"nombre": "Test User", "nit": "123456789"}
        
        # Act
        ejecutar_bot_background(job_id, accion, datos)
        
        # Assert
        # Verificar que se actualizó la BD al menos 2 veces
        self.assertGreaterEqual(mock_conn.execute.call_count, 2)
        self.assertTrue(mock_conn.commit.called)


def run_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("  EJECUTANDO TESTS DEL MOTOR RPA")
    print("="*60 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestARLBot))
    suite.addTests(loader.loadTestsFromTestCase(TestBackgroundWorker))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("  ✅ TODOS LOS TESTS PASARON")
    else:
        print("  ❌ ALGUNOS TESTS FALLARON")
    print("="*60 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
