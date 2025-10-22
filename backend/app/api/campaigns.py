"""API routes for campaign management."""
from typing import List
import re
import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Campaign, CampaignInteraction
from app.schemas import CampaignInput, CampaignResponse, CampaignUpdate
from app.services.gemini_ai import GeminiAI
from app.agents import (
    ICPPlannerAgent,
    QueryBuilderAgent,
    RedditCopyAgent,
    FacebookCopyAgent,
    PolicyReviewerAgent,
)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


def sanitize_description(description: str) -> str:
    """Sanitize user input to be more Gemini-friendly.

    - Removes URLs (replaces with [website])
    - Ensures minimum length
    - Cleans up formatting issues
    """
    if not description:
        return description

    # Remove URLs and replace with placeholder
    description = re.sub(r'https?://\S+', '[website]', description)

    # Remove excessive newlines
    description = re.sub(r'\n{3,}', '\n\n', description)

    # Ensure minimum length for better Gemini processing
    if len(description.strip()) < 50:
        description += ". This product helps businesses improve efficiency and solve real problems."

    return description.strip()


@router.post("/generate", response_model=CampaignResponse)
async def generate_campaign(data: CampaignInput, db: Session = Depends(get_db)):
    import asyncio
    print(f"🚀 Creating campaign: {data.product_name}")

    try:
        # Sanitize description
        sanitized_description = sanitize_description(data.description)

        campaign_data = data.model_dump()
        campaign_data['description'] = sanitized_description

        copy_data = {
            "product_name": data.product_name,
            "description": sanitized_description,
            "tone": data.tone,
            "cta": data.cta,
        }

        # ===== SIMPLIFIED: Only generate ICP for AI filtering =====

        # Generate ICP (필수 - AI 필터링에 사용)
        print("  Generating ICP profile...")
        icp_agent = ICPPlannerAgent()
        icp_result = await icp_agent.infer_icp(campaign_data)

        print("✅ Campaign created successfully!")

        # Save to database with minimal data
        campaign = Campaign(
            product_name=data.product_name,
            description=data.description,
            tracking_url=data.tracking_url,
            target_audience_hint=data.target_audience_hint,
            locales=data.locales,
            language_pref=data.language_pref,
            channels=data.channels,
            tone=data.tone,
            cta=data.cta,
            icp=icp_result,
            queries={},  # Empty - user provides keywords manually
            reddit_copy=None,  # Skip
            facebook_copy=None,  # Skip
            policy_review={},  # Skip
            status="draft",
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        return campaign

    except ValueError as e:
        db.rollback()
        error_msg = str(e)
        print(f"ValueError: {error_msg}")
        traceback.print_exc()

        # Provide helpful error message for safety filter blocks
        if "safety filters" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Your product description triggered content filters. Please try:\n"
                       "1. Make your description more detailed and professional\n"
                       "2. Avoid promotional language and urgency phrases\n"
                       "3. Focus on business value and problem-solving"
            )
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {error_msg}")

    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {str(e)}")


@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all campaigns."""
    campaigns = db.query(Campaign).offset(skip).limit(limit).all()
    return campaigns


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get campaign by ID."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    data: CampaignUpdate,
    db: Session = Depends(get_db)
):
    """Update campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(campaign, key, value)

    db.commit()
    db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Delete campaign."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(campaign)
    db.commit()
    return {"message": "Campaign deleted successfully"}


@router.post("/{campaign_id}/generate-message")
async def generate_message_template(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered message template for a campaign.

    based on the campaign's product, description, tone, and CTA.
    """
    try:
        # Get campaign from database
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Prepare campaign data for AI
        campaign_data = {
            'product_name': campaign.product_name,
            'description': campaign.description,
            'tone': campaign.tone or 'professional',
            'cta': campaign.cta or 'interested in learning more?'
        }

        # Call Gemini AI service
        gemini_ai = GeminiAI()
        template = await gemini_ai.generate_message_template(campaign_data)

        return {
            "success": True,
            "message_template": template,
            "campaign_id": campaign_id,
            "campaign_name": campaign.product_name
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating message template: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate message template: {str(e)}"
        )


@router.get("/interactions/recent")
async def get_recent_interactions(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent campaign interactions."""
    interactions = (
        db.query(CampaignInteraction)
        .order_by(CampaignInteraction.sent_at.desc())
        .limit(limit)
        .all()
    )

    # Convert to dict for JSON serialization
    return [
        {
            "id": interaction.id,
            "campaign_id": interaction.campaign_id,
            "channel": interaction.channel,
            "interaction_type": interaction.interaction_type,
            "sent_at": interaction.sent_at.isoformat() if interaction.sent_at else None,
        }
        for interaction in interactions
    ]
