import os

# Configuración de URLs iniciales para Scraping
LIDER_CATEGORIES = {
    "Despensa": "https://www.lider.cl/supermercado/category/Despensa/_/N-1ku587g",
    "Lacteos": "https://www.lider.cl/supermercado/category/Frescos-y-Lacteos/Lacteos/_/N-92vgyp"
}

JUMBO_CATEGORIES = {
    "Despensa": "https://www.jumbo.cl/despensa",
    "Lacteos": "https://www.jumbo.cl/lacteos"
}

# Configuración del Endpoint del Backend REST
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8080/api/v1/etl/ingest")
API_KEY = os.environ.get("API_KEY", "PROD_SECURE_EXTRACTOR_KEY_2026")

# Configuraciones de Selenium
HEADLESS = os.environ.get("HEADLESS_SCRAPE", "True").lower() == "true"
SELENIUM_TIMEOUT = 20
PAGE_LOAD_WAIT = 5
