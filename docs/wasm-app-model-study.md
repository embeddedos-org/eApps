# AkiraOS: a shipped reference for the eApps app model

**AkiraOS** (Zephyr-based) ships the app model eApps is designing
toward: **sandboxed WASM apps via WAMR**, up to 8 apps, OTA-deployable
**without reflash**, one binary running on ESP32-S3 / nRF5x / STM32.

## What AkiraOS proves

- **Third-party apps on MCUs without reflash is shippable.** The WASM
  sandbox is the trust boundary: apps cannot touch hardware except
  through the host's capability surface.
- **One binary, many chips.** WAMR's interpreter/AOT options make the
  portability story real across the ESP32-S3 / nRF5x / STM32 spread —
  the same spread eApps targets.
- **OTA as the update primitive.** Apps update independently of the
  firmware image — the marketplace model, not the monolith model.

## What eApps should borrow

1. **Manifest-declared capabilities → install-time permission model.**
   AkiraOS's sandbox works because the app's powers are declared up
   front. eApps manifests should declare capabilities
   (camera/NPU/mic/network/storage) at install time, enforced by the
   same capability envelope the #162 package signature signs
   (see `embeddedos-org/eos` secure-boot work).
2. **WASM/WAMR as the sandbox candidate.** Not the only option, but the
   only one with a shipped MCU track record to point at. Evaluate WAMR
   (interpreter for the smallest targets, AOT where flash allows)
   against eApps' isolation requirements before inventing a sandbox.
3. **OTA-deployable app packages.** The marketplace (`docs/marketplace-architecture.md`)
   should treat app updates as first-class OTA artifacts, versioned
   independently of the OS image.

## What doesn't transfer

- AkiraOS is Zephyr-based; eApps targets EoS. The sandbox *pattern*
  transfers, the integration points don't — eApps needs its own
  WAMR-on-EoS bring-up (host functions, syscall surface, memory
  isolation) as a tracked work item.
- "Up to 8 apps" is AkiraOS's packaging choice, not a law; eApps'
  limit will fall out of the memory model.

## Cross-references

- `docs/architecture.md` — the eApps architecture this study informs.
- `docs/marketplace-architecture.md` — where OTA app packages land.
- Track 1: eApps AI capability declarations in app manifests
  (needs camera/NPU/mic) are the AI-flavored version of the same
  install-time permission model.
