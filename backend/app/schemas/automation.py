"""Automation settings schemas."""
from pydantic import BaseModel
from typing import Optional


class AutomationSettingsBase(BaseModel):
    """Base automation settings schema."""
    auto_followup_enabled: bool = True
    followup_delay_days: int = 3
    max_followup_count: int = 2
    daily_limit: int = 20
    browser_notifications: bool = True
    email_notifications: bool = False


class AutomationSettingsCreate(AutomationSettingsBase):
    """Schema for creating automation settings."""
    pass


class AutomationSettingsUpdate(BaseModel):
    """Schema for updating automation settings."""
    auto_followup_enabled: Optional[bool] = None
    followup_delay_days: Optional[int] = None
    max_followup_count: Optional[int] = None
    daily_limit: Optional[int] = None
    browser_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None


class AutomationSettingsResponse(AutomationSettingsBase):
    """Schema for automation settings response."""
    id: int
    user_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
