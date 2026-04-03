# Changelog

All notable changes to the eOffice Suite project will be documented in this file.

## [1.0.0] — 2026-04-03

### Phase 4 — Advanced Features
- **Cross-app eBot AI:** All 11 apps have eBot AI integration with app-specific actions
- **Desktop app:** Full Electron app with all 11 apps accessible from the menu
- **Docker deployment:** Multi-stage Dockerfile builds all 12 apps (11 + launcher)
- **Dev scripts:** `npm run dev:*` scripts for all 11 apps + server
- **CI/CD:** GitHub Actions workflow with lint, typecheck, test, build across 3 OS × 2 Node versions

### Phase 3 — Extended Suite & Integrations
- **eConnect:** Collaboration & messaging — channels, message threads, eBot chat summarize
- **eDrive:** Cloud storage — file browser, preview, upload, folders, eBot semantic search
- **eDB:** Database manager — table viewer, row editing, SQL query editor, eBot query suggestions
- **eForms:** Forms & surveys — form builder (7 field types), preview, validation, eBot question generation
- **eSway:** Interactive presentations — quiz/poll/Q&A slides, live responses, eBot quiz generation
- **ePlanner:** Task management — kanban board (todo/in-progress/done), drag-to-move, eBot task extraction
- **Server routes:** Full CRUD APIs for all 11 apps at `/api/*`
- **Auth middleware:** JWT-based authentication with role-based authorization
- **Audit middleware:** Request logging for all API calls
- **Extensions:** Chrome/Firefox extension (Manifest V3) + VS Code extension

### Phase 2 — Core Suite
- **eSheets:** Spreadsheet with formula engine (SUM, AVG, COUNT, MIN, MAX, IF, CONCATENATE), multi-sheet, cell formatting, CSV import/export, eBot formula suggestions
- **eSlides:** Presentations — slide deck editor, element CRUD, themes, speaker notes, full-screen present mode, eBot content generation & talking points
- **eMail:** Email client — inbox/sent/drafts/starred/trash folders, compose/reply/forward, read/star, eBot smart replies & task extraction
- **Server APIs:** Spreadsheet batch cell update, presentation slide CRUD, email messages/calendar

### Phase 1 — MVP
- **eDocs:** Word processor — contentEditable editor, formatting toolbar (bold/italic/underline/heading/list), auto-save, export, print, eBot summarize/rewrite/grammar/translate
- **eNotes:** Digital notebook — two-panel layout, note CRUD, tags, search, pin, import/export JSON, eBot summarize/auto-tag/extract-tasks/find-related
- **@eoffice/core:** 12 data models, 45 types, 7 utilities, 6 constants, app registry
- **@eoffice/ebot-client:** EBotClient (9 endpoints) + EBotOffice (12 AI methods)
- **@eoffice/server:** Express.js backend with 14 route modules on port 3001
- **Suite Launcher:** App grid with category filters, search, dark/light theme
- **Browser apps:** 12 standalone HTML files (zero-dependency, offline-capable)
- **118 unit tests** across core, ebot-client, and server packages

### Tech Stack

- UI: React 18 + TypeScript 5 + Vite 5
- Backend: Node.js + Express
- AI: eBot client → EAI Server (C)
- Desktop: Electron 28
- Build: npm workspaces monorepo
- CI: GitHub Actions (3 OS × 2 Node versions)
- Docker: Multi-stage Alpine build

## [0.1.0] — 2026-04-03

### Added

- Initial project scaffold with monorepo structure
- Phase 1 MVP: eDocs + eNotes
- 9 stub apps for future phases
