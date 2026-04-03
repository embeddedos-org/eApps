# eOffice Desktop

Native desktop app for Windows, macOS, and Linux.

## Development

```bash
cd desktop
npm install
npm start        # Run in development mode
```

## Build Installers

```bash
npm run build:win    # Windows (.exe installer + portable)
npm run build:mac    # macOS (.dmg + .zip)
npm run build:linux  # Linux (.AppImage + .deb + .rpm)
npm run build:all    # All platforms
```

## Output

Installers are written to `desktop/dist/`:

| Platform | Format | File |
|----------|--------|------|
| Windows  | NSIS Installer | `eOffice Suite Setup 0.1.0.exe` |
| Windows  | Portable | `eOffice Suite 0.1.0.exe` |
| macOS    | DMG | `eOffice Suite-0.1.0.dmg` |
| macOS    | ZIP | `eOffice Suite-0.1.0-mac.zip` |
| Linux    | AppImage | `eOffice Suite-0.1.0.AppImage` |
| Linux    | Debian | `eoffice-suite_0.1.0_amd64.deb` |
| Linux    | RPM | `eoffice-suite-0.1.0.x86_64.rpm` |

## Requirements

- Node.js 18+ (for building only)
- electron-builder handles all platform packaging
