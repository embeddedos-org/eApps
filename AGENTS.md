# Repository Guidance for Agents

## Scope and architecture

eApps is the EmbeddedOS marketplace and application monorepo. Treat each product
surface as an independent delivery target: native LVGL applications live in
`apps/`, shared native code in `core/` and `shared/`, browser extensions in
`browser-extensions/`, web applications in `web-apps/`, mobile applications in
`mobile-apps/`, desktop applications in `desktop-apps/`, developer tools in
`dev-tools/`, command-line tools in `cli-tools/`, and deployment assets in
`enterprise/`. The marketplace catalog in `data/apps.json` and the storefront in
`index.html`, `css/`, and `js/` are user-facing release surfaces.

Follow the specialist role briefs in [`.ai/`](./.ai/) and the handoff protocol in
[`HANDOFF.md`](./HANDOFF.md). The implementer must not act as the approving
reviewer. Keep changes inside the affected product surface unless a shared
contract genuinely requires a coordinated update.

## Build and validation

Use the narrowest checks that cover the changed surface, then run the repository
aggregator when the change spans surfaces.

- Native C/CMake: configure with `cmake -B build -DBUILD_TESTING=ON`, build with
  `cmake --build build`, and run
  `ctest --test-dir build --output-on-failure`.
- Repository suite: run `python run_all_tests.py`.
- Web, mobile, extension, and tool changes: use the package-manager commands and
  workflow documented in the nearest manifest and in
  [`.github/workflows/`](./.github/workflows/).
- Catalog or storefront changes: validate `data/apps.json`, links, asset paths,
  and the relevant GitHub Pages build.

Do not claim a platform was tested when its SDK or runtime was unavailable.
Record skipped platform validation explicitly.

## Change discipline

Preserve platform portability and existing public catalog fields. Do not commit
build output, downloaded SDKs, credentials, signing material, or generated
release artifacts unless the repository already tracks that exact artifact.
Update documentation and changelog entries when a user-visible app, catalog,
installation, or compatibility contract changes.

Every human-authored pull request must use a GitHub-recognized closing keyword
for an issue in this repository, for example `Fixes #123`. Cross-repository
issues and plain issue mentions do not satisfy the linked-issue policy. Follow
[`.github/PULL_REQUEST_TEMPLATE.md`](./.github/PULL_REQUEST_TEMPLATE.md), and
keep the published Wiki snapshot in [`docs/wiki/`](./docs/wiki/) synchronized
when Wiki content changes.
