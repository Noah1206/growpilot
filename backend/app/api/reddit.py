"""Reddit API endpoints for automation."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.services.reddit_automation import reddit_automation
from app.services.gemini_ai import generate_personalized_message
from app.models.campaign import Campaign

router = APIRouter(prefix="/api/reddit", tags=["reddit"])


# Request/Response Models
class RedditSearchRequest(BaseModel):
    """Request model for Reddit search."""
    subreddit: str
    keywords: str
    limit: Optional[int] = 100
    time_filter: Optional[str] = "month"


class RedditProfile(BaseModel):
    """Reddit user profile."""
    username: str
    link_karma: int
    comment_karma: int
    profile_url: str
    recent_activity: Optional[str] = None


class RedditMessageRequest(BaseModel):
    """Request model for sending Reddit DM."""
    username: str
    subject: str
    message: str


class RedditAutomationRequest(BaseModel):
    """Request model for starting Reddit automation."""
    campaign_id: int
    subreddit: str
    keywords: str
    daily_limit: Optional[int] = 30


# Endpoints
@router.get("/test")
async def test_reddit_connection():
    """Test Reddit API connection."""
    is_connected = await reddit_automation.test_connection()

    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Reddit API connection failed. Check credentials in .env"
        )

    return {
        "status": "connected",
        "username": reddit_automation.username,
        "message": "Reddit API is working"
    }


@router.post("/search/posts")
async def search_reddit_posts(request: RedditSearchRequest):
    """
    Search Reddit posts in a subreddit.

    Args:
        request: Search parameters (subreddit, keywords, limit, time_filter)

    Returns:
        List of posts with user data
    """
    posts = await reddit_automation.search_subreddit(
        subreddit_name=request.subreddit,
        keywords=request.keywords,
        limit=request.limit,
        time_filter=request.time_filter
    )

    unique_users = await reddit_automation.extract_unique_users(posts)

    return {
        "total_posts": len(posts),
        "unique_users": len(unique_users),
        "subreddit": request.subreddit,
        "posts": posts[:50],  # Return first 50 for preview
        "users": unique_users[:30]  # Return first 30 usernames
    }


@router.post("/search/comments")
async def search_reddit_comments(request: RedditSearchRequest):
    """
    Search Reddit comments in a subreddit.

    Args:
        request: Search parameters (subreddit, keywords, limit)

    Returns:
        List of comments with user data
    """
    comments = await reddit_automation.search_comments_by_keywords(
        subreddit_name=request.subreddit,
        keywords=request.keywords,
        limit=request.limit
    )

    unique_users = await reddit_automation.extract_unique_users(comments)

    return {
        "total_comments": len(comments),
        "unique_users": len(unique_users),
        "subreddit": request.subreddit,
        "comments": comments[:50],
        "users": unique_users[:30]
    }


@router.get("/user/{username}")
async def get_reddit_user(username: str):
    """
    Get Reddit user profile.

    Args:
        username: Reddit username

    Returns:
        User profile data
    """
    profile = await reddit_automation.get_user_profile(username)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User u/{username} not found"
        )

    return profile


@router.post("/send-dm")
async def send_reddit_dm(request: RedditMessageRequest):
    """
    Send a direct message to a Reddit user.

    Args:
        request: Message details (username, subject, message)

    Returns:
        Success status
    """
    success = await reddit_automation.send_dm(
        username=request.username,
        subject=request.subject,
        message=request.message
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send DM to u/{request.username}"
        )

    return {
        "success": True,
        "username": request.username,
        "message": "DM sent successfully"
    }


@router.post("/automation/start")
async def start_reddit_automation(
    request: RedditAutomationRequest,
    db: Session = Depends(get_db)
):
    """
    Start Reddit automation job.

    Workflow:
    1. Search subreddit for posts/comments matching keywords
    2. Extract unique users
    3. Use Gemini AI to filter for ICP match
    4. Send personalized DMs to matched users
    5. Track sent messages

    Args:
        request: Automation parameters
        db: Database session

    Returns:
        Automation job details
    """
    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == request.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Create automation job
    job = AutomationJob(
        user_id=None,  # TODO: Add authentication
        campaign_id=request.campaign_id,
        platform="reddit",
        search_keywords=request.keywords,
        automation_mode="api",
        status="active",
        daily_limit=request.daily_limit,
        total_sent_count=0,
        daily_sent_count=0,
        next_run_at=datetime.utcnow()
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Start automation (asynchronously)
    # Search posts
    posts = await reddit_automation.search_subreddit(
        subreddit_name=request.subreddit,
        keywords=request.keywords,
        limit=100
    )

    unique_users = await reddit_automation.extract_unique_users(posts)

    return {
        "job_id": job.id,
        "campaign_id": campaign.id,
        "platform": "reddit",
        "subreddit": request.subreddit,
        "keywords": request.keywords,
        "users_found": len(unique_users),
        "daily_limit": request.daily_limit,
        "status": "active",
        "message": "Reddit automation started successfully"
    }


@router.post("/automation/{job_id}/send-batch")
async def send_reddit_batch(
    job_id: int,
    usernames: List[str],
    db: Session = Depends(get_db)
):
    """
    Send DMs to a batch of Reddit users using Gemini AI for personalization.

    Args:
        job_id: Automation job ID
        usernames: List of Reddit usernames to message
        db: Database session

    Returns:
        Batch sending results
    """
    # Get job and campaign
    job = db.query(AutomationJob).filter(AutomationJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    campaign = db.query(Campaign).filter(Campaign.id == job.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )

    # Check daily limit
    if job.daily_sent_count >= job.daily_limit:
        return {
            "success": False,
            "message": "Daily limit reached",
            "sent": 0,
            "failed": 0
        }

    # Send messages
    sent_count = 0
    failed_count = 0
    results = []

    for username in usernames[:job.daily_limit - job.daily_sent_count]:
        try:
            # Get user profile
            profile = await reddit_automation.get_user_profile(username)
            if not profile:
                failed_count += 1
                results.append({"username": username, "status": "profile_not_found"})
                continue

            # Generate personalized message using Gemini AI
            personalized_message = generate_personalized_message(
                product_name=campaign.product_name,
                description=campaign.description,
                target_audience=campaign.target_audience,
                profile_data={
                    "name": username,
                    "platform": "reddit",
                    "bio": f"Karma: {profile['link_karma']} / {profile['comment_karma']}",
                    "recent_activity": str(profile.get('recent_comments', []))[:200]
                }
            )

            # Send DM
            success = await reddit_automation.send_dm(
                username=username,
                subject=f"About {campaign.product_name}",
                message=personalized_message
            )

            if success:
                sent_count += 1
                job.daily_sent_count += 1
                job.total_sent_count += 1
                results.append({"username": username, "status": "sent"})
            else:
                failed_count += 1
                results.append({"username": username, "status": "failed"})

        except Exception as e:
            failed_count += 1
            results.append({"username": username, "status": "error", "error": str(e)})

    # Update job
    job.updated_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "job_id": job.id,
        "sent": sent_count,
        "failed": failed_count,
        "daily_total": job.daily_sent_count,
        "daily_limit": job.daily_limit,
        "results": results
    }
