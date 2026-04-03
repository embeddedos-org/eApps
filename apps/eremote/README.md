# eRemote — Universal Smart Remote App

## Overview

eRemote transforms your device into a universal remote control using **Infrared (IR)**, **Bluetooth Low Energy (BLE)**, and **Wi-Fi**. It supports two operation modes:

1. **Direct Mode** — Phone IR blaster / BLE / Wi-Fi talks directly to the target device
2. **Hub Mode** — Phone sends commands via Wi-Fi to an eRemote Hub, which blasts IR/RF signals

The app dynamically adapts its control interface based on device type — TVs, soundbars, streaming devices, air conditioners, fans, projectors, and more.

## Core Concept

> "Search for a device → Identify it → Adapt UI → Control seamlessly"

## IR Protocol Support

eRemote implements three standard IR protocols plus raw learning:

### NEC Protocol (38 kHz)
- **Carrier**: 38 kHz modulated IR LED
- **Leader**: 9ms mark + 4.5ms space
- **Bit 0**: 562µs mark + 562µs space
- **Bit 1**: 562µs mark + 1687µs space
- **Frame**: address(8) + ~address(8) + command(8) + ~command(8) = 32 bits
- **Used by**: Samsung, LG, many Asian brands
- **Example hex**: Samsung TV Power = `E0E040BF`

### RC5 Protocol (36 kHz, Manchester)
- **Carrier**: 36 kHz
- **Encoding**: Manchester (bi-phase)
- **Bit period**: 1778µs (889µs half-bit)
- **Frame**: start(1) + field(1) + toggle(1) + address(5) + command(6) = 14 bits
- **Used by**: Philips, many European brands

### Sony SIRC Protocol (40 kHz)
- **Carrier**: 40 kHz
- **Leader**: 2400µs mark + 600µs space
- **Bit 0**: 600µs mark + 600µs space
- **Bit 1**: 1200µs mark + 600µs space
- **Frame**: command(7) + address(5/8/13) = 12/15/20 bits
- **Used by**: Sony TVs, AV equipment
- **Example hex**: Sony TV Power = `A90`

### RAW (Learned Signals)
- Captured as alternating mark/space pulse durations (µs)
- Carrier frequency measured by zero-crossing counting
- Stored as hex codes for replay

## Built-in IR Code Database

Pre-loaded codes for popular brands:

| Brand | Model | Protocol | Device Type |
|-------|-------|----------|-------------|
| Sony | Bravia | SIRC 12-bit | TV |
| Samsung | Smart TV | NEC | TV |
| LG | WebOS TV | NEC | TV |
| Samsung | HW-Q Soundbar | NEC | Soundbar |
| Daikin | FTK-Series | NEC ext. | AC |
| Apple | Apple TV 4K | BLE only | Streaming |

## Connection Modes

| Mode | Range | LOS Required | Direction | Use Case |
|------|-------|-------------|-----------|----------|
| **IR** | 10-30 ft | Yes | 1-way | Classic remotes, AC, fans |
| **BLE** | 30-50 ft | No | 2-way | Smart TVs, streaming devices |
| **Wi-Fi** | Network | No | 2-way | Smart TVs (SSDP/UPnP discovery) |
| **RF 433** | 100+ ft | No | 1-way | Fans, blinds (via Hub) |

### Direct Mode vs Hub Mode

- **Direct Mode**: Phone → IR blaster / BLE / Wi-Fi → Device
  - Requires phone with IR blaster (Xiaomi, OnePlus, OPPO, vivo, Realme)
  - Or BLE/Wi-Fi for smart devices
- **Hub Mode**: Phone → Wi-Fi → eRemote Hub → IR/RF blast
  - No IR blaster needed on phone
  - Control from anywhere (even remotely)
  - Hub stores learned codes in flash memory

## Learning Mode

When a device isn't in the database:

1. Tap **"Learn"** → state changes to `LEARN_WAITING`
2. Point your physical remote at the phone/hub IR receiver
3. Press the button → raw pulses captured (`LEARN_CAPTURING`)
4. Frequency + pulse durations decoded → `LEARN_DONE`
5. Hex code generated and mapped to the UI button
6. Stored per-device (up to 16 learned codes per device)

The captured signal includes:
- **Header pulse** (long "wake up" burst)
- **Binary data** (short/long pulses representing 0s and 1s)
- **Stop bit** (end marker)

## Smart Adaptation Engine

UI dynamically rebuilds based on device type:

| Device Type | Controls Shown |
|-------------|---------------|
| TV | D-pad, volume, channels, numpad, media |
| Soundbar | Volume, media |
| Streaming | D-pad, media, volume |
| AC | Temperature (16-30°C), fan speed, mode (Cool/Heat/Dry/Fan), swing |
| Custom | D-pad, volume, media (full layout) |

## Scenes (Macros)

Combine multiple device actions into one-tap automation:

| Scene | Actions |
|-------|---------|
| **Movie Mode** | TV Power On → HDMI Input 2 → Soundbar On |
| **Night Mode** | AC Temp → 20°C → TV Off |
| **Music Mode** | Soundbar On → Volume 60 |

Each step has configurable delay (ms) between commands.

## Scheduling

Time-based automation:

| Schedule | Time | Days | Action |
|----------|------|------|--------|
| AC Off Timer | 23:00 | Daily | AC Power Off |
| Morning TV | 07:30 | Weekdays | TV Power On |

## UI Features

### Device Cards
- Tap to switch active remote panel
- Shows device name + brand
- Active card highlighted with primary color
- "+" card to add new devices (up to 8)

### Connection Badges
- Toggle IR / BLE / Wi-Fi independently per device
- Hub mode switch
- Visual indicators for active connections

### Remote Controls
- **D-Pad**: Up/Down/Left/Right/OK with toast feedback
- **Volume**: Bounded 0-100, increment/decrement
- **Channel**: Circular looping (999 → 1)
- **Number Pad**: 0-9 + Menu + Back
- **Media**: Play/Pause toggle, FF, Rewind, Skip
- **Power**: Glowing teal (ON) / dimmed (OFF)

### Bottom Navigation
| Tab | Status |
|-----|--------|
| Remote | Active |
| Scenes | Functional |
| Schedule | Functional |
| Settings | Stub |

## Architecture

```
┌─────────────────────────────────────────────┐
│           Input Layer                       │
│   Touch events → LVGL callbacks             │
├─────────────────────────────────────────────┤
│           Engine Layer (eremote_engine.c)    │
│   IR Protocol Engine (NEC/RC5/SIRC/RAW)     │
│   IR Code Database (Pronto hex codes)       │
│   Learning Mode (raw pulse capture)         │
│   Command Dispatcher (IR/BLE/WiFi/Hub)      │
│   Scenes Engine (macro sequencer)           │
│   Schedule Engine (time-based automation)   │
├─────────────────────────────────────────────┤
│           UI Layer (eremote.c)              │
│   Dynamic remote layouts per device type    │
│   Device cards with connection badges       │
│   Bottom navigation tabs                    │
│   Toast feedback system                     │
├─────────────────────────────────────────────┤
│           Transport Layer                   │
│   IR Blaster (38/40kHz carrier modulation)  │
│   BLE GATT (characteristic write)          │
│   Wi-Fi (SSDP/UPnP discovery, HTTP/WS)    │
│   Hub Relay (Wi-Fi → Hub → IR/RF blast)    │
└─────────────────────────────────────────────┘
```

## Phone Compatibility (IR Blaster)

| Brand | IR Blaster | Recommended Mode |
|-------|-----------|-----------------|
| Xiaomi / Redmi / Poco | ✅ Yes | Direct IR |
| OnePlus | ✅ Yes | Direct IR |
| OPPO | ✅ Some models | Direct IR |
| vivo / iQOO | ✅ Some models | Direct IR |
| Realme | ✅ Some models | Direct IR |
| Samsung Galaxy | ❌ No | BLE/WiFi or Hub |
| Google Pixel | ❌ No | BLE/WiFi or Hub |
| Apple iPhone | ❌ No | BLE/WiFi or Hub |

## Build

```bash
cmake -DEAPPS_BUILD_CONNECTIVITY=ON ..
make eremote
```

## Files

| File | Purpose |
|------|---------|
| `eremote.h` | Types, enums, IR code structs, engine API |
| `eremote.c` | LVGL UI layer, lifecycle |
| `eremote_engine.c` | IR protocols, code DB, learning, dispatch, scenes, schedules |
| `CMakeLists.txt` | Build configuration |

## Future Enhancements

- Wi-Fi smart device integration (SSDP/UPnP auto-discovery)
- Voice control (Google Assistant / Siri)
- Cloud sync for learned codes and layouts
- AI-based device recognition from IR signatures
- Custom remote layout builder
- IR dongle support for phones without IR blaster
- RF 433 MHz support for fans and blinds

## Philosophy

> eRemote is not just a remote — it is a universal control system that adapts to the device, not the user.
