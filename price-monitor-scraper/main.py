import sys
import logging
import requests
from datetime import datetime, timezone
import config
from scrapers.lider_scraper import LiderScraper
from scrapers.jumbo_scraper import JumboScraper

# Configuración de Logging de producción
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def send_payload_to_backend(supermarket, products):
    """Envía el payload JSON consolidado al backend mediante POST HTTP seguro"""
    if not products:
        logger.warning(f"No hay productos extraídos para {supermarket}. Se cancela el envío al backend.")
        return

    payload = {
        "supermarket": supermarket,
        "extractionDate": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "products": products
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": config.API_KEY
    }

    logger.info(f"Enviando lote de {len(products)} productos de {supermarket} a {config.BACKEND_API_URL}...")
    
    try:
        response = requests.post(config.BACKEND_API_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            res_data = response.json()
            summary = res_data.get("summary", {})
            logger.info(f"¡ÉXITO! Respuesta del servidor: {res_data.get('message')}. "
                        f"Procesados: {summary.get('processedCount')}, Nuevos: {summary.get('newProductsCount')}")
        else:
            logger.error(f"Error en la ingesta del backend. Código HTTP: {response.status_code}. Respuesta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Fallo crítico de comunicación al conectar con el backend: {e}")

def run_lider_extraction():
    """Ejecuta el ciclo de scraping para lider.cl"""
    logger.info("=== INICIANDO EXTRACCIÓN EN LÍDER ===")
    scraper = None
    all_products = []
    try:
        scraper = LiderScraper(headless=config.HEADLESS)
        for cat_name, url in config.LIDER_CATEGORIES.items():
            try:
                products = scraper.scrape_category(cat_name, url)
                all_products.extend(products)
            except Exception as cat_err:
                logger.error(f"Error procesando categoría {cat_name} en Líder: {cat_err}")
                
        send_payload_to_backend("LIDER", all_products)
        
    except Exception as e:
        logger.error(f"Error general en flujo de Líder: {e}")
    finally:
        if scraper:
            scraper.close()
    logger.info("=== EXTRACCIÓN LÍDER FINALIZADA ===")

def run_jumbo_extraction():
    """Ejecuta el ciclo de scraping para jumbo.cl"""
    logger.info("=== INICIANDO EXTRACCIÓN EN JUMBO ===")
    scraper = None
    all_products = []
    try:
        scraper = JumboScraper(headless=config.HEADLESS)
        for cat_name, url in config.JUMBO_CATEGORIES.items():
            try:
                products = scraper.scrape_category(cat_name, url)
                all_products.extend(products)
            except Exception as cat_err:
                logger.error(f"Error procesando categoría {cat_name} en Jumbo: {cat_err}")
                
        send_payload_to_backend("JUMBO", all_products)
        
    except Exception as e:
        logger.error(f"Error general en flujo de Jumbo: {e}")
    finally:
        if scraper:
            scraper.close()
    logger.info("=== EXTRACCIÓN JUMBO FINALIZADA ===")

if __name__ == "__main__":
    logger.info("Iniciando orquestador de Monitoreo de Precios...")
    
    # 1. Extracción Líder
    run_lider_extraction()
    
    # 2. Extracción Jumbo
    run_jumbo_extraction()
    
    logger.info("Ecosistema de extracción completado exitosamente.")
