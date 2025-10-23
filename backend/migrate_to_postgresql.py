"""Script to migrate from SQLite to PostgreSQL on Railway"""
import os
from sqlalchemy import create_engine
from app.core.database import Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all models to register them with Base
from app.models.campaign import Campaign
from app.models.user import User
from app.models.campaign_interaction import CampaignInteraction
from app.models.link_click import LinkClick
from app.models.automation_job import AutomationJob
from app.models.automation_log import AutomationLog
from app.models.automation_settings import AutomationSettings
from app.models.performance_metrics import PerformanceMetrics

def migrate_to_postgresql():
    """Create all tables in PostgreSQL database"""

    # Get PostgreSQL URL from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url or "postgresql" not in database_url:
        print("❌ PostgreSQL DATABASE_URL not found in environment variables")
        print("Please set DATABASE_URL with your Railway PostgreSQL connection string")
        return

    print(f"📊 Connecting to PostgreSQL...")
    print(f"   URL: {database_url.split('@')[1] if '@' in database_url else 'hidden'}")

    # Create engine for PostgreSQL
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

    try:
        # Test connection
        with engine.connect() as conn:
            print("✅ Successfully connected to PostgreSQL!")

        # Create all tables
        print("🔨 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")

        # List created tables
        print("\n📋 Created tables:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")

    except Exception as e:
        print(f"❌ Error: {e}")
        return

    print("\n🎉 Migration to PostgreSQL completed!")
    print("\n📝 Next steps:")
    print("1. Update Railway environment variable: DATABASE_URL")
    print("2. Restart your Railway application")
    print("3. Test the application with PostgreSQL")

if __name__ == "__main__":
    migrate_to_postgresql()