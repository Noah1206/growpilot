"""Pydantic schemas for campaign data validation."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Input Schemas
class CampaignInput(BaseModel):
    """Input schema for creating a new campaign."""
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: str = Field(..., min_length=10, description="Product description")
    tracking_url: str = Field(..., min_length=1, max_length=500, description="Website URL to track clicks")
    target_audience_hint: Optional[str] = Field(None, max_length=500, description="Target audience hint")
    locales: List[str] = Field(default=["US"], description="Target locales")
    language_pref: str = Field(default="en", description="Preferred language")
    channels: List[str] = Field(default=["reddit", "twitter", "facebook"], description="Target channels")
    tone: str = Field(default="friendly", description="Communication tone")
    cta: Optional[str] = Field(None, max_length=255, description="Call to action")


class ICPInput(BaseModel):
    """Input schema for ICP generation."""
    product_name: str
    description: str
    target_audience_hint: Optional[str] = None
    locales: List[str] = ["US"]
    language_pref: str = "en"


class QueryBuilderInput(BaseModel):
    """Input schema for query generation."""
    icp: Dict[str, Any]
    channels: List[str]


class CopyGeneratorInput(BaseModel):
    """Input schema for copy generation."""
    product_name: str
    description: str
    icp: Dict[str, Any]
    tone: str = "friendly"
    cta: Optional[str] = None
    channel: str  # reddit, twitter, or facebook


class PolicyReviewInput(BaseModel):
    """Input schema for policy review."""
    channel: str
    copy_variants: List[Dict[str, str]]


class ConversationAnalysisInput(BaseModel):
    """Input schema for conversation analysis."""
    prospect_reply: str
    original_message: str
    channel: str


class CampaignReportInput(BaseModel):
    """Input schema for campaign report generation."""
    campaign_id: int
    metrics: Dict[str, Any]


# Output Schemas
class ICPOutput(BaseModel):
    """Output schema for ICP data."""
    icp: Dict[str, Any]
    keywords: Dict[str, List[str]]


class QueryOutput(BaseModel):
    """Output schema for search queries."""
    queries: Dict[str, List[str]]


class CopyVariant(BaseModel):
    """Schema for a single copy variant."""
    variant: str
    copy: str
    tone: str


class CopyOutput(BaseModel):
    """Output schema for copy generation."""
    variants: List[CopyVariant]


class PolicyReviewOutput(BaseModel):
    """Output schema for policy review."""
    status: str  # pass, fail, needs_revision
    reasons: List[str]
    revised: Optional[Dict[str, Any]] = None


class ConversationAnalysisOutput(BaseModel):
    """Output schema for conversation analysis."""
    classification: str  # positive, neutral, negative, question
    sentiment_score: float
    suggested_followup: str
    reasoning: str


class CampaignReportOutput(BaseModel):
    """Output schema for campaign report."""
    summary: Dict[str, Any]
    recommendations: List[str]
    insights: List[str]


# Database Schemas
class CampaignResponse(BaseModel):
    """Response schema for campaign data."""
    id: int
    product_name: str
    description: str
    tracking_url: Optional[str]
    target_audience_hint: Optional[str]
    locales: List[str]
    language_pref: str
    channels: List[str]
    tone: str
    cta: Optional[str]
    icp: Optional[Dict[str, Any]]
    queries: Optional[Dict[str, Any]]
    reddit_copy: Optional[Dict[str, Any]]
    facebook_copy: Optional[Dict[str, Any]]
    policy_review: Optional[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CampaignUpdate(BaseModel):
    """Schema for updating campaign data."""
    product_name: Optional[str] = None
    description: Optional[str] = None
    tracking_url: Optional[str] = None
    target_audience_hint: Optional[str] = None
    locales: Optional[List[str]] = None
    language_pref: Optional[str] = None
    channels: Optional[List[str]] = None
    tone: Optional[str] = None
    cta: Optional[str] = None
    status: Optional[str] = None
