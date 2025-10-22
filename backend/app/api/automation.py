"""Automation settings and jobs API endpoints."""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.automation_settings import AutomationSettings
from app.schemas.automation import (
    AutomationSettingsCreate,
    AutomationSettingsUpdate,
    AutomationSettingsResponse
)
# TODO: Re-enable when AutomationJob model is restored
# from app.schemas.automation_job import (
#     AutomationJobCreate,
#     AutomationJobUpdate,
#     AutomationJobResponse,
#     AutomationJobStats
# )
# from app.services.automation_scheduler import get_daily_limit

router = APIRouter(prefix="/api/automation", tags=["automation"])


@router.get("/settings", response_model=AutomationSettingsResponse)
async def get_automation_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's automation settings."""
    settings = db.query(AutomationSettings).filter(
        AutomationSettings.user_id == current_user.id
    ).first()

    # If no settings exist, create default settings
    if not settings:
        settings = AutomationSettings(
            user_id=current_user.id,
            auto_followup_enabled=True,
            followup_delay_days=3,
            max_followup_count=2,
            daily_limit=20,
            browser_notifications=True,
            email_notifications=False
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.put("/settings", response_model=AutomationSettingsResponse)
async def update_automation_settings(
    settings_update: AutomationSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user's automation settings."""
    settings = db.query(AutomationSettings).filter(
        AutomationSettings.user_id == current_user.id
    ).first()

    # If no settings exist, create new
    if not settings:
        settings = AutomationSettings(user_id=current_user.id)
        db.add(settings)

    # Update fields
    update_data = settings_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)

    settings.updated_at = datetime.utcnow().isoformat()

    db.commit()
    db.refresh(settings)

    return settings


@router.post("/settings", response_model=AutomationSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_automation_settings(
    settings_data: AutomationSettingsCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create automation settings for user."""
    # Check if settings already exist
    existing_settings = db.query(AutomationSettings).filter(
        AutomationSettings.user_id == current_user.id
    ).first()

    if existing_settings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Automation settings already exist. Use PUT to update."
        )

    # Create new settings
    new_settings = AutomationSettings(
        user_id=current_user.id,
        **settings_data.model_dump()
    )

    db.add(new_settings)
    db.commit()
    db.refresh(new_settings)

    return new_settings


# ============================================================================
# AUTOMATION JOBS ENDPOINTS - DISABLED (AutomationJob model removed)
# ============================================================================
# TODO: Re-enable when AutomationJob model is restored

"""
@router.post("/jobs/start", response_model=AutomationJobResponse, status_code=status.HTTP_201_CREATED)
async def start_automation_job(
    job_data: AutomationJobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a new automation job."""
    # Create new automation job
    new_job = AutomationJob(
        user_id=current_user.id,
        campaign_id=job_data.campaign_id,
        search_keywords=job_data.search_keywords,
        message_template=job_data.message_template,
        status="active",
        is_premium=False,  # TODO: Check user's actual plan
        total_sent_count=0,
        daily_sent_count=0,
        last_reset_date=datetime.utcnow(),
        next_run_at=datetime.utcnow(),  # Start immediately
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


@router.get("/jobs", response_model=List[AutomationJobResponse])
async def get_automation_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all automation jobs for the current user."""
    jobs = db.query(AutomationJob).filter(
        AutomationJob.user_id == current_user.id
    ).order_by(AutomationJob.created_at.desc()).all()

    return jobs


@router.get("/jobs/{job_id}", response_model=AutomationJobResponse)
async def get_automation_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific automation job."""
    job = db.query(AutomationJob).filter(
        AutomationJob.id == job_id,
        AutomationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation job not found"
        )

    return job


@router.get("/jobs/{job_id}/stats", response_model=AutomationJobStats)
async def get_automation_job_stats(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific automation job."""
    job = db.query(AutomationJob).filter(
        AutomationJob.id == job_id,
        AutomationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation job not found"
        )

    # Get daily limit
    daily_limit = get_daily_limit(current_user.id, db)
    remaining_quota = max(0, daily_limit - job.daily_sent_count)

    return AutomationJobStats(
        job_id=job.id,
        status=job.status,
        total_sent=job.total_sent_count,
        daily_sent=job.daily_sent_count,
        daily_limit=daily_limit,
        remaining_quota=remaining_quota,
        last_run=job.last_run_at,
        next_run=job.next_run_at
    )


@router.put("/jobs/{job_id}/pause", response_model=AutomationJobResponse)
async def pause_automation_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Pause an automation job."""
    job = db.query(AutomationJob).filter(
        AutomationJob.id == job_id,
        AutomationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation job not found"
        )

    job.status = "paused"
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)

    return job


@router.put("/jobs/{job_id}/resume", response_model=AutomationJobResponse)
async def resume_automation_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Resume a paused automation job."""
    job = db.query(AutomationJob).filter(
        AutomationJob.id == job_id,
        AutomationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation job not found"
        )

    job.status = "active"
    job.next_run_at = datetime.utcnow()  # Resume immediately
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)

    return job


@router.put("/jobs/{job_id}", response_model=AutomationJobResponse)
async def update_automation_job(
    job_id: int,
    job_update: AutomationJobUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an automation job."""
    job = db.query(AutomationJob).filter(
        AutomationJob.id == job_id,
        AutomationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation job not found"
        )

    # Update fields
    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)

    return job


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_automation_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an automation job."""
    job = db.query(AutomationJob).filter(
        AutomationJob.id == job_id,
        AutomationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Automation job not found"
        )

    db.delete(job)
    db.commit()

    return None
"""
