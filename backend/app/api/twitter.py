"""Twitter/X.com API endpoints for automation."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.services.twitter_automation import twitter_automation
from app.services.gemini_ai import generate_personalized_message
from app.models.automation_job import AutomationJob
from app.models.campaign import Campaign

router = APIRouter(prefix="/api/twitter", tags=["twitter"])


# Request/Response Models
class TwitterSearchRequest(BaseModel):
    """Request model for Twitter search."""
    keywords: str
    max_results: Optional[int] = 100
    language: Optional[str] = "en"


class TwitterProfile(BaseModel):
    """Twitter user profile."""
    username: str
    name: str
    bio: Optional[str] = None
    followers_count: int
    profile_url: str


class TwitterMessageRequest(BaseModel):
    """Request model for sending Twitter DM."""
    username: str
    message: str


class TwitterAutomationRequest(BaseModel):
    """Request model for starting Twitter automation."""
    campaign_id: int
    keywords: str
    daily_limit: Optional[int] = 50


# Endpoints
@router.get("/test")
async def test_twitter_connection():
    """Test Twitter API connection."""
    is_connected = await twitter_automation.test_connection()

    if not is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Twitter API connection failed. Check credentials in .env"
        )

    return {
        "status": "connected",
        "username": twitter_automation.username,
        "message": "Twitter API is working"
    }


@router.post("/search/tweets")
async def search_tweets(request: TwitterSearchRequest):
    """
    Search recent tweets matching keywords.

    Args:
        request: Search parameters (keywords, max_results, language)

    Returns:
        List of tweets with user data
    """
    tweets = await twitter_automation.search_tweets(
        keywords=request.keywords,
        max_results=request.max_results,
        language=request.language
    )

    unique_users = await twitter_automation.extract_unique_users(tweets)

    return {
        "total_tweets": len(tweets),
        "unique_users": len(unique_users),
        "keywords": request.keywords,
        "tweets": tweets[:50],  # Return first 50 for preview
        "users": unique_users[:30]  # Return first 30 usernames
    }


@router.get("/user/{username}")
async def get_twitter_user(username: str):
    """
    Get Twitter user profile.

    Args:
        username: Twitter username (without @)

    Returns:
        User profile data
    """
    profile = await twitter_automation.get_user_profile(username)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User @{username} not found"
        )

    return profile


@router.post("/send-dm")
async def send_twitter_dm(request: TwitterMessageRequest):
    """
    Send a direct message to a Twitter user.

    Note: You can only send DMs to users who follow you or accept DMs from anyone.

    Args:
        request: Message details (username, message)

    Returns:
        Success status
    """
    success = await twitter_automation.send_dm(
        username=request.username,
        message=request.message
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send DM to @{request.username}. User may not accept DMs."
        )

    return {
        "success": True,
        "username": request.username,
        "message": "DM sent successfully"
    }


@router.post("/automation/start")
async def start_twitter_automation(
    request: TwitterAutomationRequest,
    db: Session = Depends(get_db)
):
    """
    Start Twitter automation job.

    Workflow:
    1. Search tweets matching keywords
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
        platform="twitter",
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
    # Search tweets
    tweets = await twitter_automation.search_tweets(
        keywords=request.keywords,
        max_results=100
    )

    unique_users = await twitter_automation.extract_unique_users(tweets)

    return {
        "job_id": job.id,
        "campaign_id": campaign.id,
        "platform": "twitter",
        "keywords": request.keywords,
        "users_found": len(unique_users),
        "daily_limit": request.daily_limit,
        "status": "active",
        "message": "Twitter automation started successfully"
    }


@router.post("/automation/{job_id}/send-batch")
async def send_twitter_batch(
    job_id: int,
    usernames: List[str],
    db: Session = Depends(get_db)
):
    """
    Send DMs to a batch of Twitter users using Gemini AI for personalization.

    Args:
        job_id: Automation job ID
        usernames: List of Twitter usernames to message
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
            profile = await twitter_automation.get_user_profile(username)
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
                    "name": profile['name'],
                    "platform": "twitter",
                    "bio": profile.get('bio', ''),
                    "followers": profile['followers_count'],
                    "recent_activity": str(profile.get('recent_tweets', []))[:200]
                }
            )

            # Send DM
            success = await twitter_automation.send_dm(
                username=username,
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
