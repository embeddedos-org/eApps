# Development

## Contribution source of truth

[CONTRIBUTING](https://github.com/embeddedos-org/eApps/blob/master/CONTRIBUTING.md)

Before proposing a change, also review the [README](https://github.com/embeddedos-org/eApps/blob/master/README.md). Keep changes scoped, add tests appropriate to the affected behavior, and follow the repository's current automation and review requirements.

## Build and dependency inputs found

`CMakeLists.txt`, `apps/dice/CMakeLists.txt`, `apps/ebirds/CMakeLists.txt`, `apps/eblocks/CMakeLists.txt`, `apps/ebot/CMakeLists.txt`, `apps/ebuffer/CMakeLists.txt`, `apps/ecal/CMakeLists.txt`, `apps/echat/CMakeLists.txt`, `apps/echess/CMakeLists.txt`, `apps/ecleaner/CMakeLists.txt`, `apps/eclock/CMakeLists.txt`, `apps/econverter/CMakeLists.txt`, and 135 more.

## Tests found in the default-branch tree

`desktop-apps/ebrowser/tests/README.md`, `desktop-apps/ebrowser/tests/test_css_parser.c`, `desktop-apps/ebrowser/tests/test_dom.c`, `desktop-apps/ebrowser/tests/test_html_parser.c`, `desktop-apps/ebrowser/tests/test_tls.c`, `desktop-apps/ebrowser/tests/test_url.c`, `desktop-apps/edb/tests/conftest.py`, `desktop-apps/edb/tests/integration/__init__.py`, `desktop-apps/edb/tests/integration/test_api.py`, `desktop-apps/edb/tests/unit/__init__.py`, `desktop-apps/edb/tests/unit/test_audit.py`, `desktop-apps/edb/tests/unit/test_database.py`, and 67 more.

## Documented test commands

These commands are reproduced from the inspected root README or contributing guide:

```bash
cmake -B build && cmake --build build && cd build && ctest
```

```bash
python -m pytest tests/test_merge_validation.py -v
```

```bash
cmake -B build -DEAPPS_PORT=sdl2 -DBUILD_TESTING=ON
```

```bash
cmake --build build
```

```bash
ctest --test-dir build --output-on-failure
```

```bash
cmake --build build --target cppcheck
```

## Verification baseline

This inventory comes from `master` at [`3d51c47a4baa`](https://github.com/embeddedos-org/eApps/commit/3d51c47a4baa319486e216bb82708370419faf42) and found 79 test-related paths among 1720 files. Re-check the source tree when that commit is no longer current.
