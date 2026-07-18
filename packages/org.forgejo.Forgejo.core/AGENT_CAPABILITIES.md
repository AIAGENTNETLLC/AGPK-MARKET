# AGENT_CAPABILITIES · org.forgejo.Forgejo.core

## Domain

Self-hosted **Git forge** (Forgejo): repositories, users, orgs, access tokens, service lifecycle.

## What agents can do (core face)

| Area | Commands |
|------|----------|
| Service | status / start / stop / restart / enable / disable / logs |
| Health | health, version, db.ping |
| Users | list / create / get |
| Tokens | ensure / revoke |
| Orgs | list / create |
| Repos | list / create / get / delete / migrate |
| Ops | config.summary, admin.dashboard |

## Parity notes

- **Functional parity** is evaluated on this **core** command face (not web UI).
- Web UI chrome is **not** required for core DoD; use `org.forgejo.Forgejo.ui` for human open/desktop.
- Upstream binary is **fetched and sha256-verified** at install (see `DIGESTS`); not re-hosted as unmarked blob without pin.

## Non-goals

- AgentNet Forge V2 task collaboration (different product)
- Default public TLS termination
- Docker Compose as primary runtime
