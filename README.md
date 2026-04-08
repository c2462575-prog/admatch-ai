# 🎯 AdMatch AI

**AI 驅動的網紅行銷媒合平台** — 用 AI 自動完成匹配推薦、價值評估、談判模擬、合約建議。

🌐 **Live Demo:** [https://yc79-admatch-ai.hf.space](https://yc79-admatch-ai.hf.space)
📖 **API Docs:** [https://yc79-admatch-ai.hf.space:8000/docs](localhost:8000/docs when running locally)

---

## Features

| Feature | Description |
|---------|-------------|
| **AI Smart Matching** | 四維加權評分 (Embedding 40% + Audience 25% + Budget 20% + Values 15%) |
| **3-Round Negotiation** | AI 模擬廣告主、創作者、觀眾三方談判 |
| **Audience Scoring** | 觀眾反應評分 + 介入警告機制 |
| **Match Insights** | 自動生成匹配解釋 + 推薦等級標籤 |
| **Pricing Calculator** | 根據粉絲數/互動率/類別估算合理報價 + ROI |
| **Dual-Role System** | 廣告主和創作者各有獨立儀表板 + Onboarding |
| **Freemium Model** | Free (3 matches/mo) / Basic (¥299) / Pro (¥999) |

## Tech Stack

```
Frontend:  Streamlit (11 pages)
Backend:   FastAPI (25 API endpoints)
Database:  SQLite with WAL mode
AI:        Google Gemini API (with keyword fallback)
Auth:      JWT (HMAC-SHA256) + PBKDF2 password hashing
Deploy:    Docker → HuggingFace Spaces
Tests:     55 passing (pytest)
```

## Quick Start

```bash
# Clone
git clone https://github.com/c2462575-prog/admatch-ai.git
cd admatch-ai

# Install
pip install -r requirements.txt

# Run (init DB + seed demo data + start API + Streamlit)
python scripts/run_dev.py
```

- **API:** http://localhost:8000/docs
- **UI:** http://localhost:8501

### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Advertiser | brewlab@demo.admatch.ai | demo123 |
| Advertiser | clouddesk@demo.admatch.ai | demo123 |
| Advertiser | naturestep@demo.admatch.ai | demo123 |
| Creator | ken@demo.admatch.ai | demo123 |
| Creator | mia@demo.admatch.ai | demo123 |
| Creator | devtalk@demo.admatch.ai | demo123 |

## Architecture

```
frontend/          Streamlit multipage app (11 pages)
  pages/           Home, Login, Register, Dashboards, Profiles,
                   Matches, Negotiation, History, Pricing, Plans
  utils/           API client, charts, onboarding, navigation, insights

api/               FastAPI application
  routes/          auth, advertisers, creators, matching,
                   negotiations, pricing, stats

services/          Business logic layer
  auth_service     Register/login with JWT
  profile_service  Wraps AI agents for profile analysis
  matching_service Embedding + keyword fallback matching
  negotiation_service  Per-round AI negotiation

core/              Infrastructure
  config           Environment-based configuration
  database         SQLite schema (6 tables) + CRUD
  security         JWT + password hashing
  dependencies     FastAPI dependency injection

agents/            AI Agents (Google Gemini)
  advertiser_agent Campaign analysis + offer generation
  creator_agent    Content analysis + response generation
  audience_agent   Audience scoring + intervention

engine/            Matching algorithms
  embedding        Gemini embedding generation
  matching         Cosine similarity + weighted scoring
```

## Environment Variables

```bash
GEMINI_API_KEY=your_key        # Required for AI features
JWT_SECRET=random_string       # Auto-generated if not set
DATABASE_PATH=data/app.db      # SQLite database path
FREE_MATCHES_PER_MONTH=3       # Freemium limit
```

## Docker

```bash
docker-compose up
```

## Tests

```bash
python -m pytest tests/ -v     # 55 tests
```

## License

MIT
