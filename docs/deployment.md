# Deployment

## Docker Compose (Development/Staging)

```bash
# Start all services
docker compose up --build

# Start in background
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Reset volumes
docker compose down -v
```

Services:
- `backend` — FastAPI on port 8000
- `worker` — Celery worker
- `db` — PostgreSQL on port 5432
- `redis` — Redis on port 6379

## Kubernetes (Production)

### Prerequisites

- Kubernetes cluster (v1.28+)
- Ingress controller (nginx-ingress)
- cert-manager for TLS
- kubectl configured

### Deploy

```bash
# Create namespace
kubectl apply -f infrastructure/kubernetes/namespace.yaml

# Create secrets (edit with your values)
kubectl create secret generic app-secrets \
  --from-literal=secret-key='your-secret-key' \
  --from-literal=gemini-api-key='your-gemini-key' \
  -n resume-builder

kubectl create secret generic db-connection \
  --from-literal=async-url='postgresql+asyncpg://user:pass@host:5432/resume_builder' \
  -n resume-builder

kubectl create secret generic redis-connection \
  --from-literal=url='redis://redis:6379/0' \
  --from-literal=broker-url='redis://redis:6379/1' \
  --from-literal=result-url='redis://redis:6379/2' \
  -n resume-builder

# Deploy applications
kubectl apply -f infrastructure/kubernetes/backend
kubectl apply -f infrastructure/kubernetes/worker
kubectl apply -f infrastructure/kubernetes/ingress.yaml

# Check status
kubectl get pods -n resume-builder
kubectl get ingress -n resume-builder
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment resume-backend --replicas=5 -n resume-builder
kubectl scale deployment resume-worker --replicas=3 -n resume-builder

# HPA auto-scaling (already configured)
kubectl get hpa -n resume-builder
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Async PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `SECRET_KEY` | Yes | JWT signing key (min 32 chars) |
| `GEMINI_API_KEY` | No | Google Gemini API key |
| `CORS_ORIGINS` | Yes | Allowed CORS origins |
| `ENVIRONMENT` | Yes | `development`, `staging`, or `production` |
| `SENTRY_DSN` | No | Sentry error tracking |
| `SMTP_HOST` | No | Email server |

## Database Migrations

```bash
# Auto-generate migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Health Checks

- Backend: `GET /health`
- Readiness: `GET /health`
- Liveness: `GET /health`

## Monitoring

- Prometheus metrics: `/metrics` (FastAPI)
- Structured logs to stdout
- Sentry error tracking (when configured)
- OpenTelemetry tracing (when configured)
