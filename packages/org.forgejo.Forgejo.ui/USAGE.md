# Forgejo UI Workbench **1.1.2**

**package_kind=ui** · **ui_face=desktop_workbench** · depends `org.forgejo.Forgejo.core >= 1.0.0`

## Language / 语言

- **Default: follow system** (`LANG` / `LC_ALL` / browser `navigator.language`, or `FORGEJO_UI_LANG=zh|en`)
- UI strings: **中文 + English**; header has manual 中文 / EN switch (stored in localStorage)
- Desktop entry: `Name[zh_CN]=Forgejo 工作台`

## What this is

- **Primary path:** `forgejo.ui.workbench.open` → dedicated window (WebKit2GTK or Chromium `--app`) hosting a **local workbench** that talks to **core** (token proxy).
- Human main chain in-workbench: see core status → **list repos** → **create repo** → **detail** → optional embedded full Forgejo web.
- **Not** the 1.0.0 launcher: 1.0.0 was xdg-open only = **launcher_only**, **not** ui functional parity.

## What this is not

- Pixel-complete rewrite of all Forgejo web features.
- Second Forgejo process / Docker.
- “Install ui = full product done” without core.

## Commands

| id | face | notes |
|----|------|--------|
| `forgejo.ui.workbench.open` | **desktop_workbench (primary)** | dedicated window |
| `forgejo.ui.workbench.status` | workbench | local server |
| `forgejo.ui.repo.list` / `create` | via core API | same data as `forgejo.repo.*` |
| `forgejo.ui.open` | **launcher_only** | system browser; **non-primary** |
| `forgejo.ui.desktop.install` | desktop entry → workbench shell | |

## Install

```bash
# core first
export FORGEJO_CORE_ROOT=/srv/agentnet-data/agpk/org.forgejo.Forgejo.core   # or /opt/...
export AGPK_INSTALL_ROOT=/srv/agentnet-data/agpk/org.forgejo.Forgejo.ui
sh INSTALL
# desktop session:
sh run_cmd.sh forgejo.ui.workbench.open '{}'
```

## Host deps for dedicated shell

- `DISPLAY` or Wayland, and one of:
  - `python3-gi` + `gir1.2-webkit2-4.0` (or 4.1), or
  - `chromium` / `google-chrome` / AgentOS browser binary

Without a dedicated shell, `workbench.open` **fails honestly** (does not silently claim xdg-open success as ui parity).
