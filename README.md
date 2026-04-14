# PromptForge AI

<p align="center">
  <strong>⚡ Transform simple requests into powerful, optimized AI prompts</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License" />
</p>

---

## What is PromptForge AI?

PromptForge AI is a full-stack SaaS platform that **automatically engineers optimized prompts** for AI models. Users describe what they need in plain language, and the system converts it into a structured, high-quality prompt using prompt engineering best practices — then executes it against the selected AI model.

### ✨ Key Features

- **🧠 Intent Analyzer** — Classifies requests into coding, content, research, marketing, education, or analysis
- **🏗️ Prompt Architect** — Structures prompts with Role, Context, Task, Constraints, Output Format
- **✨ Prompt Optimizer** — Applies chain-of-thought, few-shot examples, quality checklists
- **🔒 Security Scanner** — Detects prompt injection, API keys, credentials, PII exposure
- **🔧 Prompt Debugger** — Score any prompt and get improvement suggestions
- **🤖 6 AI Models** — OpenAI GPT-4, Claude, Gemini, Mistral, DeepSeek, Ollama (local)
- **🔄 Workflow Engine** — Chain multi-step prompts for complex tasks
- **📚 Prompt Library** — Save & organize your best prompts
- **🔐 Encrypted API Keys** — Per-user, AES-encrypted key storage at rest

---

## Architecture

```
User Input → Intent Analysis → Context Building → Prompt Architect
→ Prompt Optimizer → Security Scanner → AI Model → Response
```

| Layer | Technology | Description |
|-------|-----------|-------------|
| **Frontend** | Next.js 16, React, Tailwind CSS | SPA with dark theme, glassmorphism |
| **Backend** | FastAPI, Python 3.9+ | REST API with JWT auth |
| **Database** | SQLite (default) / PostgreSQL | SQLAlchemy ORM |
| **Encryption** | Fernet (AES) | API keys encrypted at rest |
| **Auth** | JWT + bcrypt | Stateless token authentication |

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/promptforge-ai.git
cd promptforge-ai
```

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open

Visit **http://localhost:3000** in your browser.

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | `promptforge-dev-secret...` | **Change in production!** JWT signing key |
| `ENCRYPTION_KEY` | Falls back to `JWT_SECRET` | Used to encrypt stored API keys |
| `DATABASE_URL` | `sqlite:///promptforge.db` | Database connection string |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend origins (comma-separated) |
| `RATE_LIMIT` | `60/minute` | API rate limit |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL (for local models) |

### API Keys

Users add their own API keys via **Settings → API Keys** in the dashboard.
Keys are encrypted with **Fernet (AES-128-CBC)** before being stored in the database and are never logged or exposed.

---

## Project Structure

```
promptforge-ai/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Environment configuration
│   ├── database.py                # SQLAlchemy setup
│   ├── models.py                  # Database models
│   ├── encryption.py              # Fernet encryption utilities
│   ├── requirements.txt
│   ├── api/
│   │   ├── auth.py                # JWT authentication
│   │   └── routes.py              # All API endpoints
│   ├── prompt_engine/
│   │   ├── intent_analyzer.py     # Intent classification
│   │   ├── context_builder.py     # Context extraction
│   │   ├── prompt_architect.py    # Prompt assembly
│   │   ├── prompt_optimizer.py    # Chain-of-thought, few-shot
│   │   ├── prompt_debugger.py     # Prompt scoring
│   │   └── security_scanner.py    # Injection/PII detection
│   ├── model_adapters/
│   │   ├── adapter_factory.py     # Provider selection
│   │   ├── openai_adapter.py
│   │   ├── claude_adapter.py
│   │   ├── gemini_adapter.py
│   │   ├── mistral_adapter.py
│   │   ├── deepseek_adapter.py
│   │   └── ollama_adapter.py
│   └── workflow_engine/
│       └── engine.py              # Multi-step workflows
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Landing page
│   │   │   ├── login/page.tsx
│   │   │   ├── signup/page.tsx
│   │   │   ├── dashboard/page.tsx # Main 3-panel view
│   │   │   ├── debugger/page.tsx
│   │   │   ├── history/page.tsx
│   │   │   ├── library/page.tsx
│   │   │   ├── workflows/page.tsx
│   │   │   └── settings/page.tsx  # API key management
│   │   ├── components/
│   │   │   └── Sidebar.tsx
│   │   └── lib/
│   │       ├── api.ts             # API client
│   │       └── auth.tsx           # Auth context
│   └── package.json
├── .gitignore
├── .env.example
├── LICENSE
└── README.md
```

---

## Security

- **Encrypted API Keys** — Fernet (AES) symmetric encryption at rest
- **JWT Authentication** — Stateless tokens with bcrypt password hashing
- **Rate Limiting** — Configurable via `slowapi`
- **Security Headers** — X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- **Input Validation** — Length limits on all user inputs
- **Prompt Injection Detection** — Built-in security scanner
- **CORS** — Restricted to configured origins only
- **SQL Injection** — Parameterized queries via SQLAlchemy ORM

---

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ using FastAPI + Next.js
</p>
