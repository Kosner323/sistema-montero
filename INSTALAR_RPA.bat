@echo off
REM =====================================================
REM INSTALADOR DE DEPENDENCIAS RPA
REM Sistema Montero - Módulo de Automatización
REM =====================================================

echo.
echo ========================================
echo   INSTALANDO MOTOR RPA (SELENIUM)
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Instalando Selenium...
pip install selenium>=4.15.0

echo.
echo [2/3] Instalando WebDriver Manager...
pip install webdriver-manager>=4.0.1

echo.
echo [3/3] Instalando BeautifulSoup4...
pip install beautifulsoup4>=4.12.3

echo.
echo ========================================
echo   INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo ✓ Selenium instalado
echo ✓ WebDriver Manager instalado
echo ✓ BeautifulSoup4 instalado
echo.
echo NOTA: El sistema descargará ChromeDriver automáticamente
echo       la primera vez que ejecutes una automatización.
echo.
pause
