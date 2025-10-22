"""Automation log model for tracking automation activity."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class AutomationLog(Base):
    """Model for automation activity logs."""

    __tablename__ = "automation_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("automation_jobs.id"), nullable=False, index=True)
    log_type = Column(String(50), nullable=False)  # 'search', 'send_success', 'send_fail', 'send_progress'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Target user info
    username = Column(String(255), nullable=True)
    platform_info = Column(JSON, nullable=True)  # karma, subreddit, etc

    # Message info
    message_preview = Column(Text, nullable=True)

    # Status info
    status = Column(String(50), nullable=True)  # 'success', 'failed', 'pending'
    error_message = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)  # Additional data (users_found, subreddit, etc)

    # Relationships
    job = relationship("AutomationJob", back_populates="logs")

    def __repr__(self):
        return f"<AutomationLog(id={self.id}, job_id={self.job_id}, type={self.log_type}, username={self.username})>"
