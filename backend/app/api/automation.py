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
#
# All job-related endpoints have been temporarily disabled because the
# AutomationJob model was removed during LinkedIn cleanup.
# To re-enable: restore automation_job.py model and uncomment imports above.
