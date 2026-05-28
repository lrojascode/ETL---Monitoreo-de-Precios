import time
import logging
from scrapers.base_scraper import BaseScraper, logger
from selenium.webdriver.common.by import By

class JumboScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless=headless)

    def scrape_category(self, category_name, url):
        """Extrae productos de una categoría en jumbo.cl"""
        logger.info(f"Navegando a la categoría '{category_name}' en Jumbo: {url}")
        self.driver.get(url)
        time.sleep(5)
        
        # Depuración visual de lo que carga en pantalla
        screenshot_path = f"{category_name}_jumbo_debug.png"
        self.driver.save_screenshot(screenshot_path)
        logger.info(f"Captura de pantalla de depuración guardada en: {screenshot_path}")
        
        products = []
        
        try:
            # 1. Scroll dinámico para forzar el renderizado completo de la grilla asíncrona
            self.scroll_incrementally(steps=8, delay=1.2)
            
            # 2. Localizar tarjetas de producto
            # En Jumbo las tarjetas se identifican de forma extremadamente robusta mediante el atributo 'data-cnstrc-item-id'
            cards = self.driver.find_elements(By.XPATH, "//div[@data-cnstrc-item-id]")
            logger.info(f"Se detectaron {len(cards)} tarjetas de producto visibles en Jumbo para la categoría '{category_name}'.")
            
            for card in cards:
                try:
                    # Extraer ID (SKU) y Nombre del producto directamente de los atributos del contenedor
                    sku = card.get_attribute("data-cnstrc-item-id")
                    name = card.get_attribute("data-cnstrc-item-name")
                    
                    # Precio base/activo en el atributo
                    attr_price = card.get_attribute("data-cnstrc-item-price")
                    price_val = int(attr_price) if attr_price and attr_price.isdigit() else 0
                    
                    if not sku or not name or price_val <= 0:
                        continue
                        
                    # URL del producto
                    product_url = None
                    try:
                        product_url = card.find_element(By.XPATH, ".//a").get_attribute("href")
                    except:
                        pass
                        
                    # Marca: VTEX a menudo lo tiene como una línea previa al nombre del producto en el texto acumulado
                    lines = [line.strip() for line in card.text.splitlines() if line.strip()]
                    brand = "Genérico"
                    if name in lines:
                        idx = lines.index(name)
                        if idx > 0:
                            possible_brand = lines[idx - 1]
                            if not (possible_brand.startswith("$") or "dcto" in possible_brand.lower() or possible_brand.lower() in ["patrocinado", "agregar", "sin stock", "agotado"]):
                                brand = possible_brand
                    
                    # Precios (Normal y Promo)
                    price_normal = price_val
                    price_promo = None
                    
                    # Si el producto tiene oferta/descuento, suele mostrarse con un precio tachado (line-through)
                    try:
                        lt_elem = card.find_element(By.XPATH, ".//*[contains(@class, 'line-through')]")
                        text = lt_elem.text.replace("$", "").replace(".", "").strip()
                        digits = "".join([c for c in text if c.isdigit()])
                        if digits:
                            price_normal = int(digits)
                            price_promo = price_val
                    except:
                        pass
                        
                    # Disponibilidad (Validar si hay botón de comprar o etiqueta de agotado)
                    is_available = True
                    try:
                        card_html = card.get_attribute("innerHTML").lower()
                        if "agotado" in card_html or "sin stock" in card_html or "no disponible" in card_html:
                            is_available = False
                    except:
                        pass

                    products.append({
                        "skuSupermarket": sku,
                        "name": name,
                        "brand": brand,
                        "category": category_name,
                        "priceNormal": price_normal,
                        "pricePromo": price_promo,
                        "url": product_url,
                        "isAvailable": is_available
                    })
                except Exception as card_err:
                    logger.debug(f"Error procesando tarjeta individual en Jumbo: {card_err}")
                    continue
                    
        except Exception as e:
            logger.error(f"Fallo crítico realizando scraping en Jumbo: {e}")

        logger.info(f"Extracción finalizada para Jumbo en '{category_name}'. Total productos procesados: {len(products)}")
        return products
