#!/bin/sh
# Desktop entry / agent workbench launcher.
# - Sets Wayland/X11 session env correctly
# - Detaches GUI shell from caller (never block parent on WebKit main loop)
set -e

HERE="$(cd "$(dirname "$0")" && pwd)"
# package root: .../payload/bin -> ...
if [ -n "${AGPK_INSTALL_ROOT:-}" ]; then
  ROOT="$AGPK_INSTALL_ROOT"
  HERE="$ROOT/payload/bin"
else
  ROOT="$(cd "$HERE/../.." && pwd)"
  export AGPK_INSTALL_ROOT="$ROOT"
fi

if [ -f "$ROOT/service.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . "$ROOT/service.env"
  set +a
fi

mkdir -p "$ROOT/run"
LOG="$ROOT/run/desktop-shell.log"

# --- Session display / auth (critical for .desktop / agent from TTY) ---
# Prefer existing session vars; fill common defaults only when missing.
if [ -z "${XDG_RUNTIME_DIR:-}" ] && [ -d "/run/user/$(id -u)" ]; then
  export XDG_RUNTIME_DIR="/run/user/$(id -u)"
fi

# X11
if [ -n "${DISPLAY:-}" ]; then
  if [ -z "${XAUTHORITY:-}" ]; then
    if [ -f "${HOME:-}/.Xauthority" ]; then
      export XAUTHORITY="${HOME}/.Xauthority"
    elif [ -n "${XDG_RUNTIME_DIR:-}" ] && [ -f "${XDG_RUNTIME_DIR}/.mutter-Xwaylandauth."* ] 2>/dev/null; then
      # best-effort: leave empty if glob fails
      :
    fi
  fi
  # If still empty, try standard paths
  if [ -z "${XAUTHORITY:-}" ] && [ -f "${HOME:-}/.Xauthority" ]; then
    export XAUTHORITY="${HOME}/.Xauthority"
  fi
fi

# Wayland
if [ -z "${WAYLAND_DISPLAY:-}" ] && [ -n "${XDG_RUNTIME_DIR:-}" ]; then
  if [ -S "${XDG_RUNTIME_DIR}/wayland-0" ]; then
    export WAYLAND_DISPLAY=wayland-0
  elif [ -S "${XDG_RUNTIME_DIR}/wayland-1" ]; then
    export WAYLAND_DISPLAY=wayland-1
  fi
fi

# GTK: prefer Wayland when available, fall back to X11
if [ -n "${WAYLAND_DISPLAY:-}" ] && [ -z "${GDK_BACKEND:-}" ]; then
  export GDK_BACKEND=wayland,x11
elif [ -n "${DISPLAY:-}" ] && [ -z "${GDK_BACKEND:-}" ]; then
  export GDK_BACKEND=x11,wayland
fi

# DBus session (desktop portals / some WebKit paths)
if [ -z "${DBUS_SESSION_BUS_ADDRESS:-}" ] && [ -n "${XDG_RUNTIME_DIR:-}" ] && [ -S "${XDG_RUNTIME_DIR}/bus" ]; then
  export DBUS_SESSION_BUS_ADDRESS="unix:path=${XDG_RUNTIME_DIR}/bus"
fi

export PYTHONUNBUFFERED=1

SHELL_PY="$HERE/forgejo-desktop-shell.py"
if [ ! -f "$SHELL_PY" ]; then
  echo "forgejo-desktop-launch: missing $SHELL_PY" >&2
  exit 2
fi

# When already re-exec'd as GUI child, run shell in foreground (WebKit blocks here).
if [ "${FORGEJO_UI_SHELL_FOREGROUND:-0}" = "1" ]; then
  exec python3 "$SHELL_PY"
fi

# Detach GUI from parent (agent / desktop starter must not wait for WebKit).
# Double-fork style via start_new_session equivalent: setsid if available.
export FORGEJO_UI_SHELL_FOREGROUND=1
if command -v setsid >/dev/null 2>&1; then
  setsid -f env FORGEJO_UI_SHELL_FOREGROUND=1 \
    AGPK_INSTALL_ROOT="$AGPK_INSTALL_ROOT" \
    FORGEJO_CORE_ROOT="${FORGEJO_CORE_ROOT:-}" \
    DISPLAY="${DISPLAY:-}" \
    WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}" \
    XAUTHORITY="${XAUTHORITY:-}" \
    XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-}" \
    DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-}" \
    GDK_BACKEND="${GDK_BACKEND:-}" \
    python3 "$SHELL_PY" >>"$LOG" 2>&1
else
  # nohup fallback
  nohup env FORGEJO_UI_SHELL_FOREGROUND=1 \
    AGPK_INSTALL_ROOT="$AGPK_INSTALL_ROOT" \
    FORGEJO_CORE_ROOT="${FORGEJO_CORE_ROOT:-}" \
    DISPLAY="${DISPLAY:-}" \
    WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-}" \
    XAUTHORITY="${XAUTHORITY:-}" \
    XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-}" \
    DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-}" \
    GDK_BACKEND="${GDK_BACKEND:-}" \
    python3 "$SHELL_PY" >>"$LOG" 2>&1 &
fi

# Emit JSON for agent callers (launch script returns immediately after detach)
python3 -c "
import json, os
print(json.dumps({
  'ok': True,
  'detached': True,
  'shell': 'forgejo-desktop-launch.sh',
  'ui_face': 'desktop_workbench',
  'log': '''$LOG''',
  'display': os.environ.get('DISPLAY'),
  'wayland': os.environ.get('WAYLAND_DISPLAY'),
  'xauthority': bool(os.environ.get('XAUTHORITY')),
  'xdg_runtime_dir': os.environ.get('XDG_RUNTIME_DIR'),
}, ensure_ascii=False))
"
exit 0
