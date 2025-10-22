"""Extension API request/response schemas."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProfileData(BaseModel):
    """LinkedIn profile data from extension."""
    name: str
    title: str
    company: str
    profileUrl: str
    extractedAt: str


class FilterProfilesRequest(BaseModel):
    """Request to filter profiles based on ICP."""
    profiles: List[ProfileData]
    campaign_id: int


class ApprovedProfile(BaseModel):
    """Approved profile with generated message."""
    name: str
    title: str
    company: str
    profileUrl: str
    message: str
    matchScore: Optional[float] = None


class FilterProfilesResponse(BaseModel):
    """Response with filtered profiles and messages."""
    approved_profiles: List[ApprovedProfile]
    rejected_count: int
    total_processed: int


class LogMessageRequest(BaseModel):
    """Request to log sent message."""
    job_id: int
    profile_url: str
    profile_name: str
    message_content: str
    status: str = "sent"


class LogMessageResponse(BaseModel):
    """Response after logging message."""
    success: bool
    message_id: Optional[int] = None
    daily_sent: int
    total_sent: int


class UpdateStatsRequest(BaseModel):
    """Request to update job statistics."""
    daily_sent_count: Optional[int] = None
    total_sent_count: Optional[int] = None
