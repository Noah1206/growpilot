# 🚀 GrowthPilot - AI-Powered SaaS Outreach Automation

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11+-yellow.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal.svg)

**GrowthPilot** is an AI-powered outreach automation platform that helps SaaS founders generate personalized, platform-specific marketing content for LinkedIn, Reddit, and Facebook. Using Google Gemini AI, it automatically infers your Ideal Customer Profile (ICP), generates targeted search queries, creates compliant copy variants, and provides analytics-driven recommendations.

---

## ✨ Features

### 🎯 Core Capabilities
- **Intelligent ICP Inference**: Automatically deduce target customer profiles from product descriptions
- **Multi-Platform Support**: Native content generation for LinkedIn, Reddit, and Facebook
- **A/B Testing**: Generate 2-3 variants per platform with different tones
- **Compliance Enforcement**: Built-in platform rule validation and anti-spam guardrails
- **Performance Analytics**: Track metrics and get AI-powered strategic recommendations
- **Response Analysis**: Classify prospect replies and suggest intelligent follow-ups

### 🤖 AI Agent Chain
1. **ICP Planner**: Infers ideal customer roles, industries, keywords, and search parameters
2. **Query Builder**: Generates platform-specific search queries for prospect discovery
3. **Copy Generators**: Creates LinkedIn DMs, Reddit comments, and Facebook posts
4. **Policy Reviewer**: Validates content against platform rules and safety policies
5. **Conversation Analyst**: Classifies responses and suggests follow-up messages
6. **Campaign Reporter**: Analyzes performance data and recommends optimizations

### 🛡️ Safety & Compliance
- Daily send limits per platform
- Blocked phrase detection
- Mandatory disclosure requirements
- Link policy enforcement
- Tone and length validation
- Human-in-the-loop approval workflow

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Frontend (HTML/CSS/JavaScript)             │
│         Responsive UI • Form Validation • Results       │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (HTTPS)
┌────────────────────▼────────────────────────────────────┐
│                FastAPI Backend (Python)                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │  API Routes • Agent Orchestration • Validation   │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  6 AI Agents (Gemini-powered)                    │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  SQLAlchemy ORM • Pydantic Validation            │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│             Supabase PostgreSQL Database                │
│    campaigns • performance_metrics • users (optional)   │
└─────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               Google Gemini API                         │
│          AI Agent Chain Execution Engine                │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend development)
- Supabase account (free tier available)
- Google AI Studio API key (Gemini)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/GrowthPilot.git
cd GrowthPilot

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database URL

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 6000

# Frontend setup (in new terminal)
cd ../frontend
python -m http.server 9000  # Or use any static server
```

Visit `http://localhost:9000` to access the application.

---

## 📖 Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)** - System design, tech stack, patterns
- **[API Reference](docs/API.md)** - Complete endpoint documentation
- **[Setup Guide](docs/SETUP.md)** - Development and deployment instructions
- **[Agent Specifications](docs/AGENTS.md)** - AI agent prompts and schemas
- **[Database Schema](docs/DATABASE.md)** - Tables, relationships, migrations
- **[Frontend Guide](docs/FRONTEND.md)** - UI components and user flows
- **[Deployment](docs/DEPLOYMENT.md)** - Railway deployment guide
- **[Security](docs/SECURITY.md)** - Security best practices

---

## 🎮 Usage Example

### 1. Input Product Information
```javascript
{
  "product_name": "AIStockAnalyst",
  "description": "AI-powered stock recommendation tool for retail investors",
  "target_audience_hint": "retail investors using TradingView",
  "locales": ["US", "SG", "IN"],
  "language_pref": "en",
  "channels": ["linkedin", "reddit", "facebook"],
  "tone": "friendly",
  "cta": "free beta?"
}
```

### 2. Generated ICP
```json
{
  "icp": {
    "roles": ["Retail Investor", "Finance Blogger", "Day Trader"],
    "industries": ["Finance", "Fintech", "Investment Management"],
    "regions": ["US", "Singapore", "India"]
  },
  "keywords": {
    "root": ["stock investing", "AI investing", "stock analysis"],
    "long_tail": ["find trending stocks", "ai stock screener"]
  }
}
```

### 3. Generated LinkedIn Copy (Variant A)
```
Hey Alex, noticed you're into stock analysis tools. Built an AI that
spots trending stocks early using sentiment signals. Want to try the
beta? Would love your feedback as an active investor.
```

### 4. Policy Review Result
```json
{
  "status": "pass",
  "reasons": [],
  "revised": { /* approved variants */ }
}
```

---

## 🔧 Configuration

### Platform Rules
```python
PLATFORM_RULES = {
    "linkedin": {
        "max_chars": 280,
        "links": "one_link",
        "tone": "value_first",
        "ban": ["financial guarantees", "spammy urgency"]
    },
    "reddit": {
        "max_sentences": 5,
        "links": "one_link",
        "tone": "conversational",
        "ban": ["pure self-promo", "multi-link dumping"]
    },
    "facebook": {
        "max_sentences": 6,
        "links": "one_link",
        "tone": "friendly",
        "ban": ["aggressive selling", "misleading claims"]
    }
}
```

### Safety Limits
```python
SAFETY_CONFIG = {
    "max_daily_sends": {
        "linkedin": 200,
        "reddit": 30,
        "facebook": 50
    },
    "require_approval": True,
    "blocked_phrases": [
        "guaranteed returns",
        "get rich quick",
        "limited time only"
    ]
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v

# Run integration tests only
pytest tests/test_api.py -v
```

---

## 📊 API Endpoints

### Agent Chain
- `POST /api/agents/icp` - Generate ICP from product description
- `POST /api/agents/queries` - Build platform-specific search queries
- `POST /api/agents/linkedin` - Generate LinkedIn copy variants
- `POST /api/agents/reddit` - Generate Reddit copy variants
- `POST /api/agents/facebook` - Generate Facebook copy variants
- `POST /api/agents/review` - Review copy for compliance
- `POST /api/agents/analyze` - Analyze prospect responses
- `POST /api/agents/report` - Generate performance report

### Campaign Management
- `POST /api/campaigns/generate` - Run full agent chain
- `GET /api/campaigns` - List all campaigns
- `GET /api/campaigns/{id}` - Get campaign details
- `PUT /api/campaigns/{id}` - Update campaign
- `DELETE /api/campaigns/{id}` - Delete campaign

### Utilities
- `GET /health` - Health check
- `GET /docs` - Swagger UI (auto-generated)
- `GET /redoc` - ReDoc API documentation

---

## 🚢 Deployment

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Environment Variables
```env
GEMINI_API_KEY=your_key
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_key
DATABASE_URL=postgresql://...
SECRET_KEY=your_secret
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Code style guidelines
- Pull request process
- Development workflow
- Testing requirements

---

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** - AI agent execution engine
- **FastAPI** - High-performance async web framework
- **Supabase** - PostgreSQL database and auth
- **Railway** - Deployment platform

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/GrowthPilot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/GrowthPilot/discussions)

---

## 🗺️ Roadmap

- [ ] Multi-language support (Korean, Spanish, French)
- [ ] Email outreach integration
- [ ] Twitter/X thread generator
- [ ] CRM integrations (HubSpot, Salesforce)
- [ ] Advanced analytics dashboard
- [ ] Browser extension for LinkedIn
- [ ] Mobile app (iOS/Android)

---

**Built with ❤️ for SaaS founders who want to grow efficiently and authentically.**
# growpilot
