# eOffice for Raycast

Raycast extension for quick access to eOffice apps, eDocs search, eNotes creation, and eBot AI.

## Features

| Command | Description |
|---------|-------------|
| **Search eDocs** | Fuzzy search across all documents in eDocs |
| **Create eNote** | Quick note creation form → saves to eNotes |
| **Ask eBot** | Ask eBot AI a question, get inline Markdown response |
| **Open eOffice App** | Grid launcher for all 11 eOffice apps |
| **Recent Files** | List of recently accessed files across eOffice |

## Prerequisites

- [Raycast](https://raycast.com/) installed (macOS)
- eOffice backend running on `localhost:3001`
- Node.js 18+ (for development)

## Install from Raycast Store

1. Open Raycast
2. Search for "eOffice" in the Store
3. Click **Install**
4. Set the backend URL in preferences (default: `http://localhost:3001`)

## Install in Dev Mode

```bash
cd extensions/raycast
npm install
npm run dev
```

This opens Raycast with the extension loaded in development mode. Changes auto-reload.

## Configuration

Open Raycast preferences (`⌘ + ,`) → Extensions → eOffice:

| Preference | Default | Description |
|-----------|---------|-------------|
| Backend URL | `http://localhost:3001` | The eOffice backend server URL |

## Commands

### Search eDocs (`search-docs`)
- Fuzzy search with debounced input
- Shows document title, preview, tags, and last updated date
- Actions: Open in browser, copy content, copy link

### Create eNote (`create-note`)
- Form with title and Markdown content
- Saves directly to eNotes via API
- Markdown preview support

### Ask eBot (`ebot-ask`)
- Text input for questions
- Renders AI response as Markdown
- Copy response or ask follow-up

### Open eOffice App (`open-app`)
- Grid of all 11 apps with icons
- Opens selected app in default browser
- Copy URL shortcut

### Recent Files (`recent-files`)
- Lists recently accessed files across all eOffice apps
- Shows file type, app, and last access date
- Open in browser or copy link

## Project Structure

```
raycast/
├── package.json             # Raycast extension manifest
├── src/
│   ├── api.ts               # Shared API client for localhost:3001
│   ├── search-docs.tsx       # Search eDocs command
│   ├── create-note.tsx       # Create eNote command
│   ├── ebot-ask.tsx          # Ask eBot command
│   ├── open-app.tsx          # App launcher grid
│   └── recent-files.tsx      # Recent files list
└── README.md
```

## Development

```bash
# Build for production
npm run build

# Lint
npm run lint

# Fix lint issues
npm run fix-lint

# Publish to Raycast Store
npm run publish
```
