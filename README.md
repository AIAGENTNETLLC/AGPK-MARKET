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
Live from share catalog (`healthy` | `degraded`) · **2** official row(s).

Classification: `download_uri` under `github.com/AIAGENTNETLLC/` **or** vendor **AIAGENTNET LLC** / AgentNet.

| Package ID | Version | Status | Vendor | Description | Artifact |
|---|---|---|---|---|---|
| `org.agentnet.agpk.sdk` | **1.2.0** | `healthy` | AIAGENTNET LLC | Vendor toolkit C1–C4: scaffold/pack/validate with entry+driver; list_commands + invoke ready templates. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/agpk-sdk-v1.2.0) |
| `org.chromium.Chromium.runtime` | **1.2.0** | `healthy` | AIAGENTNET LLC | Headless Chromium engine + full chrome.*/browser.* agent command surface (78 cmds). Functional parity browser automation; projection.* for human view. | [release](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/chromium-runtime-v1.2.0) |

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
| **Chromium** | The Chromium Authors / Google Chromium project | Headless browser engine basis for our agent command surface. | [https://www.chromium.org/](https://www.chromium.org/) |

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
_Last auto-sync: **2026-07-14 08:26 UTC** from `https://api.agentnet.ink/share/v1/agpk/sources` · official=2 · other-vendor=0 · live_total=2. Regenerate: `python3 scripts/sync_readme_from_share.py --write` (or GitHub Action `sync-readme-from-share`)._
<!-- AUTO:SYNC_META:END -->
