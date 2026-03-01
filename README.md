# Telegram Stealth Marketing Agent

AI-powered Telegram marketing automation agent with warm-up tracking, persona management, and lead generation capabilities.

## ⚠️ Important Disclaimer

**This tool is for educational purposes only.** Using automated accounts on Telegram may violate their Terms of Service and could result in account restrictions or bans. Use responsibly and at your own risk.

## Features

- 🤖 **AI-Powered Conversations**: Natural conversations using OpenAI GPT models
- 🎭 **Persona Management**: Create and manage different personas for campaigns
- 📈 **Warm-up Tracking**: 5-stage warm-up system to protect account health
- 🎯 **Lead Generation**: Automatic lead detection and scoring
- 📩 **DM Campaigns**: Personalized direct message outreach
- 📊 **Analytics Dashboard**: Track campaign performance
- 🔒 **Rate Limiting**: Built-in protection against spam detection

## Tech Stack

- **Python 3.11+**
- **Telethon** - Telegram MTProto API client
- **FastAPI** - REST API framework
- **PostgreSQL** - Database
- **Redis** - Caching and rate limiting
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **OpenAI API** - LLM for conversations
- **Docker** - Containerization

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Telegram API credentials ([my.telegram.org](https://my.telegram.org))
- OpenAI API key

### Installation

1. **Clone the repository**

```bash
cd /home/ubuntu/telegram_agent
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Configure settings**

```bash
cp config/settings.example.yaml config/settings.yaml
cp config/personas.example.yaml config/personas.yaml
# Customize as needed
```

6. **Start services (PostgreSQL and Redis)**

```bash
# Using Docker Compose
cd docker && docker-compose up -d db redis

# Or use local installations
```

7. **Run database migrations**

```bash
alembic upgrade head
```

8. **Start the API server**

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
cd docker
docker-compose up -d
```

This will start:
- Application on port 8000
- PostgreSQL on port 5432
- Redis on port 6379

## Configuration

### Environment Variables (.env)

```env
# Telegram
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+905551234567

# OpenAI
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4-turbo-preview

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/telegram_agent

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Warm-up Stages

The agent uses a 5-stage warm-up system to gradually increase activity:

| Stage | Days | Messages/Day | Groups | Actions |
|-------|------|--------------|--------|----------|
| 1 | 1-7 | 5 | 2 | Read, React |
| 2 | 8-14 | 15 | 5 | + Reply |
| 3 | 15-28 | 30 | 10 | + Initiate |
| 4 | 29-42 | 50 | 15 | + DM Reply |
| 5 | 43+ | 100 | 25 | + DM Initiate |

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

```
GET  /api/analytics/dashboard     - Dashboard statistics
GET  /api/warmup/status           - Warm-up status

POST /api/campaigns               - Create campaign
GET  /api/campaigns               - List campaigns
POST /api/campaigns/{id}/activate - Activate campaign

POST /api/groups                  - Add group
GET  /api/groups                  - List groups

GET  /api/leads                   - List leads
GET  /api/leads/export/csv        - Export leads

POST /api/personas                - Create persona
GET  /api/personas                - List personas
```

## Project Structure

```
telegram_agent/
├── src/
│   ├── core/              # Core bot and config
│   ├── modules/
│   │   ├── account/       # Account management
│   │   ├── warmup/        # Warm-up tracking
│   │   ├── persona/       # Persona engine
│   │   ├── conversation/  # Conversation handler
│   │   ├── marketing/     # Marketing manager
│   │   ├── group_discovery/ # Group finder
│   │   └── analytics/     # Analytics dashboard
│   ├── api/               # FastAPI endpoints
│   ├── database/          # SQLAlchemy models
│   ├── services/          # External services
│   └── utils/             # Utilities
├── config/                # Configuration files
├── alembic/               # Database migrations
├── docker/                # Docker files
├── tests/                 # Test suite
└── requirements.txt
```

## Usage Guide

### 1. First-Time Setup

1. Get Telegram API credentials from [my.telegram.org](https://my.telegram.org)
2. Run the login script to generate session string
3. Configure warm-up settings based on your account age

### 2. Create a Campaign

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/campaigns",
        json={
            "name": "Tech Product Launch",
            "user_id": 1,
            "persona_id": 1,
            "target_keywords": ["AI", "automation", "productivity"],
            "product_info": "Our AI tool helps with..."
        }
    )
```

### 3. Add Target Groups

```python
await client.post(
    "http://localhost:8000/api/groups",
    json={
        "telegram_id": 1234567890,
        "title": "Tech Enthusiasts",
        "username": "techenthusiasts",
        "campaign_id": 1
    }
)
```

### 4. Monitor Progress

```python
# Check warm-up status
status = await client.get("http://localhost:8000/api/warmup/status")

# Get dashboard stats
stats = await client.get("http://localhost:8000/api/analytics/dashboard")

# Export leads
leads = await client.get("http://localhost:8000/api/leads/export/csv")
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
black src/ tests/
isort src/ tests/
```

### Type Checking

```bash
mypy src/
```

## Security Considerations

- Never commit `.env` or session strings
- Use environment variables for sensitive data
- Rotate API keys regularly
- Monitor for suspicious activity
- Implement proper access controls in production

## License

MIT License - Use at your own risk.

## Contributing

Contributions are welcome! Please read the contributing guidelines first.

---

**Remember**: Always respect platform Terms of Service and local laws regarding automated messaging.
