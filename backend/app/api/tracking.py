"""API routes for link tracking and analytics."""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models import LinkClick

router = APIRouter(prefix="/api/track", tags=["tracking"])


class LinkClickInput(BaseModel):
    """Input schema for tracking a link click."""
    campaign_id: int = Field(..., description="Campaign ID")
    source: Optional[str] = Field(None, description="Traffic source (linkedin, reddit, facebook, direct)")
    utm_source: Optional[str] = Field(None, description="UTM source parameter")
    utm_medium: Optional[str] = Field(None, description="UTM medium parameter")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign parameter")
    utm_content: Optional[str] = Field(None, description="UTM content parameter")


@router.post("/click")
async def track_click(
    data: LinkClickInput,
    request: Request,
    db: Session = Depends(get_db)
):
    """Track a link click from a campaign."""
    try:
        # Extract request metadata
        user_agent = request.headers.get("user-agent", "")
        referrer = request.headers.get("referer", "")

        # Get client IP (considering proxy headers)
        client_ip = request.client.host if request.client else None
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Create link click record
        link_click = LinkClick(
            campaign_id=data.campaign_id,
            source=data.source,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=client_ip,
            utm_source=data.utm_source,
            utm_medium=data.utm_medium,
            utm_campaign=data.utm_campaign,
            utm_content=data.utm_content,
            clicked_at=datetime.utcnow()
        )

        db.add(link_click)
        db.commit()
        db.refresh(link_click)

        return {
            "success": True,
            "click_id": link_click.id,
            "message": "Click tracked successfully"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to track click: {str(e)}"
        )


@router.get("/campaign/{campaign_id}/clicks")
async def get_campaign_clicks(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get all clicks for a specific campaign."""
    try:
        clicks = db.query(LinkClick).filter(
            LinkClick.campaign_id == campaign_id
        ).order_by(LinkClick.clicked_at.desc()).all()

        # Group by source
        click_data = {
            "total_clicks": len(clicks),
            "by_source": {},
            "recent_clicks": []
        }

        # Count by source
        for click in clicks:
            source = click.source or "direct"
            click_data["by_source"][source] = click_data["by_source"].get(source, 0) + 1

        # Add recent clicks (last 10)
        for click in clicks[:10]:
            click_data["recent_clicks"].append({
                "id": click.id,
                "source": click.source,
                "clicked_at": click.clicked_at.isoformat() if click.clicked_at else None,
                "utm_source": click.utm_source,
                "utm_campaign": click.utm_campaign
            })

        return click_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve clicks: {str(e)}"
        )
