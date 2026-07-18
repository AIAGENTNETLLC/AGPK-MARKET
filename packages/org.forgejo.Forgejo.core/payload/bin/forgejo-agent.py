#!/usr/bin/env python3
"""Forgejo AGPK core agent surface — real HTTP API + systemd/pg helpers. No mock success."""
from __future__ import annotations

import json
import os
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


def load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def install_root() -> Path:
    raw = os.environ.get("AGPK_INSTALL_ROOT")
    if raw:
        return Path(raw)
    # driver places us under payload/bin
    return Path(__file__).resolve().parents[2]


def base_url() -> str:
    u = (
        os.environ.get("AGPK_SERVICE_URL")
        or os.environ.get("FORGEJO_ROOT_URL")
        or os.environ.get("FORGEJO_URL")
    )
    if not u:
        addr = os.environ.get("FORGEJO_HTTP_ADDR", "127.0.0.1")
        port = os.environ.get("FORGEJO_HTTP_PORT", "3000")
        u = f"http://{addr}:{port}/"
    return u.rstrip("/")


def token() -> str | None:
    t = os.environ.get("AGPK_API_TOKEN") or os.environ.get("FORGEJO_TOKEN")
    if t:
        return t.strip()
    root = install_root()
    for p in (root / "secrets" / "agent_token", root / "agent_token"):
        if p.is_file():
            return p.read_text(encoding="utf-8").strip()
    return None


def unit_name() -> str:
    return os.environ.get("FORGEJO_SYSTEMD_UNIT", "forgejo.service")


def binary_path() -> str:
    b = os.environ.get("FORGEJO_BINARY")
    if b and Path(b).is_file():
        return b
    root = install_root()
    cand = root / "bin" / "forgejo"
    if cand.is_file():
        return str(cand)
    which = subprocess.run(["command", "-v", "forgejo"], capture_output=True, text=True)
    # command -v via shell
    r = subprocess.run(["sh", "-c", "command -v forgejo"], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    return str(cand)


def run_cmd(argv: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def systemctl(*args: str) -> subprocess.CompletedProcess[str]:
    return run_cmd(["systemctl", *args], timeout=120)


def api(
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    *,
    auth: bool = True,
    timeout: int = 30,
) -> tuple[int, Any]:
    url = base_url() + path
    data = None if body is None else json.dumps(body).encode()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "agpk-forgejo-core/1.0",
    }
    if auth:
        tok = token()
        if not tok:
            out(
                {
                    "ok": False,
                    "error": "token_missing",
                    "hint": "set AGPK_API_TOKEN or secrets/agent_token; run forgejo.token.ensure after install",
                },
                2,
            )
        headers["Authorization"] = f"token {tok}"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode() or "null"
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, {"raw": raw[:2000]}
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            j = json.loads(raw)
        except Exception:
            j = {"raw": raw[:500]}
        out({"ok": False, "http": e.code, "error": j, "path": path}, 1)
    except urllib.error.URLError as e:
        out({"ok": False, "error": "unreachable", "detail": str(e.reason), "url": url}, 1)


def cmd_service(action: str, args: dict[str, Any]) -> None:
    unit = unit_name()
    if action == "status":
        st = systemctl("is-active", unit)
        show = systemctl("show", unit, "-p", "MainPID", "-p", "ActiveState", "-p", "SubState", "--value")
        api_ok = False
        version: Any = None
        try:
            url = base_url() + "/api/v1/version"
            with urllib.request.urlopen(url, timeout=5) as resp:
                api_ok = True
                version = json.loads(resp.read().decode() or "null")
        except Exception as e:
            version = {"error": str(e)}
        out(
            {
                "ok": st.returncode == 0 or st.stdout.strip() in ("active", "activating"),
                "unit": unit,
                "is_active": st.stdout.strip(),
                "is_active_rc": st.returncode,
                "show": show.stdout.strip(),
                "api_reachable": api_ok,
                "api_version": version,
                "base_url": base_url(),
            }
        )
    if action in ("start", "stop", "restart", "enable", "disable"):
        if action == "enable":
            r = systemctl("enable", "--now", unit)
        elif action == "disable":
            r = systemctl("disable", "--now", unit)
        else:
            r = systemctl(action, unit)
        if r.returncode != 0:
            out(
                {
                    "ok": False,
                    "error": "systemctl_failed",
                    "action": action,
                    "stderr": r.stderr.strip(),
                    "stdout": r.stdout.strip(),
                    "rc": r.returncode,
                    "hint": "requires root and installed unit",
                },
                1,
            )
        if action in ("start", "restart", "enable"):
            # wait for API
            import time

            last = None
            for _ in range(30):
                try:
                    with urllib.request.urlopen(base_url() + "/api/v1/version", timeout=2) as resp:
                        last = json.loads(resp.read().decode() or "null")
                        out({"ok": True, "action": action, "unit": unit, "api_version": last})
                except Exception as e:
                    last = str(e)
                    time.sleep(1)
            out({"ok": False, "action": action, "error": "api_timeout", "last": last}, 1)
        out({"ok": True, "action": action, "unit": unit})
    if action == "logs":
        n = int(args.get("n") or args.get("lines") or 50)
        r = run_cmd(["journalctl", "-u", unit, "-n", str(n), "--no-pager"], timeout=30)
        out(
            {
                "ok": r.returncode == 0,
                "unit": unit,
                "lines": r.stdout.splitlines()[-n:],
                "stderr": r.stderr.strip() if r.returncode else None,
            },
            0 if r.returncode == 0 else 1,
        )
    out({"ok": False, "error": f"unknown_service_action:{action}"}, 1)


def cmd_health() -> None:
    try:
        with urllib.request.urlopen(base_url() + "/api/v1/version", timeout=10) as resp:
            body = json.loads(resp.read().decode() or "null")
            out({"ok": True, "http": resp.status, "base_url": base_url(), "version": body})
    except Exception as e:
        out({"ok": False, "error": "health_failed", "detail": str(e), "base_url": base_url()}, 1)


def cmd_version() -> None:
    b = binary_path()
    bin_ver = None
    if Path(b).is_file():
        r = run_cmd([b, "--version"], timeout=10)
        bin_ver = (r.stdout or r.stderr).strip()
    try:
        with urllib.request.urlopen(base_url() + "/api/v1/version", timeout=10) as resp:
            api_ver = json.loads(resp.read().decode() or "null")
            api_ok = True
    except Exception as e:
        api_ver = str(e)
        api_ok = False
    out(
        {
            "ok": bool(bin_ver or api_ok),
            "binary": b,
            "binary_version": bin_ver,
            "api_ok": api_ok,
            "api_version": api_ver,
            "pinned_env": os.environ.get("FORGEJO_VERSION"),
        },
        0 if (bin_ver or api_ok) else 1,
    )


def cmd_db_ping() -> None:
    host = os.environ.get("FORGEJO_DB_HOST", "127.0.0.1")
    port = os.environ.get("FORGEJO_DB_PORT", "5432")
    name = os.environ.get("FORGEJO_DB_NAME", "forgejo")
    user = os.environ.get("FORGEJO_DB_USER", "forgejo")
    password = os.environ.get("FORGEJO_DB_PASSWORD", "")
    if not password:
        # try service.env already loaded
        secrets = install_root() / "secrets" / "db_password"
        if secrets.is_file():
            password = secrets.read_text(encoding="utf-8").strip()
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    r = subprocess.run(
        ["psql", "-h", host, "-p", str(port), "-U", user, "-d", name, "-tAc", "SELECT 1"],
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
    )
    ok = r.returncode == 0 and r.stdout.strip() == "1"
    out(
        {
            "ok": ok,
            "host": host,
            "port": port,
            "name": name,
            "user": user,
            "stderr": r.stderr.strip() if not ok else None,
        },
        0 if ok else 1,
    )


def cmd_user_list() -> None:
    code, body = api("GET", "/api/v1/admin/users?limit=50")
    out({"ok": True, "http": code, "users": body})


def cmd_user_create(args: dict[str, Any]) -> None:
    username = args.get("username") or args.get("user")
    email = args.get("email")
    password = args.get("password")
    if not username or not email:
        out({"ok": False, "error": "username_and_email_required"}, 2)
    if not password:
        import secrets

        password = secrets.token_urlsafe(16)
    payload = {
        "username": username,
        "email": email,
        "password": password,
        "must_change_password": bool(args.get("must_change_password", False)),
        "send_notify": False,
    }
    if args.get("admin"):
        payload["admin"] = True
    code, body = api("POST", "/api/v1/admin/users", payload)
    out(
        {
            "ok": True,
            "http": code,
            "user": {k: body.get(k) for k in ("id", "login", "email", "full_name", "is_admin") if isinstance(body, dict)},
            "password_generated": "password" not in args,
            # only echo generated password once for operator bootstrap
            "password": password if "password" not in args else None,
        }
    )


def cmd_user_get(args: dict[str, Any]) -> None:
    username = args.get("username") or args.get("user")
    if not username:
        out({"ok": False, "error": "username_required"}, 2)
    code, body = api("GET", f"/api/v1/users/{urllib.parse.quote(str(username))}")
    out({"ok": True, "http": code, "user": body})


def cmd_token_ensure(args: dict[str, Any]) -> None:
    """Ensure agent token file exists. Uses basic auth admin bootstrap if no token yet."""
    root = install_root()
    tok_path = root / "secrets" / "agent_token"
    if tok_path.is_file() and tok_path.read_text(encoding="utf-8").strip():
        # validate
        os.environ["AGPK_API_TOKEN"] = tok_path.read_text(encoding="utf-8").strip()
        try:
            code, body = api("GET", "/api/v1/user")
            out({"ok": True, "action": "existing", "http": code, "login": body.get("login") if isinstance(body, dict) else None})
        except SystemExit:
            # recreate
            pass
    username = args.get("username") or os.environ.get("FORGEJO_ADMIN_USER", "agpk-admin")
    password = args.get("password") or os.environ.get("FORGEJO_ADMIN_PASSWORD")
    if not password:
        pw_file = root / "secrets" / "admin_password"
        if pw_file.is_file():
            password = pw_file.read_text(encoding="utf-8").strip()
    if not password:
        out(
            {
                "ok": False,
                "error": "admin_password_missing",
                "hint": "set FORGEJO_ADMIN_PASSWORD or secrets/admin_password (created by INSTALL)",
            },
            2,
        )
    token_name = args.get("name") or "agpk-agent"
    # Create token via API with basic auth
    url = base_url() + f"/api/v1/users/{urllib.parse.quote(username)}/tokens"
    payload = json.dumps(
        {
            "name": token_name,
            "scopes": [
                "all",
            ],
        }
    ).encode()
    import base64

    basic = base64.b64encode(f"{username}:{password}".encode()).decode()
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        # token name may exist — list and fail with guidance
        out({"ok": False, "http": e.code, "error": raw[:800], "hint": "delete old token or use new name"}, 1)
    except Exception as e:
        out({"ok": False, "error": str(e)}, 1)

    sha = body.get("sha1") if isinstance(body, dict) else None
    if not sha:
        out({"ok": False, "error": "no_token_in_response", "body": body}, 1)
    tok_path.parent.mkdir(parents=True, exist_ok=True)
    tok_path.write_text(sha + "\n", encoding="utf-8")
    os.chmod(tok_path, 0o600)
    # also write service.env token
    env_path = root / "service.env"
    if env_path.is_file():
        lines = env_path.read_text(encoding="utf-8").splitlines()
        lines = [ln for ln in lines if not ln.startswith("AGPK_API_TOKEN=") and not ln.startswith("FORGEJO_TOKEN=")]
        lines.append(f"AGPK_API_TOKEN={sha}")
        lines.append(f"FORGEJO_TOKEN={sha}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.chmod(env_path, 0o600)
    out({"ok": True, "action": "created", "token_file": str(tok_path), "name": token_name, "id": body.get("id")})


def cmd_token_revoke(args: dict[str, Any]) -> None:
    token_id = args.get("id") or args.get("token_id")
    username = args.get("username") or os.environ.get("FORGEJO_ADMIN_USER", "agpk-admin")
    if not token_id:
        out({"ok": False, "error": "id_required"}, 2)
    code, body = api("DELETE", f"/api/v1/users/{urllib.parse.quote(username)}/tokens/{token_id}")
    out({"ok": True, "http": code, "result": body})


def cmd_org_list() -> None:
    code, body = api("GET", "/api/v1/user/orgs")
    out({"ok": True, "http": code, "orgs": body})


def cmd_org_create(args: dict[str, Any]) -> None:
    name = args.get("name") or args.get("username")
    if not name:
        out({"ok": False, "error": "name_required"}, 2)
    payload = {
        "username": name,
        "full_name": args.get("full_name") or name,
        "description": args.get("description") or "created by agpk forgejo agent",
        "visibility": args.get("visibility") or "private",
    }
    code, body = api("POST", "/api/v1/orgs", payload)
    out({"ok": True, "http": code, "org": body})


def cmd_repo_list(args: dict[str, Any]) -> None:
    org = args.get("org")
    if org:
        code, body = api("GET", f"/api/v1/orgs/{urllib.parse.quote(str(org))}/repos?limit=50")
    else:
        code, body = api("GET", "/api/v1/user/repos?limit=50")
    out({"ok": True, "http": code, "repos": body})


def cmd_repo_create(args: dict[str, Any]) -> None:
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
        "auto_init": bool(args.get("auto_init", True)),
        "default_branch": args.get("default_branch") or "main",
    }
    org = args.get("org")
    if org:
        code, body = api("POST", f"/api/v1/orgs/{urllib.parse.quote(str(org))}/repos", payload)
    else:
        code, body = api("POST", "/api/v1/user/repos", payload)
    out({"ok": True, "http": code, "repo": body})


def cmd_repo_get(args: dict[str, Any]) -> None:
    owner = args.get("owner")
    repo = args.get("repo") or args.get("name")
    if not owner or not repo:
        out({"ok": False, "error": "owner_and_repo_required"}, 2)
    code, body = api(
        "GET",
        f"/api/v1/repos/{urllib.parse.quote(str(owner))}/{urllib.parse.quote(str(repo))}",
    )
    out({"ok": True, "http": code, "repo": body})


def cmd_repo_delete(args: dict[str, Any]) -> None:
    owner = args.get("owner")
    repo = args.get("repo") or args.get("name")
    confirm = args.get("confirm")
    if not owner or not repo:
        out({"ok": False, "error": "owner_and_repo_required"}, 2)
    if confirm not in (True, "true", "yes", "1", 1):
        out({"ok": False, "error": "confirm_required", "hint": 'pass "confirm": true'}, 2)
    code, body = api(
        "DELETE",
        f"/api/v1/repos/{urllib.parse.quote(str(owner))}/{urllib.parse.quote(str(repo))}",
    )
    out({"ok": True, "http": code, "result": body})


def cmd_repo_migrate(args: dict[str, Any]) -> None:
    clone_addr = args.get("clone_addr") or args.get("url")
    repo_name = args.get("repo_name") or args.get("name")
    if not clone_addr or not repo_name:
        out({"ok": False, "error": "clone_addr_and_repo_name_required"}, 2)
    payload = {
        "clone_addr": clone_addr,
        "repo_name": repo_name,
        "mirror": bool(args.get("mirror", False)),
        "private": bool(args.get("private", True)),
        "service": args.get("service") or "git",
    }
    if args.get("repo_owner"):
        payload["repo_owner"] = args["repo_owner"]
    code, body = api("POST", "/api/v1/repos/migrate", payload)
    out({"ok": True, "http": code, "repo": body})


def cmd_config_summary() -> None:
    cfg = os.environ.get("FORGEJO_CONFIG") or str(install_root() / "conf" / "app.ini")
    path = Path(cfg)
    summary: dict[str, Any] = {
        "ok": True,
        "config_path": str(path),
        "exists": path.is_file(),
        "base_url": base_url(),
        "db_host": os.environ.get("FORGEJO_DB_HOST"),
        "db_name": os.environ.get("FORGEJO_DB_NAME"),
        "db_user": os.environ.get("FORGEJO_DB_USER"),
        "http_addr": os.environ.get("FORGEJO_HTTP_ADDR"),
        "http_port": os.environ.get("FORGEJO_HTTP_PORT"),
        "work_dir": os.environ.get("FORGEJO_WORK_DIR"),
        "unit": unit_name(),
        "docker_primary": False,
        "package_kind": "core",
    }
    if path.is_file():
        # non-secret keys only
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "PASSWD" in line.upper() or "SECRET" in line.upper() or "TOKEN" in line.upper() or "PASSWORD" in line.upper():
                continue
            if "=" in line and not line.strip().startswith(";") and not line.strip().startswith("["):
                k, v = line.split("=", 1)
                k = k.strip()
                if k in ("APP_NAME", "HTTP_ADDR", "HTTP_PORT", "ROOT_URL", "DB_TYPE", "HOST", "NAME", "USER", "DOMAIN"):
                    summary[k] = v.strip()
    out(summary)


def cmd_admin_dashboard() -> None:
    # best-effort stats
    users = None
    repos = None
    try:
        _, users = api("GET", "/api/v1/admin/users?limit=1")
    except SystemExit:
        raise
    except Exception:
        pass
    code, me = api("GET", "/api/v1/user")
    code2, repos = api("GET", "/api/v1/user/repos?limit=1")
    # admin users list length when available
    user_count = None
    try:
        _, allu = api("GET", "/api/v1/admin/users?limit=50")
        if isinstance(allu, list):
            user_count = len(allu)
    except Exception:
        pass
    repo_count = len(repos) if isinstance(repos, list) else None
    out(
        {
            "ok": True,
            "me": me.get("login") if isinstance(me, dict) else me,
            "user_count_sample": user_count,
            "repo_count_sample": repo_count,
            "note": "sample limits apply; not full SQL stats",
        }
    )


def main() -> None:
    root = install_root()
    load_env_file(root / "service.env")
    if len(sys.argv) < 2:
        out({"ok": False, "error": "usage: forgejo-agent.py <command_id> [json_args]"}, 2)
    cmd = sys.argv[1]
    args: dict[str, Any] = {}
    if len(sys.argv) > 2 and sys.argv[2]:
        args = json.loads(sys.argv[2])
    if os.environ.get("AGPK_INVOKE_ARGS"):
        args = {**args, **json.loads(os.environ["AGPK_INVOKE_ARGS"])}

    if cmd.startswith("forgejo.service.") or cmd in (
        "forgejo.service.status",
        "forgejo.service.start",
        "forgejo.service.stop",
        "forgejo.service.restart",
        "forgejo.service.enable",
        "forgejo.service.disable",
        "forgejo.service.logs",
    ):
        action = cmd.split(".")[-1]
        cmd_service(action, args)

    table = {
        "forgejo.health": lambda: cmd_health(),
        "forgejo.version": lambda: cmd_version(),
        "forgejo.db.ping": lambda: cmd_db_ping(),
        "forgejo.user.list": lambda: cmd_user_list(),
        "forgejo.user.create": lambda: cmd_user_create(args),
        "forgejo.user.get": lambda: cmd_user_get(args),
        "forgejo.token.ensure": lambda: cmd_token_ensure(args),
        "forgejo.token.revoke": lambda: cmd_token_revoke(args),
        "forgejo.org.list": lambda: cmd_org_list(),
        "forgejo.org.create": lambda: cmd_org_create(args),
        "forgejo.repo.list": lambda: cmd_repo_list(args),
        "forgejo.repo.create": lambda: cmd_repo_create(args),
        "forgejo.repo.get": lambda: cmd_repo_get(args),
        "forgejo.repo.delete": lambda: cmd_repo_delete(args),
        "forgejo.repo.migrate": lambda: cmd_repo_migrate(args),
        "forgejo.config.summary": lambda: cmd_config_summary(),
        "forgejo.admin.dashboard": lambda: cmd_admin_dashboard(),
    }
    if cmd in table:
        table[cmd]()
    out({"ok": False, "error": f"unknown_command:{cmd}"}, 1)


if __name__ == "__main__":
    main()
