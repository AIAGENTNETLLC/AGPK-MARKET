# AGENT_CAPABILITIES · org.forgejo.Forgejo.ui **1.1.2**

## ui_face

| Version | ui_face | Parity claim |
|---------|---------|--------------|
| 1.0.0 | `launcher_only` | **None** (入口适配 / superseded) |
| **1.1.2** | **`desktop_workbench`** | Desktop main-chain shell (open workbench → list/create repo via core) |

## Agent

- Automation **must** prefer **core** `forgejo.repo.*` / `forgejo.user.*`.
- UI package helps human desktop + projection; does not replace core.

## Transformation points (书面改造)

1. Local workbench server proxies Forgejo API with core token (token not in page JS).
2. Dedicated window: WebKit2GTK or Chromium `--app` (not xdg-open primary).
3. Repo list/create UI wired to same core API as agent commands.
4. `.desktop` launches workbench shell, not raw URL.

## Forbidden claims

- 「ui 功能对等完成」for 1.0.0 launcher
- 「装 ui 即得完整视觉 Forgejo 全部页面重写」
