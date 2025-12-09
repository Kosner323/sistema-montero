"""
Test rápido de Selenium sin espera larga
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

print("Iniciando prueba Selenium...")

# Configurar Chrome
chrome_options = Options()
chrome_options.add_argument('--start-maximized')

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navegar
driver.get("https://www.google.com")
print(f"Titulo: {driver.title}")
print(f"URL: {driver.current_url}")

# Esperar 3 segundos
time.sleep(3)

# Cerrar
driver.quit()

print("[OK] Prueba completada - Selenium funcional!")
