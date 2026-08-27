# Retail collectors

The Python 3.11 collector owns browser automation and retailer-specific extraction. It emits one normalized JSON batch per supermarket to the Spring ingestion API; it does not write to PostgreSQL directly.

## Adapters

- `scrapers/lider_scraper.py` first reads the page's Next.js hydration data and falls back to visible product cards.
- `scrapers/jumbo_scraper.py` scrolls the catalog and reads product-card data attributes.
- `scrapers/base_scraper.py` configures Chromium, Selenium Stealth, waits, scrolling, screenshots, and the persistent browser profile.
- `main.py` runs both adapters and submits their batches.

## Run locally

Chrome or Chromium is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
BACKEND_API_URL=http://localhost:8085/api/v1/etl/ingest \
API_KEY=local-dev-api-key \
python3 main.py
```

Set `HEADLESS_SCRAPE=False` for the first Lider run if a delivery-location modal must be completed. Browser state is stored in the ignored `chrome_profile/` directory.

## Run with Docker

From the repository root, with the backend running:

```bash
docker compose run --rm scraper-service
```

The collector screenshots are diagnostics from third-party source sites, not a project user interface. Review site terms and applicable law before operating the collectors.
