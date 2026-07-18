#!/bin/sh
# Ensure system PostgreSQL role + database for Forgejo.
# stdout: exactly ONE JSON line. All DDL noise → stderr only.
set -e

DB_HOST="${FORGEJO_DB_HOST:-127.0.0.1}"
DB_PORT="${FORGEJO_DB_PORT:-5433}"
DB_NAME="${FORGEJO_DB_NAME:-forgejo}"
DB_USER="${FORGEJO_DB_USER:-forgejo}"
DB_PASSWORD="${FORGEJO_DB_PASSWORD:-}"

out_json() {
  printf '%s\n' "$1"
}

log() {
  printf '%s\n' "$*" >&2
}

if ! command -v psql >/dev/null 2>&1; then
  out_json '{"ok":false,"error":"psql_missing","hint":"install postgresql client/server on host"}'
  exit 2
fi

if ! command -v pg_isready >/dev/null 2>&1; then
  out_json '{"ok":false,"error":"pg_isready_missing"}'
  exit 2
fi

if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q 2>/dev/null; then
  out_json "{\"ok\":false,\"error\":\"postgres_not_ready\",\"host\":\"$DB_HOST\",\"port\":\"$DB_PORT\",\"hint\":\"set FORGEJO_DB_PORT (AgentOS often 5433)\"}"
  exit 2
fi

if [ -z "$DB_PASSWORD" ]; then
  DB_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(24))')"
fi

# Run SQL as postgres; swallow all command output (ALTER ROLE notices break INSTALL JSON).
psql_as_postgres() {
  mode="$1" # query|exec
  sql="$2"
  if [ "$(id -u)" = 0 ] && id postgres >/dev/null 2>&1; then
    if [ "$mode" = "query" ]; then
      printf '%s\n' "$sql" | su -s /bin/sh postgres -c 'psql -v ON_ERROR_STOP=1 -q -t -A' 2>/dev/null
    else
      printf '%s\n' "$sql" | su -s /bin/sh postgres -c 'psql -v ON_ERROR_STOP=1 -q -t -A' >/dev/null 2>&1
    fi
  elif [ "$(id -un)" = "postgres" ]; then
    if [ "$mode" = "query" ]; then
      printf '%s\n' "$sql" | psql -v ON_ERROR_STOP=1 -q -t -A 2>/dev/null
    else
      printf '%s\n' "$sql" | psql -v ON_ERROR_STOP=1 -q -t -A >/dev/null 2>&1
    fi
  else
    if [ "$mode" = "query" ]; then
      printf '%s\n' "$sql" | psql -v ON_ERROR_STOP=1 -q -t -A 2>/dev/null
    else
      printf '%s\n' "$sql" | psql -v ON_ERROR_STOP=1 -q -t -A >/dev/null 2>&1
    fi
  fi
}

ROLE_EXISTS="$(psql_as_postgres query "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER';" | tr -d '[:space:]' || true)"
if [ "$ROLE_EXISTS" != "1" ]; then
  if ! psql_as_postgres exec "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"; then
    out_json '{"ok":false,"error":"create_role_failed","hint":"need postgres superuser (root+postgres) or pre-create role"}'
    exit 2
  fi
  log "ensure-pg: created role $DB_USER"
else
  if ! psql_as_postgres exec "ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"; then
    log "ensure-pg: alter password skipped/failed (role exists)"
  else
    log "ensure-pg: updated password for role $DB_USER (silent)"
  fi
fi

DB_EXISTS="$(psql_as_postgres query "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" | tr -d '[:space:]' || true)"
if [ "$DB_EXISTS" != "1" ]; then
  if ! psql_as_postgres exec "CREATE DATABASE $DB_NAME OWNER $DB_USER;"; then
    out_json '{"ok":false,"error":"create_db_failed"}'
    exit 2
  fi
  log "ensure-pg: created database $DB_NAME"
fi

export PGPASSWORD="$DB_PASSWORD"
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -q -t -A -c 'SELECT 1' >/dev/null 2>&1; then
  out_json "{\"ok\":false,\"error\":\"app_user_connect_failed\",\"port\":\"$DB_PORT\"}"
  exit 2
fi

export H="$DB_HOST" P="$DB_PORT" N="$DB_NAME" U="$DB_USER" PW="$DB_PASSWORD"
python3 -c 'import json,os; print(json.dumps({"ok":True,"host":os.environ["H"],"port":os.environ["P"],"name":os.environ["N"],"user":os.environ["U"],"password":os.environ["PW"]},separators=(",",":")))'
