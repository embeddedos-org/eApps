# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
COPY packages/core/package.json packages/core/
COPY packages/ebot-client/package.json packages/ebot-client/
COPY packages/server/package.json packages/server/
COPY apps/launcher/package.json apps/launcher/
COPY apps/edocs/package.json apps/edocs/
COPY apps/enotes/package.json apps/enotes/
RUN npm install --workspace=packages/core --workspace=packages/ebot-client --workspace=packages/server --workspace=apps/launcher --workspace=apps/edocs --workspace=apps/enotes
COPY . .
RUN npm run build --workspace=packages/core
RUN npm run build --workspace=packages/ebot-client
RUN npm run build --workspace=packages/server
RUN npm run build --workspace=apps/launcher
RUN npm run build --workspace=apps/edocs
RUN npm run build --workspace=apps/enotes

# Production stage
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/packages/server/dist ./server/
COPY --from=builder /app/apps/launcher/dist ./public/launcher/
COPY --from=builder /app/apps/edocs/dist ./public/edocs/
COPY --from=builder /app/apps/enotes/dist ./public/enotes/
COPY --from=builder /app/packages/server/package.json ./
RUN npm install --omit=dev
EXPOSE 3001
CMD ["node", "server/index.js"]
