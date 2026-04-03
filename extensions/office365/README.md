# eOffice for Microsoft 365

Office Add-in that brings eOffice apps and eBot AI assistant into Word, Excel, PowerPoint, and Outlook.

## Features

- **eBot AI Chat** — Ask eBot questions with document context directly from the task pane
- **Summarize with eBot** — Select text and get an AI-powered summary via ribbon button
- **Rewrite with eBot** — Rewrite selected text for clarity and professionalism
- **App Launcher** — Quick access to all 9 eOffice apps (eDocs, eNotes, eSheets, eSlides, eMail, eDrive, eConnect, eForms, ePlanner)
- **Document Integration** — Read/write selected text in Word, Excel, PowerPoint

## Prerequisites

- Node.js 18+
- eOffice backend running on `localhost:3001`
- Microsoft 365 subscription (for sideloading)

## Setup

```bash
cd extensions/office365
npm install
npm run dev
```

## Sideloading

### Word / Excel / PowerPoint (Desktop)

1. Run `npm run sideload` to start the dev server and sideload automatically
2. Or manually: **Insert → My Add-ins → Upload My Add-in** → select `manifest.xml`
3. The eOffice group appears in the Home tab ribbon

### Word / Excel (Web)

1. Open Office on the web (office.com)
2. Open a document → **Insert → Office Add-ins → Upload My Add-in**
3. Upload `manifest.xml`
4. The eOffice panel appears in the ribbon

### Outlook

1. Go to **Outlook → Settings → Manage Integrations → Custom Add-ins**
2. Upload `manifest.xml`
3. eOffice buttons appear in the message read/compose toolbar

## Build for Production

```bash
npm run build
```

Output goes to `dist/`. Deploy the contents to your hosting provider and update URLs in `manifest.xml`.

## Project Structure

```
office365/
├── manifest.xml                  # Office Add-in manifest (VersionOverridesV1_1)
├── package.json                  # Dependencies and scripts
├── webpack.config.js             # Build configuration
├── src/
│   ├── taskpane/
│   │   ├── taskpane.html         # Task pane UI (eBot chat + app launcher)
│   │   └── taskpane.js           # Task pane logic
│   └── commands/
│       └── commands.js           # Ribbon button handlers
└── README.md
```
