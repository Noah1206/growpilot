"""Simple script to test GrowthPilot backend setup."""
import sys
import os

def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.11+")
        return False

def check_env_file():
    """Check if .env file exists."""
    print("\nChecking .env file...")
    if os.path.exists(".env"):
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found - copy .env.example to .env")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "alembic",
        "google.generativeai",
        "pydantic",
    ]

    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not found")
            missing.append(package)

    return len(missing) == 0

def check_env_variables():
    """Check if required environment variables are set."""
    print("\nChecking environment variables...")

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv not installed")
        return False

    required_vars = [
        "GEMINI_API_KEY",
        "DATABASE_URL",
        "SECRET_KEY",
    ]

    missing = []
    for var in required_vars:
        if os.getenv(var):
            # Mask sensitive values
            value = os.getenv(var)
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var} not set")
            missing.append(var)

    return len(missing) == 0

def check_database_connection():
    """Check database connection."""
    print("\nChecking database connection...")

    try:
        from app.core.database import engine
        from sqlalchemy import text

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def check_migrations():
    """Check if migrations are up to date."""
    print("\nChecking database migrations...")

    try:
        from app.core.database import engine
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = ["campaigns", "performance_metrics"]
        missing = [t for t in required_tables if t not in tables]

        if missing:
            print(f"❌ Missing tables: {', '.join(missing)}")
            print("   Run: alembic upgrade head")
            return False
        else:
            print(f"✅ All required tables exist: {', '.join(required_tables)}")
            return True
    except Exception as e:
        print(f"❌ Migration check failed: {str(e)}")
        return False

def main():
    """Run all checks."""
    print("=" * 50)
    print("GrowthPilot Backend Setup Verification")
    print("=" * 50)

    checks = [
        check_python_version(),
        check_env_file(),
        check_dependencies(),
        check_env_variables(),
        check_database_connection(),
        check_migrations(),
    ]

    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)

    passed = sum(checks)
    total = len(checks)

    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print("\nYour backend is ready! Start the server with:")
        print("  uvicorn app.main:app --reload --port 8000")
    else:
        print(f"❌ {total - passed} check(s) failed ({passed}/{total} passed)")
        print("\nPlease fix the issues above before starting the server.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
