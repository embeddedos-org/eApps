# eOffice GitHub App

GitHub App powered by Probot that integrates eBot AI for code review, issue tracking, and changelog generation.

## Features

- **PR Auto-Review** — eBot automatically reviews pull requests on open with AI-powered suggestions
- **Issue → ePlanner** — Extracts actionable tasks from new issues and syncs to ePlanner
- **Comment Commands** — `/ebot summarize`, `/ebot review`, `/ebot docs`
- **Auto Changelog** — Generates changelogs from push events to main/master → saves to eDocs
- **Repository Events** — Auto-creates ePlanner projects for new repositories
- **Status Checks** — Integrates with GitHub status checks API

## Prerequisites

- Node.js 18+
- eOffice backend running on `localhost:3001`
- A GitHub account with permission to create GitHub Apps

## GitHub App Registration

### 1. Register the App

1. Go to **GitHub → Settings → Developer settings → GitHub Apps → New GitHub App**
2. Fill in:
   - **Name**: `eOffice Bot`
   - **Homepage URL**: `http://localhost:3001`
   - **Webhook URL**: `http://localhost:3001/api/github/webhook` (use smee.io for local dev)
   - **Webhook secret**: Generate a secret and save it
3. Set permissions (as defined in `app.yml`):
   - Issues: Read & Write
   - Pull Requests: Read & Write
   - Contents: Read
   - Checks: Read & Write
   - Statuses: Read & Write
4. Subscribe to events: Issues, Issue comments, Pull requests, Push, Check suites
5. Click **Create GitHub App**

### 2. Download the Private Key

1. After creation, click **Generate a private key**
2. Save the `.pem` file to the project root

### 3. Install the App

1. Go to your GitHub App settings → **Install App**
2. Select the repositories you want to use with eOffice

## Setup

```bash
cd extensions/github
npm install
```

### Environment Variables

Create a `.env` file:

```env
APP_ID=your_app_id
PRIVATE_KEY_PATH=./your-app-name.pem
WEBHOOK_SECRET=your_webhook_secret
WEBHOOK_PROXY_URL=https://smee.io/your-channel
EOFFICE_API=http://localhost:3001
```

### Local Development with smee.io

```bash
# Install smee client
npm install -g smee-client

# Create a channel at https://smee.io/new
# Set WEBHOOK_PROXY_URL in .env

# Start the bot
npm run dev
```

### Production

```bash
npm start
```

## Comment Commands

| Command | Description |
|---------|-------------|
| `/ebot summarize` | Summarizes the issue/PR conversation |
| `/ebot review` | AI code review (pull requests only) |
| `/ebot docs` | Generates documentation and saves to eDocs |
| `/ebot` | Shows available commands |

## Project Structure

```
github/
├── app.yml              # GitHub App manifest
├── package.json         # Dependencies (probot)
├── src/
│   └── index.js         # Probot app (PR review, issues, commands, push, webhooks)
└── README.md
```
