# 🎯 AdMatch AI

**AI 驅動的網紅行銷媒合平台** — 用 AI 自動完成匹配推薦、價值評估、談判模擬、合約建議。

🌐 **Live Demo:** [https://yc79-admatch-ai.hf.space](https://yc79-admatch-ai.hf.space)

---

## Features

| Feature | Description |
|---------|-------------|
| **AI Smart Matching** | 四維加權評分 (Embedding 40% + Audience 25% + Budget 20% + Values 15%) + 無 API 時 keyword fallback |
| **3-Round Negotiation** | AI 模擬廣告主、創作者、觀眾三方談判 |
| **Audience Scoring** | 觀眾反應評分 + 介入警告機制 |
| **Match Insights** | 自動生成中文匹配解釋 + 推薦等級標籤 (🟢🟡🟠🔴) |
| **Public Creator Explore** | 未登入即可瀏覽創作者，驅動 top-of-funnel 獲客 |
| **Pricing Calculator** | 根據粉絲數/互動率/類別估算合理報價 + ROI |
| **Dual-Role Dashboards** | 廣告主/創作者獨立儀表板 + Onboarding checklist |
| **Activity Feed** | 匹配/談判/新用戶動態時間線，促進留存 |
| **Referral System** | 邀請碼 + 每邀 1 人 +2 次匹配，病毒式增長 |
| **Freemium Plans** | Free / Basic (¥299) / Pro (¥999) 三種方案 |
| **Profile Completeness** | 視覺化完成度指標，Zeigarnik effect 驅動填寫 |
| **Admin Dashboard** | 用戶/匹配/談判/增長/錯誤全面分析 |
| **Error Tracking** | Ring buffer 錯誤追蹤 + admin 可視化 |
| **Security** | JWT auto-secret + PBKDF2 + rate limiting (60 req/min/IP) |
| **Legal** | 使用條款 + 隱私政策（中文） |

## Tech Stack

```
Frontend:  Streamlit (15 pages)
Backend:   FastAPI (30+ API endpoints)
Database:  SQLite with WAL mode (7 tables)
AI:        Google Gemini API (with keyword fallback)
Auth:      JWT (HMAC-SHA256) + PBKDF2 password hashing
Deploy:    Docker → HuggingFace Spaces
Tests:     62 passing (pytest)
```

## Quick Start

```bash
git clone https://github.com/c2462575-prog/admatch-ai.git
cd admatch-ai
pip install -r requirements.txt
python scripts/run_dev.py
```

- **API:** http://localhost:8000/docs
- **UI:** http://localhost:8501

### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Advertiser | brewlab@demo.admatch.ai | demo123 |
| Advertiser | clouddesk@demo.admatch.ai | demo123 |
| Creator | ken@demo.admatch.ai | demo123 |
| Creator | mia@demo.admatch.ai | demo123 |

## Architecture

```
frontend/          Streamlit multipage app (15 pages)
  pages/           Home, Explore, Login, Register, Dashboards, Profiles,
                   Matches, Negotiation, History, Pricing, Plans, Admin, Terms
  utils/           API client, charts, onboarding, navigation, insights,
                   profile completeness

api/               FastAPI application
  routes/          auth, advertisers, creators, matching, negotiations,
                   pricing, stats, referrals, explore, activity

services/          Business logic layer
  auth_service     Register/login with JWT + referral codes
  profile_service  AI agent analysis + embedding generation
  matching_service Embedding + keyword fallback matching
  negotiation_service  Per-round AI negotiation

core/              Infrastructure
  config           Environment-based config + security validation
  database         SQLite schema (7 tables) + CRUD
  security         JWT + password hashing
  dependencies     FastAPI dependency injection
  error_tracker    In-memory error ring buffer
```

## Environment Variables

```bash
GEMINI_API_KEY=your_key        # Required for AI features
JWT_SECRET=random_string       # Auto-generated if not set
DATABASE_PATH=data/app.db      # SQLite database path
FREE_MATCHES_PER_MONTH=3       # Freemium limit
```

## Tests

```bash
python -m pytest tests/ -v     # 62 tests
```

## Development History

20 iterations of VC-driven improvement:
1. Platform stats social proof
2. Keyword matching fallback
3. Onboarding checklist
4. Pricing plans page
5. Health check + logging
6. Auth redirect flow
7. Match insights + verdicts
8. JWT security hardening
9. Security + matching tests
10. Production README
11. Referral system
12. Admin analytics dashboard
13. Profile completeness bar
14. Terms + privacy + rate limiting
15. AI pipeline wired up
16. Match filtering + growth prompt
17. Public creator explore
18. Activity feed
19. Error tracking system
20. Final sync + README update

## License

MIT
