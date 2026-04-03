# eOffice Architecture

## Tech Stack

```
┌─────────────────────────────────────────────────┐
│                  UI Layer                        │
│            React + TypeScript + Vite             │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ eDocs    │ │ eNotes   │ │ 9 more apps...   │ │
│  │ (5173)   │ │ (5174)   │ │ (5175-5183)      │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────────────────────────────────────────┐│
│  │            Suite Launcher (5170)              ││
│  └──────────────────────────────────────────────┘│
└───────────────────────┬─────────────────────────┘
                        │ HTTP / REST
┌───────────────────────▼─────────────────────────┐
│                Backend Layer                     │
│              Node.js + Express                   │
│  /api/ebot/*       — AI proxy to EAI            │
│  /api/documents/*  — Document CRUD              │
│  /api/notes/*      — Notes CRUD                 │
│  Port: 3001                                      │
└───────────────────────┬─────────────────────────┘
                        │ HTTP / JSON
┌───────────────────────▼─────────────────────────┐
│               EAI Server (C)                     │
│         Embedded AI — LLM + Agents               │
│  /v1/chat, /v1/complete, /v1/summarize           │
│  /v1/task-extract, /v1/search                    │
│  192.168.1.100:8420                              │
└─────────────────────────────────────────────────┘
```

## Project Structure

```
eOffice/
├── packages/
│   ├── core/              @eoffice/core — shared types, models, utils
│   ├── ebot-client/       @eoffice/ebot-client — TypeScript EAI client
│   └── server/            @eoffice/server — Node.js backend
├── apps/
│   ├── launcher/          Suite launcher (port 5170)
│   ├── edocs/             Word processor (port 5173) ★ Phase 1
│   ├── enotes/            Digital notebook (port 5174) ★ Phase 1
│   ├── esheets/           Spreadsheets (port 5175)
│   ├── eslides/           Presentations (port 5176)
│   ├── email/             Email & Calendar (port 5177)
│   ├── edb/               Database (port 5178)
│   ├── edrive/            Cloud storage (port 5179)
│   ├── econnect/          Collaboration (port 5180)
│   ├── eforms/            Forms & surveys (port 5181)
│   ├── esway/             Interactive slides (port 5182)
│   └── eplanner/          Task management (port 5183)
├── package.json           Monorepo root (npm workspaces)
├── tsconfig.json          Shared TypeScript config
└── README.md              Development plan
```

## Data Flow

1. User interacts with React UI (e.g., clicks "Summarize" in eDocs)
2. React component calls `EBotOffice.summarizeText(content)`
3. `EBotOffice` formats the prompt and calls `EBotClient.summarize()`
4. `EBotClient` sends HTTP POST to Node.js server at `/api/ebot/summarize`
5. Server proxies the request to EAI Server at `192.168.1.100:8420/v1/summarize`
6. EAI runs LLM inference and returns JSON response
7. Response flows back through the chain to the React UI

## eBot Integration per App

| App | eBot Features |
|---|---|
| eDocs | Summarize, Rewrite, Grammar Check, Translate |
| eNotes | Summarize, Auto-Tag, Extract Tasks, Find Related |
| eSheets | Formula Suggestions, Data Explanation |
| eSlides | Content Generation, Talking Points |
| eMail | Smart Replies, Task Extraction |
| eConnect | Meeting Summaries, Action Items |
| eForms | Question Generation, Response Summary |
| ePlanner | Task Suggestions, Prioritization |
