# AGPK Market packages

This repository hosts **downloadable software package files** used by the [AgentNet](https://www.aiagentnet.cloud) AGPK software catalog.

AgentNet’s catalog is **agent-first**: packages are built so **agents on AgentOS X** can discover, install, and use software—not merely so humans can download archives. Official packages are **agentized adaptations** of upstream products (command surfaces / drivers), not tar wrappers of GUIs.

**Metadata** (discovery, health, registration) lives on AgentNet. **Binaries** are GitHub Release assets in this repo (or a vendor’s own HTTPS host).

Machine index (website / docs):  
`https://docs.aiagentnet.cloud/agpk/v1/firstparty-catalog.json`

---

## Official packages

Current **AgentNet-maintained** market packages (10). Prefer the tags below; older Chromium/SDK seeds (1.0.x / 1.1.x) are historical only—do not re-register them.

| Package ID | Version | Description | Release |
|---|---|---|---|
| `org.chromium.Chromium.runtime` | **1.2.0** | Agent Chromium: headless engine + full `chrome.*` / `browser.*` command surface | [chromium-runtime-v1.2.0](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/chromium-runtime-v1.2.0) |
| `org.agentnet.agpk.sdk` | **1.2.0** | Vendor SDK C1–C4: scaffold / pack / validate + entry+driver templates | [agpk-sdk-v1.2.0](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/agpk-sdk-v1.2.0) |
| `org.actualbudget.Actual.agent` | **1.1.0** | Agentized Actual Budget (HTTP when configured) | [actualbudget-Actual-agent-v1-1-0-71c12af4](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/actualbudget-Actual-agent-v1-1-0-71c12af4) |
| `org.audacityteam.Audacity.agent` | **1.1.0** | Agentized audio path (audacity/ffmpeg probe; headless export) | [audacityteam-Audacity-agent-v1-1-0-64bc5b86](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/audacityteam-Audacity-agent-v1-1-0-64bc5b86) |
| `org.bookstack.BookStack.agent` | **1.1.0** | Agentized BookStack REST (books / pages / search) | [bookstack-BookStack-agent-v1-1-0-f119d28f](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/bookstack-BookStack-agent-v1-1-0-f119d28f) |
| `org.crater.Crater.agent` | **1.1.0** | Agentized Crater invoices API | [crater-Crater-agent-v1-1-0-cb61ea41](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/crater-Crater-agent-v1-1-0-cb61ea41) |
| `org.docuseal.DocuSeal.agent` | **1.1.0** | Agentized DocuSeal REST submissions | [docuseal-DocuSeal-agent-v1-1-0-8a287a65](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/docuseal-DocuSeal-agent-v1-1-0-8a287a65) |
| `org.jitsi.JitsiMeet.agent` | **1.1.0** | Agentized Jitsi Meet room create | [jitsi-JitsiMeet-agent-v1-1-0-7141a289](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/jitsi-JitsiMeet-agent-v1-1-0-7141a289) |
| `org.kde.Kdenlive.agent` | **1.1.0** | Agentized video batch path (melt/ffmpeg; not GUI-primary) | [kde-Kdenlive-agent-v1-1-0-41cfe7fe](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/kde-Kdenlive-agent-v1-1-0-41cfe7fe) |
| `org.nextcloud.Nextcloud.agent` | **1.1.0** | Agentized Nextcloud WebDAV + OCS probe | [nextcloud-Nextcloud-agent-v1-1-0-572dd393](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/nextcloud-Nextcloud-agent-v1-1-0-572dd393) |

Each release ships the installable archive **and** a matching `.sha256` file.

### Not AGPK market packages

**Office** and **IM** ship **preinstalled** with AgentOS X. They are product entitlements, not market install packages, and will not appear in this table.

---

## Catalog API

Live discovery (share registry — metadata only):

```http
GET https://api.agentnet.ink/share/v1/agpk/sources
```

Anonymous registration (metadata + `download_uri` + `sha256`; package file must already be on HTTPS):

```http
POST https://api.agentnet.ink/share/v1/agpk/sources
```

Website proxy (same market): `POST https://www.aiagentnet.cloud/api/agpk/sources`

Human docs: [AGPK software](https://docs.aiagentnet.cloud/agpk)

---

## Publishing your package

1. Build an **agent-usable** package (Vendor SDK `org.agentnet.agpk.sdk` — list_commands / invoke ready).
2. Host the archive on GitHub Releases (this org or yours) or any public HTTPS URL.
3. Register with AgentNet with `download_uri` + SHA-256.
4. Automated probe/scan → `healthy` / `degraded` / reject if no command surface.

---

## Links

- Website: https://www.aiagentnet.cloud  
- Docs (AGPK): https://docs.aiagentnet.cloud/agpk  
- First-party catalog JSON: https://docs.aiagentnet.cloud/agpk/v1/firstparty-catalog.json  
- Live catalog API: https://api.agentnet.ink/share/v1/agpk/sources  
- Releases: https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases  

---

*README synced to official catalog · 2026-07-13*
