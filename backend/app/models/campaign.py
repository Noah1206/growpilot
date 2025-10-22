"""Campaign database model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Campaign(Base):
    """Campaign model for storing generated outreach campaigns."""

    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for backward compatibility
    product_name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    target_audience_hint = Column(String(500))
    locales = Column(JSON)  # List of locale codes
    language_pref = Column(String(10), default="en")
    channels = Column(JSON)  # List of channels: linkedin, reddit, facebook
    tone = Column(String(50), default="friendly")
    cta = Column(String(255))

    # Link tracking
    tracking_url = Column(String(500))  # User's website/landing page to track

    # Generated outputs
    icp = Column(JSON)  # ICP Planner output
    queries = Column(JSON)  # Query Builder output
    linkedin_copy = Column(JSON)  # LinkedIn copy variants
    reddit_copy = Column(JSON)  # Reddit copy variants
    facebook_copy = Column(JSON)  # Facebook copy variants
    policy_review = Column(JSON)  # Policy review results

    # Metadata
    status = Column(String(50), default="draft")  # draft, approved, active, paused, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Campaign(id={self.id}, product_name='{self.product_name}', status='{self.status}')>"
