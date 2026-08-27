import requests
import json
import os
from datetime import datetime, timedelta, timezone

API_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8085/api/v1/etl/ingest")
API_KEY = os.environ.get("API_KEY", "local-dev-api-key")

def send_ingest(supermarket, date_str, products):
    payload = {
        "supermarket": supermarket,
        "extractionDate": date_str,
        "products": products
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }
    
    print(f"\n---> Enviando payload de {supermarket} para la fecha {date_str}...")
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        print(f"Respuesta HTTP {response.status_code}")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    today = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # 1. Productos del Día Anterior (Estableciendo histórico de precios altos)
    products_yesterday = [
        {
            "skuSupermarket": "LECHE-123",
            "name": "Leche Entera Soprole 1L",
            "brand": "Soprole",
            "category": "Lácteos",
            "priceNormal": 1500,
            "pricePromo": None,
            "url": "https://www.lider.cl/supermercado/product/sku/LECHE-123",
            "isAvailable": True
        },
        {
            "skuSupermarket": "ACEITE-456",
            "name": "Aceite de Oliva Extra Virgen 500ml",
            "brand": "Casta de Olivia",
            "category": "Despensa",
            "priceNormal": 8000,
            "pricePromo": 7500,
            "url": "https://www.lider.cl/supermercado/product/sku/ACEITE-456",
            "isAvailable": True
        }
    ]
    
    # Enviar lote 1
    send_ingest("LIDER", yesterday, products_yesterday)
    
    # 2. Productos de Hoy (Baja crítica de precios en la Leche Entera del 40%)
    products_today = [
        {
            "skuSupermarket": "LECHE-123",
            "name": "Leche Entera Soprole 1L",
            "brand": "Soprole",
            "category": "Lácteos",
            "priceNormal": 1500,
            "pricePromo": 900,  # Promoción agresiva: $900 frente al promedio $1500 (baja del 40%)
            "url": "https://www.lider.cl/supermercado/product/sku/LECHE-123",
            "isAvailable": True
        },
        {
            "skuSupermarket": "ACEITE-456",
            "name": "Aceite de Oliva Extra Virgen 500ml",
            "brand": "Casta de Olivia",
            "category": "Despensa",
            "priceNormal": 8000,
            "pricePromo": 7450,  # Baja mínima de precio, no debería gatillar alerta
            "url": "https://www.lider.cl/supermercado/product/sku/ACEITE-456",
            "isAvailable": True
        }
    ]
    
    # Enviar lote 2
    send_ingest("LIDER", today, products_today)
    
    print("\nSimulación finalizada. Comprueba los logs del backend y la BD para verificar alertas.")
