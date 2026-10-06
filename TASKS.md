<!-- generated: eos-ai-scaffold -->
# Tasks

Working ledger for `eApps`. The planner writes entries; each owning role
updates its own row. Roles are in [AGENTS.md](./AGENTS.md), the workflow in
[ORCHESTRATION.md](./ORCHESTRATION.md), the gate in [VERIFY.md](./VERIFY.md).

Status is one of: `todo`, `in-progress`, `blocked`, `review`, `done`.

## Active

| ID | Task | Owner | Mode | Status | Depends on |
|----|------|-------|------|--------|------------|
| —  | No active tasks. | — | — | — | — |

## Completed

| ID | Task | Owner | Verified by | Evidence |
|----|------|-------|-------------|----------|
| T-001 | Fix the lvgl stub include path that failed 46 native-app syntax checks | testing | reviewer | `tests/test_native_apps.py` wrote its LVGL stub to `<stub_dir>/lvgl/lvgl.h` but passed only `-I<stub_dir>` to gcc, while every app source does `#include "lvgl.h"`. The header never resolved, so all 46 apps failed with `fatal error: lvgl.h: No such file or directory` reported as *the app's own* syntax error. Added `-I<stub_dir>/lvgl`. `tests/test_native_apps.py`: 1058 passed, 0 failed (was 46 failed). |
| T-002 | Unblock collection of the vendored eDB suite | testing | reviewer | `desktop-apps/edb/tests/conftest.py` imports `edb`, which is a `src/`-layout package in the sibling eDB repo and so importable only once installed. Collection aborted for the entire eApps run before any test executed. With eDB installed the vendored suite runs: 150 passed. It then surfaced two genuine eDB defects — see eDB T-001 and T-002. |

## Open — unfinished features, not defects

These are missing implementation files, found by tests that are themselves
correct. Each needs product decisions, so none was invented here.

| Item | Count | Evidence |
|---|---|---|
| Web apps with no `service-worker.js` | 33 | `tests/test_web_apps.py::TestServiceWorker` — 5 assertions each (exists, non-empty, cache name, install handler, fetch handler) = 165 failures. No build step generates them. |
| Browser extensions with no `popup.js` / `background.js` | 20 | `tests/test_browser_extensions.py` — 40 failures. Every `popup.html` has `<script src="popup.js">`; the file exists in none of the 20 extensions, and nothing generates it. Each extension is currently `manifest.json` + `popup.html` + icons only, so every popup is non-functional. |
| Files an incomplete merge should have produced | 10 | `tests/test_merge_validation.py` — e.g. `desktop-apps/eoffice/desktop/main.js`, `desktop-apps/eoffice/packages/core`. |

---

## Task template

```markdown
### T-000 — <short title>

Owner: <role>
Mode: <see MODES.md>
Status: todo
Depends on: <task ids, or none>

Goal
: <one sentence: what is true afterwards that is not true now>

Acceptance criteria
: - <observable, checkable statement>
  - <observable, checkable statement>

Files in scope
: <paths the owner is expected to touch>

Out of scope
: <what this task deliberately does not change>

Risks
: <what could break, and what would reveal it>

Verification
: | Check | Command | Result |
  |-------|---------|--------|
  | <name> | `<command>` | `NOT RUN` |
```

## Verification commands for this repository

These commands were derived from the manifests at the repository root. Confirm one works before relying on it; a listed script may still be a stub.

| Check | Command | Default state |
|-------|---------|---------------|
| Build | `cmake --build build -j` | `NOT RUN` |
| Unit tests | `ctest --test-dir build --output-on-failure` | `NOT RUN` |

## Rules

- One task per unit of work that can be verified on its own.
- Acceptance criteria are written before work starts and are not edited to match
  what was built. If they were wrong, say so and rewrite them explicitly.
- A task reaches `done` only when the definition of done in
  [ORCHESTRATION.md](./ORCHESTRATION.md) is met and the verification commands
  were actually run.
- `blocked` requires a note naming what it is blocked on and who can unblock it.
