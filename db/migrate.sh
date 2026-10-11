#!/bin/sh
# Applies db/migrations/*.sql in order, once each. Safe to re-run.
set -eu

psql -v ON_ERROR_STOP=1 -q -c "CREATE TABLE IF NOT EXISTS schema_migrations (version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())"

for file in /migrations/*.sql; do
  version=$(basename "$file" .sql)
  done_already=$(psql -At -v ON_ERROR_STOP=1 -c "SELECT 1 FROM schema_migrations WHERE version = '$version'")
  if [ "$done_already" = "1" ]; then
    echo "skip $version"
    continue
  fi
  psql -v ON_ERROR_STOP=1 -q -1 \
    -v catalog_pw="$CATALOG_DB_PASSWORD" \
    -v admin_pw="$ADMIN_DB_PASSWORD" \
    -f "$file"
  psql -v ON_ERROR_STOP=1 -q -c "INSERT INTO schema_migrations (version) VALUES ('$version')"
  echo "applied $version"
done
echo "migrations complete"
