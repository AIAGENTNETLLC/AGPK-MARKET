#!/bin/sh
# Process driver entry for org.forgejo.Forgejo.core
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
# package root: .../payload/bin -> .../
ROOT="$(cd "$HERE/../.." && pwd)"
# When installed via INSTALL, structure is $AGPK_INSTALL_ROOT/{payload/bin,service.env}
if [ -n "${AGPK_INSTALL_ROOT:-}" ]; then
  ROOT="$AGPK_INSTALL_ROOT"
  HERE="$ROOT/payload/bin"
fi
export AGPK_INSTALL_ROOT="$ROOT"
if [ -f "$ROOT/service.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/service.env"
  set +a
fi
CMD="${1:-}"
shift || true
ARGS="${AGPK_INVOKE_ARGS:-}"
if [ -z "$ARGS" ]; then
  if [ "$#" -gt 0 ]; then
    ARGS="$1"
  else
    ARGS='{}'
  fi
fi
exec python3 "$HERE/forgejo-agent.py" "$CMD" "$ARGS"
