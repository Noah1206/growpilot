# GrowthPilot - Quick Start Guide

Get GrowthPilot running in 5 minutes!

## Prerequisites

- Python 3.11+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Supabase account (free tier) or local PostgreSQL

## Setup Steps

### 1. Clone and Setup Backend

```bash
# Clone repo
git clone https://github.com/yourusername/GrowthPilot.git
cd GrowthPilot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

**Required variables:**
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/growthpilot
SECRET_KEY=any_random_string_here
```

### 3. Setup Database

**Option A: Supabase (Recommended)**
```bash
# Get connection string from Supabase dashboard
# Update DATABASE_URL in .env
# Run migrations
alembic upgrade head
```

**Option B: Local PostgreSQL**
```bash
# Create database
createdb growthpilot

# Run migrations
alembic upgrade head
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload --port 6000
```

Visit http://localhost:6000/docs to see API documentation.

### 5. Start Frontend

In a new terminal:

```bash
cd ../frontend
python -m http.server 9000
```

Visit http://localhost:9000 to use the application!

## Test the Application

1. Open http://localhost:9000
2. Fill in the form:
   - Product Name: `TestProduct`
   - Description: `An AI tool for testing GrowthPilot`
   - Leave other fields as default
3. Click "Generate Campaign"
4. Wait 30-60 seconds for results

## Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (must be 3.11+)
- Activate virtual environment
- Verify all requirements installed: `pip list`

**Database errors?**
- Verify DATABASE_URL format is correct
- For Supabase, use the pooler connection string
- Run migrations: `alembic upgrade head`

**Frontend can't connect?**
- Ensure backend is running on port 6000
- Check browser console for CORS errors
- Verify API_BASE_URL in `frontend/static/js/app.js`

**Gemini API errors?**
- Verify API key is correct in `.env`
- Restart backend after changing `.env`
- Check API key at https://makersuite.google.com/app/apikey

## Next Steps

- Read [full setup guide](docs/SETUP.md) for detailed instructions
- Review [API documentation](docs/API.md) for endpoint details
- Check [README.md](README.md) for feature overview

## Need Help?

- Check [GitHub Issues](https://github.com/yourusername/GrowthPilot/issues)
- Read the [documentation](docs/)
- Join [discussions](https://github.com/yourusername/GrowthPilot/discussions)

Happy automating! 🚀
