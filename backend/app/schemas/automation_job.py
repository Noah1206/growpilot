"""Automation Job schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AutomationJobCreate(BaseModel):
    """Schema for creating an automation job."""
    campaign_id: Optional[int] = None
    search_keywords: str = Field(..., min_length=1, max_length=500)
    message_template: str = Field(..., min_length=1)


class AutomationJobUpdate(BaseModel):
    """Schema for updating an automation job."""
    status: Optional[str] = None  # active, paused, completed
    search_keywords: Optional[str] = None
    message_template: Optional[str] = None


class AutomationJobResponse(BaseModel):
    """Schema for automation job response."""
    id: int
    user_id: int
    campaign_id: Optional[int]
    search_keywords: str
    message_template: str
    status: str
    is_premium: bool
    total_sent_count: int
    daily_sent_count: int
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    last_reset_date: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AutomationJobStats(BaseModel):
    """Schema for automation job statistics."""
    job_id: int
    status: str
    total_sent: int
    daily_sent: int
    daily_limit: int
    remaining_quota: int
    last_run: Optional[datetime]
    next_run: Optional[datetime]
