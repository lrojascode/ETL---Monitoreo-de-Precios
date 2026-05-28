import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

# Configuración de Logs básicos
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless=new")
        
        # Argumentos de evasión activa de sandbox y automatización
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent estándar y robusto de escritorio
        self.options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Perfil de usuario persistente para almacenar cookies, sesión y preferencias (ej. ubicación seleccionada)
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        profile_path = os.path.join(os.path.dirname(current_dir), "chrome_profile")
        self.options.add_argument(f"--user-data-dir={profile_path}")
        
        # Detección adaptativa de la ruta del navegador para portabilidad local/Docker
        import os
        chromedriver_path = "/usr/bin/chromedriver"
        
        if os.path.exists("/usr/bin/chromium"):
            self.options.binary_location = "/usr/bin/chromium"
        elif os.path.exists("/usr/bin/chromium-browser"):
            self.options.binary_location = "/usr/bin/chromium-browser"
            
        logger.info("Inicializando Chrome WebDriver...")
        if os.path.exists(chromedriver_path):
            logger.info(f"Usando ChromeDriver local del sistema: {chromedriver_path}")
            service = Service(executable_path=chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=self.options)
        else:
            logger.info("ChromeDriver local no detectado, usando Selenium Manager de forma automática.")
            self.driver = webdriver.Chrome(options=self.options)
        self.driver.set_window_size(1920, 1080)
        
        # Inyectar evasión avanzada por stealth
        stealth(self.driver,
            languages=["es-CL", "es"],
            vendor="Google Inc.",
            platform="MacIntel",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
        logger.info("WebDriver inicializado exitosamente con emulación Stealth activa.")

    def wait_for_presence(self, xpath, timeout=15):
        """Espera explícita a la presencia del elemento en el DOM"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    def wait_for_visible(self, xpath, timeout=15):
        """Espera explícita a la visibilidad física del elemento"""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )

    def scroll_incrementally(self, steps=5, delay=1.0):
        """Scroll incremental controlado para gatillar carga perezosa (lazy-load) de imágenes/datos"""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        step_height = total_height / steps
        for i in range(1, steps + 1):
            self.driver.execute_script(f"window.scrollTo(0, {step_height * i});")
            time.sleep(delay)
        # Volver al inicio
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

    def close(self):
        """Cierre ordenado de los procesos de Selenium"""
        if self.driver:
            logger.info("Cerrando WebDriver...")
            self.driver.quit()
