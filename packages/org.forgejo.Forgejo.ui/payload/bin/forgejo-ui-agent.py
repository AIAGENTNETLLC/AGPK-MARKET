#!/usr/bin/env python3
"""Forgejo UI 1.1 — desktop workbench (not launcher-only).

ui_face=desktop_workbench: dedicated shell + local workbench main chain.
forgejo.ui.open remains as explicit launcher (non-primary, labeled).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def out(obj: dict[str, Any], code: int = 0) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    sys.exit(code)


def install_root() -> Path:
    if os.environ.get("AGPK_INSTALL_ROOT"):
        return Path(os.environ["AGPK_INSTALL_ROOT"])
    return Path(__file__).resolve().parents[2]


def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() and k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")


def core_roots() -> list[Path]:
    env = os.environ.get("FORGEJO_CORE_ROOT")
    roots: list[Path] = []
    if env:
        roots.append(Path(env))
    ui = install_root()
    roots.extend(
        [
            ui.parent / "org.forgejo.Forgejo.core",
            Path("/srv/agentnet-data/agpk/org.forgejo.Forgejo.core"),
            Path("/opt/agentx/agpk/org.forgejo.Forgejo.core"),
            Path.home() / ".local/share/agentx/agpk/org.forgejo.Forgejo.core",
        ]
    )
    return roots


def resolve_core() -> tuple[Path | None, str | None]:
    for root in core_roots():
        if not root.is_dir():
            continue
        load_env(root / "service.env")
        url = (
            os.environ.get("AGPK_SERVICE_URL")
            or os.environ.get("FORGEJO_ROOT_URL")
            or "http://127.0.0.1:3000/"
        )
        return root, url.rstrip("/") + "/"
    if os.environ.get("AGPK_SERVICE_URL") or os.environ.get("FORGEJO_ROOT_URL"):
        url = (os.environ.get("AGPK_SERVICE_URL") or os.environ.get("FORGEJO_ROOT_URL") or "").rstrip("/") + "/"
        return None, url
    return None, None


def core_reachable(url: str) -> bool:
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/api/v1/version", timeout=5) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def require_core() -> tuple[Path | None, str]:
    root, url = resolve_core()
    if not url:
        out(
            {
                "ok": False,
                "error": "core_missing",
                "hint": "install org.forgejo.Forgejo.core first",
                "looked": [str(p) for p in core_roots()],
            },
            2,
        )
    return root, url  # type: ignore


def token_from_core(core: Path | None) -> str | None:
    t = os.environ.get("AGPK_API_TOKEN") or os.environ.get("FORGEJO_TOKEN")
    if t:
        return t.strip()
    if core:
        p = core / "secrets" / "agent_token"
        if p.is_file():
            return p.read_text(encoding="utf-8").strip()
    return None


def forge_api(url: str, tok: str | None, method: str, path: str, body: dict | None = None) -> Any:
    data = None if body is None else json.dumps(body).encode()
    headers = {"Accept": "application/json", "Content-Type": "application/json", "User-Agent": "agpk-forgejo-ui/1.1"}
    if tok:
        headers["Authorization"] = f"token {tok}"
    req = urllib.request.Request(url.rstrip("/") + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        out({"ok": False, "http": e.code, "error": raw[:500], "path": path}, 1)


def cmd_url() -> None:
    root, url = require_core()
    out(
        {
            "ok": True,
            "url": url,
            "core_root": str(root) if root else None,
            "core_reachable": core_reachable(url),
            "package_kind": "ui",
            "ui_face": "desktop_workbench",
            "package_version": "1.1.2",
            "depends": "org.forgejo.Forgejo.core",
            "i18n": ["zh", "en", "system"],
        }
    )


def cmd_open_launcher() -> None:
    """Explicit non-primary launcher (system browser). Labeled — not ui parity."""
    root, url = require_core()
    opened = False
    err = None
    for tool in ("xdg-open", "gio", "open"):
        if shutil.which(tool):
            r = subprocess.run([tool, url], capture_output=True, text=True)
            opened = r.returncode == 0
            err = r.stderr.strip() if not opened else None
            break
    out(
        {
            "ok": opened,
            "opened": opened,
            "url": url,
            "core_root": str(root) if root else None,
            "opener_error": err,
            "ui_face": "launcher_only",
            "parity": False,
            "warning": "launcher only — not ui functional parity; use forgejo.ui.workbench.open",
        }
    )


def cmd_workbench_open() -> None:
    """Detach desktop shell — never subprocess.run/wait on WebKit main loop."""
    root, url = require_core()
    if not core_reachable(url):
        out({"ok": False, "error": "core_unreachable", "url": url, "core_root": str(root) if root else None}, 1)
    ui = install_root()
    launch = ui / "payload" / "bin" / "forgejo-desktop-launch.sh"
    if not launch.is_file():
        launch = Path(__file__).resolve().parent / "forgejo-desktop-launch.sh"
    if not launch.is_file():
        out({"ok": False, "error": "launch_script_missing", "path": str(launch)}, 2)
    env = os.environ.copy()
    env["AGPK_INSTALL_ROOT"] = str(ui)
    if root:
        env["FORGEJO_CORE_ROOT"] = str(root)
    # Inherit DISPLAY/WAYLAND/XAUTHORITY/XDG_RUNTIME_DIR from caller session;
    # launch.sh fills defaults. Do NOT block on GUI.
    (ui / "run").mkdir(parents=True, exist_ok=True)
    log = ui / "run" / "workbench-open-agent.log"
    with open(log, "ab") as lf:
        proc = subprocess.Popen(
            ["sh", str(launch)],
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=lf,
            start_new_session=True,
            text=True,
        )
    # Brief wait only for launch script JSON (it exits after detach), not for WebKit.
    try:
        stdout, _ = proc.communicate(timeout=8)
    except subprocess.TimeoutExpired:
        # Launch should have returned; if still running, treat as detached ok
        out(
            {
                "ok": True,
                "detached": True,
                "pid": proc.pid,
                "note": "launch still running; GUI shell detached",
                "ui_face": "desktop_workbench",
                "core_url": url,
                "log": str(log),
            }
        )
        return
    body: dict[str, Any]
    try:
        # last JSON line
        line = [ln for ln in (stdout or "").splitlines() if ln.strip().startswith("{")]
        body = json.loads(line[-1]) if line else {"raw_stdout": (stdout or "")[:400]}
    except Exception:
        body = {"raw_stdout": (stdout or "")[:400]}
    if proc.returncode not in (0, None) and not body.get("ok"):
        out({**body, "ok": False, "rc": proc.returncode, "ui_face": "desktop_workbench", "log": str(log)}, 1)
    out(
        {
            **body,
            "ok": True,
            "detached": True,
            "ui_face": "desktop_workbench",
            "core_url": url,
            "parity_claim": "desktop_main_chain_shell",
            "log": str(log),
        }
    )


def cmd_workbench_status() -> None:
    root, url = require_core()
    run = install_root() / "run"
    port = (run / "workbench.port").read_text().strip() if (run / "workbench.port").is_file() else None
    wb_url = (run / "workbench.url").read_text().strip() if (run / "workbench.url").is_file() else None
    wb_ok = False
    if port:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/local/status", timeout=2) as resp:
                wb_ok = resp.status == 200
        except Exception:
            wb_ok = False
    out(
        {
            "ok": True,
            "core_url": url,
            "core_reachable": core_reachable(url),
            "workbench_port": port,
            "workbench_url": wb_url,
            "workbench_up": wb_ok,
            "ui_face": "desktop_workbench",
            "package_version": "1.1.2",
            "i18n": ["zh", "en", "system"],
        }
    )


def cmd_repo_list(args: dict[str, Any]) -> None:
    root, url = require_core()
    tok = token_from_core(root)
    if not tok:
        out({"ok": False, "error": "token_missing", "hint": "core forgejo.token.ensure"}, 2)
    data = forge_api(url, tok, "GET", "/api/v1/user/repos?limit=50")
    out({"ok": True, "repos": data, "source": "core_api", "ui_face": "desktop_workbench"})


def cmd_repo_create(args: dict[str, Any]) -> None:
    root, url = require_core()
    tok = token_from_core(root)
    if not tok:
        out({"ok": False, "error": "token_missing"}, 2)
    name = args.get("name") or args.get("repo")
    if not name:
        out({"ok": False, "error": "name_required"}, 2)
    private = args.get("private", True)
    if isinstance(private, str):
        private = private.lower() in ("1", "true", "yes")
    payload = {
        "name": name,
        "description": args.get("description") or "",
        "private": bool(private),
        "auto_init": True,
        "default_branch": args.get("default_branch") or "main",
    }
    data = forge_api(url, tok, "POST", "/api/v1/user/repos", payload)
    out({"ok": True, "repo": data, "source": "core_api", "ui_face": "desktop_workbench"})


def desktop_path() -> Path:
    base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local/share"))
    return base / "applications" / "forgejo-agentos.desktop"


def cmd_desktop_install() -> None:
    root, url = require_core()
    ui = install_root()
    launch = ui / "payload" / "bin" / "forgejo-desktop-launch.sh"
    if not launch.is_file():
        launch = Path(__file__).resolve().parent / "forgejo-desktop-launch.sh"
    launch.chmod(0o755)
    core_s = str(root) if root else ""
    # Desktop entry MUST call shell launcher (Wayland/Xauth), not raw python shell.
    text = f"""[Desktop Entry]
Type=Application
Name=Forgejo Workbench (AgentOS)
Name[zh_CN]=Forgejo 工作台 (AgentOS)
Name[zh]=Forgejo 工作台 (AgentOS)
Comment=AgentOS Forgejo desktop workbench — depends core; follows system language
Comment[zh_CN]=AgentOS Forgejo 桌面工作台 — 依赖 core；界面随系统语言
Comment[zh]=AgentOS Forgejo 桌面工作台 — 依赖 core；界面随系统语言
Exec=env AGPK_INSTALL_ROOT={ui} FORGEJO_CORE_ROOT={core_s} {launch}
Icon=utilities-terminal
Terminal=false
Categories=Development;RevisionControl;
StartupWMClass=ForgejoAgentOS
"""
    path = desktop_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o644)
    out(
        {
            "ok": True,
            "desktop": str(path),
            "exec": str(launch),
            "ui_face": "desktop_workbench",
            "core_url": url,
            "note": "desktop uses forgejo-desktop-launch.sh (Wayland/Xauth); agent workbench.open detaches",
        }
    )


def cmd_desktop_remove() -> None:
    path = desktop_path()
    if path.is_file():
        path.unlink()
        out({"ok": True, "removed": str(path)})
    out({"ok": True, "removed": None, "note": "not_present"})


def cmd_projection() -> None:
    root, url = require_core()
    run = install_root() / "run"
    wb = (run / "workbench.url").read_text().strip() if (run / "workbench.url").is_file() else None
    out(
        {
            "ok": True,
            "projection": {
                "kind": "desktop_workbench",
                "title": "Forgejo Workbench",
                "workbench_url": wb,
                "core_url": url,
                "depends_package": "org.forgejo.Forgejo.core",
                "core_installed": root is not None and root.is_dir(),
                "core_reachable": core_reachable(url),
                "ui_face": "desktop_workbench",
                "not": "launcher_only",
            },
            "package_kind": "ui",
            "package_version": "1.1.2",
            "i18n": ["zh", "en", "system"],
        }
    )


def main() -> None:
    load_env(install_root() / "service.env")
    if len(sys.argv) < 2:
        out({"ok": False, "error": "usage"}, 2)
    cmd = sys.argv[1]
    args: dict[str, Any] = {}
    if len(sys.argv) > 2 and sys.argv[2]:
        args = json.loads(sys.argv[2])
    if os.environ.get("AGPK_INVOKE_ARGS"):
        args = {**args, **json.loads(os.environ["AGPK_INVOKE_ARGS"])}
    table = {
        "forgejo.ui.url": cmd_url,
        "forgejo.ui.open": cmd_open_launcher,
        "forgejo.ui.workbench.open": cmd_workbench_open,
        "forgejo.ui.workbench.status": cmd_workbench_status,
        "forgejo.ui.repo.list": lambda: cmd_repo_list(args),
        "forgejo.ui.repo.create": lambda: cmd_repo_create(args),
        "forgejo.ui.desktop.install": cmd_desktop_install,
        "forgejo.ui.desktop.remove": cmd_desktop_remove,
        "forgejo.ui.projection.info": cmd_projection,
    }
    if cmd in table:
        table[cmd]()
    out({"ok": False, "error": f"unknown:{cmd}"}, 1)


if __name__ == "__main__":
    main()
