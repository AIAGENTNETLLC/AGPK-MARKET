# Forgejo Core — agent usage

**Package:** `org.forgejo.Forgejo.core` **1.0.1** · **package_kind=core**  
**Runtime:** official Forgejo binary (pin in `DIGESTS`) + **systemd** + **system PostgreSQL**  
**Not:** Docker primary path · tar shell · UI package (see `org.forgejo.Forgejo.ui`)

## Install

```bash
export AGPK_INSTALL_ROOT=/opt/agentx/agpk/org.forgejo.Forgejo.core
# requires root + local PostgreSQL + git
# AgentOS X PG is often on 5433 — set explicitly or let INSTALL probe (5433→5432)
export FORGEJO_DB_PORT="${FORGEJO_DB_PORT:-5433}"
sudo -E sh INSTALL
```

Layout-only (no binary download / no unit) for structure tests:

```bash
AGPK_DRY_LAYOUT=1 AGPK_INSTALL_ROOT=/tmp/fj-core sh INSTALL
```

## Invoke (after install)

```bash
export AGPK_INSTALL_ROOT=...
sh run_cmd.sh forgejo.health '{}'
sh run_cmd.sh forgejo.service.status '{}'
sh run_cmd.sh forgejo.repo.create '{"name":"demo","private":true}'
sh run_cmd.sh forgejo.user.list '{}'
```

Args JSON via argv or `AGPK_INVOKE_ARGS`.

## Environment

| Var | Default |
|-----|---------|
| `FORGEJO_HTTP_ADDR` / `PORT` | `127.0.0.1` / `3000` |
| `FORGEJO_WORK_DIR` | `/var/lib/forgejo` |
| `FORGEJO_CONFIG` | `/etc/forgejo/app.ini` (owned by `forgejo`, mode 0600 — writable for JWT) |
| `FORGEJO_DB_PORT` | **probe 5433→5432** (AgentOS often **5433**); set to pin |
| `FORGEJO_DB_*` | local postgres role/db `forgejo` |
| `AGPK_API_TOKEN` | written by `forgejo.token.ensure` |

**Host deps:** `git` (INSTALL apt-installs if missing), `postgresql` client/server, `systemd`.

## Uninstall

```bash
sudo -E sh UNINSTALL          # keeps data
sudo AGPK_PURGE=1 sh UNINSTALL  # drops work dir + DB
```

## Human review

Agent results → AgentOS **projection.*** (no GUI primary path in core).  
Desktop open URL → **ui** package.
