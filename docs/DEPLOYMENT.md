# Deployment

## Docker

Build and run the Docker image:

```bash
docker build -t aidia-blog .
docker run -p 8080:8080 --env-file .env aidia-blog
```

The image uses the Python 3.12-slim base image. It uses Node.js 20.x to build the frontend assets. On startup, `start.sh` runs the database migrations and starts Gunicorn with 4 workers and a 120-second timeout.

## Railway

The `railway.json` file deploys the app with the Nixpacks builder. It configures one replica with a restart-on-failure policy (maximum 10 retries).

## CI/CD Pipeline

The GitHub Actions workflow is at `.github/workflows/ci-cd.yml`. On every push to `main`, it runs four jobs:

1. **Test** — Runs pytest against a PostgreSQL 16 service container.
2. **Build** — Builds a Docker image. Trivy scans the image for HIGH and CRITICAL vulnerabilities.
3. **Deploy** — Deploys to Railway with the Railway CLI. Verifies the deployment with a health check.
4. **Backup** — Runs `scripts/backup.sh` to back up the database.

## Database Migrations

Create a new migration:

```bash
flask db migrate -m "description of changes"
```

Apply migrations:

```bash
flask db upgrade
```

Roll back the last migration:

```bash
flask db downgrade
```

## Backup

The script `scripts/backup.sh` creates automated database backups. It uses `pg_dump` to create SQL backups and gzip to compress them. It deletes backups that are older than 7 days. The script needs the `DATABASE_URL` and `BACKUP_DIR` environment variables.

Manual backup:

```bash
bash scripts/backup.sh
```