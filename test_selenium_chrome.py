"""
=====================================================================
PRUEBA: SELENIUM - NAVEGADOR CHROME
Abre Chrome local, navega a SURA login y espera interacción del usuario
Automation Engineer - Test Browser Automation
=====================================================================
"""

import os
import time
from datetime import datetime

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    
    SELENIUM_DISPONIBLE = True
except ImportError as e:
    print(f"[ERROR] Selenium no instalado: {e}")
    print("Ejecute: pip install selenium webdriver-manager")
    SELENIUM_DISPONIBLE = False


def test_selenium_chrome():
    """
    Prueba de Selenium:
    1. Abre Chrome (visible, NO headless)
    2. Navega a SURA login
    3. Espera 30 segundos para que el usuario se loguee manualmente
    4. Cierra el navegador
    """
    
    print("\n" + "="*70)
    print("PRUEBA SELENIUM - CHROME BROWSER")
    print("="*70)
    
    if not SELENIUM_DISPONIBLE:
        print("[ERROR] Selenium no disponible. Abortando.")
        return False
    
    try:
        # Configurar opciones de Chrome
        print("\n[1/5] Configurando opciones de Chrome...")
        chrome_options = Options()
        
        # NO headless - queremos ver el navegador
        # chrome_options.add_argument('--headless')  # COMENTADO para modo visible
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # Configurar carpeta de descargas (Desktop del usuario)
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        
        prefs = {
            "download.default_directory": desktop_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        print(f"   - Modo: VISIBLE (no headless)")
        print(f"   - Carpeta descargas: {desktop_path}")
        
        # Iniciar driver con webdriver-manager
        print("\n[2/5] Iniciando ChromeDriver...")
        print("   (Primera vez descarga chromedriver automaticamente)")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("   [OK] ChromeDriver iniciado exitosamente")
        
        # Navegar a SURA login
        print("\n[3/5] Navegando a SURA login...")
        url_sura = "https://login.sura.com/"  # URL simplificada
        
        driver.get(url_sura)
        print(f"   URL: {url_sura}")
        print(f"   Titulo: {driver.title}")
        print(f"   URL actual: {driver.current_url}")
        
        # Esperar a que el usuario se loguee manualmente
        print("\n[4/5] Esperando interaccion del usuario...")
        print("   INSTRUCCIONES:")
        print("   - El navegador Chrome esta abierto")
        print("   - Puede interactuar con la pagina manualmente")
        print("   - Loguese si lo desea (opcional)")
        print("   - El script esperara 30 segundos antes de cerrar")
        print("\n   Tiempo de espera: 30 segundos")
        
        # Countdown
        for i in range(30, 0, -5):
            print(f"   ... {i} segundos restantes")
            time.sleep(5)
        
        # Información final
        print("\n[5/5] Finalizando prueba...")
        print(f"   URL final: {driver.current_url}")
        print(f"   Titulo final: {driver.title}")
        
        # Cerrar navegador
        driver.quit()
        print("\n[OK] Navegador cerrado exitosamente")
        
        print("\n" + "="*70)
        print("PRUEBA COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\nRESULTADOS:")
        print("  [OK] ChromeDriver instalado y funcional")
        print("  [OK] Selenium puede abrir Chrome (modo visible)")
        print("  [OK] Navegacion a URL externa exitosa")
        print("  [OK] Driver responde correctamente")
        print("\nPROXIMOS PASOS:")
        print("  1. Implementar selectores especificos (XPath/CSS)")
        print("  2. Agregar logica de espera inteligente (WebDriverWait)")
        print("  3. Crear funciones para cada tarea (afiliar, descargar, etc.)")
        print("  4. Manejar excepciones y reintentos")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fallo en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
        
        try:
            driver.quit()
        except:
            pass
        
        return False


def test_selenium_con_elementos():
    """
    Prueba avanzada: Busca elementos en la página
    """
    print("\n" + "="*70)
    print("PRUEBA AVANZADA - BUSQUEDA DE ELEMENTOS")
    print("="*70)
    
    if not SELENIUM_DISPONIBLE:
        print("[ERROR] Selenium no disponible.")
        return False
    
    try:
        print("\n[1/3] Iniciando navegador...")
        chrome_options = Options()
        chrome_options.add_argument('--start-maximized')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navegar a una página de prueba (Google)
        print("\n[2/3] Navegando a Google (para testing)...")
        driver.get("https://www.google.com")
        
        # Buscar campo de búsqueda
        print("\n[3/3] Buscando elementos en la pagina...")
        
        try:
            # Google search box (varios selectores posibles)
            search_box = driver.find_element(By.NAME, "q")
            print("   [OK] Campo de busqueda encontrado (By.NAME)")
            
            # Escribir texto
            search_box.send_keys("Selenium Python Tutorial")
            print("   [OK] Texto ingresado en el campo")
            
            # Esperar 3 segundos para ver el resultado
            time.sleep(3)
            
        except Exception as e:
            print(f"   [WARNING] No se pudo interactuar con elementos: {e}")
        
        # Cerrar
        driver.quit()
        print("\n[OK] Prueba avanzada completada")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Fallo: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          AUTOMATION ENGINEER - SELENIUM TEST SUITE                ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    # Prueba 1: Navegador básico
    resultado_1 = test_selenium_chrome()
    
    # Pregunta si desea ejecutar prueba avanzada
    if resultado_1:
        print("\n\nDesea ejecutar la prueba avanzada (busqueda de elementos)?")
        print("Presione Enter para continuar o Ctrl+C para salir...")
        
        try:
            input()
            resultado_2 = test_selenium_con_elementos()
        except KeyboardInterrupt:
            print("\n\n[INFO] Prueba avanzada omitida por el usuario")
            resultado_2 = None
    
    # Exit code
    if resultado_1:
        print("\n\n[SUCCESS] Todas las pruebas basicas pasaron")
        sys.exit(0)
    else:
        print("\n\n[FAILED] Algunas pruebas fallaron")
        sys.exit(1)
