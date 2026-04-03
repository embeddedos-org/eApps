# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Current |

## Reporting a Vulnerability

**Email:** security@embeddedos.org

**Response time:** Within 48 hours.

### What to include

- Description of the vulnerability
- Steps to reproduce
- Affected versions
- Impact assessment (if known)

### Process

1. Report via email (do NOT open a public issue)
2. We acknowledge within 48 hours
3. We investigate and provide a fix timeline
4. CVE assigned for confirmed issues
5. Security advisory published after fix is released

### Scope

**In scope:**
- EoSim Python package code (`eosim/`)
- Platform configuration parsing and validation
- Engine backends (native, QEMU, Renode integration)
- CLI and GUI components
- HIL/OpenOCD integration

**Out of scope:**
- Third-party dependencies (report to upstream)
- Vulnerabilities in QEMU, Renode, or OpenOCD themselves
- Issues in example/demo configurations
- Denial of service via large platform configs (expected behavior)

## Security Updates

Security fixes are released as patch versions (e.g., 0.1.1) and announced via GitHub Security Advisories.
