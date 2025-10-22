# GrowthPilot - Project Structure

Complete overview of the project directory structure and file organization.

## Directory Tree

```
GrowthPilot/
├── README.md                          # Main project documentation
├── QUICKSTART.md                      # Quick start guide
├── .gitignore                         # Git ignore rules
│
├── backend/                           # Backend application
│   ├── .env.example                   # Environment variables template
│   ├── requirements.txt               # Python dependencies
│   ├── alembic.ini                    # Alembic configuration
│   │
│   ├── alembic/                       # Database migrations
│   │   ├── env.py                     # Alembic environment
│   │   ├── script.py.mako             # Migration template
│   │   └── versions/                  # Migration files
│   │       └── 001_initial_migration.py
│   │
│   └── app/                           # Main application package
│       ├── __init__.py
│       ├── main.py                    # FastAPI application entry point
│       │
│       ├── core/                      # Core configuration
│       │   ├── __init__.py
│       │   ├── config.py              # Application settings
│       │   └── database.py            # Database connection
│       │
│       ├── models/                    # SQLAlchemy models
│       │   ├── __init__.py
│       │   ├── campaign.py            # Campaign model
│       │   └── performance_metrics.py # Metrics model
│       │
│       ├── schemas/                   # Pydantic schemas
│       │   ├── __init__.py
│       │   └── campaign.py            # Request/response schemas
│       │
│       ├── agents/                    # AI Agents
│       │   ├── __init__.py
│       │   ├── base.py                # Base agent class
│       │   ├── icp_planner.py         # ICP generation
│       │   ├── query_builder.py       # Search query builder
│       │   ├── linkedin_copy.py       # LinkedIn copy generator
│       │   ├── reddit_copy.py         # Reddit copy generator
│       │   ├── facebook_copy.py       # Facebook copy generator
│       │   ├── policy_reviewer.py     # Compliance reviewer
│       │   ├── conversation_analyst.py # Response analyzer
│       │   └── campaign_reporter.py   # Performance reporter
│       │
│       └── api/                       # API routes
│           ├── __init__.py
│           ├── agents.py              # Agent endpoints
│           └── campaigns.py           # Campaign endpoints
│
├── frontend/                          # Frontend application
│   ├── index.html                     # Main HTML file
│   └── static/                        # Static assets
│       ├── css/
│       │   └── styles.css             # Application styles
│       └── js/
│           └── app.js                 # Application JavaScript
│
└── docs/                              # Documentation
    ├── SETUP.md                       # Setup guide
    └── API.md                         # API documentation
```

## File Descriptions

### Root Level

- **README.md**: Main project documentation with features, architecture, and usage
- **QUICKSTART.md**: Quick start guide for getting up and running fast
- **.gitignore**: Git ignore patterns for Python, Node, and environment files

### Backend

#### Configuration Files
- **requirements.txt**: Python package dependencies
- **.env.example**: Template for environment variables
- **alembic.ini**: Alembic migration tool configuration

#### Core Application (`app/`)
- **main.py**: FastAPI application initialization, CORS setup, route registration
- **core/config.py**: Application settings using Pydantic
- **core/database.py**: SQLAlchemy engine and session management

#### Database Models (`models/`)
- **campaign.py**: Campaign data model with all generated content
- **performance_metrics.py**: Campaign performance tracking model

#### Schemas (`schemas/`)
- **campaign.py**: Pydantic models for request/response validation

#### AI Agents (`agents/`)
- **base.py**: Base agent class with Gemini API integration
- **icp_planner.py**: Generates ideal customer profiles
- **query_builder.py**: Creates platform-specific search queries
- **linkedin_copy.py**: Generates LinkedIn DM variants
- **reddit_copy.py**: Generates Reddit comment variants
- **facebook_copy.py**: Generates Facebook post variants
- **policy_reviewer.py**: Validates content against platform rules
- **conversation_analyst.py**: Analyzes prospect responses
- **campaign_reporter.py**: Generates performance reports

#### API Routes (`api/`)
- **agents.py**: Individual agent endpoints
- **campaigns.py**: Campaign CRUD and full chain generation

#### Database Migrations (`alembic/`)
- **env.py**: Alembic environment configuration
- **versions/001_initial_migration.py**: Initial database schema

### Frontend

- **index.html**: Main application interface
- **static/css/styles.css**: Responsive design with gradient theme
- **static/js/app.js**: Form handling, API calls, results display

### Documentation

- **SETUP.md**: Detailed setup instructions for development and production
- **API.md**: Complete API endpoint documentation with examples

## Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migration management
- **Pydantic**: Data validation and settings
- **Google Gemini AI**: AI agent execution engine
- **PostgreSQL**: Primary database (via Supabase)

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern responsive design
- **Vanilla JavaScript**: No framework dependencies
- **Fetch API**: RESTful API communication

## Key Features by Component

### ICP Planner Agent
- Infers target roles, industries, regions
- Identifies pain points
- Generates root and long-tail keywords

### Query Builder Agent
- LinkedIn boolean search queries
- Reddit subreddit and keyword combinations
- Facebook group and interest targeting

### Copy Generator Agents
- Platform-specific tone and format
- 2-3 variants per channel
- Value-first messaging approach

### Policy Reviewer Agent
- Character/sentence limit validation
- Banned phrase detection
- Tone compliance checking
- Auto-revision suggestions

### Conversation Analyst Agent
- Sentiment classification
- Follow-up suggestion
- Response type categorization

### Campaign Reporter Agent
- Performance metrics analysis
- Channel comparison
- Strategic recommendations

## Development Workflow

1. **Backend Development**: Modify agents, add routes, update models
2. **Database Changes**: Create migrations with `alembic revision --autogenerate`
3. **Frontend Updates**: Edit HTML, CSS, or JavaScript as needed
4. **Testing**: Manual testing via frontend or API docs
5. **Documentation**: Update relevant docs when adding features

## Deployment Structure

```
Production/
├── Backend: Railway/Heroku
├── Database: Supabase PostgreSQL
├── Frontend: Vercel/Netlify or serve via FastAPI
└── Environment: Managed via platform secrets
```

## Adding New Features

### New AI Agent
1. Create agent file in `app/agents/`
2. Inherit from `BaseAgent`
3. Add route in `app/api/agents.py`
4. Update `app/agents/__init__.py`

### New Database Model
1. Create model in `app/models/`
2. Create schema in `app/schemas/`
3. Generate migration: `alembic revision --autogenerate`
4. Apply migration: `alembic upgrade head`

### New API Endpoint
1. Add route in appropriate file in `app/api/`
2. Define request/response schemas
3. Update API documentation

## Configuration Files

All configuration is managed through environment variables:
- `.env` for local development (not committed)
- `.env.example` as template
- Platform environment variables for production

## Next Steps

For detailed setup: see [SETUP.md](docs/SETUP.md)
For API details: see [API.md](docs/API.md)
For quick start: see [QUICKSTART.md](QUICKSTART.md)
