"""Campaign Interaction tracking model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class CampaignInteraction(Base):
    """Track interactions/responses for campaigns."""

    __tablename__ = "campaign_interactions"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)

    # Interaction details
    channel = Column(String(50), nullable=False)  # linkedin, reddit, facebook
    interaction_type = Column(String(50), nullable=False, index=True)  # sent, replied, interested, not_interested, converted

    # Optional metadata
    prospect_name = Column(String(255))
    prospect_profile = Column(String(500))  # URL to their profile
    message_sent = Column(Text)  # The actual message that was sent
    response_text = Column(Text)  # Their response (if any)
    notes = Column(Text)  # User's notes about this interaction

    # Timestamps
    sent_at = Column(DateTime)
    responded_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<CampaignInteraction(id={self.id}, campaign_id={self.campaign_id}, type='{self.interaction_type}')>"
