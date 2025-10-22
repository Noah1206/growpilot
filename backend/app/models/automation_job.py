"""Automation Job model for background LinkedIn outreach."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class AutomationJob(Base):
    """Background automation job for LinkedIn outreach."""

    __tablename__ = "automation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)

    # Search configuration
    search_keywords = Column(String(500), nullable=False)  # User-provided search keywords
    message_template = Column(Text, nullable=False)  # Message template to send

    # Automation status
    status = Column(String(50), default="active", index=True)  # active, paused, completed, error
    automation_mode = Column(String(50), default="extension", index=True)  # extension, backend
    is_premium = Column(Boolean, default=False)  # Premium user flag for higher limits

    # Progress tracking
    total_sent_count = Column(Integer, default=0)  # Total messages sent by this job
    daily_sent_count = Column(Integer, default=0)  # Messages sent today
    last_run_at = Column(DateTime)  # Last time the job ran
    next_run_at = Column(DateTime)  # Next scheduled run time
    last_reset_date = Column(DateTime)  # Last time daily_sent_count was reset

    # Error tracking
    error_message = Column(Text)  # Last error message if status is 'error'
    retry_count = Column(Integer, default=0)  # Number of retry attempts

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AutomationJob(id={self.id}, user_id={self.user_id}, status='{self.status}', sent={self.total_sent_count})>"