#!/usr/bin/env python3
"""Local workbench HTTP server: static UI + token-bearing proxy to core Forgejo API.

Token stays server-side. Human main chain does not require typing URL in system browser.
"""
from __future__ import annotations

import json
import os
import signal
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k:
            os.environ.setdefault(k, v)


def ui_root() -> Path:
    if os.environ.get("AGPK_INSTALL_ROOT"):
        return Path(os.environ["AGPK_INSTALL_ROOT"])
    return Path(__file__).resolve().parents[2]


def core_root() -> Path | None:
    env = os.environ.get("FORGEJO_CORE_ROOT")
    if env and Path(env).is_dir():
        return Path(env)
    cand = ui_root().parent / "org.forgejo.Forgejo.core"
    if cand.is_dir():
        return cand
    for p in (
        Path("/opt/agentx/agpk/org.forgejo.Forgejo.core"),
        Path("/srv/agentnet-data/agpk/org.forgejo.Forgejo.core"),
    ):
        if p.is_dir():
            return p
    return None


def core_url() -> str:
    u = os.environ.get("AGPK_SERVICE_URL") or os.environ.get("FORGEJO_ROOT_URL")
    if u:
        return u.rstrip("/") + "/"
    return "http://127.0.0.1:3000/"


def token() -> str | None:
    t = os.environ.get("AGPK_API_TOKEN") or os.environ.get("FORGEJO_TOKEN")
    if t:
        return t.strip()
    cr = core_root()
    if cr:
        for p in (cr / "secrets" / "agent_token", cr / "agent_token"):
            if p.is_file():
                return p.read_text(encoding="utf-8").strip()
    return None


def forge_api(method: str, path: str, body: bytes | None = None) -> tuple[int, bytes, str]:
    base = core_url().rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    url = base + path
    headers = {
        "Accept": "application/json",
        "User-Agent": "agpk-forgejo-workbench/1.1",
    }
    tok = token()
    if tok:
        headers["Authorization"] = f"token {tok}"
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read(), resp.headers.get("Content-Type", "application/json")
    except urllib.error.HTTPError as e:
        return e.code, e.read(), e.headers.get("Content-Type", "application/json") if e.headers else "application/json"
    except Exception as e:
        return 502, json.dumps({"error": str(e)}).encode(), "application/json"


STATIC_DIR = Path(__file__).resolve().parents[1] / "workbench" / "static"
# installed layout
if not STATIC_DIR.is_dir():
    STATIC_DIR = ui_root() / "payload" / "workbench" / "static"


class Handler(BaseHTTPRequestHandler):
    server_version = "ForgejoWorkbench/1.1"

    def log_message(self, fmt: str, *args) -> None:  # quieter
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, ctype: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path in ("/", "/workbench", "/workbench/"):
            self._serve_static("/index.html")
            return
        if path.startswith("/workbench/"):
            rel = path[len("/workbench") :]  # /app.js or /index.html
            if rel in ("", "/"):
                rel = "/index.html"
            self._serve_static(rel)
            return
        if path.startswith("/static/"):
            self._serve_static(path[len("/static") :])
            return
        if path in ("/app.js", "/index.html"):
            self._serve_static(path)
            return
        if path == "/api/local/status":
            cr = core_root()
            if cr:
                load_env(cr / "service.env")
            url = core_url()
            reachable = False
            detail = None
            try:
                code, raw, _ = forge_api("GET", "/api/v1/version")
                reachable = 200 <= code < 300
                if not reachable:
                    detail = raw.decode(errors="replace")[:200]
            except Exception as e:
                detail = str(e)
            # system locale for UI i18n (FORGEJO_UI_LANG > LANG/LC_ALL)
            sys_loc = (
                os.environ.get("FORGEJO_UI_LANG")
                or os.environ.get("LC_ALL")
                or os.environ.get("LC_MESSAGES")
                or os.environ.get("LANG")
                or ""
            )
            body = json.dumps(
                {
                    "ok": True,
                    "core_url": url,
                    "core_root": str(cr) if cr else None,
                    "core_reachable": reachable,
                    "has_token": bool(token()),
                    "detail": detail,
                    "ui_face": "desktop_workbench",
                    "package_version": "1.1.2",
                    "system_locale": sys_loc,
                    "locales": ["zh", "en"],
                }
            ).encode()
            self._send(200, body)
            return
        if path.startswith("/api/proxy/"):
            rel = path[len("/api/proxy") :]
            # map to forge /api/v1
            if not rel.startswith("/api/"):
                rel = "/api/v1" + rel
            code, raw, ctype = forge_api("GET", rel + (("?" + parsed.query) if parsed.query else ""))
            self._send(code, raw, ctype or "application/json")
            return
        self._send(404, b'{"error":"not_found"}')

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        if path.startswith("/api/proxy/"):
            rel = path[len("/api/proxy") :]
            if not rel.startswith("/api/"):
                rel = "/api/v1" + rel
            code, raw, ctype = forge_api("POST", rel, body)
            self._send(code, raw, ctype or "application/json")
            return
        self._send(404, b'{"error":"not_found"}')

    def _serve_static(self, rel: str) -> None:
        rel = rel.split("?", 1)[0]
        if ".." in rel:
            self._send(400, b"bad path")
            return
        if not rel.startswith("/"):
            rel = "/" + rel
        fp = STATIC_DIR / rel.lstrip("/")
        if not fp.is_file():
            self._send(404, b"missing " + rel.encode())
            return
        data = fp.read_bytes()
        ctype = "text/plain"
        if rel.endswith(".html"):
            ctype = "text/html; charset=utf-8"
        elif rel.endswith(".js"):
            ctype = "application/javascript; charset=utf-8"
        elif rel.endswith(".css"):
            ctype = "text/css; charset=utf-8"
        self._send(200, data, ctype)


def write_pid(port: int) -> None:
    root = ui_root()
    (root / "run").mkdir(parents=True, exist_ok=True)
    (root / "run" / "workbench.pid").write_text(str(os.getpid()) + "\n", encoding="utf-8")
    (root / "run" / "workbench.port").write_text(str(port) + "\n", encoding="utf-8")
    (root / "run" / "workbench.url").write_text(f"http://127.0.0.1:{port}/workbench/\n", encoding="utf-8")


def main() -> None:
    root = ui_root()
    load_env(root / "service.env")
    cr = core_root()
    if cr:
        load_env(cr / "service.env")
        os.environ.setdefault("FORGEJO_CORE_ROOT", str(cr))
    port = int(os.environ.get("FORGEJO_WORKBENCH_PORT") or "17890")
    host = os.environ.get("FORGEJO_WORKBENCH_HOST") or "127.0.0.1"
    httpd = ThreadingHTTPServer((host, port), Handler)
    write_pid(port)
    print(json.dumps({"ok": True, "url": f"http://{host}:{port}/workbench/", "port": port}), flush=True)

    def _stop(*_a):
        threading.Thread(target=httpd.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
