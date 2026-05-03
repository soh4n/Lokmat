# 🏆 LokMat — GEMINI.md Rubric Audit

**Current Estimated Score: ~35/100**

This audit scores every criterion from the GEMINI.md hackathon rubric and identifies exact gaps.

---

## 📊 Score Breakdown

| #  | Criterion        | Max | Current | Status |
|----|-----------------|-----|---------|--------|
| 1  | Code Quality     | ~17 | 10      | 🟡 Partial |
| 2  | Security         | ~17 | 5       | 🔴 Critical gaps |
| 3  | Efficiency       | ~17 | 6       | 🔴 Critical gaps |
| 4  | Testing          | ~17 | 0       | 🔴 Nothing exists |
| 5  | Accessibility    | ~16 | 8       | 🟡 Partial |
| 6  | Google Services  | ~16 | 6       | 🔴 Only 1 of 5+ required |

---

## 1️⃣ Code Quality (~10/17)

### ✅ What's Done
- FastAPI backend with modular routers (`auth`, `health`, `assistant`, `voter`)
- `pydantic-settings` for configuration (no raw `os.environ`)
- Type hints on service functions (`classify_intent`, `generate_chat_response`)
- Docstrings on all service functions
- Frontend modularized into pages, components, context, services, i18n
- Bilingual i18n (English + Hindi)

### ❌ What's Missing
| Gap | Impact | Required By GEMINI.md |
|-----|--------|----------------------|
| **No `repositories/` layer** — empty directory, SQL queries would go directly in routers | HIGH | "Repository pattern for all DB access. No SQL in routers" |
| **No `models/` ORM layer** — empty directory, in-memory dicts used | HIGH | "SQLAlchemy ORM models" |
| **No Alembic migrations** | HIGH | "db/ — Session factory, Alembic migrations" |
| **Frontend uses `any`-style JS** — no TypeScript, no typed props | MED | "All props typed — zero `any`" |
| **No error boundaries** in React | MED | "Error boundaries wrapping every page-level component" |
| **No `constants/strings.ts`** — strings in components | LOW | "All user-visible strings in constants/strings.ts" |
| **`__init__.py` module docstrings** incomplete | LOW | "All new modules need module-level docstring" |
| **No `ruff` or `mypy` config** | MED | "ruff for linting, mypy --strict" |
| **No `Dockerfile`** | HIGH | Project structure requirement |
| **No `docker-compose.yml`** | HIGH | "Local dev only" |
| **No `README.md`** | HIGH | Project root requirement |
| **No `LICENSE`** file | MED | "Apache-2.0" |
| **No `.github/workflows/ci.yml`** | HIGH | CI pipeline requirement |
| **No `cloudbuild.yaml`** | HIGH | Cloud Build requirement |

---

## 2️⃣ Security (~5/17)

### ✅ What's Done
- JWT-based authentication (`python-jose`)
- Global exception handler (no raw errors leaked)
- CORS configured (not wildcard)
- `.env.example` exists
- Pydantic request validation

### ❌ What's Missing
| Gap | Impact | Required |
|-----|--------|----------|
| **No Firebase Auth** — using custom phone/OTP mock | CRITICAL | "Verify server-side with Firebase Admin SDK" |
| **No Secret Manager** — secrets in `.env` file | HIGH | "All credentials in Secret Manager" |
| **API key HARDCODED in frontend** (`AIzaSyC7d...`) | CRITICAL | "Zero secrets in code or committed files" |
| **No rate limiting middleware** | HIGH | "Redis-backed middleware in FastAPI. Default: 60 req/min" |
| **No Cloud Armor** | MED | "Rate limiting and DDoS at load balancer" |
| **No HTTPS enforcement** | MED | "Cloud Run enforces TLS termination" |
| **No Content Safety on backend** | HIGH | "Vertex AI safety settings on every Gemini call" — only done on frontend |
| **No `aria-required` or input validation** on forms | MED | "Required fields marked with aria-required" |
| **No prompt injection hardening** | MED | "User content sandboxed behind role boundary" |

> [!CAUTION]
> **The Gemini API key is hardcoded in two frontend files** (`Home.jsx` and `AIGuide.jsx`). This is the #1 security issue to fix.

---

## 3️⃣ Efficiency (~6/17)

### ✅ What's Done
- `gemini-2.0-flash-lite` used for chat (cheap model)
- Retry with exponential backoff decorator (`utils/retry.py`)
- Rolling window of last 10 turns for context
- `maxOutputTokens: 1024` cap

### ❌ What's Missing
| Gap | Impact | Required |
|-----|--------|----------|
| **No Redis caching** — no response caching | HIGH | "Cache repeated prompts in Redis with 5-min TTL" |
| **No streaming** — waits for full response | CRITICAL | "Use streaming (stream=True) for all chat inference" |
| **No model routing logic** — no Flash vs Pro switching | MED | "Model Routing: Flash (default), Pro (complex)" |
| **No Cloud Tasks** for background jobs | MED | "Batch non-urgent calls via Cloud Tasks" |
| **No token budget tracking** | MED | "WARN_THRESHOLD_TOKENS = 50,000" |
| **No connection pooling** — no real DB | HIGH | "SQLAlchemy pool_size=10, max_overflow=20" |
| **No GCS lifecycle rules** | LOW | "auto-delete temp objects after 7 days" |
| **No cost guardrails** (budget alerts) | LOW | "GCP resource tags + monitoring" |

---

## 4️⃣ Testing (~0/17)

### ❌ NOTHING EXISTS

| Gap | Impact | Required |
|-----|--------|----------|
| **No `tests/` directory** at all | CRITICAL | Must have `unit/`, `integration/`, `e2e/` |
| **No pytest** setup | CRITICAL | "pytest + pytest-asyncio, >= 80% coverage" |
| **No integration tests** | CRITICAL | "All API routes, auth flows" |
| **No Playwright E2E** | CRITICAL | "Happy path + auth + a11y audit" |
| **No k6 load tests** | HIGH | "50 concurrent users, <2% errors" |
| **No axe-core a11y tests** | HIGH | "WCAG 2.1 AA with zero violations" |
| **No `respx` mocking** | MED | "Use respx for async HTTP mocking" |

> [!WARNING]
> Testing is 0%. This alone loses ~17 points. This is the single largest deficit.

---

## 5️⃣ Accessibility (~8/16)

### ✅ What's Done
- Semantic HTML (`<main>`, `<section>`, `<nav>`, `<button>`)
- `role="log"` and `aria-live="polite"` on chat
- `aria-label` on interactive elements
- `aria-busy` on send button
- Keyboard-accessible form inputs
- Mobile-responsive layout (tested at 480px)
- One `<h1>` per page
- Material Symbols icons

### ❌ What's Missing
| Gap | Impact | Required |
|-----|--------|----------|
| **No focus ring management** — no custom visible focus styles | MED | "Visible focus ring on all focusable elements" |
| **No focus trap** on modals/drawers | MED | "Modal traps focus inside while open" |
| **No `prefers-reduced-motion`** handling | MED | "Honour prefers-reduced-motion" |
| **No `prefers-contrast`** support | LOW | "Provide high-contrast mode" |
| **No skip-to-content link** | MED | Keyboard nav best practice |
| **No `aria-describedby` on errors** | MED | "Error messages linked to inputs" |
| **No loading skeletons** | MED | "Skeleton/loading state on every async fetch" |
| **No offline banner** | LOW | "Show meaningful offline banner" |
| **Touch targets not verified** | MED | "Touch targets >= 44x44px" |
| **No axe-core CI validation** | HIGH | "axe-core WCAG 2.1 AA audit with zero violations" |

---

## 6️⃣ Google Services (~6/16)

### Current Integration

| Service | Status | How Used |
|---------|--------|----------|
| **Gemini API (Flash)** | ✅ Working | VoteSathi AI chat, intent classification |

### ❌ Missing Services (GEMINI.md requires 5+ meaningful services)

| Service | Status | Required Use |
|---------|--------|-------------|
| **Cloud Run** | 🔴 Missing | Serverless container hosting |
| **Cloud SQL (PostgreSQL)** | 🔴 Missing | Persistent storage for users, sessions |
| **Secret Manager** | 🔴 Missing | Runtime injection of API keys |
| **Memorystore (Redis)** | 🔴 Missing | Session cache, rate limits |
| **Cloud Storage (GCS)** | 🔴 Missing | File uploads, session transcripts |
| **Firebase Auth** | 🔴 Missing | OAuth sign-in, token verification |
| **Cloud Build** | 🔴 Missing | CI/CD pipeline |
| **Cloud Logging** | 🔴 Missing | Structured JSON logs, audit |
| **Cloud Monitoring** | 🔴 Missing | Custom metrics, alerts |
| **Cloud Armor** | 🔴 Missing | DDoS, rate limiting |
| **Cloud Tasks / Pub/Sub** | 🔴 Missing | Async background jobs |
| **Artifact Registry** | 🔴 Missing | Container images + vuln scanning |
| **Text Embeddings API** | 🔴 Missing | Semantic search over sessions |

> [!IMPORTANT]
> Only **1 of 15 required Google Services** is integrated. The rubric requires **at least 5 meaningful** integrations. This is the second-largest deficit after testing.

---

## 🎯 Demonstration Requirements Audit

| Requirement | Status | Details |
|-------------|--------|---------|
| Smart, dynamic assistant | 🟡 Partial | VoteSathi AI works but no streaming, no context pipeline through backend |
| Logical decision-making on user context | 🟡 Partial | Intent classification exists, but no context enrichment (step 2) |
| Effective use of Google Services (≥5) | 🔴 Only 1 | Only Gemini Flash |
| Practical and real-world usability | 🟡 Partial | Good UI but no session persistence, no streaming, no offline states |
| Clean and maintainable code | 🟡 Partial | Good structure but no types, no tests, no linting |

---

## 📋 Context Pipeline Check (Required for every interaction)

| Step | Status |
|------|--------|
| 1. Intent Classification | ✅ `classify_intent()` in `gemini_service.py` |
| 2. Context Enrichment (Redis + DB) | 🔴 Missing — no Redis, no DB |
| 3. Prompt Construction | 🟡 System prompt exists but no user profile enrichment |
| 4. Model Routing (Flash vs Pro) | 🔴 Missing — always uses Flash |
| 5. Gemini Inference | ✅ Working |
| 6. Response Validation (safety check) | 🔴 Missing on backend |
| 7. Structured Output | 🟡 Partial — suggestions extracted |
| 8. Audit Log (Cloud Logging) | 🔴 Missing |

---

## 🗺️ UX Patterns Check

| Pattern | Status |
|---------|--------|
| Streaming responses (first token <500ms) | 🔴 Missing — full completion wait |
| Optimistic UI | 🟡 Message appears immediately |
| Session persistence (survive browser close) | 🟡 Auth persists, chat history doesn't |
| Context-aware follow-up suggestions | 🟡 Extracted from response |
| Clear error recovery | 🟡 Basic error messages |
| Typing indicator | ✅ Animated dots |
| Copy to clipboard | 🔴 Missing |
| Clear conversation | 🔴 Missing |

---

## 🚀 Priority Fixes to Maximize Score

### Tier 1 — High ROI, Quick Wins (+25 pts)

1. **Remove hardcoded API key** from frontend → route through backend only
2. **Add `tests/`** with at least 5 unit tests + 3 integration tests
3. **Add `Dockerfile`, `docker-compose.yml`, `README.md`, `LICENSE`**
4. **Add `.github/workflows/ci.yml`** with lint + test
5. **Add streaming responses** (`stream=True` on Gemini calls)
6. **Add Firebase Auth** (replace mock OTP)

### Tier 2 — Medium Effort, High Impact (+20 pts)

7. **Add Cloud SQL** (PostgreSQL) for user/session storage
8. **Add Redis** (Memorystore) for session cache + rate limiting
9. **Add Cloud Logging** (structured JSON logs)
10. **Add rate limiting middleware** in FastAPI
11. **Add accessibility improvements** (focus management, skip link, `prefers-reduced-motion`)
12. **Add Playwright E2E test** with axe-core

### Tier 3 — Full Score Polish (+20 pts)

13. **Cloud Run deployment** with `cloudbuild.yaml`
14. **Secret Manager** for all credentials
15. **Cloud Storage** for voter slip PDFs
16. **Cloud Monitoring** with custom metrics
17. **Text Embeddings** for semantic search
18. **TypeScript migration** for frontend
