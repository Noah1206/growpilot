"""Automation settings model."""
from datetime import datetime
from sqlalchemy import Column, Integer, Boolean, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class AutomationSettings(Base):
    """User automation preferences and configuration."""

    __tablename__ = "automation_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    # Follow-up settings
    auto_followup_enabled = Column(Boolean, default=True)
    followup_delay_days = Column(Integer, default=3)  # Days to wait before follow-up
    max_followup_count = Column(Integer, default=2)   # Maximum number of follow-ups per prospect

    # Daily limits
    daily_limit = Column(Integer, default=20)  # Maximum messages per day

    # Notification settings
    browser_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    # user = relationship("User", back_populates="automation_settings")

    def __repr__(self):
        return f"<AutomationSettings(user_id={self.user_id}, daily_limit={self.daily_limit})>"
