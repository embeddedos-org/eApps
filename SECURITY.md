# Security Policy

## Scope

This security policy covers all 38 applications in the eApps suite, the core libraries (`core/common`, `core/ui`, `core/storage`, `core/network`, `core/platform`), platform ports (`port/sdl2`, `port/eos`, `port/web`), and build infrastructure.

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 2.0.x   | ✅ Active support  |
| < 2.0   | ❌ No support      |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

### Preferred Method

1. Email **security@embeddedos.org** with:
   - Description of the vulnerability
   - Affected component(s) (e.g., `core/network/http.c`, `apps/essh/`)
   - Steps to reproduce
   - Impact assessment (see Severity Classification below)
   - Any suggested fix or mitigation

2. Alternatively, use [GitHub Security Advisories](https://github.com/embeddedos-org/eApps/security/advisories/new) to privately report the issue.

### PGP Encryption (Optional)

If you prefer encrypted communication, use the PGP key published at:

```
https://embeddedos.org/.well-known/pgp-key.asc
Fingerprint: [TO BE PUBLISHED]
```

## Severity Classification

| Severity | Description | Example |
|----------|-------------|---------|
| **Critical** | Remote code execution, authentication bypass, memory corruption exploitable over network | Buffer overflow in SSH handshake parser |
| **High** | Privilege escalation, data exfiltration, denial of service on network services | Unauthenticated VNC session hijack |
| **Medium** | Information disclosure, local privilege escalation, resource exhaustion | Unvalidated file path in eFiles |
| **Low** | Minor information leak, UI spoofing, non-exploitable crash | Stack trace exposed in error dialog |

## Response Timeline

| Action | SLA |
|--------|-----|
| Acknowledge receipt | 48 hours |
| Initial triage and severity assessment | 5 business days |
| Provide fix timeline | 10 business days |
| Release patch (Critical/High) | 30 days |
| Release patch (Medium/Low) | 90 days |

## Disclosure Policy

- We follow **coordinated disclosure**. We request that reporters give us reasonable time to address vulnerabilities before public disclosure.
- Once a fix is released, we will publish a security advisory on GitHub with full details and credit to the reporter (unless anonymity is requested).
- CVE IDs will be requested for Critical and High severity issues.

## Security-Sensitive Components

The following components handle untrusted input or network data and receive priority security review:

| Component | Risk Area |
|-----------|-----------|
| `apps/essh/` | SSH protocol, key management, terminal I/O |
| `apps/evnc/` | VNC protocol, framebuffer access, authentication |
| `apps/etunnel/` | SSH tunneling, SOCKS proxy, port forwarding |
| `apps/eweb/` | HTTP/HTML parsing, JavaScript execution, cookies |
| `apps/eftp/` | FTP protocol, file system access |
| `apps/evpn/` | VPN tunnel, cryptographic operations |
| `apps/eguard/` | Firewall rules, packet inspection |
| `apps/echat/` | Message transport, encryption |
| `apps/eserial/` | Serial protocol, raw data handling |
| `core/network/` | HTTP client, socket operations |
| `core/platform/` | File I/O, process management, clipboard |

## Security Measures in Place

- **Static Analysis**: cppcheck and clang-tidy run on every PR
- **SAST**: GitHub CodeQL scans on push/PR to protected branches
- **Dependency Monitoring**: Dependabot for GitHub Actions and git submodules
- **Supply Chain**: OSSF Scorecard weekly analysis
- **Branch Protection**: Required PR reviews, CI pass, and CODEOWNERS review

## Hall of Fame

We gratefully acknowledge security researchers who responsibly disclose vulnerabilities. Contributors will be listed here upon request.
# Security Policy

## Reporting a Vulnerability

The eApps team takes security seriously. If you discover a security vulnerability,
please report it responsibly.

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Email security findings to: **security@embeddedos.org**
3. Include the following in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Affected component(s) and version(s)
   - Potential impact assessment
   - Any suggested fix (optional)

### PGP Key

For encrypted communications, use our PGP key:

```
Fingerprint: [TO BE ADDED]
```

The full public key is available at: https://embeddedos.org/.well-known/security.txt

## Response Timeline

| Action | SLA |
|--------|-----|
| Acknowledgment of report | 48 hours |
| Initial triage and severity assessment | 5 business days |
| Status update to reporter | 10 business days |
| Fix development and testing | Varies by severity |
| Public disclosure (coordinated) | 90 days from report |

## Severity Classification

| Severity | Description | Examples |
|----------|-------------|----------|
| **Critical** | Remote code execution, complete system compromise | Buffer overflow in network module, arbitrary code execution via crafted input |
| **High** | Significant data exposure, privilege escalation | Authentication bypass in eSSH, credential leak in eVPN |
| **Medium** | Limited data exposure, denial of service | Crash via malformed HTTP response, directory traversal in eFiles |
| **Low** | Minor information disclosure, hardening gaps | Version disclosure, missing security headers |

## Scope

The following components are in scope for security reports:

### Core Libraries
- `core/common/` — Types, math, string, date utilities, expression parser, registry
- `core/ui/` — Theme, widgets, canvas, game engine
- `core/storage/` — Preferences (key-value store)
- `core/network/` — HTTP client (POSIX, Win32, Web backends)
- `core/platform/` — Platform abstraction layer

### Applications (38 apps)
- **High priority**: eSSH, eVNC, eTunnel, eVPN, eGuard, eWeb, eFTP, eChat (network-facing)
- **Medium priority**: eFiles, eZip, ePDF, eViewer (file-handling)
- **Standard priority**: All remaining apps

### Platform Ports
- `port/sdl2/` — Desktop display/input drivers
- `port/eos/` — Embedded EoS drivers
- `port/web/` — Emscripten/WASM drivers

### Out of Scope
- Third-party dependencies (report to upstream maintainers)
- The EoS operating system itself (report to [embeddedos-org/eos](https://github.com/embeddedos-org/eos))
- Social engineering attacks

## Security Measures

### Current
- Static analysis via cppcheck in CI
- Multi-platform build matrix (GCC, MSVC, Clang)
- Unit tests with CTest
- SPDX license identifiers on all source files
- SHA256 checksums on release artifacts

### Planned
- CodeQL SAST scanning
- Dependabot dependency monitoring
- AddressSanitizer / UBSan in nightly builds
- libFuzzer harnesses for parsers and network modules
- SBOM generation (CycloneDX)
- OSSF Scorecard tracking

## Acknowledgments

We gratefully acknowledge security researchers who help keep eApps safe.
Responsible disclosures will be credited in release notes (with reporter's consent).

## License

This security policy is part of the eApps project, licensed under MIT.
