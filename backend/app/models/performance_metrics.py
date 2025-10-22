"""Performance metrics database model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.core.database import Base


class PerformanceMetrics(Base):
    """Performance metrics model for tracking campaign performance."""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    channel = Column(String(50), nullable=False)  # linkedin, reddit, facebook

    # Engagement metrics
    sends = Column(Integer, default=0)
    opens = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    positive_replies = Column(Integer, default=0)
    neutral_replies = Column(Integer, default=0)
    negative_replies = Column(Integer, default=0)

    # Conversion metrics
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    reply_rate = Column(Float, default=0.0)
    positive_rate = Column(Float, default=0.0)

    # Timestamps
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PerformanceMetrics(campaign_id={self.campaign_id}, channel='{self.channel}', date='{self.date}')>"
