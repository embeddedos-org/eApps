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
https://embeddedos-org.github.io/.well-known/pgp-key.asc
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
