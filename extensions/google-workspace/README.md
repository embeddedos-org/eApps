# eOffice for Google Workspace

Google Workspace Add-on that integrates eOffice apps and eBot AI into Google Docs, Sheets, and Gmail.

## Features

- **Google Docs** — eBot AI sidebar for summarizing, rewriting, and exporting to eDocs
- **Google Sheets** — Bidirectional sync with eSheets (push/pull)
- **Gmail** — eBot compose helper with tone selection and AI-generated drafts
- **Homepage** — App launcher for all 9 eOffice apps + eBot chat

## Prerequisites

- Google Cloud project with Apps Script API enabled
- eOffice backend running on `localhost:3001`
- [clasp](https://github.com/google/clasp) CLI installed globally

## Google Cloud Project Setup

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project named "eOffice Add-on"
3. Enable the following APIs:
   - Google Docs API
   - Google Sheets API
   - Gmail API
   - Google Drive API
   - Apps Script API

### 2. Configure OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Choose **Internal** (for organization) or **External** (for testing)
3. Fill in app name: "eOffice"
4. Add the scopes listed in `appsscript.json`

### 3. Deploy with clasp

```bash
# Install clasp globally
npm install -g @google/clasp

# Login to Google
clasp login

# Create a new Apps Script project
clasp create --title "eOffice Add-on" --type webapp

# Push files to Apps Script
clasp push

# Open in Apps Script editor
clasp open
```

### 4. Install the Add-on

1. In the Apps Script editor, go to **Deploy → Test deployments**
2. Select **Google Workspace Add-on**
3. Click **Install** to add it to your Google Workspace apps
4. Open Google Docs, Sheets, or Gmail — the eOffice sidebar appears

## Development

### Local Testing with clasp

```bash
# Watch for changes and auto-push
clasp push --watch

# Pull latest from Apps Script
clasp pull

# View logs
clasp logs
```

### Tunnel for localhost

Since Google Apps Script runs server-side, it needs to reach `localhost:3001`. Options:

1. **ngrok**: `ngrok http 3001` — use the generated URL in `Code.gs`
2. **Cloudflare Tunnel**: `cloudflared tunnel --url localhost:3001`
3. Update the `EOFFICE_API` constant in `Code.gs` with your tunnel URL

## Project Structure

```
google-workspace/
├── appsscript.json     # Apps Script manifest (scopes, triggers, add-on config)
├── Code.gs             # Main logic (triggers, eBot API, import/sync)
├── CardService.gs      # Card UI builder functions
└── README.md
```

## Files

| File | Purpose |
|------|---------|
| `appsscript.json` | Manifest with OAuth scopes, add-on triggers, URL whitelist |
| `Code.gs` | Homepage, Docs, Sheets, Gmail handlers + eBot API calls |
| `CardService.gs` | Card UI builders for each context (Docs sidebar, Sheets sync, Gmail compose) |
