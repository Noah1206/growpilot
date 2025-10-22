"""API routes for analytics and reporting."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models import Campaign, LinkClick, CampaignInteraction

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/campaign/{campaign_id}/overview")
async def get_campaign_overview(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a specific campaign."""
    try:
        # Get campaign details
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Get link clicks
        total_clicks = db.query(func.count(LinkClick.id)).filter(
            LinkClick.campaign_id == campaign_id
        ).scalar() or 0

        # Get unique clicks (by IP address)
        unique_clicks = db.query(func.count(func.distinct(LinkClick.ip_address))).filter(
            LinkClick.campaign_id == campaign_id,
            LinkClick.ip_address.isnot(None)
        ).scalar() or 0

        # Get clicks by source
        clicks_by_source = {}
        source_data = db.query(
            LinkClick.source,
            func.count(LinkClick.id)
        ).filter(
            LinkClick.campaign_id == campaign_id
        ).group_by(LinkClick.source).all()

        for source, count in source_data:
            clicks_by_source[source or "direct"] = count

        # Get interactions
        total_sent = db.query(func.count(CampaignInteraction.id)).filter(
            CampaignInteraction.campaign_id == campaign_id,
            CampaignInteraction.interaction_type == "sent"
        ).scalar() or 0

        total_replied = db.query(func.count(CampaignInteraction.id)).filter(
            CampaignInteraction.campaign_id == campaign_id,
            CampaignInteraction.interaction_type == "replied"
        ).scalar() or 0

        total_interested = db.query(func.count(CampaignInteraction.id)).filter(
            CampaignInteraction.campaign_id == campaign_id,
            CampaignInteraction.interaction_type == "interested"
        ).scalar() or 0

        total_converted = db.query(func.count(CampaignInteraction.id)).filter(
            CampaignInteraction.campaign_id == campaign_id,
            CampaignInteraction.interaction_type == "converted"
        ).scalar() or 0

        # Calculate response rate
        response_rate = (total_replied / total_sent * 100) if total_sent > 0 else 0
        interest_rate = (total_interested / total_replied * 100) if total_replied > 0 else 0
        conversion_rate = (total_converted / total_sent * 100) if total_sent > 0 else 0

        # Get interactions by channel
        interactions_by_channel = {}
        channel_data = db.query(
            CampaignInteraction.channel,
            func.count(CampaignInteraction.id)
        ).filter(
            CampaignInteraction.campaign_id == campaign_id
        ).group_by(CampaignInteraction.channel).all()

        for channel, count in channel_data:
            interactions_by_channel[channel] = count

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.product_name,
            "tracking_url": campaign.tracking_url,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
            "clicks": {
                "total": total_clicks,
                "unique": unique_clicks,
                "by_source": clicks_by_source
            },
            "outreach": {
                "sent": total_sent,
                "replied": total_replied,
                "interested": total_interested,
                "converted": total_converted,
                "response_rate": round(response_rate, 2),
                "interest_rate": round(interest_rate, 2),
                "conversion_rate": round(conversion_rate, 2),
                "by_channel": interactions_by_channel
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )


@router.get("/campaign/{campaign_id}/timeline")
async def get_campaign_timeline(
    campaign_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get time-series data for campaign performance."""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get clicks over time
        clicks_data = db.query(
            func.date(LinkClick.clicked_at).label('date'),
            func.count(LinkClick.id).label('count')
        ).filter(
            LinkClick.campaign_id == campaign_id,
            LinkClick.clicked_at >= start_date
        ).group_by(func.date(LinkClick.clicked_at)).all()

        clicks_timeline = {
            str(date): count for date, count in clicks_data
        }

        # Get interactions over time
        interactions_data = db.query(
            func.date(CampaignInteraction.created_at).label('date'),
            func.count(CampaignInteraction.id).label('count')
        ).filter(
            CampaignInteraction.campaign_id == campaign_id,
            CampaignInteraction.created_at >= start_date
        ).group_by(func.date(CampaignInteraction.created_at)).all()

        interactions_timeline = {
            str(date): count for date, count in interactions_data
        }

        return {
            "campaign_id": campaign_id,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            },
            "clicks_timeline": clicks_timeline,
            "interactions_timeline": interactions_timeline
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve timeline data: {str(e)}"
        )


@router.get("/campaigns/summary")
async def get_all_campaigns_summary(
    db: Session = Depends(get_db)
):
    """Get summary analytics for all campaigns."""
    try:
        campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()

        summary_data = []
        for campaign in campaigns:
            # Get click count
            click_count = db.query(func.count(LinkClick.id)).filter(
                LinkClick.campaign_id == campaign.id
            ).scalar() or 0

            # Get interaction counts
            sent_count = db.query(func.count(CampaignInteraction.id)).filter(
                CampaignInteraction.campaign_id == campaign.id,
                CampaignInteraction.interaction_type == "sent"
            ).scalar() or 0

            replied_count = db.query(func.count(CampaignInteraction.id)).filter(
                CampaignInteraction.campaign_id == campaign.id,
                CampaignInteraction.interaction_type == "replied"
            ).scalar() or 0

            response_rate = (replied_count / sent_count * 100) if sent_count > 0 else 0

            summary_data.append({
                "id": campaign.id,
                "product_name": campaign.product_name,
                "tracking_url": campaign.tracking_url,
                "channels": campaign.channels,
                "status": campaign.status,
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                "metrics": {
                    "clicks": click_count,
                    "messages_sent": sent_count,
                    "replies": replied_count,
                    "response_rate": round(response_rate, 2)
                }
            })

        return {
            "total_campaigns": len(campaigns),
            "campaigns": summary_data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve campaigns summary: {str(e)}"
        )


@router.post("/campaign/{campaign_id}/interaction")
async def record_interaction(
    campaign_id: int,
    channel: str,
    interaction_type: str,
    prospect_name: str = None,
    prospect_profile: str = None,
    message_sent: str = None,
    response_text: str = None,
    notes: str = None,
    db: Session = Depends(get_db)
):
    """Record a campaign interaction (sent message, reply, etc.)."""
    try:
        # Validate interaction type
        valid_types = ["sent", "replied", "interested", "not_interested", "converted"]
        if interaction_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid interaction type. Must be one of: {', '.join(valid_types)}"
            )

        # Create interaction record
        interaction = CampaignInteraction(
            campaign_id=campaign_id,
            channel=channel,
            interaction_type=interaction_type,
            prospect_name=prospect_name,
            prospect_profile=prospect_profile,
            message_sent=message_sent,
            response_text=response_text,
            notes=notes,
            sent_at=datetime.utcnow() if interaction_type == "sent" else None,
            responded_at=datetime.utcnow() if interaction_type in ["replied", "interested", "not_interested"] else None,
            created_at=datetime.utcnow()
        )

        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return {
            "success": True,
            "interaction_id": interaction.id,
            "message": "Interaction recorded successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record interaction: {str(e)}"
        )
