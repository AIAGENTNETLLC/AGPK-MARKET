# AGPK Market packages

This repository hosts **downloadable software package files** used by the [AgentNet](https://www.aiagentnet.cloud) AGPK software catalog.

AgentNet’s catalog is **agent-first**: packages are built so **agents on AgentOS X** can discover, install, and use software—not merely so humans can download archives. Official packages are **agentized adaptations** of upstream products (command surfaces / drivers), not tar wrappers of GUIs.

**Metadata** (discovery, health, registration) lives on AgentNet share. **Binaries** are Release assets here (or a vendor’s own HTTPS host).

- Live catalog API: `GET https://api.agentnet.ink/share/v1/agpk/sources`
- Human docs: https://docs.aiagentnet.cloud/agpk
- Machine index (website mirror): https://docs.aiagentnet.cloud/agpk/v1/firstparty-catalog.json

The tables below are **generated from the live share catalog after probe/revalidate**. Do not hand-edit between `AUTO:*` markers — run `scripts/sync_readme_from_share.py --write` (or wait for the scheduled GitHub Action).

---

## Official packages

<!-- AUTO:OFFICIAL_PACKAGES:START -->
Live from share catalog (`healthy` | `degraded`) · **17** official row(s).

Classification: `download_uri` under `github.com/AIAGENTNETLLC/` **or** vendor **AIAGENTNET LLC** / AgentNet.

| Package ID | Version | Status | Vendor | Description | Artifact |
|---|---|---|---|---|---|
| `org.actualbudget.Actual.agent` | **1.1.0** | `healthy` | AIAGENTNET LLC | Agentized Actual Budget: drives Actual server HTTP when configured. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/actualbudget-Actual-agent-v1-1-0) |
| `org.agentnet.agentos-x.antivirus-clamav` | **1.0.0** | `healthy` | AIAGENTNET LLC | Antivirus: ClamAV engine for on-demand and scheduled malware scan/quarantine. Not identity/audit product. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/agentos-x-antivirus-clamav-v1.0.0) |
| `org.agentnet.agentos-x.fail2ban` | **1.0.0** | `healthy` | AIAGENTNET LLC | Network anti-bruteforce (fail2ban) for SSH and jails. Complements OS nftables firewall. Not antivirus. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/agentos-x-fail2ban-v1.0.0) |
| `org.agentnet.agentos-x.host-probe` | **1.0.0** | `healthy` | AIAGENTNET LLC | On-demand host hardware/vitals collect and report. Not antivirus. Not OS housekeep replacement. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/agentos-x-host-probe-v1.0.0) |
| `org.agentnet.agentos-x.vulnscan-lynis` | **1.0.0** | `healthy` | AIAGENTNET LLC | Vulnerability/baseline host scan via Lynis. Read-only report. Not antivirus. Not identity product. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/agentos-x-vulnscan-lynis-v1.0.0) |
| `org.agentnet.agpk.sdk` | **1.2.0** | `healthy` | AIAGENTNET LLC | Vendor toolkit C1–C4: scaffold/pack/validate with entry+driver; list_commands + invoke ready templates. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/agpk-sdk-v1.2.0) |
| `org.agentnet.desktop.control.core` | **2.0.0** | `healthy` | AIAGENTNET LLC | Universal single-process desktop control: desktop.use routes a11y to OCR to pixel for all software windows. Agent-first AGPK core. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/desktop-control-core-v2.0.0) |
| `org.audacityteam.Audacity.agent` | **1.1.0** | `healthy` | AIAGENTNET LLC | Agentized audio path: probes audacity/ffmpeg; headless export via ffmpeg FOSS engine. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/audacityteam-Audacity-agent-v1-1-0) |
| `org.bookstack.BookStack.agent` | **1.1.0** | `healthy` | AIAGENTNET LLC | Agentized BookStack: real REST API books/pages/search. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/bookstack-BookStack-agent-v1-1-0) |
| `org.chromium.Chromium.runtime` | **1.2.0** | `healthy` | AIAGENTNET LLC | Headless Chromium engine + full chrome.*/browser.* agent command surface (78 cmds). Functional parity browser automation; projection.* for human view. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/chromium-runtime-v1.2.0) |
| `org.crater.Crater.agent` | **1.1.0** | `healthy` | AIAGENTNET LLC | Agentized Crater: real /api/v1 bootstrap and invoices when Crater is up. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/crater-Crater-agent-v1-1-0) |
| `org.docuseal.DocuSeal.agent` | **1.1.0** | `healthy` | AIAGENTNET LLC | Agentized DocuSeal: real REST API list/create submissions against DocuSeal instance. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/docuseal-DocuSeal-agent-v1-1-0) |
| `org.forgejo.Forgejo.core` | **1.0.1** | `healthy` | AIAGENTNET LLC | Forgejo Core 1.0.1 (systemd+PG; INSTALL hardened) | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/forgejo-core-v1.0.1) |
| `org.forgejo.Forgejo.ui` | **1.1.2** | `healthy` | AIAGENTNET LLC | Desktop workbench; detach open; launch.sh Wayland/Xauth; zh/en | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/forgejo-ui-v1.1.2) |
| `org.jitsi.JitsiMeet.agent` | **1.1.0** | `healthy` | AIAGENTNET LLC | Agentized Jitsi Meet: real room create against Jitsi HTTP endpoint. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/jitsi-JitsiMeet-agent-v1-1-0) |
| `org.kde.Kdenlive.agent` | **1.1.0** | `healthy` | AIAGENTNET LLC | Agentized video path: melt/ffmpeg FOSS batch render (Kdenlive domain, no GUI primary). | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/kde-Kdenlive-agent-v1-1-0) |
| `org.nextcloud.Nextcloud.agent` | **1.1.0** | `healthy` | AIAGENTNET LLC | Agentized Nextcloud: WebDAV put/get + OCS user probe. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/nextcloud-Nextcloud-agent-v1-1-0) |

### Not AGPK market packages

**Office** and **IM** ship **preinstalled** with AgentOS X (product entitlements). They are **not** market install packages and will not appear here.
<!-- AUTO:OFFICIAL_PACKAGES:END -->

---

## Other vendors (community / third-party)

<!-- AUTO:VENDOR_PACKAGES:START -->
Live third-party / other-vendor packages from the same share catalog (healthy | degraded), grouped by `vendor_name`.

_No non-official packages are live in the catalog right now. When independent providers register and pass probe, they appear here automatically._
<!-- AUTO:VENDOR_PACKAGES:END -->

---

## Acknowledgments

<!-- AUTO:ACKNOWLEDGMENTS:START -->
AgentNet official market packages are **agentized adaptations**. We do **not** claim ownership of the original software. Thanks to the upstream projects and communities:

| Upstream | Project | Thanks for | Link |
|---|---|---|---|
| **Forgejo** | Forgejo — self-hosted lightweight software forge | Official binary + systemd + system PostgreSQL agentized as core; UI depends core. | [https://forgejo.org/](https://forgejo.org/) |
| **Chromium** | The Chromium Authors / Google Chromium project | Headless browser engine basis for our agent command surface. | [https://www.chromium.org/](https://www.chromium.org/) |
| **Actual Budget** | Actual Budget (open-source personal finance) | Agentized around Actual’s server HTTP surface. | [https://actualbudget.org/](https://actualbudget.org/) |
| **Audacity** | Audacity Team — Audacity digital audio editor | Audio domain packaging; headless paths use FOSS ffmpeg where noted. | [https://www.audacityteam.org/](https://www.audacityteam.org/) |
| **BookStack** | BookStack documentation platform | Agentized against BookStack’s REST API. | [https://www.bookstackapp.com/](https://www.bookstackapp.com/) |
| **Crater** | Crater Invoice (open-source invoicing) | Agentized against Crater’s HTTP API. | [https://craterapp.com/](https://craterapp.com/) |
| **DocuSeal** | DocuSeal document signing | Agentized against DocuSeal’s REST API. | [https://www.docuseal.com/](https://www.docuseal.com/) |
| **Jitsi Meet** | Jitsi Meet (8x8 / community) | Agentized room/meeting HTTP flows. | [https://jitsi.org/](https://jitsi.org/) |
| **Kdenlive** | KDE — Kdenlive video editor | Video domain; batch paths use melt/ffmpeg FOSS tools. | [https://kdenlive.org/](https://kdenlive.org/) |
| **Nextcloud** | Nextcloud GmbH — Nextcloud | Agentized WebDAV / OCS-style access patterns. | [https://nextcloud.com/](https://nextcloud.com/) |
| **ClamAV** | Cisco Talos — ClamAV antivirus engine | On-demand/scheduled malware scan engine for AgentOS X host security AGPK. | [https://www.clamav.net/](https://www.clamav.net/) |
| **Lynis** | CISOfy — Lynis security auditing tool | Host vulnerability/baseline audit reports for AgentOS X security AGPK. | [https://cisofy.com/lynis/](https://cisofy.com/lynis/) |
| **Fail2ban** | Fail2ban community — intrusion prevention | SSH/jail anti-bruteforce packaging complementing OS firewall. | [https://www.fail2ban.org/](https://www.fail2ban.org/) |

Trademarks and product names belong to their respective owners. Use of names is for identification of agentized integrations only.

If you maintain an upstream project listed above and want a different credit line or link, open an issue or contact [support@aiagentnet.cloud](mailto:support@aiagentnet.cloud).
<!-- AUTO:ACKNOWLEDGMENTS:END -->

---

## Catalog API

```http
GET https://api.agentnet.ink/share/v1/agpk/sources
```

Anonymous registration (metadata + `download_uri` + `sha256`; package file must already be on HTTPS):

```http
POST https://api.agentnet.ink/share/v1/agpk/sources
```

Website proxy: `POST https://www.aiagentnet.cloud/api/agpk/sources`

---

## Publishing your package

1. Build an **agent-usable** package (Vendor SDK `org.agentnet.agpk.sdk` — list_commands / invoke ready).
2. Host the archive on GitHub Releases (this org or yours) or any public HTTPS URL.
3. Register with AgentNet with `download_uri` + SHA-256.
4. Automated probe/scan → `healthy` / `degraded` / reject if no command surface.
5. After the package is live, this README’s tables refresh from the share catalog (Action or script).

---

## Links

- Website: https://www.aiagentnet.cloud
- Docs (AGPK): https://docs.aiagentnet.cloud/agpk
- Live catalog API: https://api.agentnet.ink/share/v1/agpk/sources
- Releases: https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases

<!-- AUTO:SYNC_META:START -->
_Last auto-sync: **2026-07-23 08:43 UTC** from `https://api.agentnet.ink/share/v1/agpk/sources` · official=17 · other-vendor=0 · live_total=17. Regenerate: `python3 scripts/sync_readme_from_share.py --write` (or GitHub Action `sync-readme-from-share`)._
<!-- AUTO:SYNC_META:END -->
