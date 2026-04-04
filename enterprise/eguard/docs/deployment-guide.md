# Security Suite — Enterprise Deployment Guide

## Prerequisites
- Docker 24+ / Kubernetes 1.28+
- EoS Enterprise License Key
- SSO/LDAP configured (optional)

## Docker Deployment
```bash
cd enterprise/eguard/docker
docker-compose up -d
```

## Kubernetes Deployment
```bash
cd enterprise/eguard/helm
helm install eos-eguard . -f values.yaml -n eos-enterprise
```

## Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| EOS_LICENSE_KEY | Enterprise license | required |
| SSO_ENABLED | Enable SSO/SAML | false |
| LOG_LEVEL | Logging level | info |
