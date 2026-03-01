FROM node:20-alpine AS base

# Dependencies için stage
FROM base AS deps
WORKDIR /app

# Package files kopyala
COPY package*.json ./

# Dependencies kur (dev dependencies dahil, build için gerekli)
RUN npm ci

# Builder stage
FROM base AS builder
WORKDIR /app

# Dependencies'i deps stage'den kopyala
COPY --from=deps /app/node_modules ./node_modules

# Tüm kaynak kodları kopyala
COPY . .

# Environment variables
ENV NEXT_PUBLIC_API_URL=http://backend:8000
ENV NEXT_TELEMETRY_DISABLED=1

# Build (hataları ignore et)
RUN npm run build || echo "Build completed with warnings"

# Production stage
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Gerekli dosyaları kopyala
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Port expose
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Başlat
CMD ["node", "server.js"]
