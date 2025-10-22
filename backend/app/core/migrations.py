"""Database migrations for schema updates."""
import logging
from sqlalchemy import inspect, text
from app.core.database import engine

logger = logging.getLogger(__name__)


def run_migrations():
    """Run database migrations to update schema."""
    try:
        inspector = inspect(engine)

        # Check if automation_jobs table exists
        if "automation_jobs" in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('automation_jobs')]

            # Add missing columns if they don't exist
            with engine.connect() as conn:
                if 'platform' not in columns:
                    logger.info("📊 Adding 'platform' column to automation_jobs...")
                    conn.execute(text("ALTER TABLE automation_jobs ADD COLUMN platform VARCHAR(50) DEFAULT 'reddit'"))
                    conn.commit()
                    logger.info("✅ Added 'platform' column")

                if 'use_ai_enhancement' not in columns:
                    logger.info("📊 Adding 'use_ai_enhancement' column to automation_jobs...")
                    conn.execute(text("ALTER TABLE automation_jobs ADD COLUMN use_ai_enhancement BOOLEAN DEFAULT 0"))
                    conn.commit()
                    logger.info("✅ Added 'use_ai_enhancement' column")

                if 'daily_limit' not in columns:
                    logger.info("📊 Adding 'daily_limit' column to automation_jobs...")
                    conn.execute(text("ALTER TABLE automation_jobs ADD COLUMN daily_limit INTEGER DEFAULT 20"))
                    conn.commit()
                    logger.info("✅ Added 'daily_limit' column")

                if 'success_count' not in columns:
                    logger.info("📊 Adding 'success_count' column to automation_jobs...")
                    conn.execute(text("ALTER TABLE automation_jobs ADD COLUMN success_count INTEGER DEFAULT 0"))
                    conn.commit()
                    logger.info("✅ Added 'success_count' column")

                if 'error_count' not in columns:
                    logger.info("📊 Adding 'error_count' column to automation_jobs...")
                    conn.execute(text("ALTER TABLE automation_jobs ADD COLUMN error_count INTEGER DEFAULT 0"))
                    conn.commit()
                    logger.info("✅ Added 'error_count' column")

            logger.info("✅ Database migrations completed successfully")
        else:
            logger.info("ℹ️ No migrations needed - tables will be created fresh")

    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        logger.info("ℹ️ Continuing with table creation...")
