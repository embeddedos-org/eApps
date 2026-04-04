# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in eDB, please report it responsibly.

### How to Report

1. **Do NOT open a public GitHub issue** for security vulnerabilities.
2. Email the security team at: **security@edb-project.org**
3. Include the following in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment** within 48 hours of your report
- **Assessment** within 5 business days
- **Fix timeline** communicated within 10 business days
- **Credit** in the security advisory (unless you prefer anonymity)

## Security Best Practices for eDB Users

### Authentication
- Always change default credentials before deploying
- Use strong JWT secrets (minimum 256-bit)
- Rotate API keys regularly
- Enable refresh token rotation

### Encryption
- Always enable TLS for production deployments
- Use AES-256 encryption for sensitive data at rest
- Store encryption keys separately from the database
- Use environment variables or a secrets manager for keys

### Network
- Bind the API server to `127.0.0.1` unless external access is required
- Use a reverse proxy (nginx, Caddy) for TLS termination in production
- Enable rate limiting on all API endpoints

### Access Control
- Follow the principle of least privilege for RBAC roles
- Regularly audit user permissions
- Remove unused accounts promptly

### Monitoring
- Enable audit logging in production
- Monitor for unusual query patterns
- Set up alerts for authentication failures

## Security Features in eDB

- **JWT Authentication** with access and refresh tokens
- **Role-Based Access Control (RBAC)** with granular permissions
- **AES-256 Encryption** at rest for sensitive fields
- **Parameterized Queries** to prevent SQL injection
- **Input Sanitization** for all API endpoints
- **Tamper-Resistant Audit Logs** with hash chain verification
- **Prompt Injection Detection** for AI/ebot queries
