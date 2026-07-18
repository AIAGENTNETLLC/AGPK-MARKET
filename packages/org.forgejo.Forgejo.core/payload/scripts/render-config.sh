#!/bin/sh
set -e
TEMPLATE="${1:?template}"
OUTPUT="${2:?output}"
# env substitutions
: "${FORGEJO_RUN_USER:=forgejo}"
: "${FORGEJO_WORK_DIR:=/var/lib/forgejo}"
: "${FORGEJO_HTTP_ADDR:=127.0.0.1}"
: "${FORGEJO_HTTP_PORT:=3000}"
: "${FORGEJO_ROOT_URL:=http://${FORGEJO_HTTP_ADDR}:${FORGEJO_HTTP_PORT}/}"
: "${FORGEJO_DB_HOST:=127.0.0.1}"
: "${FORGEJO_DB_PORT:=5432}"
: "${FORGEJO_DB_NAME:=forgejo}"
: "${FORGEJO_DB_USER:=forgejo}"
: "${FORGEJO_DB_PASSWORD:?FORGEJO_DB_PASSWORD required}"
: "${FORGEJO_SECRET_KEY:?}"
: "${FORGEJO_INTERNAL_TOKEN:?}"
: "${FORGEJO_JWT_SECRET:?}"

mkdir -p "$(dirname "$OUTPUT")"
sed \
  -e "s|__RUN_USER__|${FORGEJO_RUN_USER}|g" \
  -e "s|__WORK_DIR__|${FORGEJO_WORK_DIR}|g" \
  -e "s|__HTTP_ADDR__|${FORGEJO_HTTP_ADDR}|g" \
  -e "s|__HTTP_PORT__|${FORGEJO_HTTP_PORT}|g" \
  -e "s|__ROOT_URL__|${FORGEJO_ROOT_URL}|g" \
  -e "s|__DB_HOST__|${FORGEJO_DB_HOST}|g" \
  -e "s|__DB_PORT__|${FORGEJO_DB_PORT}|g" \
  -e "s|__DB_NAME__|${FORGEJO_DB_NAME}|g" \
  -e "s|__DB_USER__|${FORGEJO_DB_USER}|g" \
  -e "s|__DB_PASSWORD__|${FORGEJO_DB_PASSWORD}|g" \
  -e "s|__SECRET_KEY__|${FORGEJO_SECRET_KEY}|g" \
  -e "s|__INTERNAL_TOKEN__|${FORGEJO_INTERNAL_TOKEN}|g" \
  -e "s|__JWT_SECRET__|${FORGEJO_JWT_SECRET}|g" \
  "$TEMPLATE" >"$OUTPUT"
# Forgejo may rewrite secrets (JWT etc.) — run user must own the file
chmod 0600 "$OUTPUT" 2>/dev/null || true
