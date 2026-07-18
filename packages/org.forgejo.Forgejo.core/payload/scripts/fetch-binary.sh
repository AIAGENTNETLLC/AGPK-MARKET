#!/bin/sh
# Fetch official Forgejo linux-amd64.xz, verify sha256, install as $DEST_BIN
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PKG_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
# shellcheck source=/dev/null
. "$PKG_ROOT/DIGESTS"

DEST_BIN="${1:?usage: fetch-binary.sh /path/to/forgejo}"
CACHE_DIR="${FORGEJO_CACHE_DIR:-${TMPDIR:-/tmp}/agpk-forgejo-cache}"
mkdir -p "$CACHE_DIR"
XZ_PATH="$CACHE_DIR/$FORGEJO_ASSET_XZ"

sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

need_fetch=1
if [ -f "$XZ_PATH" ]; then
  got="$(sha256_file "$XZ_PATH")"
  if [ "$got" = "$FORGEJO_SHA256_XZ" ]; then
    need_fetch=0
  fi
fi

if [ "$need_fetch" = 1 ]; then
  echo "fetching $FORGEJO_URL_XZ" >&2
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -o "$XZ_PATH.partial" "$FORGEJO_URL_XZ"
  else
    wget -q -O "$XZ_PATH.partial" "$FORGEJO_URL_XZ"
  fi
  mv "$XZ_PATH.partial" "$XZ_PATH"
fi

got="$(sha256_file "$XZ_PATH")"
if [ "$got" != "$FORGEJO_SHA256_XZ" ]; then
  echo "sha256 mismatch for $XZ_PATH: got $got want $FORGEJO_SHA256_XZ" >&2
  exit 1
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
# decompress xz → binary
if command -v xz >/dev/null 2>&1; then
  xz -dc "$XZ_PATH" >"$tmpdir/forgejo"
elif command -v unxz >/dev/null 2>&1; then
  unxz -c "$XZ_PATH" >"$tmpdir/forgejo"
else
  # python3 lzma fallback
  python3 - "$XZ_PATH" "$tmpdir/forgejo" <<'PY'
import lzma, sys
src, dst = sys.argv[1], sys.argv[2]
with lzma.open(src, "rb") as f, open(dst, "wb") as o:
    o.write(f.read())
PY
fi

gotb="$(sha256_file "$tmpdir/forgejo")"
if [ "$gotb" != "$FORGEJO_SHA256_BIN" ]; then
  echo "sha256 mismatch for decompressed binary: got $gotb want $FORGEJO_SHA256_BIN" >&2
  exit 1
fi

mkdir -p "$(dirname "$DEST_BIN")"
install -m 0755 "$tmpdir/forgejo" "$DEST_BIN"
echo "installed official forgejo $FORGEJO_VERSION -> $DEST_BIN" >&2
