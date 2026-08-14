#!/bin/bash
set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATABASE_URL="${DATABASE_URL}"

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable not set"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/bloggr_backup_$TIMESTAMP.sql"

run_pg_dump() {
    local server_major local_major
    server_major=$(psql "$DATABASE_URL" -tAc "SHOW server_version_num;" 2>/dev/null | head -c 2)
    local_major=$(pg_dump --version | sed -E 's/.* ([0-9]+).*/\1/')

    if command -v docker >/dev/null 2>&1 && [ -n "$server_major" ] && [ "$local_major" -lt "$server_major" ]; then
        echo "Local pg_dump ($local_major) is older than server ($server_major); using docker postgres:$server_major"
        docker run --rm "postgres:$server_major" pg_dump "$DATABASE_URL"
    else
        pg_dump "$DATABASE_URL"
    fi
}

echo "Starting database backup..."
run_pg_dump > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup created successfully: $BACKUP_FILE"
    gzip "$BACKUP_FILE"
    echo "Backup compressed: ${BACKUP_FILE}.gz"
    
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
    echo "Old backups (older than 7 days) cleaned up"
else
    echo "ERROR: Backup failed"
    exit 1
fi
