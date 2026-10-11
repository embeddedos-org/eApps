# AI capability permissions — install-time permission model

Track 1. This document defines how the AI capabilities an app declares in
`data/apps.json` (`ai_capabilities`, per `schemas/app-metadata.schema.json`)
become install-time user consent and runtime enforcement.

## The vocabulary

The curated vocabulary lives in `schemas/ai-capabilities.registry.json` — it
is the single source of truth. Only these capability names are valid; anything
else is rejected at catalogue validation time by `scripts/validate_apps.py`
(fail-closed). To add a capability, extend the registry — never accept a
dotted name the registry does not know.

| Capability | Kind | Default access | Meaning |
|---|---|---|---|
| `camera_frames` | sensor | `none` | Camera frames (stills, video, depth where available) |
| `mic_frames` | sensor | `none` | Microphone audio frames |
| `speaker_frames` | effector | `none` | Audio rendered through the device speaker (TTS, alerts) |
| `inference.local` | compute | `read` | On-device inference — compute only, no data leaves the device |
| `inference.cloud` | compute+export | `none` | Off-device inference — data leaves the device |
| `npu` | compute | `read` | On-device neural accelerator (Track-1 accelerator HAL tier) |
| `location` | personal data | `none` | Device location (GNSS, network, fused) |
| `contacts` | personal data | `none` | Device contacts/people graph |

Access levels are `none`, `read`, `write`, `readwrite`. Their meaning depends
on the kind:

- **Sensors / personal data** (`camera_frames`, `mic_frames`, `location`,
  `contacts`): `read` = consume the data; `write` = consume *and* reconfigure
  the source (e.g. capture rate, resolution); `readwrite` = both.
- **Effectors** (`speaker_frames`): `read` = query playback state;
  `write` = emit audio; `readwrite` = both.
- **Compute** (`inference.local`, `inference.cloud`, `npu`): `read` = run
  inference/submit jobs; `write` = install models, manage partitions, or
  train with app data; `readwrite` = both.

Declaring `none` is an explicit no-access intent (e.g. the app's entry in
`data/apps.json` today declares `camera_frames: "none"` to state the camera
is never used). Absent `ai_capabilities` means the app declares no AI
capabilities at all.

## Default access — the fail-closed baseline

`default_access` in the registry is the level granted at install **with no
user decision**. A default of `none` means *nothing flows until the user
explicitly allows it* — the installer must prompt (see below).

- **Sensors, effectors, personal data, and cloud inference default to
  `none`.** Camera, mic, speaker, location, contacts, and anything that sends
  data off the device are never granted silently.
- **On-device compute defaults to `read`.** `inference.local` and `npu` are
  compute over data the app may already access; they cannot exfiltrate by
  themselves, so `read` is granted at install and shown on the granted list.
  (`write` — installing models, managing NPU partitions — still prompts.)

## Install-time prompts: declared level -> UX

For each declared capability, the installer maps the *requested* level to
user-facing UX, bounded by the registry default:

| Requested | Registry default `none` (sensitive) | Registry default `read` (on-device compute) |
|---|---|---|
| `none` | No prompt. Access denied. | No prompt. Access denied. |
| `read` | Prompt: **Allow / Ask every time / Deny**. Nothing granted until the user decides. | Granted silently at install; listed under "granted". |
| `write` | Prompt: **Allow / Ask every time / Deny**. Nothing granted until the user decides. | Prompt: **Allow / Deny**. |
| `readwrite` | Prompt: **Allow / Ask every time / Deny**. Nothing granted until the user decides. | Prompt: **Allow / Deny**. |

Rules:

1. The granted level never exceeds the requested level.
2. For `default_access: "none"` capabilities, the grant is zero until the user
   picks **Allow** (or **Ask every time**, which re-prompts per session).
   Install does not proceed with partial silent grants.
3. **Deny** on any requested capability either blocks the install or installs
   with the capability permanently off for that app — the app's choice, stated
   in its manifest metadata; the platform never silently downgrades.
4. Upgrades: if an app update adds a capability (or raises a level), the new
   capability goes through the prompt matrix again at update time. The update
   must not land the new grant without consent.

## Runtime binding

Declarations and prompts are only the front half. Enforcement binds to two
existing Track-1 mechanisms:

1. **#162 envelope claims.** After the install-time prompts, the installer
   mints the *granted* capabilities (name + granted level) as claims inside
   the app's #162 package-signature envelope. The envelope is Ed25519-signed,
   so the granted set is tamper-evident: the OS loader verifies the envelope
   at launch and refuses to start the app with capabilities beyond its claims.

2. **eIPC `Message.Capability`.** At runtime, any message carrying frames,
   tensors, or other capability-gated payloads must set
   `core.Message.Capability` to the dotted capability name (e.g.
   `"mic_frames"`, `"inference.local"`). The receiving driver/broker checks
   the sender's envelope claims before delivering: no claim, no delivery.
   Unknown or empty `Capability` on a gated payload is rejected —
   fail-closed, matching the registry.

The chain is: `data/apps.json` declares -> registry validates the names ->
installer prompts -> granted set minted as #162 envelope claims ->
`Message.Capability` checked against claims at delivery.

## Fail-closed summary

- Unknown capability name in `data/apps.json` -> catalogue validation fails;
  the app cannot be listed or installed.
- Unknown capability name in the registry -> impossible; the registry is the
  only place names are defined.
- Bad access level -> catalogue validation fails.
- Sensitive capability with no user decision -> zero access, always.
- `Message.Capability` unset or unclaimed on a gated payload -> delivery refused.
