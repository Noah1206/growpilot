"""Automation scheduler service for background outreach on Reddit and Twitter."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import SessionLocal
from app.models.automation_job import AutomationJob
from app.models.automation_log import AutomationLog
from app.models.automation_settings import AutomationSettings
from app.models.campaign_interaction import CampaignInteraction
from app.services.reddit_automation import reddit_automation
from app.services.twitter_automation import twitter_automation
from app.services.gemini_ai import GeminiAI

# Initialize Gemini AI service
gemini_ai = GeminiAI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: Optional[AsyncIOScheduler] = None


def create_log(job_id: int, log_type: str, db: Session, **kwargs) -> AutomationLog:
    """Helper function to create automation log entries."""
    log = AutomationLog(
        job_id=job_id,
        log_type=log_type,
        timestamp=datetime.utcnow(),
        username=kwargs.get('username'),
        platform_info=kwargs.get('platform_info'),
        message_preview=kwargs.get('message_preview'),
        status=kwargs.get('status'),
        error_message=kwargs.get('error_message'),
        metadata=kwargs.get('metadata')
    )
    db.add(log)
    db.commit()
    logger.info(f"📝 Log created: {log_type} for job {job_id}")
    return log


def get_daily_limit(user_id: int, db: Session) -> int:
    """Get user's daily limit based on their plan."""
    settings = db.query(AutomationSettings).filter(
        AutomationSettings.user_id == user_id
    ).first()

    # Check if user is premium (placeholder for future implementation)
    # TODO: Implement proper plan checking when payment system is added
    is_premium = False

    if is_premium:
        return 40  # Premium users get 40 messages per day
    else:
        return settings.daily_limit if settings else 20  # Free users get 20


def reset_daily_count_if_needed(job: AutomationJob, db: Session) -> None:
    """Reset daily_sent_count if it's a new day."""
    if not job.last_reset_date:
        job.last_reset_date = datetime.utcnow()
        job.daily_sent_count = 0
        db.commit()
        return

    # Check if it's a new day
    today = datetime.utcnow().date()
    last_reset = job.last_reset_date.date()

    if today > last_reset:
        logger.info(f"Resetting daily count for job {job.id}")
        job.daily_sent_count = 0
        job.last_reset_date = datetime.utcnow()
        db.commit()


async def process_automation_job(job_id: int, db: Session) -> None:
    """Process automation job for Reddit or Twitter."""
    try:
        job = db.query(AutomationJob).filter(AutomationJob.id == job_id).first()
        if not job or job.status != "active":
            return

        logger.info(f"🚀 Starting automation job {job_id} for user {job.user_id}")
        logger.info(f"   Platform: {job.platform}")
        logger.info(f"   Keywords: '{job.search_keywords}'")

        # Get campaign data
        from app.models.campaign import Campaign

        campaign = db.query(Campaign).filter(Campaign.id == job.campaign_id).first()
        if not campaign:
            job.status = "error"
            job.error_message = "Campaign not found"
            db.commit()
            return

        # Get daily limit
        daily_limit = get_daily_limit(job.user_id, db)
        logger.info(f"   Daily limit: {daily_limit}")

        # Reset daily count if needed
        reset_daily_count_if_needed(job, db)

        # Check if we've reached daily limit
        if job.daily_sent_count >= daily_limit:
            logger.info(f"Daily limit reached for job {job.id}")
            return

        # Process based on platform
        if job.platform == "reddit":
            await process_reddit_job(job, campaign, daily_limit, db)
        elif job.platform == "twitter":
            await process_twitter_job(job, campaign, daily_limit, db)
        else:
            job.status = "error"
            job.error_message = f"Unsupported platform: {job.platform}"
            db.commit()
            return

        # Update job
        job.last_run_at = datetime.utcnow()
        job.next_run_at = datetime.utcnow() + timedelta(hours=1)  # Run again in 1 hour
        db.commit()

    except Exception as e:
        logger.error(f"❌ Error processing job {job_id}: {e}")
        import traceback
        traceback.print_exc()

        job = db.query(AutomationJob).filter(AutomationJob.id == job_id).first()
        if job:
            job.status = "error"
            job.error_message = str(e)
            job.retry_count += 1
            db.commit()


async def process_reddit_job(job: AutomationJob, campaign, daily_limit: int, db: Session) -> None:
    """Process Reddit automation job."""
    import json

    # Parse search keywords - handle both JSON and plain text
    try:
        # Try to parse as JSON first (old format: {"subreddit": "...", "keywords": "..."})
        keywords_data = json.loads(job.search_keywords)
        subreddit = keywords_data.get("subreddit", "investing")
        keywords = keywords_data.get("keywords", job.search_keywords)
    except (json.JSONDecodeError, TypeError):
        # Plain text format (new format: just keywords)
        # Use default subreddits based on keywords
        keywords = job.search_keywords

        # Smart subreddit selection based on keywords
        keywords_lower = keywords.lower()
        if any(word in keywords_lower for word in ['developer', 'programming', 'code', 'git', 'software']):
            subreddit = "programming"
        elif any(word in keywords_lower for word in ['product', 'startup', 'entrepreneur']):
            subreddit = "startups"
        elif any(word in keywords_lower for word in ['design', 'ui', 'ux']):
            subreddit = "design"
        else:
            subreddit = "technology"  # Default fallback

    logger.info(f"🔍 Searching r/{subreddit} for: {keywords}")

    # Create search start log
    create_log(
        job.id,
        'search_start',
        db,
        metadata={'subreddit': subreddit, 'keywords': keywords},
        status='searching'
    )

    # Search Reddit posts
    posts = await reddit_automation.search_subreddit(
        subreddit_name=subreddit,
        keywords=keywords,
        limit=100
    )

    if not posts:
        logger.warning(f"No posts found in r/{subreddit}")
        create_log(
            job.id,
            'search_complete',
            db,
            metadata={'subreddit': subreddit, 'users_found': 0},
            status='no_results'
        )
        return

    # Extract unique users
    unique_users = await reddit_automation.extract_unique_users(posts)
    logger.info(f"Found {len(unique_users)} unique users")

    # Create search complete log
    create_log(
        job.id,
        'search_complete',
        db,
        metadata={'subreddit': subreddit, 'users_found': len(unique_users)},
        status='success'
    )

    # Send messages to users
    sent_count = 0
    remaining_slots = daily_limit - job.daily_sent_count

    for username in unique_users[:remaining_slots]:
        try:
            # Get user profile
            profile = await reddit_automation.get_user_profile(username)
            if not profile:
                continue

            # Create sending progress log
            create_log(
                job.id,
                'send_progress',
                db,
                username=username,
                platform_info={
                    'subreddit': subreddit,
                    'karma': profile.get('karma', 0)
                },
                status='sending'
            )

            # Generate personalized message
            if job.use_ai_enhancement:
                # Use AI to enhance the template
                campaign_data = {
                    "product_name": campaign.product_name,
                    "description": campaign.description,
                    "tone": campaign.tone or "friendly",
                    "cta": campaign.cta or "interested in learning more?"
                }
                profile_data = {
                    "name": username,
                    "title": "Reddit user",
                    "company": f"r/{profile.get('recent_comments', [{}])[0].get('subreddit', 'reddit') if profile.get('recent_comments') else 'reddit'}"
                }
                personalized_message = await gemini_ai.generate_personalized_message(
                    campaign_data=campaign_data,
                    profile_data=profile_data
                )
            else:
                # Use template as-is with simple placeholder replacement
                personalized_message = job.message_template.replace("{username}", username)
                personalized_message = personalized_message.replace("{name}", username)

            # Send DM
            success = await reddit_automation.send_dm(
                username=username,
                subject=f"About {campaign.product_name}",
                message=personalized_message
            )

            if success:
                # Save to database
                interaction = CampaignInteraction(
                    campaign_id=job.campaign_id,
                    channel="reddit",
                    interaction_type="sent",
                    prospect_name=username,
                    prospect_profile=f"https://www.reddit.com/user/{username}",
                    message_sent=personalized_message,
                    sent_at=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                db.add(interaction)

                # Update counters
                job.total_sent_count += 1
                job.daily_sent_count += 1
                job.success_count += 1
                sent_count += 1
                db.commit()

                # Create success log
                create_log(
                    job.id,
                    'send_success',
                    db,
                    username=username,
                    platform_info={
                        'subreddit': subreddit,
                        'karma': profile.get('karma', 0)
                    },
                    message_preview=personalized_message[:150] + '...' if len(personalized_message) > 150 else personalized_message,
                    status='success'
                )

                logger.info(f"  ✅ Sent {sent_count}/{remaining_slots} to u/{username}")
            else:
                # Create failure log
                job.error_count += 1
                db.commit()

                create_log(
                    job.id,
                    'send_fail',
                    db,
                    username=username,
                    platform_info={
                        'subreddit': subreddit,
                        'karma': profile.get('karma', 0)
                    },
                    status='failed',
                    error_message='Failed to send DM (user may not accept DMs)'
                )

            # Rate limiting
            await asyncio.sleep(10)

        except Exception as e:
            logger.error(f"  ❌ Error sending to u/{username}: {e}")
            job.error_count += 1
            db.commit()

            # Create error log
            create_log(
                job.id,
                'send_fail',
                db,
                username=username,
                platform_info={'subreddit': subreddit},
                status='error',
                error_message=str(e)
            )
            continue

    logger.info(f"✅ Reddit automation completed! Sent {sent_count} messages")


async def process_twitter_job(job: AutomationJob, campaign, daily_limit: int, db: Session) -> None:
    """Process Twitter automation job."""
    logger.info(f"🔍 Searching Twitter for: {job.search_keywords}")

    # Search tweets
    tweets = await twitter_automation.search_tweets(
        keywords=job.search_keywords,
        max_results=100
    )

    if not tweets:
        logger.warning(f"No tweets found for: {job.search_keywords}")
        return

    # Extract unique users
    unique_users = await twitter_automation.extract_unique_users(tweets)
    logger.info(f"Found {len(unique_users)} unique users")

    # Send messages to users
    sent_count = 0
    remaining_slots = daily_limit - job.daily_sent_count

    for username in unique_users[:remaining_slots]:
        try:
            # Get user profile
            profile = await twitter_automation.get_user_profile(username)
            if not profile:
                continue

            # Generate personalized message
            if job.use_ai_enhancement:
                # Use AI to enhance the template
                campaign_data = {
                    "product_name": campaign.product_name,
                    "description": campaign.description,
                    "tone": campaign.tone or "friendly",
                    "cta": campaign.cta or "interested in learning more?"
                }
                profile_data = {
                    "name": profile['name'],
                    "title": profile.get('bio', 'Twitter user')[:50],
                    "company": "Twitter"
                }
                personalized_message = await gemini_ai.generate_personalized_message(
                    campaign_data=campaign_data,
                    profile_data=profile_data
                )
            else:
                # Use template as-is with simple placeholder replacement
                personalized_message = job.message_template.replace("{username}", username)
                personalized_message = personalized_message.replace("{name}", profile['name'])

            # Send DM
            success = await twitter_automation.send_dm(
                username=username,
                message=personalized_message
            )

            if success:
                # Save to database
                interaction = CampaignInteraction(
                    campaign_id=job.campaign_id,
                    channel="twitter",
                    interaction_type="sent",
                    prospect_name=profile['name'],
                    prospect_profile=profile['profile_url'],
                    message_sent=personalized_message,
                    sent_at=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                db.add(interaction)

                # Update counters
                job.total_sent_count += 1
                job.daily_sent_count += 1
                sent_count += 1
                db.commit()

                logger.info(f"  ✅ Sent {sent_count}/{remaining_slots} to @{username}")

            # Rate limiting
            await asyncio.sleep(15)

        except Exception as e:
            logger.error(f"  ❌ Error sending to @{username}: {e}")
            continue

    logger.info(f"✅ Twitter automation completed! Sent {sent_count} messages")


async def process_all_active_jobs():
    """Process all active automation jobs."""
    db = SessionLocal()
    try:
        # Get all active jobs (Reddit/Twitter only)
        active_jobs = db.query(AutomationJob).filter(
            AutomationJob.status == "active"
        ).all()

        logger.info(f"Found {len(active_jobs)} active automation jobs")

        for job in active_jobs:
            try:
                await process_automation_job(job.id, db)
            except Exception as e:
                logger.error(f"Error processing job {job.id}: {e}")
                continue

    finally:
        db.close()


def start_scheduler():
    """Start the automation scheduler."""
    global scheduler

    if scheduler and scheduler.running:
        logger.info("Scheduler is already running")
        return

    try:
        scheduler = AsyncIOScheduler()

        # Add job to run every 1 minute
        scheduler.add_job(
            process_all_active_jobs,
            trigger=IntervalTrigger(minutes=1),
            id='process_automation_jobs',
            name='Process Active Automation Jobs',
            replace_existing=True
        )

        scheduler.start()
        logger.info("✅ Automation scheduler started successfully!")
        logger.info("📅 Will check for active jobs every 1 minute")

    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")


def stop_scheduler():
    """Stop the automation scheduler."""
    global scheduler

    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
