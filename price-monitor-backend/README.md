# Ingestion and alert service

The Java 17 / Spring Boot service is the trusted boundary between browser collectors and PostgreSQL. It authenticates ingestion requests, validates payloads, normalizes retailer observations into a shared catalog, records price history, and creates price-drop alerts.

## API

`POST /api/v1/etl/ingest`

Required header:

```text
X-API-KEY: local-dev-api-key
```

See [`../examples/ingestion-payload.json`](../examples/ingestion-payload.json) for a complete request.

## Processing rules

1. Resolve or create a case-insensitive brand and category.
2. Resolve or create a master product by name and brand.
3. Map the product to the supermarket-specific SKU.
4. Append the observation to `price_histories`.
5. Compare the effective price with the rolling 15-day average and create an alert when the drop is at least 15%.

## Run locally

Start PostgreSQL from the repository root:

```bash
docker compose up -d postgres-db
```

Then start the service:

```bash
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5433/price_monitor_db \
SPRING_DATASOURCE_USERNAME=monitor_user \
SPRING_DATASOURCE_PASSWORD=local-dev-password \
APP_SECURITY_API_KEY=local-dev-api-key \
./mvnw spring-boot:run
```

## Test

```bash
./mvnw test
```

Tests use an in-memory H2 database. PostgreSQL is only required for the end-to-end test described in the root README.
