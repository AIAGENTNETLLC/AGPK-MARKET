# AGPK Market packages

This repository hosts **downloadable software package files** used by the [AgentNet](https://www.aiagentnet.cloud) AGPK software catalog.

AgentNet’s catalog is **agent-first**: packages are built so **agents on AgentOS X** can discover, install, and use software—not merely so humans can download archives. See the product standard in the AgentNet monorepo (`AGPK_AGENT优先与官方包标准`).

**Metadata** lives on AgentNet. **Binaries** are GitHub Release assets (here or your own host).

## Official packages

| Package ID | Version | Description | Release |
|---|---|---|---|
| `org.chromium.Chromium.runtime` | **1.1.0** | Agent-first headless Chromium (install layout, `AGENTX_BROWSER_BINARY`, probe, AHCP surface) | [chromium-runtime-v1.1.0](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/chromium-runtime-v1.1.0) |
| `org.agentnet.agpk.sdk` | **1.0.0** | Vendor SDK: scaffold / pack / validate + publish guide | [agpk-sdk-v1.0.0](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/agpk-sdk-v1.0.0) |

`org.chromium.Chromium.runtime` **1.0.0** remains as a transitional pipeline seed; prefer **1.1.0**.

Office and IM ship **preinstalled** with AgentOS X and are **not** AGPK market packages.

## Catalog API

```http
GET https://api.agentnet.ink/share/v1/agpk/sources
```

## Publishing your package

1. Build an **agent-usable** package (use the Vendor SDK above).
2. Host the archive on GitHub Releases (this org or yours) or any HTTPS URL.
3. Register with AgentNet (`POST /share/v1/agpk/sources`) with `download_uri` + SHA-256.
4. Wait for automated probe/scan → `healthy` / `degraded`.

## Links

- Website: https://www.aiagentnet.cloud  
- Catalog: https://api.agentnet.ink/share/v1/agpk/sources  
- Releases: https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases  
