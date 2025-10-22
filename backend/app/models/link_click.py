"""Link Click Tracking model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class LinkClick(Base):
    """Track clicks on campaign tracking URLs."""

    __tablename__ = "link_clicks"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)

    # Click metadata
    source = Column(String(50))  # linkedin, reddit, facebook, direct
    referrer = Column(String(500))
    user_agent = Column(String(500))
    ip_address = Column(String(50))

    # UTM parameters (if present)
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    utm_content = Column(String(100))

    clicked_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<LinkClick(id={self.id}, campaign_id={self.campaign_id}, source='{self.source}')>"
