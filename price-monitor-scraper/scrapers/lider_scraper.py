import json
import logging
from scrapers.base_scraper import BaseScraper, logger
from selenium.webdriver.common.by import By

class LiderScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless=headless)

    def scrape_category(self, category_name, url):
        """Extrae productos de una categoría en lider.cl"""
        logger.info(f"Navegando a la categoría '{category_name}' en Líder: {url}")
        self.driver.get(url)
        time_to_wait = 6
        import time
        time.sleep(time_to_wait)
        
        products = []
        
        # Estrategia A: Intercepción del JSON Hydrate (__NEXT_DATA__)
        try:
            logger.info("Intentando extraer datos vía hidratación __NEXT_DATA__...")
            next_data_elem = self.driver.find_element(By.ID, "__NEXT_DATA__")
            next_data_json = json.loads(next_data_elem.get_attribute("innerHTML"))
            
            # Buscar recursivamente la lista de productos en el estado hidratado
            # Las estructuras típicas son props.pageProps.initialState.search.results o similares
            props = next_data_json.get("props", {})
            page_props = props.get("pageProps", {})
            initial_state = page_props.get("initialState", {})
            
            raw_products = []
            # Intentar diferentes rutas comunes en Next.js para catalogación de Líder
            if "products" in page_props:
                raw_products = page_props["products"]
            elif "products" in initial_state:
                raw_products = initial_state["products"]
            elif "search" in initial_state and "results" in initial_state["search"]:
                raw_products = initial_state["search"]["results"]
            elif "catalog" in initial_state and "products" in initial_state["catalog"]:
                raw_products = initial_state["catalog"]["products"]
                
            if raw_products:
                logger.info(f"__NEXT_DATA__ interceptado con éxito. Se encontraron {len(raw_products)} productos.")
                for p in raw_products:
                    # Mapear los campos del JSON de Líder
                    sku = str(p.get("sku") or p.get("id") or "")
                    name = p.get("displayName") or p.get("name") or ""
                    brand = p.get("brand") or "Genérico"
                    
                    price_info = p.get("price", {})
                    price_normal = price_info.get("priceNumber") or p.get("priceNormal") or 0
                    price_promo = price_info.get("promoPrice") or p.get("pricePromo") or None
                    
                    # Convertir a entero
                    price_normal = int(price_normal) if price_normal else 0
                    price_promo = int(price_promo) if price_promo else None
                    
                    url_suffix = p.get("productUrl") or f"/product/{sku}"
                    product_url = f"https://www.lider.cl/supermercado{url_suffix}" if not url_suffix.startswith("http") else url_suffix
                    
                    if sku and name:
                        products.append({
                            "skuSupermarket": sku,
                            "name": name,
                            "brand": brand,
                            "category": category_name,
                            "priceNormal": price_normal,
                            "pricePromo": price_promo,
                            "url": product_url,
                            "isAvailable": p.get("available", True)
                        })
                return products
        except Exception as e:
            logger.warning(f"Fallo en Estrategia A (__NEXT_DATA__): {e}. Activando Estrategia B (Inspección DOM)...")

        # Estrategia B: Extracción mediante selectores clásicos del DOM
        try:
            self.scroll_incrementally(steps=6, delay=1.0)
            
            # Buscar contenedores de productos
            # Las tarjetas de productos de Líder suelen usar selectores consistentes con 'product-card'
            cards = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'product-card')] | //div[contains(@class, 'ProductCard')]")
            logger.info(f"Estrategia B: Se detectaron {len(cards)} tarjetas de producto visibles en el DOM.")
            
            for card in cards:
                try:
                    # Título / Nombre
                    name_elem = card.find_element(By.XPATH, ".//span[contains(@class, 'name')] | .//div[contains(@class, 'name')] | .//h3")
                    name = name_elem.text.strip()
                    
                    # Marca
                    try:
                        brand_elem = card.find_element(By.XPATH, ".//span[contains(@class, 'brand')] | .//div[contains(@class, 'brand')]")
                        brand = brand_elem.text.strip()
                    except:
                        brand = "Genérico"
                    
                    # URL & SKU
                    link_elem = card.find_element(By.XPATH, ".//a[contains(@href, '/product/')]")
                    product_url = link_elem.get_attribute("href")
                    sku = product_url.split("/product/")[-1].split("?")[0].split("/")[0]
                    
                    # Precios
                    price_normal = 0
                    price_promo = None
                    
                    # En Líder suele haber precios con clases que contienen 'price' o etiquetas descriptivas
                    try:
                        price_elems = card.find_elements(By.XPATH, ".//*[contains(@class, 'price')] | .//*[contains(@class, 'Price')]")
                        prices_found = []
                        for pe in price_elems:
                            text = pe.text.replace("$", "").replace(".", "").strip()
                            if text.isdigit():
                                prices_found.append(int(text))
                                
                        if len(prices_found) == 1:
                            price_normal = prices_found[0]
                        elif len(prices_found) >= 2:
                            # Habitualmente el más bajo es la oferta y el más alto el normal
                            price_promo = min(prices_found)
                            price_normal = max(prices_found)
                    except Exception as pe_err:
                        logger.debug(f"Error parseando precio en tarjeta: {pe_err}")

                    if sku and name and price_normal > 0:
                        products.append({
                            "skuSupermarket": sku,
                            "name": name,
                            "brand": brand,
                            "category": category_name,
                            "priceNormal": price_normal,
                            "pricePromo": price_promo,
                            "url": product_url,
                            "isAvailable": True
                        })
                except Exception as card_err:
                    logger.debug(f"Error procesando tarjeta individual: {card_err}")
                    continue
                    
        except Exception as e:
            logger.error(f"Fallo crítico en Estrategia B de scraping en Líder: {e}")

        logger.info(f"Extracción finalizada para Líder en '{category_name}'. Total productos procesados: {len(products)}")
        return products
