# Screen Record Core — long guide (market copy)

**Package:** `org.agentnet.screen.record.core` **1.0.0**  
Canonical longform lives on AGPK-MARKET under `docs/packages/org.agentnet.screen.record.core/USAGE.md`.

## What it is

Agent-first **session recording** on AgentOS X / Linux desktop:

1. Install AGPK package (no ISO rebake).
2. Invoke `screen.record.*` commands.
3. Get on-disk segments + `manifest.json` under `$AGENTX_HOME/agpk/runtime/screen-record/sessions/`.

Independent of `org.agentnet.desktop.control.*` (clicks/keys are a different product).

## State machine

| State | Meaning | Resume? |
|-------|---------|---------|
| recording | capture running | — |
| paused | sealed segment | yes |
| stopped | sealed segment | **yes** (product rule) |
| interrupted | crash/kill/display loss | yes, **manual only** |
| finalized | closed | **no** |

**stop does not end the session** — only `finalize` does.

## Commands (invoke)

All verbs accept JSON args via `AGPK_INVOKE_ARGS_JSON` or `run_cmd.sh <verb> '<json>'`.

### start

```json
{"fps": 15, "audio": false, "region": null}
```

Returns `session_id`, `segment_id` (`001`), `state=recording`.

### pause / stop

```json
{"session_id": "<id>"}
```

Both seal the current segment. Session remains resumable.

### resume

```json
{"session_id": "<id>"}
```

Starts segment `N+1` with **locked** config from `config.json` (no silent display/fps change).

### finalize

```json
{"session_id": "<id>", "compose": false}
```

Returns segment list. Further `resume` → `invalid_state`.

### status / list_sessions / list_segments

Query; `status` and list paths run a **recover_scan**: if `state==recording` but capture PID is dead → mark `interrupted` (never auto-resume).

### abandon

```json
{"session_id": "<id>", "confirm": true, "delete": true}
```

## Dependencies

| Env | Role |
|-----|------|
| `ffmpeg` on PATH | Real capture (X11 `x11grab`; macOS avfoundation best-effort) |
| Graphical session | `DISPLAY` for X11; Wayland portal path not fully wired in 1.0.0 → `display_unavailable` |
| `RECORD_ENGINE=synthetic` | Lab/E2E without display (writes `.bin` segments) |

## Install (developer / agent)

```bash
export AGPK_INSTALL_ROOT=/opt/agentx/agpk/org.agentnet.screen.record.core
sh INSTALL
sh run_cmd.sh start '{"fps":15}'
```

On AgentOS X with AGPK registry: use platform `agpk install` + `agpk.invoke` for the same command ids.

## Lab E2E

```bash
bash lab/run_record_e2e.sh
# expect RECORD_E2E_PASS
```

## Privacy

- Default store under `$AGENTX_HOME` with mode 0600/0700.
- No network upload.
- Microphone only if `audio:true` (ffmpeg path).

## Errors

See package `AGENT_CAPABILITIES.md` for stable `code` strings (`already_recording`, `invalid_state`, `engine_missing`, …).
