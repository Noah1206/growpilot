# GrowthPilot Setup Guide

Complete setup instructions for development and production environments.

## Prerequisites

- Python 3.11 or higher
- PostgreSQL database (or Supabase account)
- Google AI Studio API key for Gemini
- Git

## Backend Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/GrowthPilot.git
cd GrowthPilot
```

### 2. Create Virtual Environment

```bash
cd backend
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Google Gemini API
GEMINI_API_KEY=your_actual_key_here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/growthpilot

# Application
SECRET_KEY=generate_a_random_secret_key_here
ENVIRONMENT=development
DEBUG=True

# Security
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 5. Set Up Database

#### Option A: Local PostgreSQL

```bash
# Create database
createdb growthpilot

# Run migrations
alembic upgrade head
```

#### Option B: Supabase

1. Create a new project at [supabase.com](https://supabase.com)
2. Get your database connection string from Settings > Database
3. Update `DATABASE_URL` in `.env`
4. Run migrations:

```bash
alembic upgrade head
```

### 6. Start Backend Server

```bash
uvicorn app.main:app --reload --port 6000
```

The API will be available at `http://localhost:6000`

API Documentation: `http://localhost:6000/docs`

## Frontend Setup

### 1. Navigate to Frontend

```bash
cd ../frontend
```

### 2. Start Static Server

```bash
# Using Python
python -m http.server 9000

# Or using Node.js http-server
npx http-server -p 9000
```

The application will be available at `http://localhost:9000`

## Verify Installation

1. Open `http://localhost:9000` in your browser
2. Fill out the campaign form
3. Click "Generate Campaign"
4. Wait for results (30-60 seconds)

## Troubleshooting

### Database Connection Issues

**Error**: `could not connect to server`

**Solution**:
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL format: `postgresql://user:password@host:port/database`
- For Supabase, ensure you're using the connection pooler URL

### Gemini API Issues

**Error**: `API key not valid`

**Solution**:
- Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Ensure key is correctly set in `.env`
- Restart the backend server after updating `.env`

### CORS Issues

**Error**: `CORS policy blocked`

**Solution**:
- Add frontend URL to `ALLOWED_ORIGINS` in `.env`
- Restart backend server
- Clear browser cache

### Migration Issues

**Error**: `relation "campaigns" does not exist`

**Solution**:
```bash
# Reset migrations
alembic downgrade base
alembic upgrade head
```

## Next Steps

- Read [API Documentation](API.md) for endpoint details
- Review [Architecture Overview](ARCHITECTURE.md) for system design
- Check [Agent Specifications](AGENTS.md) for AI agent details
- See [Deployment Guide](DEPLOYMENT.md) for production setup
