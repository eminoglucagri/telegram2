# Telegram Agent Dashboard

Telegram Stealth Marketing Agent için modern, responsive yönetim paneli.

## 🛠 Teknoloji Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Shadcn UI (Radix UI)
- **Charts:** Recharts
- **State Management:** Zustand
- **Data Fetching:** React Query (TanStack Query)
- **Forms:** React Hook Form + Zod
- **HTTP Client:** Axios

## 🚀 Kurulum

### Gereksinimler

- Node.js 18+
- npm veya yarn

### Adımlar

```bash
# Dizine git
cd frontend

# Bağımlılıkları yükle
npm install

# Environment dosyasını kopyala
cp .env.local.example .env.local

# Geliştirme sunucusunu başlat
npm run dev
```

Çalıştırmak için: http://localhost:3000

## 📁 Proje Yapısı

```
frontend/
├── app/                    # Next.js App Router sayfaları
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Dashboard
│   ├── campaigns/          # Kampanya yönetimi
│   ├── groups/             # Grup yönetimi
│   ├── messages/           # Mesaj geçmişi
│   ├── leads/              # Lead yönetimi
│   ├── personas/           # Persona yönetimi
│   ├── analytics/          # Analitik
│   └── settings/           # Ayarlar
├── components/             # React bileşenleri
│   ├── ui/                 # Temel UI bileşenleri (Shadcn)
│   ├── layout/             # Layout bileşenleri
│   ├── dashboard/          # Dashboard bileşenleri
│   └── ...                 # Diğer bileşenler
├── hooks/                  # Custom React hooks
├── lib/                    # Yardımcı fonksiyonlar
│   ├── api.ts              # API istemcisi
│   ├── types.ts            # TypeScript tipleri
│   └── utils.ts            # Utility fonksiyonlar
├── store/                  # Zustand store
└── public/                 # Statik dosyalar
```

## 📱 Sayfalar

### Dashboard (`/`)
- KPI kartları (kampanya, grup, lead, mesaj sayıları)
- Aktivite grafiği (son 7 gün)
- Warm-up durum widget'ı
- Son lead'ler listesi

### Kampanyalar (`/campaigns`)
- Kampanya listesi ve filtreleme
- Yeni kampanya oluşturma
- Kampanya detay ve analitik
- Aktivasyon/duraklatma

### Gruplar (`/groups`)
- Katılınan gruplar listesi
- Yeni grup ekleme
- Grup istatistikleri

### Mesajlar (`/messages`)
- Mesaj geçmişi
- Bot/kullanıcı filtresi
- Duygu analizi gösterimi

### Lead'ler (`/leads`)
- Lead listesi ve yönetimi
- Huni grafiği
- CSV export
- Durum güncelleme

### Personalar (`/personas`)
- Persona kartları
- Yeni persona oluşturma
- Prompt önizleme

### Analitik (`/analytics`)
- Detaylı grafikler
- Kampanya performansı
- Lead hunisi
- Grup aktivitesi

### Ayarlar (`/settings`)
- Telegram hesap bilgileri
- Warm-up konfigurasyonu
- API anahtarları
- Bildirim ayarları

## ⚙️ Environment Değişkenleri

```env
# API URL (Backend)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🐳 Docker

### Standalone Build

```bash
# Image oluştur
docker build -t telegram-agent-frontend .

# Container'u başlat
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://backend:8000 telegram-agent-frontend
```

### Docker Compose ile

Ana dizindeki `docker-compose.yml` ile:

```bash
docker-compose up -d
```

## 📜 Scriptler

```bash
# Geliştirme sunucusu
npm run dev

# Production build
npm run build

# Production sunucusu
npm start

# Lint kontrolü
npm run lint
```

## 🎨 UI Components

Shadcn UI tabanlı bileşenler:

- Button, Card, Table, Input, Select
- Dialog, Tabs, Badge, Progress
- Alert, Switch, Dropdown Menu
- Skeleton (loading states)

## 📊 Grafikler

Recharts ile oluşturulan grafikler:

- LineChart (aktivite trendi)
- BarChart (kampanya performansı)
- PieChart (lead hunisi)

## 🔗 API Entegrasyonu

Backend API'leri ile entegrasyon:

- Campaigns API
- Groups API
- Messages API
- Leads API
- Personas API
- Analytics API
- Warmup API
- Settings API

## 🛡️ Güvenlik

- API isteklerinde token auth (TODO)
- Form validasyonu (Zod)
- XSS korunması
- CSRF korunması

## 📝 Notlar

- Backend API'si `http://localhost:8000` adresinde çalışıyor olmalı
- Mock data ile demo modu mevcuttur (API bağlantısı olmadan)
- Responsive tasarım (mobil, tablet, desktop)
- Türkçe arayüz
