#!/usr/bin/env python3
"""
Regenerate AIAGENTNETLLC/AGPK-MARKET README tables from share live catalog.

Data plane (source of truth for what is discoverable):
  GET https://api.agentnet.ink/share/v1/agpk/sources
  → only status healthy|degraded (post probe / revalidate)

Classification:
  - Official table: hosted under github.com/AIAGENTNETLLC/ or vendor AIAGENTNET LLC / AgentNet
  - Per-vendor tables: everyone else, grouped by vendor_name

Acknowledgments:
  - Static map of agentized upstream projects (thank the original software).

Markers in README.md (must exist):
  <!-- AUTO:OFFICIAL_PACKAGES:START --> ... <!-- AUTO:OFFICIAL_PACKAGES:END -->
  <!-- AUTO:VENDOR_PACKAGES:START --> ... <!-- AUTO:VENDOR_PACKAGES:END -->
  <!-- AUTO:ACKNOWLEDGMENTS:START --> ... <!-- AUTO:ACKNOWLEDGMENTS:END -->
  <!-- AUTO:SYNC_META:START --> ... <!-- AUTO:SYNC_META:END -->

Usage:
  python3 sync_agpk_market_readme.py --readme path/to/README.md
  python3 sync_agpk_market_readme.py --readme README.md --write
  SHARE_AGPK_SOURCES_URL=... python3 ... --write
  GITHUB_TOKEN=... python3 ... --readme README.md --write --push  # optional git commit+push cwd

Exit 0 if README unchanged or updated; non-zero on fetch/parse failure.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

DEFAULT_SOURCES_URL = "https://api.agentnet.ink/share/v1/agpk/sources"
OFFICIAL_URI_HOST_PATH = "github.com/aiagentnetllc/"
OFFICIAL_VENDOR_NEEDLES = (
    "aiagentnet llc",
    "aiagentnet",
    "agentnet",
)

# Upstream FOSS / product credits for agentized packages (package_id prefix → credit).
# Keep thanking the original authors; our packages are adaptations, not ownership claims.
UPSTREAM_ACK: list[dict[str, str]] = [
        {
        "package_prefix": "org.forgejo.Forgejo",
        "upstream": "Forgejo",
        "project": "Forgejo — self-hosted lightweight software forge",
        "url": "https://forgejo.org/",
        "note": "Official binary + systemd + system PostgreSQL agentized as core; UI depends core.",
    },
{
        "package_prefix": "org.chromium.Chromium",
        "upstream": "Chromium",
        "project": "The Chromium Authors / Google Chromium project",
        "url": "https://www.chromium.org/",
        "note": "Headless browser engine basis for our agent command surface.",
    },
    {
        "package_prefix": "org.actualbudget.Actual",
        "upstream": "Actual Budget",
        "project": "Actual Budget (open-source personal finance)",
        "url": "https://actualbudget.org/",
        "note": "Agentized around Actual’s server HTTP surface.",
    },
    {
        "package_prefix": "org.audacityteam.Audacity",
        "upstream": "Audacity",
        "project": "Audacity Team — Audacity digital audio editor",
        "url": "https://www.audacityteam.org/",
        "note": "Audio domain packaging; headless paths use FOSS ffmpeg where noted.",
    },
    {
        "package_prefix": "org.bookstack.BookStack",
        "upstream": "BookStack",
        "project": "BookStack documentation platform",
        "url": "https://www.bookstackapp.com/",
        "note": "Agentized against BookStack’s REST API.",
    },
    {
        "package_prefix": "org.crater.Crater",
        "upstream": "Crater",
        "project": "Crater Invoice (open-source invoicing)",
        "url": "https://craterapp.com/",
        "note": "Agentized against Crater’s HTTP API.",
    },
    {
        "package_prefix": "org.docuseal.DocuSeal",
        "upstream": "DocuSeal",
        "project": "DocuSeal document signing",
        "url": "https://www.docuseal.com/",
        "note": "Agentized against DocuSeal’s REST API.",
    },
    {
        "package_prefix": "org.jitsi.JitsiMeet",
        "upstream": "Jitsi Meet",
        "project": "Jitsi Meet (8x8 / community)",
        "url": "https://jitsi.org/",
        "note": "Agentized room/meeting HTTP flows.",
    },
    {
        "package_prefix": "org.kde.Kdenlive",
        "upstream": "Kdenlive",
        "project": "KDE — Kdenlive video editor",
        "url": "https://kdenlive.org/",
        "note": "Video domain; batch paths use melt/ffmpeg FOSS tools.",
    },
    {
        "package_prefix": "org.nextcloud.Nextcloud",
        "upstream": "Nextcloud",
        "project": "Nextcloud GmbH — Nextcloud",
        "url": "https://nextcloud.com/",
        "note": "Agentized WebDAV / OCS-style access patterns.",
    },
    {
        "package_prefix": "org.agentnet.agentos-x.antivirus-clamav",
        "upstream": "ClamAV",
        "project": "Cisco Talos — ClamAV antivirus engine",
        "url": "https://www.clamav.net/",
        "note": "On-demand/scheduled malware scan engine for AgentOS X host security AGPK.",
    },
    {
        "package_prefix": "org.agentnet.agentos-x.vulnscan-lynis",
        "upstream": "Lynis",
        "project": "CISOfy — Lynis security auditing tool",
        "url": "https://cisofy.com/lynis/",
        "note": "Host vulnerability/baseline audit reports for AgentOS X security AGPK.",
    },
    {
        "package_prefix": "org.agentnet.agentos-x.fail2ban",
        "upstream": "Fail2ban",
        "project": "Fail2ban community — intrusion prevention",
        "url": "https://www.fail2ban.org/",
        "note": "SSH/jail anti-bruteforce packaging complementing OS firewall.",
    },
]


def fetch_sources(url: str) -> list[dict[str, Any]]:
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "agpk-market-readme-sync/1.0"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8")
    data = json.loads(body)
    if isinstance(data, dict):
        sources = data.get("sources") or data.get("items") or data.get("packages") or []
    elif isinstance(data, list):
        sources = data
    else:
        raise ValueError(f"unexpected catalog shape: {type(data)}")
    if not isinstance(sources, list):
        raise ValueError("sources is not a list")
    return [s for s in sources if isinstance(s, dict)]


def is_official(src: dict[str, Any]) -> bool:
    uri = (src.get("download_uri") or "").strip().lower()
    if OFFICIAL_URI_HOST_PATH in uri:
        return True
    vendor = (src.get("vendor_name") or "").strip().lower()
    if not vendor:
        return False
    for needle in OFFICIAL_VENDOR_NEEDLES:
        if vendor == needle or vendor.startswith(needle + " "):
            return True
    return False


def release_page_url(download_uri: str) -> str:
    """Map …/releases/download/<tag>/<file> → …/releases/tag/<tag>."""
    uri = (download_uri or "").strip()
    m = re.search(r"(https://github\.com/[^/]+/[^/]+)/releases/download/([^/]+)/", uri)
    if m:
        return f"{m.group(1)}/releases/tag/{m.group(2)}"
    return uri


def dedupe_latest(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One row per package_id: prefer updated_at, then version string."""
    best: dict[str, dict[str, Any]] = {}
    for s in sources:
        pid = (s.get("package_id") or "").strip()
        if not pid:
            continue
        prev = best.get(pid)
        if prev is None:
            best[pid] = s
            continue
        pu = prev.get("updated_at") or prev.get("created_at") or ""
        su = s.get("updated_at") or s.get("created_at") or ""
        if su > pu:
            best[pid] = s
            continue
        if su == pu and str(s.get("version") or "") > str(prev.get("version") or ""):
            best[pid] = s
    return sorted(best.values(), key=lambda x: (x.get("package_id") or "").lower())


def md_cell(text: str) -> str:
    return str(text or "").replace("|", "\\|").replace("\n", " ").strip()


def render_package_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "_None in the live catalog right now._\n"
    lines = [
        "| Package ID | Version | Status | Vendor | Description | Artifact |",
        "|---|---|---|---|---|---|",
    ]
    for s in rows:
        pid = md_cell(s.get("package_id"))
        ver = md_cell(s.get("version"))
        st = md_cell(s.get("status"))
        vendor = md_cell(s.get("vendor_name"))
        summary = md_cell(s.get("summary") or s.get("name"))
        uri = (s.get("download_uri") or "").strip()
        rel = release_page_url(uri)
        art = f"[release]({rel})" if rel else "—"
        lines.append(f"| `{pid}` | **{ver}** | `{st}` | {vendor} | {summary} | {art} |")
    return "\n".join(lines) + "\n"


def render_official_section(official: list[dict[str, Any]]) -> str:
    parts = [
        f"Live from share catalog (`healthy` | `degraded`) · **{len(official)}** official row(s).",
        "",
        "Classification: `download_uri` under `github.com/AIAGENTNETLLC/` **or** vendor **AIAGENTNET LLC** / AgentNet.",
        "",
        render_package_table(official).rstrip(),
        "",
        "### Not AGPK market packages",
        "",
        "**Office** and **IM** ship **preinstalled** with AgentOS X (product entitlements). They are **not** market install packages and will not appear here.",
        "",
    ]
    return "\n".join(parts)


def render_vendor_section(by_vendor: dict[str, list[dict[str, Any]]]) -> str:
    if not by_vendor:
        return (
            "Live third-party / other-vendor packages from the same share catalog "
            "(healthy | degraded), grouped by `vendor_name`.\n\n"
            "_No non-official packages are live in the catalog right now. "
            "When independent providers register and pass probe, they appear here automatically._\n"
        )
    parts = [
        "Live third-party / other-vendor packages from the same share catalog "
        f"(healthy | degraded) · **{sum(len(v) for v in by_vendor.values())}** row(s) across "
        f"**{len(by_vendor)}** vendor(s).",
        "",
        "These are **not** AgentNet first-party packages. Artifacts are hosted by each provider; "
        "AgentNet only lists metadata after automated probe.",
        "",
    ]
    for vendor in sorted(by_vendor.keys(), key=str.lower):
        rows = by_vendor[vendor]
        parts.append(f"### {md_cell(vendor)}")
        parts.append("")
        parts.append(render_package_table(rows).rstrip())
        parts.append("")
    return "\n".join(parts)


def render_ack_section(official: list[dict[str, Any]], vendors: list[dict[str, Any]]) -> str:
    live_ids = {(s.get("package_id") or "") for s in official + vendors}
    # Always show full AgentNet official upstream thanks for known map entries that are live;
    # also list map entries we agentize even if temporarily offline? Prefer live-only + always-known first-party set.
    live_prefixes_hit: list[dict[str, str]] = []
    for ack in UPSTREAM_ACK:
        pref = ack["package_prefix"]
        if any(pid == pref or pid.startswith(pref + ".") or pid.startswith(pref) for pid in live_ids):
            live_prefixes_hit.append(ack)
        else:
            # Still credit if any live id contains the middle brand token
            brand = pref.split(".")[-1].lower()
            if any(brand in pid.lower() for pid in live_ids):
                live_prefixes_hit.append(ack)

    # Deduplicate acks while preserving order
    seen = set()
    unique_acks = []
    for a in live_prefixes_hit:
        if a["package_prefix"] in seen:
            continue
        seen.add(a["package_prefix"])
        unique_acks.append(a)

    parts = [
        "AgentNet official market packages are **agentized adaptations**. We do **not** claim ownership of the original software. Thanks to the upstream projects and communities:",
        "",
    ]
    if unique_acks:
        parts.extend(
            [
                "| Upstream | Project | Thanks for | Link |",
                "|---|---|---|---|",
            ]
        )
        for a in unique_acks:
            parts.append(
                f"| **{md_cell(a['upstream'])}** | {md_cell(a['project'])} | {md_cell(a['note'])} | [{md_cell(a['url'])}]({a['url']}) |"
            )
        parts.append("")
    else:
        parts.append("_No upstream-mapped packages are live in the catalog at the moment._")
        parts.append("")

    parts.extend(
        [
            "Trademarks and product names belong to their respective owners. Use of names is for identification of agentized integrations only.",
            "",
            "If you maintain an upstream project listed above and want a different credit line or link, open an issue or contact [support@aiagentnet.cloud](mailto:support@aiagentnet.cloud).",
            "",
        ]
    )
    return "\n".join(parts)


def render_sync_meta(sources_url: str, official_n: int, vendor_n: int, total: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"_Last auto-sync: **{now}** from `{sources_url}` · "
        f"official={official_n} · other-vendor={vendor_n} · live_total={total}. "
        f"Regenerate: `python3 scripts/sync_readme_from_share.py --write` "
        f"(or GitHub Action `sync-readme-from-share`)._\n"
    )


def replace_marker_block(text: str, start: str, end: str, body: str) -> str:
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        re.DOTALL,
    )
    replacement = f"{start}\n{body.rstrip()}\n{end}"
    if not pattern.search(text):
        raise ValueError(f"missing markers {start} … {end}")
    return pattern.sub(replacement, text, count=1)


def ensure_template(readme: str) -> str:
    """If markers missing (legacy README), wrap/replace whole file with standard skeleton."""
    need = [
        "<!-- AUTO:OFFICIAL_PACKAGES:START -->",
        "<!-- AUTO:VENDOR_PACKAGES:START -->",
        "<!-- AUTO:ACKNOWLEDGMENTS:START -->",
        "<!-- AUTO:SYNC_META:START -->",
    ]
    if all(m in readme for m in need):
        return readme
    return BASE_README_TEMPLATE


BASE_README_TEMPLATE = """# AGPK Market packages

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
_pending sync_
<!-- AUTO:OFFICIAL_PACKAGES:END -->

---

## Other vendors (community / third-party)

<!-- AUTO:VENDOR_PACKAGES:START -->
_pending sync_
<!-- AUTO:VENDOR_PACKAGES:END -->

---

## Acknowledgments

<!-- AUTO:ACKNOWLEDGMENTS:START -->
_pending sync_
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
_pending sync_
<!-- AUTO:SYNC_META:END -->
"""


def sync_readme(readme_path: str, sources_url: str, write: bool) -> tuple[bool, str]:
    sources = fetch_sources(sources_url)
    # public API already filters healthy|degraded; keep defensive filter
    live = [
        s
        for s in sources
        if str(s.get("status") or "").lower() in ("healthy", "degraded")
    ]
    live = dedupe_latest(live)
    official = dedupe_latest([s for s in live if is_official(s)])
    other = [s for s in live if not is_official(s)]
    other = dedupe_latest(other)
    by_vendor: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for s in other:
        by_vendor[(s.get("vendor_name") or "Unknown vendor").strip() or "Unknown vendor"].append(s)
    for k in by_vendor:
        by_vendor[k] = dedupe_latest(by_vendor[k])

    with open(readme_path, encoding="utf-8") as f:
        text = f.read()
    text = ensure_template(text)

    text = replace_marker_block(
        text,
        "<!-- AUTO:OFFICIAL_PACKAGES:START -->",
        "<!-- AUTO:OFFICIAL_PACKAGES:END -->",
        render_official_section(official),
    )
    text = replace_marker_block(
        text,
        "<!-- AUTO:VENDOR_PACKAGES:START -->",
        "<!-- AUTO:VENDOR_PACKAGES:END -->",
        render_vendor_section(dict(by_vendor)),
    )
    text = replace_marker_block(
        text,
        "<!-- AUTO:ACKNOWLEDGMENTS:START -->",
        "<!-- AUTO:ACKNOWLEDGMENTS:END -->",
        render_ack_section(official, other),
    )
    text = replace_marker_block(
        text,
        "<!-- AUTO:SYNC_META:START -->",
        "<!-- AUTO:SYNC_META:END -->",
        render_sync_meta(sources_url, len(official), len(other), len(live)),
    )

    if not write:
        return False, text
    with open(readme_path, "r", encoding="utf-8") as f:
        old = f.read()
    if old == text:
        return False, text
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(text)
    return True, text


def git_push_if_requested(repo_dir: str, changed: bool) -> None:
    if not changed:
        print("no README change; skip push")
        return
    env = os.environ.copy()
    subprocess.check_call(["git", "add", "README.md"], cwd=repo_dir, env=env)
    # only commit if staged diff
    st = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=repo_dir,
        env=env,
    )
    if st.returncode == 0:
        print("nothing staged")
        return
    msg = "docs: auto-sync official/vendor package tables from share catalog"
    subprocess.check_call(["git", "commit", "-m", msg], cwd=repo_dir, env=env)
    subprocess.check_call(["git", "push", "origin", "HEAD"], cwd=repo_dir, env=env)
    print("pushed README sync commit")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--readme",
        default="README.md",
        help="Path to AGPK-MARKET README.md",
    )
    ap.add_argument(
        "--sources-url",
        default=os.environ.get("SHARE_AGPK_SOURCES_URL", DEFAULT_SOURCES_URL),
    )
    ap.add_argument("--write", action="store_true", help="Write README in place")
    ap.add_argument(
        "--push",
        action="store_true",
        help="git commit+push README if changed (cwd = repo root)",
    )
    ap.add_argument(
        "--print",
        dest="do_print",
        action="store_true",
        help="Print resulting README to stdout",
    )
    args = ap.parse_args()
    readme_path = os.path.abspath(args.readme)
    if not os.path.isfile(readme_path) and args.write:
        # create from template
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(BASE_README_TEMPLATE)
    elif not os.path.isfile(readme_path):
        print(f"missing {readme_path}", file=sys.stderr)
        return 2

    try:
        changed, text = sync_readme(readme_path, args.sources_url, write=args.write)
    except urllib.error.URLError as e:
        print(f"fetch failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"sync failed: {e}", file=sys.stderr)
        return 1

    if args.do_print or not args.write:
        sys.stdout.write(text)
    print(
        f"\n# sync ok write={args.write} changed={changed} sources={args.sources_url}",
        file=sys.stderr,
    )
    if args.push:
        if not args.write:
            print("--push requires --write", file=sys.stderr)
            return 2
        git_push_if_requested(os.path.dirname(readme_path) or ".", changed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
