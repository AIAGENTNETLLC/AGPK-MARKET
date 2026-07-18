#!/bin/sh
# Probe local PostgreSQL port. Prints a single port number on stdout only.
# Order: FORGEJO_DB_PORT (if set) → 5433 (AgentOS common) → 5432 → 5434.
set -e
HOST="${FORGEJO_DB_HOST:-127.0.0.1}"

if [ -n "${FORGEJO_DB_PORT:-}" ]; then
  printf '%s\n' "$FORGEJO_DB_PORT"
  exit 0
fi

if ! command -v pg_isready >/dev/null 2>&1; then
  printf '%s\n' "5432"
  exit 0
fi

for p in 5433 5432 5434; do
  if pg_isready -h "$HOST" -p "$p" -q 2>/dev/null; then
    printf '%s\n' "probe-pg-port: detected $HOST:$p" >&2
    printf '%s\n' "$p"
    exit 0
  fi
done

# no live port — default AgentOS-oriented 5433 so error messages match host habit
printf '%s\n' "probe-pg-port: no pg_isready hit; defaulting 5433 (set FORGEJO_DB_PORT to override)" >&2
printf '%s\n' "5433"
