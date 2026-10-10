# WASM runtime integration architecture (WAMR on EoS)

The AkiraOS study (`wasm-app-model-study.md`) concluded WAMR is the
sandbox candidate. This note is the architecture for embedding WAMR in
the eApps runtime: how manifests become sandboxes, what the per-app
limits are, and how OTA updates flow. Decision points carry
recommendations; the ones marked **[DECIDE]** need a maintainer call
before implementation.

## Runtime shape

```text
+------------------- eApps runtime (EoS process) -------------------+
|  manifest ──► capability map ──► WAMR instance per app             |
|                                                                    |
|  app A (wasm)      app B (wasm)                                    |
|  ┌──────────┐      ┌──────────┐                                    |
|  │ linear   │      │ linear   │   one WAMR instance per app:       |
|  │ memory   │      │ memory   │   a crash in A cannot touch B      |
|  │ 64 KiB   │      │ 256 KiB  │                                    |
|  └──────────┘      └──────────┘                                    |
|  host functions = the ONLY syscall surface (capability-gated)      |
+-------------------------------------------------------------------+
```

One WAMR instance per app (not one runtime with many modules): the
instance boundary is the fault-isolation boundary. An app that traps
kills its instance; the runtime restarts or retires it per policy.

**Interpreter vs AOT.** Interpreter for the smallest targets (no
executable-memory requirement, smallest TCB); AOT where flash allows
and the target permits W^X carve-outs. The manifest declares which the
app was built for; the runtime refuses to run an AOT module on a target
without executable-memory support (fail closed, not fallback).

## Manifest → capability mapping

The manifest declares capabilities; the #162 envelope signs them; the
runtime enforces them at the host-function boundary:

| Manifest capability | Host surface granted | Denied by default |
|---|---|---|
| `camera` | `eos_camera_*` host functions | mic, network |
| `mic` | `eos_audio_capture_*` | camera, network |
| `npu` | `eos_npu_submit_*` (quota'd) | raw DMA |
| `network` | `eos_net_*` (allowlisted hosts) | raw sockets |
| `storage` | namespaced KV dir only | whole FS |

No capability → no host function: an app that does not declare `network`
gets a WAMR instance with zero network imports. The mapping is
deny-by-default; adding a capability is a manifest change, which is a
re-sign event, which is an update the user approves. (Track 1: AI
capability declarations — needs camera/NPU/mic — are this table's
AI-flavored rows.)

**[DECIDE]** Capability *versioning*: when eApps adds a new host
function, do old manifests keep working unchanged (additive only), or do
manifests pin a capability-schema version? Recommendation: additive-only
with a schema version field reserved for breaking changes.

## Per-app sandbox limits

Enforced by the runtime at instance creation, from the manifest (with
runtime ceilings no manifest can exceed):

- **Linear memory cap** — per-app maximum (e.g. 64 KiB – 1 MiB by tier);
  growth beyond the cap traps.
- **Fuel / instruction budget** — per-tick execution cap so a hot loop in
  one app cannot starve the others; exceeding it suspends the instance
  to the next tick.
- **NPU quota** — submissions per second; the NPU is the scarcest shared
  resource on vision SKUs.
- **Host-call rate limit** — host functions are the exfiltration surface;
  bursty call patterns are throttled and logged.

Limits are declared in the manifest and *signed* — an app cannot
self-escalate its own limits without a re-signed manifest (which the
user must approve as an update).

## OTA update flow

Apps update independently of the firmware image (the marketplace model):

1. Marketplace publishes the new `.eapp` (WASM module + manifest).
2. The runtime verifies the #162 envelope (signature + capability set)
   **before** touching the running instance.
3. New instance is created alongside the old; state migration runs if
   the manifest declares a migration entry point.
4. Cutover is atomic: the old instance is retired only after the new one
   passes its first-tick health check. A failed update leaves the old
   app running — never a half-updated app.

Rollback is a first-class operation: the runtime keeps the last known
good `.eapp` until the new version completes N successful ticks.

## What this note does not decide

WAMR-vs-alternative evaluation (the study says evaluate before
inventing), the exact memory-tier table per board class, and the
migration-entry ABI — all tracked as implementation work items once the
**[DECIDE]** above is called.
