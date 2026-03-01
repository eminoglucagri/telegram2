FROM node:20-alpine

WORKDIR /app

# Package files kopyala
COPY package*.json ./

# Dependencies kur
RUN npm install

# Tüm dosyaları kopyala
COPY . .

# Environment variables
ENV NEXT_PUBLIC_API_URL=http://backend:8000
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build (hataları ignore et)
RUN npm run build || true

# Port expose
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Başlat (eğer build başarısızsa dev mode'da çalış)
CMD if [ -d ".next" ]; then npm start; else npm run dev; fi
