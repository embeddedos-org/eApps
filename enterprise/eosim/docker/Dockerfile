FROM node:20-alpine AS base
LABEL maintainer="embeddedos-org" description="Simulation Server — EoS Enterprise"

WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://localhost:8080/health || exit 1
CMD ["node", "server.js"]
