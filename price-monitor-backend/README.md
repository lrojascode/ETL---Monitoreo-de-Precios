# Price Monitor API Backend

Este servicio es la API REST central del Sistema ETL de Monitoreo de Precios. Está encargado de recibir los payloads JSON del scraper de forma segura, desduplicar catálogos e histórico de precios en PostgreSQL y calcular alertas de variaciones de precios de forma inmediata y transaccional.

## Stack Tecnológico
* **Core:** Java 17, Spring Boot 4.0.6
* **Persistencia:** Spring Data JPA, Hibernate 7.x
* **Base de Datos:** PostgreSQL JDBC Driver
* **Seguridad:** Spring Security
* **Utilidades:** Project Lombok, Jakarta Validation API
* **Compilación:** Maven 3.9+

## Arquitectura y Flujo de Datos
1. El Scraper envía un payload JSON al endpoint `/api/v1/etl/ingest`.
2. El `ApiKeyFilter` intercepta y valida la cabecera `X-API-KEY`.
3. El `IngestionService` procesa de forma transaccional (`@Transactional`) el lote:
   * Desduplica y guarda de forma case-insensitive marcas y categorías.
   * Asocia o crea el producto unificado en el catálogo maestro.
   * Crea o actualiza la relación de equivalencia del SKU por cadena.
   * Persiste el historial de precios en lote (optimización Hibernate batch size = 100).
4. El `AlertEngineService` calcula si el precio efectivo es inferior en un 15% o más frente al promedio móvil de 15 días del producto, y en tal caso persiste una alerta en `price_alerts`.

## Endpoints de la API
* **`POST /api/v1/etl/ingest`**
  * **Cabecera requerida:** `X-API-KEY: PROD_SECURE_EXTRACTOR_KEY_2026`
  * **Payload esperado (JSON):**
    ```json
    {
      "supermarket": "LIDER",
      "extractionDate": "2026-05-27T18:00:00Z",
      "products": [
        {
          "skuSupermarket": "758493",
          "name": "Aceite de Oliva Extra Virgen 500ml",
          "brand": "Casta de Olivia",
          "category": "Despensa",
          "priceNormal": 7890,
          "pricePromo": 6490,
          "url": "https://www.lider.cl/supermercado/product/sku/758493",
          "isAvailable": true
        }
      ]
    }
    ```
  * **Respuesta HTTP 200 (Éxito):**
    ```json
    {
      "message": "Ingesta procesada de forma exitosa",
      "summary": {
        "processedCount": 1,
        "newProductsCount": 0
      }
    }
    ```

## Variables de Entorno
| Variable | Descripción | Valor sugerido (Local) | Valor sugerido (Docker) |
|---|---|---|---|
| `SERVER_PORT` | Puerto de escucha de Tomcat | `8080` | `8080` (remapeado en host a `8085`) |
| `SPRING_DATASOURCE_URL` | URL de conexión JDBC a PostgreSQL | `jdbc:postgresql://localhost:5433/price_monitor_db` | `jdbc:postgresql://postgres-db:5432/price_monitor_db` |
| `SPRING_DATASOURCE_USERNAME` | Usuario de PostgreSQL | `monitor_user` | `monitor_user` |
| `SPRING_DATASOURCE_PASSWORD` | Contraseña de PostgreSQL | `SecretProductionPassword2026` | `SecretProductionPassword2026` |
| `APP_SECURITY_API-KEY` | Clave API exigida para la ingesta | `PROD_SECURE_EXTRACTOR_KEY_2026` | `PROD_SECURE_EXTRACTOR_KEY_2026` |

## Instrucciones de Despliegue Local (Fuera de Docker)
1. Asegurar que PostgreSQL esté corriendo en el puerto 5433 en tu host.
2. Navegar al directorio e iniciar la compilación y ejecución de la aplicación:
   ```bash
   ./mvnw spring-boot:run
   ```

## Docker Setup
Para construir y correr el contenedor del backend de forma independiente:
```bash
docker build -t price-monitor-backend .
docker run -d -p 8085:8080 --name etl-spring-backend price-monitor-backend
```
