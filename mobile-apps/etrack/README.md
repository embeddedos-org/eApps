# eTrack — Universal Package Tracking

Privacy-first, offline-first universal tracking app for packages, flights, and immigration cases.

## Features

- 📦 **Multi-carrier tracking** — USPS, FedEx, UPS, DHL, and more
- ✈️ **Flight tracking** — via AviationStack API
- 🏛️ **Immigration case tracking** — USCIS case numbers (IOE, EAC, WAC, etc.)
- 🔍 **Auto-detect carrier** — regex-based detection from tracking number format
- 💬 **Plain-language status** — translates carrier jargon into human-readable explanations
- ⏱️ **ETA prediction** — rule-based delivery estimates
- 🔒 **Privacy-first** — all data stored locally, no accounts, no cloud
- 🌙 **Dark mode** — full light/dark theme support
- 🔔 **Local notifications** — reminders without cloud messaging

## Architecture

```
Mobile / Web
[Flutter UI + Riverpod State]
         ↓
[SQLite Local Database]
         ↓
[Optional Free API Layer] ← Only on manual refresh
```

## Getting Started

```bash
git clone https://github.com/yourusername/eTrack.git
cd eTrack
flutter pub get
flutter run
```

## API Keys (Optional)

The app works fully offline without any API keys. To enable live tracking:

1. Go to **Settings** → **API Keys**
2. Enter your free API keys:
   - **USPS**: Register at [usps.com/webtools](https://registration.shippingapis.com/)
   - **FedEx**: Get keys at [developer.fedex.com](https://developer.fedex.com/)
   - **UPS**: Get keys at [developer.ups.com](https://developer.ups.com/)
   - **AviationStack**: Register at [aviationstack.com](https://aviationstack.com/)

All keys are stored locally on your device only.

## Privacy

- No accounts required
- Data stored locally only (SQLite)
- No GPS or Bluetooth access
- Optional APIs are stateless
- Data removed on app uninstall

## License

MIT
