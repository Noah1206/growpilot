"""Update existing automation job daily limit to 2000"""
import sqlite3
import os

def update_job_limit():
    """Update the daily limit for job ID 1 to 2000"""

    # Connect to local SQLite database
    db_path = "/Users/johyeon-ung/Desktop/GrowthPilot/backend/growthpilot.db"

    if not os.path.exists(db_path):
        print("❌ Local SQLite database not found")
        print("   The job limit will be updated when Railway redeploys with new config")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current job
        cursor.execute("SELECT id, daily_limit, daily_sent_count, status FROM automation_jobs WHERE id=1")
        job = cursor.fetchone()

        if job:
            job_id, current_limit, sent_count, status = job
            print(f"📊 Current Job Status:")
            print(f"   Job ID: {job_id}")
            print(f"   Current daily limit: {current_limit}")
            print(f"   Already sent today: {sent_count}")
            print(f"   Status: {status}")

            # Update daily limit
            cursor.execute("UPDATE automation_jobs SET daily_limit = 2000 WHERE id = 1")
            conn.commit()

            print(f"✅ Updated daily limit to 2000!")
            print(f"   Remaining today: {2000 - sent_count}")

        else:
            print("❌ No automation job found with ID 1")

        conn.close()

    except Exception as e:
        print(f"❌ Error updating job limit: {e}")

if __name__ == "__main__":
    update_job_limit()