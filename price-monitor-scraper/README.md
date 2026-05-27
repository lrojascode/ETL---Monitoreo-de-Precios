# Price Monitor Scraper Modular

Este componente es el encargado del proceso de extracción (E) dentro de nuestro pipeline ETL. Recorre de forma automatizada las secciones correspondientes de los supermercados chilenos Líder (lider.cl) y Jumbo (jumbo.cl), emulando comportamiento humano y procesando los datos para transmitirlos al backend.

## Stack Tecnológico
* **Core:** Python 3.11
* **Evasión & Automatización:** Selenium WebDriver, Selenium Stealth
* **Transmisión de Datos:** Requests, Urllib3
* **Navegadores Soportados:** Chromium / Google Chrome

## Estructura del Módulo de Extracción
* `scrapers/base_scraper.py`: Clase base abstracta. Inicializa el navegador Chrome con argumentos específicos, inyecta la evasión de firmas automatizadas por `selenium-stealth`, maneja scrolling incremental controlado y esperas explícitas.
* `scrapers/lider_scraper.py`: Estrategia acelerada. Intenta capturar el JSON hydrate `__NEXT_DATA__` en el DOM para recolectar datos al instante. Dispone de un fallback por XPath y Selectores en caso de reestructuración de la web.
* `scrapers/jumbo_scraper.py`: Selector basado en VTEX. Ejecuta scroll incremental para forzar la grilla asíncrona y extrae nombres, SKUs, precios y stock mediante selectores adaptativos.
* `main.py`: Orquestador principal. Sincroniza secuencialmente las extracciones, formatea los datos y los envía en lotes al API REST del backend.

## Variables de Entorno
| Variable | Descripción | Valor sugerido (Local) | Valor sugerido (Docker) |
|---|---|---|---|
| `BACKEND_API_URL` | Endpoint receptor de datos de ingesta | `http://localhost:8085/api/v1/etl/ingest` | `http://backend-api:8080/api/v1/etl/ingest` |
| `API_KEY` | Clave API requerida para la autenticación | `PROD_SECURE_EXTRACTOR_KEY_2026` | `PROD_SECURE_EXTRACTOR_KEY_2026` |
| `HEADLESS_SCRAPE` | Ejecutar navegador sin interfaz gráfica | `True` | `True` |

## Instrucciones de Despliegue Local (Fuera de Docker)
1. Instalar Google Chrome y ChromeDriver en tu máquina.
2. Crear un entorno virtual e instalar las dependencias:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Ejecutar el scraper:
   ```bash
   python3 main.py
   ```

## Docker Setup
Para construir y correr el contenedor de extracción de forma aislada (el cual autodetectará la arquitectura e instalará Chromium nativo optimizado compatible con ARM64/aarch64 y AMD64):
```bash
docker build -t price-monitor-scraper .
docker run --rm --network etl_network -e BACKEND_API_URL=http://backend-api:8080/api/v1/etl/ingest price-monitor-scraper
```
