#!/bin/sh
set -e
TEMPLATE="${1:?}"
OUTPUT="${2:?}"
: "${FORGEJO_RUN_USER:=forgejo}"
: "${FORGEJO_WORK_DIR:=/var/lib/forgejo}"
: "${FORGEJO_BINARY:?}"
: "${FORGEJO_CONFIG:?}"
# config dir for ReadWritePaths (JWT rewrites)
CONFIG_DIR="$(dirname "$FORGEJO_CONFIG")"
mkdir -p "$(dirname "$OUTPUT")"
sed \
  -e "s|__RUN_USER__|${FORGEJO_RUN_USER}|g" \
  -e "s|__WORK_DIR__|${FORGEJO_WORK_DIR}|g" \
  -e "s|__BINARY__|${FORGEJO_BINARY}|g" \
  -e "s|__CONFIG__|${FORGEJO_CONFIG}|g" \
  -e "s|__CONFIG_DIR__|${CONFIG_DIR}|g" \
  "$TEMPLATE" >"$OUTPUT"
