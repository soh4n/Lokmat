# 🗳️ LokMat — AI-Powered Election Companion

> **Google for Developers — PromptWars Hackathon**

## 🎯 Chosen Vertical
**Civic / Elections**

LokMat (लोकमत) is a smart, AI-powered election assistant that helps Indian voters navigate the entire electoral process — from registration to casting their vote. It features **VoteSathi AI**, a bilingual (Hindi/English) chatbot powered by Google Gemini, that answers election-related queries with factual, politically neutral information.

## 🧠 Approach and Logic
Our approach prioritizes **speed, security, and accessibility**.
- **Context-Aware AI:** We don't just pass strings to an LLM. We classify intents, retrieve session memory from Redis/Cloud SQL, and enforce strict "Civic/Elections" sandboxing rules before routing to the right Gemini model (Flash for chat, Pro for deep reasoning).
- **Streaming UI:** Using Server-Sent Events (SSE), we bypassed proxy buffering to deliver a sub-500ms first-token latency. The frontend reads the stream in real-time, accompanied by a dynamic blinking cursor.
- **Production-Ready Infrastructure:** We utilized Terraform to provision a fully isolated VPC, Cloud SQL, Redis, and Secret Manager on Google Cloud. 
- **Robust Authentication:** Leveraging Firebase Auth (Google Sign-In), the backend validates JWTs natively without exposing any API keys to the frontend.

## ⚙️ How the Solution Works
1. **Authentication:** The user logs in via Google (Firebase Auth). A secure ID token is passed to the FastAPI backend.
2. **Interaction:** The user asks a question to VoteSathi AI.
3. **Processing:** The FastAPI backend verifies the token, retrieves the user's past session context from Redis, and builds an enriched prompt.
4. **Inference:** The prompt is sent to Vertex AI (Gemini 1.5 Flash).
5. **Streaming:** The response is streamed back via SSE. The React frontend consumes the stream chunks and paints them to the screen instantly, preventing UI blocking or jumping.

## 📝 Assumptions Made
- Users have a relatively modern browser capable of utilizing `ReadableStream` and Server-Sent Events (SSE).
- The target demographic is Indian citizens, so the AI is explicitly tuned to provide context regarding the Election Commission of India (ECI) guidelines and the Indian electoral calendar.
- The GCP environment running the backend has Billing enabled (required for Serverless VPC Access, Cloud SQL, and Vertex AI inference).

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **VoteSathi AI** | Gemini-powered bilingual chatbot for election guidance |
| 🗳️ **Voter Slip** | Digital voter slip generation with EPIC validation |
| 📅 **Election Timeline** | Upcoming elections 2024–2028 with phase tracking |
| 📍 **Booth Finder** | Find your polling station and check queue status |
| 📋 **Candidate Info** | View candidates and party manifestos at a glance |
| 🆘 **SOS / Helpline** | One-tap access to Election Helpline 1950 |
| 🤝 **Volunteering** | Sign up for election day volunteering |
| 📚 **Learn** | Educational content on Lok Sabha & Vidhan Sabha |
| 🌐 **Bilingual** | Full Hindi + English support |
| ♿ **Accessible** | WCAG 2.1 AA compliant with keyboard nav & screen reader support |

---

## 🏗️ Architecture

```
┌───────────────────────────────────────┐
│           Frontend (React + Vite)     │
│    Mobile-first, a11y, Error Boundary │
└───────────────┬───────────────────────┘
                │ HTTPS
┌───────────────▼───────────────────────┐
│          FastAPI Backend              │
│   Rate Limiting · Cloud Logging       │
│   Intent Classification Pipeline      │
├───────────────────────────────────────┤
│   Gemini Flash    │   Gemini Pro      │
│   (Classification │   (Complex        │
│    + Chat)        │    Reasoning)     │
├───────────────────┼───────────────────┤
│   Cloud SQL       │   Memorystore     │
│   (PostgreSQL)    │   (Redis)         │
├───────────────────┴───────────────────┤
│   Cloud Run · Cloud Build · Artifact  │
│   Registry · Cloud Storage · Cloud    │
│   Logging · Cloud Monitoring · Armor  │
└───────────────────────────────────────┘
```

---

## ☁️ Google Services Integration

| # | Service | Role |
|---|---------|------|
| 1 | **Vertex AI — Gemini Flash** | Intent classification, real-time chat, context summarisation |
| 2 | **Vertex AI — Gemini Pro** | Complex multi-step reasoning |
| 3 | **Cloud SQL (PostgreSQL)** | Persistent storage — users, sessions, messages, audit |
| 4 | **Memorystore (Redis)** | Session cache, response cache, rate limit counters |
| 5 | **Cloud Run** | Serverless container hosting |
| 6 | **Cloud Build** | CI/CD pipeline: lint → test → build → deploy |
| 7 | **Artifact Registry** | Container images with vulnerability scanning |
| 8 | **Cloud Storage (GCS)** | Voter slip exports, document storage |
| 9 | **Cloud Logging** | Structured JSON audit logs |
| 10 | **Cloud Monitoring** | Latency, token usage, error rate metrics |
| 11 | **Cloud Armor** | DDoS protection, rate limiting at LB layer |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (optional)

### Local Development

```bash
# Clone the repository
git clone https://github.com/<your-username>/Lokmat.git
cd Lokmat

# Backend
cp api/.env.example api/.env    # Fill in your GEMINI_API_KEY
pip install -r api/requirements.txt
uvicorn api.main:app --reload

# Frontend (in a new terminal)
cd frontend
cp .env.example .env
npm install
npm run dev
```

### Docker Compose

```bash
docker compose up --build
```

This starts PostgreSQL, Redis, the API, and the frontend dev server.

### Run Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests
pytest -v
```

---

## 📐 Project Structure

```
Lokmat/
├── api/                    # FastAPI backend
│   ├── config.py           # pydantic-settings configuration
│   ├── main.py             # App entry, middleware, CORS
│   ├── routers/            # Auth, Health, Chat, Voter endpoints
│   ├── services/           # Gemini, Audit, Cache services
│   ├── repositories/       # User, Session DB repositories
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── db/                 # Database session management
│   └── utils/              # Retry, rate limit, logging
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # Navbar, BottomNav, ErrorBoundary
│   │   ├── pages/          # Home, Login, Profile, Election, etc.
│   │   ├── context/        # Auth, Language providers
│   │   ├── services/       # Typed API client
│   │   └── i18n/           # en.json, hi.json
│   └── public/             # Static assets
├── tests/                  # pytest test suite
│   ├── unit/               # Schema, retry, auth tests
│   └── integration/        # Health, auth flow, chat tests
├── Dockerfile              # Multi-stage production build
├── docker-compose.yml      # Local dev stack
├── cloudbuild.yaml         # GCP CI/CD pipeline
├── .github/workflows/      # GitHub Actions CI
├── LICENSE                 # Apache-2.0
└── GEMINI.md               # Hackathon rubric & rules
```

---

## 🔐 Security

- ✅ **Zero secrets in frontend** — all AI calls routed through backend
- ✅ **JWT authentication** on all protected routes
- ✅ **Pydantic validation** — malformed requests → 422 before service logic
- ✅ **Rate limiting** — 60 req/min general, 10 req/min inference
- ✅ **CORS allowlist** — no wildcard origins
- ✅ **Content safety** — Gemini safety settings on every call
- ✅ **Non-root container** — Docker runs as unprivileged user

---

## ♿ Accessibility (WCAG 2.1 AA)

- Semantic HTML with proper landmark elements
- Keyboard-only navigation with visible focus rings
- Screen reader support (`aria-live`, `aria-label`, `role="log"`)
- Touch targets ≥ 44×44px for mobile
- `prefers-reduced-motion` support
- Error boundaries with recovery actions
- Skip-to-content link

---

## 📄 License

Apache-2.0 — see [LICENSE](./LICENSE)
