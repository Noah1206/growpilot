"""Automation job model for Reddit/Twitter automation."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


class AutomationJob(Base):
    """Automation job for social media outreach (Reddit/Twitter)."""

    __tablename__ = "automation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)

    # Platform selection
    platform = Column(String(50), nullable=False)  # 'reddit' or 'twitter'

    # Search and targeting
    search_keywords = Column(Text, nullable=False)
    message_template = Column(Text, nullable=False)

    # Status and limits
    status = Column(String(50), default="active")  # active, paused, stopped, error
    daily_limit = Column(Integer, default=20)

    # Counters
    total_sent_count = Column(Integer, default=0)
    daily_sent_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

    # Scheduling
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_reset_date = Column(DateTime, default=datetime.utcnow)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="automation_jobs")
    campaign = relationship("Campaign")

    def __repr__(self):
        return f"<AutomationJob(id={self.id}, platform='{self.platform}', status='{self.status}')>"
