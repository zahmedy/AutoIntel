# NicheRides
Curated used car marketplace for niche buyers, starting with cold-weather commuter cars.

## Run With Docker Compose

```bash
docker compose -f infra/docker-compose.yaml up --build
```

- Web UI: `http://localhost:3001`
- API: `http://localhost:8000`
- MinIO API: `http://localhost:9000`
- MinIO Console: `http://localhost:9001`

## Price Prediction

Price prediction is served by the separate `nicherides-ml-platform` service. Point the API at its prediction endpoint:

```bash
PRICE_PREDICTION_API_URL=http://localhost:8001/v1/price/predict
```

Docker Compose points the API container at the host gateway by default:

```bash
PRICE_PREDICTION_API_URL=http://host.docker.internal:8080/v1/price/predict
```

## VIN Photo OCR

VIN photo scanning calls the separate `nicherides-ml-platform` service by default, then validates the 17-character VIN checksum before decoding vehicle details:

```bash
VIN_SCAN_API_URL=http://localhost:8001/v1/vin/photo
```

Docker Compose uses `http://host.docker.internal:8080/v1/vin/photo` for the same host service when the ML container publishes host port `8080`.

If that service is not available, VIN photo scanning falls back to local Tesseract OCR. Docker installs Tesseract automatically. For local API development, install the system binary first:

```bash
brew install tesseract
```

## Car Photo Storage

Car listing photos are uploaded through API-generated S3 presigned PUT URLs. Object keys default to the `cars-photos/` folder:

```bash
S3_KEY_PREFIX=cars-photos
```

For the production NicheRides bucket, point public photo URLs at the bucket host and leave custom S3 endpoints empty so boto3 uses AWS S3:

```bash
S3_BUCKET=nicherides
S3_ENDPOINT_URL=
S3_PRESIGN_BASE_URL=
S3_PUBLIC_BASE_URL=https://nicherides.s3.us-east-1.amazonaws.com
S3_KEY_PREFIX=cars-photos
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
```

```
nicherides/
  apps/
    api/
      app/
        api/v1/routes/
          auth.py
          cars.py
          admin.py
          media.py
        core/
          config.py
          security.py
          deps.py
        db/
          session.py
        models/
          user.py
          car.py
        schemas/
          auth.py
          car.py
          media.py
        services/
          s3.py
        tasks/
          worker.py
        main.py
      alembic.ini
      pyproject.toml
      Dockerfile
      alembic/
        env.py
        script.py.mako
        versions/
  infra/
    compose.yaml
  .env.example
  README.md

```
