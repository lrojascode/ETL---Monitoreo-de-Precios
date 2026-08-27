import os

# Configuración de URLs iniciales para Scraping
LIDER_CATEGORIES = {
    "Despensa": "https://super.lider.cl/content/despensa/46589040",
    "Lacteos": "https://super.lider.cl/content/lacteos,fiambreria-y-huevos/45669105"
}

JUMBO_CATEGORIES = {
    "Despensa": "https://www.jumbo.cl/despensa",
    "Lacteos": "https://www.jumbo.cl/lacteos-huevos-y-congelados"
}

# Configuración del Endpoint del Backend REST
BACKEND_API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8085/api/v1/etl/ingest")
API_KEY = os.environ.get("API_KEY", "local-dev-api-key")

# Configuraciones de Selenium
HEADLESS = os.environ.get("HEADLESS_SCRAPE", "True").lower() == "true"
SELENIUM_TIMEOUT = 20
PAGE_LOAD_WAIT = 5
