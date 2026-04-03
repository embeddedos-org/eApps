# eOffice Suite — Slack App

> Create documents, save notes, ask eBot AI, manage tasks, and auto-import files — all from Slack.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **`/edocs create <title>`** | Create a new eDocs document |
| **`/enotes add <text>`** | Save a quick note to eNotes |
| **`/ebot ask <question>`** | Ask eBot AI a question |
| **`/esheets import`** | Import spreadsheet files to eSheets |
| **`/eplanner task <title>`** | Create a task in ePlanner |
| **App Home** | Dashboard showing recent documents and quick actions |
| **Message Shortcut** | Right-click any message → "Summarize with eBot" |
| **URL Unfurling** | Rich previews for eOffice links shared in channels |
| **File Auto-Import** | Files shared in Slack auto-imported to eDrive |

## 📦 Setup

### Prerequisites

- Node.js 18+
- A Slack workspace where you have admin permissions
- eOffice server running on `localhost:3001`

### 1. Create the Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"** → **"From a manifest"**
3. Select your workspace
4. Paste the contents of `manifest.yaml`
5. Click **Create**

### 2. Get Tokens

From your app's settings page:

1. **Bot Token**: Go to **OAuth & Permissions** → Install to workspace → Copy `xoxb-...` token
2. **Signing Secret**: Go to **Basic Information** → Copy the Signing Secret
3. **App Token**: Go to **Basic Information** → **App-Level Tokens** → Generate a token with `connections:write` scope → Copy `xapp-...` token

### 3. Configure Environment

Create a `.env` file in this directory:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token
EOFFICE_URL=http://localhost:3001
PORT=3002
```

### 4. Install & Run

```bash
cd extensions/slack
npm install
npm start
```

For development with auto-reload:

```bash
npm run dev
```

## 🤖 Slash Commands

### `/edocs create <title>`
Creates a new document in eDocs and returns a link.
```
/edocs create Q4 Planning Doc
```

### `/enotes add <text>`
Saves text as a note in eNotes.
```
/enotes add Remember to update the API docs for v2 release
```

### `/ebot ask <question>`
Asks eBot AI a question and returns the answer.
```
/ebot ask What are the key differences between REST and GraphQL?
```

### `/esheets import`
Shows instructions for importing spreadsheet files to eSheets.
```
/esheets import
```

### `/eplanner task <title>`
Creates a new task in ePlanner.
```
/eplanner task Update deployment scripts
```

## 💬 Message Shortcut

1. Hover over any message in Slack
2. Click the **⋯** (More actions) menu
3. Select **"Summarize with eBot"**
4. A modal displays the original message and AI summary

## 🔗 URL Unfurling

When someone shares an eOffice URL in a channel (e.g., `http://localhost:3001/edocs/abc123`), the app automatically provides a rich preview with the document title and a direct link.

## 📁 Auto-Import to eDrive

When files are shared in channels where the app is installed, compatible files (CSV, XLSX, DOCX, PDF, TXT, Markdown) are automatically imported to eDrive.

## 🗂️ Project Structure

```
extensions/slack/
├── app.js            # Main Slack Bolt application
├── manifest.yaml     # Slack App manifest
├── package.json      # Node.js dependencies
├── .env              # Environment variables (create this)
└── README.md         # This file
```

## 📄 License

MIT © embeddedos — Part of the EmbeddedOS project by nicheOS.
