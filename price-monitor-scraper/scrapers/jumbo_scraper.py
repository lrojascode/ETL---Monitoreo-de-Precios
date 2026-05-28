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
            # En Jumbo (VTEX) las tarjetas tienen atributos data-testid='product-card' o clases similares
            cards = self.driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'vtex-product-summary-2-x-container') or contains(@class, 'vtex-product-summary') or contains(@class, 'product-card') or @data-testid='product-card']"
            )
            logger.info(f"Se detectaron {len(cards)} tarjetas de producto visibles en Jumbo para la categoría '{category_name}'.")
            
            for card in cards:
                try:
                    # Nombre de Producto
                    name_elem = card.find_element(By.XPATH, 
                        ".//*[contains(@class, 'product-card-name')] | .//*[contains(@class, 'brandName')] | .//*[contains(@class, 'vtex-product-summary-2-x-name')] | .//h2 | .//h3"
                    )
                    name = name_elem.text.strip()
                    
                    # URL del producto
                    link_elem = card.find_element(By.XPATH, ".//a[contains(@href, '/')]")
                    product_url = link_elem.get_attribute("href")
                    
                    # Extraer SKU de la URL o usar un ID generado/data-id
                    # Jumbo VTEX a veces tiene urls como https://www.jumbo.cl/aceite-oliva-virgen-500ml/p
                    # El SKU final o ID del producto está contenido en atributos
                    sku = None
                    try:
                        sku = card.get_attribute("id") or card.get_attribute("data-sku")
                    except:
                        pass
                        
                    if not sku:
                        # Fallback a hash o segmento de la URL si no hay ID disponible
                        sku = product_url.split("/")[-2] if product_url else None
                    
                    # Marca (VTEX suele tener una clase vtex-product-summary-2-x-brandName)
                    try:
                        brand_elem = card.find_element(By.XPATH, ".//span[contains(@class, 'brandName')] | .//span[contains(@class, 'brand')]")
                        brand = brand_elem.text.strip()
                    except:
                        brand = "Genérico"
                        
                    # Validar si el nombre contiene la marca al inicio (limpieza)
                    if brand != "Genérico" and name.lower().startswith(brand.lower()):
                        # Opcional: limpieza de redundancias
                        pass

                    # Precios (Normal y Promo)
                    price_normal = 0
                    price_promo = None
                    
                    try:
                        # Buscar valores monetarios en la tarjeta
                        # Jumbo VTEX estructura precios en componentes como '.jumbo-price' o '.price-selling'
                        price_elements = card.find_elements(By.XPATH, 
                            ".//*[contains(@class, 'price')] | .//*[contains(@class, 'Price')] | .//*[contains(@class, 'selling')] | .//*[contains(@class, 'value')]"
                        )
                        prices_found = []
                        for pe in price_elements:
                            text = pe.text.replace("$", "").replace(".", "").replace("/un", "").strip()
                            # Extraer solo dígitos
                            digits = "".join([c for c in text if c.isdigit()])
                            if digits:
                                prices_found.append(int(digits))
                        
                        # Eliminar duplicados manteniendo orden
                        prices_found = list(dict.fromkeys(prices_found))
                        
                        if len(prices_found) == 1:
                            price_normal = prices_found[0]
                        elif len(prices_found) >= 2:
                            # Típicamente el menor es la oferta activa y el mayor es el precio lista/normal
                            price_promo = min(prices_found)
                            price_normal = max(prices_found)
                    except Exception as pe_err:
                        logger.debug(f"Error procesando precios de Jumbo: {pe_err}")

                    # Disponibilidad (Validar si hay botón de comprar o etiqueta de agotado)
                    is_available = True
                    try:
                        card_html = card.get_attribute("innerHTML").lower()
                        if "agotado" in card_html or "sin stock" in card_html or "no disponible" in card_html:
                            is_available = False
                    except:
                        pass

                    if sku and name and price_normal > 0:
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
