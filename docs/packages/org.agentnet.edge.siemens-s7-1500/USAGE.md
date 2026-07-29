> **Human long-form docs** (AGPK-MARKET).  
> Package tarball keeps a **short** USAGE with pointers only — agents discover URIs via `agpk.list_commands` → `faces[].docs`.  
> Package: `org.agentnet.edge.siemens-s7-1500` · AGPK protocol: optional read (`docs.read_policy=optional`).

# USAGE — org.agentnet.edge.siemens-s7-1500

**Siemens SIMATIC S7-1500 Edge Bridge** (official AGPK IoT sample)

Agent-first **tag face** over **sim / MQTT / CoAP**.  
This is **not** a full TIA Portal replacement: agents control mapped tags, not engineering projects.

| Item | Value |
|------|--------|
| package_id | `org.agentnet.edge.siemens-s7-1500` |
| version | **1.0.1** |
| driver | `agentx_edge_transport` |
| runtime binary | `agentx-edge-driver` (AgentOS X / `crates/agentx-edge`) |
| default profile | `payload/device-profile.json` |

Also see: **`AGENT_CAPABILITIES.md`** (command ids + ACL).

---

## 0. What you need

| Component | Role |
|-----------|------|
| AgentOS X with AGPK install | install / list_commands / invoke |
| This package | device profile + shell entry + command face |
| `agentx-edge-driver` on PATH or `/opt/agentx/bin` or `payload/bin/` | real MQTT/CoAP/sim engine |
| (Optional) MQTT broker | real plant path, e.g. Mosquitto / Industrial Edge MQTT |
| (Optional) S7 ↔ MQTT gateway | maps PLC DBs to MQTT topics (Node-RED, IE apps, etc.) |

**No PLC required** for the default **sim** path.

---

## 1. Step-by-step — offline sim (no broker, no PLC)

### Step 1 — Ensure the edge driver binary

```bash
# Prefer platform install after FULL agentx / agentos-x build:
which agentx-edge-driver || ls /opt/agentx/bin/agentx-edge-driver

# Or build from agentos-x tip:
#   cargo build -p agentx-edge --release --bin agentx-edge-driver
#   sudo install -m 755 target/release/agentx-edge-driver /opt/agentx/bin/
```

### Step 2 — Install the AGPK package

```bash
# From market (after share healthy):
agentx agpk list-options --query siemens
agentx agpk install org.agentnet.edge.siemens-s7-1500 --approve -y

# Or from a local tarball / directory:
agentx agpk install /path/to/org.agentnet.edge.siemens-s7-1500 --approve -y
```

### Step 3 — Discover commands

```bash
agentx agpk list-commands --package-id org.agentnet.edge.siemens-s7-1500
```

Expect ids like:

- `…device.list`
- `…device.read` / `…device.write`
- `…device.acl.get` / `…device.acl.set`
- `…device.subscribe`

### Step 4 — List devices & tags (sim)

```bash
agentx agpk invoke org.agentnet.edge.siemens-s7-1500.device.list
```

Default transport is **sim** (in-memory shadow of `device-profile.json` tags).

### Step 5 — Read a tag

```bash
agentx agpk invoke org.agentnet.edge.siemens-s7-1500.device.read \
  --args '{"tag":"DB1.DBD0"}'
```

Aliases: tag name `line_speed` also works if present in the profile.

### Step 6 — Write a tag (ACL)

Writes need an allowed **actor group**:

```bash
agentx agpk invoke org.agentnet.edge.siemens-s7-1500.device.write \
  --args '{"tag":"DB1.DBX4.0","value":true,"actor_group":"operator"}'
```

Allowed groups (demo profile): `operator` | `engineer` | `admin`.  
**Denied by design:** `I0.0` (estop input) — expect `acl_denied`.

### Step 7 — ACL inspect

```bash
agentx agpk invoke org.agentnet.edge.siemens-s7-1500.device.acl.get
```

### Step 8 — Subscribe recipe (not a long-lived process)

```bash
agentx agpk invoke org.agentnet.edge.siemens-s7-1500.device.subscribe \
  --args '{"tag":"DB1.DBD0"}'
```

Returns MQTT topic / CoAP path recipe for agents to attach their own subscriber.

---

## 2. Step-by-step — MQTT wiring (plant / lab)

### Architecture (recommended)

```text
  AgentOS X agent
       │  agpk.invoke (read/write/list)
       ▼
  agentx-edge-driver  ──MQTT──►  Broker (e.g. Mosquitto / IE MQTT)
                                      │
                                      ▼
                              S7 gateway / Industrial Edge app
                                      │
                                      ▼
                              SIMATIC S7-1500 (DB / I / Q)
```

The AGPK package talks **MQTT topics**, not ISO-on-TCP/Snap7 directly.  
Your gateway is responsible for PLC protocol and for publishing/consuming the tag topics below.

### Topic map (demo profile)

Prefix (from `device-profile.json`):

```text
agentos/edge/s7-1500/s1500-demo-01
```

| Tag id | MQTT topic (JSON payload = value) |
|--------|-------------------------------------|
| `DB1.DBD0` | `agentos/edge/s7-1500/s1500-demo-01/tags/DB1_DBD0` |
| `DB1.DBX4.0` | `…/tags/DB1_DBX4_0` |
| `DB1.DBW6` | `…/tags/DB1_DBW6` |
| `I0.0` | `…/tags/I0_0` |
| `Q0.0` | `…/tags/Q0_0` |
| status | `agentos/edge/s7-1500/s1500-demo-01/status` |

Rules:

- Dots in tag ids become **underscores** in the topic last segment.
- Payload is **JSON** (number / bool / string / object). Examples: `12.5`, `true`, `"idle"`.
- **Write** = MQTT **publish** to the tag topic (QoS 1 by default).
- **Read** = MQTT **subscribe** and wait for a message (retained preferred).

### Lab: Mosquitto on the same LAN

**A. Start broker (example)**

```bash
# Docker quick lab
docker run --rm -p 1883:1883 eclipse-mosquitto:2
# or host package: mosquitto -c /etc/mosquitto/mosquitto.conf
```

**B. Publish retained telemetry (gateway simulator)**

```bash
# Line speed (DB1.DBD0)
mosquitto_pub -h 192.168.1.10 -p 1883 -r \
  -t 'agentos/edge/s7-1500/s1500-demo-01/tags/DB1_DBD0' \
  -m '12.5'

# Motor run
mosquitto_pub -h 192.168.1.10 -p 1883 -r \
  -t 'agentos/edge/s7-1500/s1500-demo-01/tags/DB1_DBX4_0' \
  -m 'false'
```

**C. Point AgentOS edge driver at the broker**

Environment for the agent process / session (or install unit drop-in):

```bash
export EDGE_TRANSPORT=mqtt          # or mqtt_prefer
export EDGE_MQTT_URL=mqtt://192.168.1.10:1883
export EDGE_ACTOR_GROUP=operator    # default group for writes if args omit it
# optional:
# export EDGE_MQTT_CLIENT_ID=agentos-s7-bridge-01
# export EDGE_PROFILE=/path/to/device-profile.json
# export EDGE_TIMEOUT_MS=5000
```

If the package is already installed, profile defaults to:

```text
$AGPK_INSTALL_ROOT/device-profile.json
```

**D. Invoke over MQTT**

```bash
agentx agpk invoke org.agentnet.edge.siemens-s7-1500.device.list
agentx agpk invoke org.agentnet.edge.siemens-s7-1500.device.read \
  --args '{"tag":"DB1.DBD0"}'
agentx agpk invoke org.agentnet.edge.siemens-s7-1500.device.write \
  --args '{"tag":"DB1.DBX4.0","value":true,"actor_group":"operator"}'
```

**E. Observe writes on the bus**

```bash
mosquitto_sub -h 192.168.1.10 -p 1883 -v \
  -t 'agentos/edge/s7-1500/s1500-demo-01/#'
```

You should see publishes when the agent writes tags.

### Gateway notes (real S7-1500)

Typical production pattern:

1. **Industrial Edge / Node-RED / custom gateway** near the PLC.  
2. Gateway reads/writes S7 (OPC UA, S7 protocol, etc.).  
3. Gateway **mirrors** each mapped tag to the MQTT topics above (retain telemetry).  
4. AgentOS only sees MQTT — no PLC credentials inside the AGPK tarball.

Example mapping table for integrators:

| PLC address | Logical name | MQTT topic suffix | Access |
|-------------|--------------|-------------------|--------|
| DB1.DBD0 | line_speed | `tags/DB1_DBD0` | rw |
| DB1.DBX4.0 | motor_run | `tags/DB1_DBX4_0` | rw |
| DB1.DBW6 | batch_count | `tags/DB1_DBW6` | rw |
| I0.0 | estop | `tags/I0_0` | ro only (ACL deny write) |
| Q0.0 | beacon | `tags/Q0_0` | rw |

To customize tags: edit `device-profile.json` (or ship a forked package version), keep topic naming rules consistent, reinstall.

### Auth / TLS (MQTT)

Demo defaults are **plain MQTT** (`mqtt://host:1883`).  
For production brokers with TLS/auth, extend `agentx-edge` config / broker ACLs; **do not** put broker passwords in the AGPK package.

---

## 3. CoAP path (optional)

```bash
export EDGE_TRANSPORT=coap
export EDGE_COAP_HOST=192.168.1.20
export EDGE_COAP_PORT=5683
```

Tag paths (demo):

```text
/s7/1500/s1500-demo-01/tags/DB1_DBD0
```

- **read** → CoAP GET  
- **write** → CoAP PUT (JSON body)

---

## 4. Transport modes cheat sheet

| `EDGE_TRANSPORT` | Behavior |
|------------------|----------|
| `sim` (default) | In-memory tags only |
| `mqtt` | Require `EDGE_MQTT_URL`; hard fail if broker down |
| `mqtt_prefer` | Try MQTT, fall back to sim on failure |
| `coap` | Require `EDGE_COAP_HOST` |

---

## 5. Invoke args reference

| op | args JSON |
|----|-----------|
| list | `{}` |
| read | `{"tag":"DB1.DBD0"}` |
| write | `{"tag":"DB1.DBX4.0","value":true,"actor_group":"operator"}` |
| acl.get | `{}` |
| acl.set | `{"acl":{"write_groups":["operator","engineer"]}}` |
| subscribe | `{"tag":"DB1.DBD0"}` optional |

Platform also injects: `AGPK_EDGE_OP`, `AGPK_INVOKE_ARGS_JSON`, `AGPK_INSTALL_ROOT`, `AGPK_PACKAGE_ID`.

---

## 6. Troubleshooting

| Symptom | Check |
|---------|--------|
| `agentx-edge-driver not found` | Install binary to PATH / `/opt/agentx/bin` / `payload/bin` |
| read timeout on MQTT | Publish **retained** values; confirm topic spelling (`DB1_DBD0` not `DB1.DBD0` in topic) |
| write `acl_denied` | Pass `actor_group`; do not write `I0.0` |
| empty list commands | Reinstall package; confirm C1 `agent-commands.json` registered |
| broker connection refused | `EDGE_MQTT_URL`, firewall, broker bind address |

---

## 7. Uninstall

```bash
agentx agpk remove org.agentnet.edge.siemens-s7-1500 --approve -y
```

---

## 8. Scope reminder

| In scope | Out of scope (this sample) |
|----------|----------------------------|
| Tag list/read/write/ACL via agent | Full TIA Portal engineering |
| MQTT/CoAP edge facade + sim | Native Snap7 in this package version |
| Demo S7 address map | Entire plant PROFINET design |

Human-facing result presentation: **projection.*** — not vendor HMI as the primary agent path.


---

## Production deployment (industrial — not demo)

See monorepo SPEC_AGPK_Edge_工业生产就绪_标签总线_2026-07-29.md.

### Envelope / write-ack / plant env

Envelope schema `agpk.edge.tag-value.v1` on topic `…/tags/<TAG>`.
Write ack on `…/tags/<TAG>/ack` as `agpk.edge.write-ack.v1`.

```bash
export EDGE_MODE=production
export EDGE_TRANSPORT=mqtt
export EDGE_MQTT_URL=mqtt://broker:1883
export EDGE_MQTT_USERNAME=agentos
export EDGE_MQTT_PASSWORD=***
export EDGE_REQUIRE_WRITE_ACK=1
```

Credentials never in AGPK tarball. Runtime agentx-edge >= 0.2.
