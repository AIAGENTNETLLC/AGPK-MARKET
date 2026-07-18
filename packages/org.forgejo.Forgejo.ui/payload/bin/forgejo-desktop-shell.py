#!/usr/bin/env python3
"""Dedicated desktop window for Forgejo workbench.

Priority:
  1) WebKit2GTK (python3-gi) — true embedded WebView
  2) Chromium/Chrome/Edge --app= — dedicated app window (not system browser tab via xdg-open)
Never uses xdg-open as primary path for workbench.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def out(obj: dict, code: int = 0) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    sys.exit(code)


def ui_root() -> Path:
    if os.environ.get("AGPK_INSTALL_ROOT"):
        return Path(os.environ["AGPK_INSTALL_ROOT"])
    return Path(__file__).resolve().parents[2]


def ensure_server() -> str:
    root = ui_root()
    port_file = root / "run" / "workbench.port"
    url_file = root / "run" / "workbench.url"
    # health check existing
    if port_file.is_file():
        port = port_file.read_text().strip()
        url = f"http://127.0.0.1:{port}/workbench/"
        try:
            with urllib.request.urlopen(url.replace("/workbench/", "/api/local/status"), timeout=2):
                return url
        except Exception:
            pass
    # start server
    server = root / "payload" / "bin" / "forgejo-workbench-server.py"
    if not server.is_file():
        server = Path(__file__).resolve().parent / "forgejo-workbench-server.py"
    log = root / "run" / "workbench-server.log"
    (root / "run").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["AGPK_INSTALL_ROOT"] = str(root)
    with open(log, "ab") as lf:
        subprocess.Popen(
            [sys.executable, str(server)],
            env=env,
            stdout=lf,
            stderr=lf,
            start_new_session=True,
        )
    for _ in range(40):
        time.sleep(0.15)
        if url_file.is_file():
            url = url_file.read_text().strip()
            try:
                with urllib.request.urlopen(url.replace("/workbench/", "/api/local/status"), timeout=1):
                    return url
            except Exception:
                continue
    out({"ok": False, "error": "workbench_server_start_failed", "log": str(log)}, 1)
    return ""


def open_webkit(url: str) -> bool:
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        gi.require_version("WebKit2", "4.0")
        from gi.repository import Gtk, WebKit2  # type: ignore
    except Exception:
        try:
            import gi

            gi.require_version("Gtk", "3.0")
            gi.require_version("WebKit2", "4.1")
            from gi.repository import Gtk, WebKit2  # type: ignore
        except Exception:
            return False

    # Window title follows system locale (zh* → 中文)
    loc = (
        os.environ.get("FORGEJO_UI_LANG")
        or os.environ.get("LC_ALL")
        or os.environ.get("LANG")
        or ""
    ).lower()
    title = "Forgejo 工作台 · AgentOS" if loc.startswith("zh") else "Forgejo Workbench · AgentOS"
    win = Gtk.Window(title=title)
    win.set_default_size(1200, 800)
    win.connect("destroy", Gtk.main_quit)
    view = WebKit2.WebView()
    view.load_uri(url)
    win.add(view)
    win.show_all()
    Gtk.main()
    return True


def open_chromium_app(url: str) -> tuple[bool, str | None]:
    candidates = [
        "chromium-browser",
        "chromium",
        "google-chrome",
        "google-chrome-stable",
        "microsoft-edge",
        "brave-browser",
    ]
    bin_path = None
    for c in candidates:
        p = shutil.which(c)
        if p:
            bin_path = p
            break
    # AgentOS browser binary env
    for envk in ("AGENTX_BROWSER_BINARY", "CHROME_BIN", "CHROMIUM_BIN"):
        if os.environ.get(envk) and Path(os.environ[envk]).is_file():
            bin_path = os.environ[envk]
            break
    if not bin_path:
        return False, "no_chromium_family"
    profile = ui_root() / "run" / "chromium-app-profile"
    profile.mkdir(parents=True, exist_ok=True)
    argv = [
        bin_path,
        f"--app={url}",
        f"--user-data-dir={profile}",
        "--class=ForgejoAgentOS",
        "--no-first-run",
        "--disable-extensions",
    ]
    subprocess.Popen(argv, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True, bin_path


def main() -> None:
    url = ensure_server()
    # 1 WebKit
    if os.environ.get("FORGEJO_UI_FORCE_SHELL") in (None, "", "webkit", "auto"):
        # WebKit runs blocking main loop — only if DISPLAY set
        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            try:
                if open_webkit(url):
                    out({"ok": True, "shell": "webkit2gtk", "url": url, "ui_face": "desktop_workbench"})
            except Exception as e:
                # fall through
                webkit_err = str(e)
            else:
                webkit_err = None
        else:
            webkit_err = "no_display"
    else:
        webkit_err = "skipped"

    if os.environ.get("FORGEJO_UI_FORCE_SHELL") in (None, "", "chromium", "auto", "chrome"):
        ok, detail = open_chromium_app(url)
        if ok:
            out(
                {
                    "ok": True,
                    "shell": "chromium_app",
                    "binary": detail,
                    "url": url,
                    "ui_face": "desktop_workbench",
                    "note": "dedicated --app window; not xdg-open system browser primary path",
                }
            )

    out(
        {
            "ok": False,
            "error": "no_dedicated_desktop_shell",
            "url": url,
            "webkit": webkit_err,
            "hint": "install python3-gi gir1.2-webkit2-4.0/4.1 or chromium; DISPLAY required for GUI",
            "ui_face": "desktop_workbench",
            "forbidden_primary": "xdg-open",
        },
        1,
    )


if __name__ == "__main__":
    main()
