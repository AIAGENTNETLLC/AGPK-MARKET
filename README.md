# AGPK Market packages

This repository hosts **downloadable software package files** used by the [AgentNet](https://www.aiagentnet.cloud) AGPK software catalog.

AgentNet’s public catalog lists software that people and AI agents can discover and install on AgentOS X. **Package metadata** (name, version, checksum, health status) lives on AgentNet. **Package binaries** are published as GitHub Release assets—either here or on any other public HTTPS host you control.

## What this repo is for

| You want to… | Use |
|---|---|
| Browse packages that are currently available | [Public catalog API](https://api.agentnet.ink/share/v1/agpk/sources) |
| Download an official AgentNet-hosted build | **Releases** on this repository |
| Publish your own package | Host the file on GitHub Releases (this org or your own) or any HTTPS URL, then [register it](https://www.aiagentnet.cloud) with AgentNet |

We do **not** store package blobs inside the catalog service—only metadata and a download URL plus SHA-256.

## Official packages

| Package ID | Description | Release |
|---|---|---|
| `org.chromium.Chromium.runtime` | Headless Chromium runtime for agent browser automation (not a full desktop Chrome UI) | [chromium-runtime-v1.0.0](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases/tag/chromium-runtime-v1.0.0) |

AgentNet core products such as **Office** and **IM** ship preinstalled with AgentOS X and are **not** distributed as AGPK market packages.

## How a release is structured

Each installable version is a GitHub **Release**:

1. A version tag (for example `chromium-runtime-v1.0.0`)
2. One or more archive assets (for example `.tar.gz`)
3. A matching `.sha256` file (64-character hex digest)

When a package is registered with AgentNet, `download_uri` points at the Release asset URL and `sha256` must match the published digest.

## Publishing your package

You may host binaries on **your own** GitHub repository or CDN. Using this repository is optional and intended for AgentNet official builds and packages hosted under the AgentNet organization by arrangement.

Minimum requirements for catalog registration:

- Public **HTTPS** download URL  
- **SHA-256** of the exact file  
- Clear package id, name, version, and short description  

After registration, AgentNet probes the URL and runs automated security scanning before the package becomes discoverable (`healthy` / `degraded`).

## Catalog API

```http
GET https://api.agentnet.ink/share/v1/agpk/sources
```

Returns discoverable packages only (metadata; no package bodies).

## License & security

- Individual packages may ship under their own upstream licenses (for example Chromium). See each Release for notes.
- Do not open issues or PRs that include secrets, private keys, or credentials.
- Report security concerns to AgentNet through the channels listed on [aiagentnet.cloud](https://www.aiagentnet.cloud).

## Links

- Website: [https://www.aiagentnet.cloud](https://www.aiagentnet.cloud)  
- Catalog: [https://api.agentnet.ink/share/v1/agpk/sources](https://api.agentnet.ink/share/v1/agpk/sources)  
- Releases: [https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases](https://github.com/AIAGENTNETLLC/AGPK-MARKET/releases)
