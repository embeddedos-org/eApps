# ☁️ Service Apps

Backend services, APIs, and cloud-connected applications merged from **eServiceApps** and **eOffice**.

## Contents

| Service | Technology | Source |
|---|---|---|
| **eServiceApps Backend** | Firebase / Firestore | `backend/` |
| **Auth Service** | Firebase Auth | `backend/auth/` |
| **Wallet Service** | Firebase + Stripe | `backend/wallet/` |
| **Notification Service** | Firebase Cloud Messaging | `backend/notifications/` |
| **eOffice Server** | Node.js + Docker | `eoffice-server/` |

## Origin

| Folder | Merged From |
|---|---|
| `backend/` | [embeddedos-org/eServiceApps](https://github.com/embeddedos-org/eServiceApps) |
| `eoffice-server/` | [embeddedos-org/eOffice → packages/server/](https://github.com/embeddedos-org/eOffice/tree/main/packages/server) |

## Deploy

```bash
# Firebase backend
cd backend && firebase deploy

# eOffice Server (Docker)
cd eoffice-server && docker-compose up -d
```

## Configuration

- `firebase.json` — Firebase project configuration
- `firestore.rules` — Firestore security rules
- `firestore.indexes.json` — Firestore indexes
- `docker-compose.yml` — Docker Compose for eOffice Server

All service endpoints and versions registered in `data/apps.json` and listed on the **[EoS App Store](https://embeddedos-org.github.io/eApps/)**.

## CI/CD

- **Firebase backend:** Deploy via `firebase deploy`
- **eOffice Server:** Docker build/push via CI
- **Mobile apps:** See `.github/workflows/build-mobile.yml`

```bash
# Tag to release mobile apps
git tag eride-v2.0.0 && git push origin eride-v2.0.0
git tag esocial-v1.1.0 && git push origin esocial-v1.1.0
```

Builds produce:
- `.apk` + `.aab` (Android — signed if `ANDROID_KEYSTORE` secret configured)
- `.ipa` (iOS — uploaded to TestFlight if `IOS_CERTIFICATE` secret configured)
