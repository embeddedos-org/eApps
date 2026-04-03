# Branch Protection — Recommended Settings

This document describes the recommended branch protection rules for the eApps repository.
These settings must be configured via the GitHub UI or API (Settings → Branches → Branch protection rules).

## Protected Branches

Apply these rules to: `main`, `master`, `develop`

## Required Settings

### Pull Request Reviews
- ✅ Require pull request reviews before merging
- ✅ Required number of approvals: **1** (recommend 2 for `core/network/` and security-sensitive apps)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from CODEOWNERS

### Status Checks
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- Required checks:
  - `Linux (GCC)` — CI build and test
  - `Windows (MSVC)` — CI build and test
  - `macOS (Clang)` — CI build and test
  - `Lint (cppcheck)` — Static analysis
  - `Analyze (C/C++)` — CodeQL SAST

### Commit Signing (Optional but Recommended)
- ☐ Require signed commits (GPG or SSH)
  - Recommended for release branches
  - See: https://docs.github.com/en/authentication/managing-commit-signature-verification

### Additional Restrictions
- ✅ Do not allow bypassing the above settings
- ✅ Restrict who can push to matching branches (maintainers only)
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

## Tag Protection

- Protect tags matching `v*`
- Only repository admins can create version tags

## Setup via GitHub CLI

```bash
gh api repos/embeddedos-org/eApps/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Linux (GCC)","Windows (MSVC)","macOS (Clang)","Lint (cppcheck)","Analyze (C/C++)"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```
