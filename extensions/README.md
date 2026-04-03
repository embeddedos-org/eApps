# 🧩 Extensions

Browser and editor extensions from the **eOffice** ecosystem, merged into eApps.

## Contents

| Extension | Platform | Source |
|---|---|---|
| eOffice for Chrome | Chrome Web Store | `browser/chrome/` |
| eOffice for Firefox | Firefox Add-ons | `browser/firefox/` |
| eOffice for Safari | Safari Extensions | `safari/` |
| eOffice for VS Code | VS Code Marketplace | `vscode/` |
| eOffice for JetBrains | JetBrains Plugins | `jetbrains/` |
| eOffice for Obsidian | Obsidian Plugins | `obsidian/` |
| eOffice for Slack | Slack App Directory | `slack/` |
| eOffice for Raycast | Raycast Store | `raycast/` |
| eOffice GitHub App | GitHub Apps | `github/` |
| eOffice for Google Workspace | Google Workspace | `google-workspace/` |
| eOffice for Office 365 | Microsoft AppSource | `office365/` |

## Origin

Merged from [embeddedos-org/eOffice → extensions/](https://github.com/embeddedos-org/eOffice/tree/main/extensions)

## Build

Each extension has its own build process. See the individual `README.md` or `package.json` inside each folder.

```bash
cd browser/chrome && npm install && npm run build
cd vscode && npm install && npm run package
```

## Release

CI/CD via GitHub Actions builds and publishes:
- `.zip` / `.crx` for Chrome
- `.xpi` for Firefox
- `.vsix` for VS Code
- Native packages for other platforms

All release artifacts are attached to [GitHub Releases](https://github.com/embeddedos-org/eApps/releases) and registered in `data/apps.json`.
