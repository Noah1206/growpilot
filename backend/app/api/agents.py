"""API routes for AI agent operations."""
from fastapi import APIRouter, HTTPException
from app.schemas import (
    ICPInput,
    ICPOutput,
    QueryBuilderInput,
    QueryOutput,
    CopyGeneratorInput,
    CopyOutput,
    PolicyReviewInput,
    PolicyReviewOutput,
    ConversationAnalysisInput,
    ConversationAnalysisOutput,
    CampaignReportInput,
    CampaignReportOutput,
)
from app.agents import (
    ICPPlannerAgent,
    QueryBuilderAgent,
    RedditCopyAgent,
    FacebookCopyAgent,
    PolicyReviewerAgent,
    ConversationAnalystAgent,
    CampaignReporterAgent,
)

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/icp", response_model=ICPOutput)
async def generate_icp(data: ICPInput):
    """Generate Ideal Customer Profile from product information."""
    try:
        agent = ICPPlannerAgent()
        result = await agent.infer_icp(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ICP generation failed: {str(e)}")


@router.post("/queries", response_model=QueryOutput)
async def build_queries(data: QueryBuilderInput):
    """Build platform-specific search queries."""
    try:
        agent = QueryBuilderAgent()
        result = await agent.build_queries(data.icp, data.channels)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query building failed: {str(e)}")


@router.post("/linkedin", response_model=CopyOutput)
async def generate_linkedin_copy(data: CopyGeneratorInput):
    """Generate LinkedIn DM copy variants."""
    try:
        agent = LinkedInCopyAgent()
        result = await agent.generate_copy(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LinkedIn copy generation failed: {str(e)}")


@router.post("/reddit", response_model=CopyOutput)
async def generate_reddit_copy(data: CopyGeneratorInput):
    """Generate Reddit comment copy variants."""
    try:
        agent = RedditCopyAgent()
        result = await agent.generate_copy(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reddit copy generation failed: {str(e)}")


@router.post("/facebook", response_model=CopyOutput)
async def generate_facebook_copy(data: CopyGeneratorInput):
    """Generate Facebook post copy variants."""
    try:
        agent = FacebookCopyAgent()
        result = await agent.generate_copy(data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Facebook copy generation failed: {str(e)}")


@router.post("/review", response_model=PolicyReviewOutput)
async def review_copy(data: PolicyReviewInput):
    """Review copy for platform policy compliance."""
    try:
        agent = PolicyReviewerAgent()
        result = await agent.review_copy(data.channel, data.copy_variants)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy review failed: {str(e)}")


@router.post("/analyze", response_model=ConversationAnalysisOutput)
async def analyze_conversation(data: ConversationAnalysisInput):
    """Analyze prospect response and suggest follow-up."""
    try:
        agent = ConversationAnalystAgent()
        result = await agent.analyze_conversation(
            data.prospect_reply,
            data.original_message,
            data.channel
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation analysis failed: {str(e)}")


@router.post("/report", response_model=CampaignReportOutput)
async def generate_report(data: CampaignReportInput):
    """Generate campaign performance report and recommendations."""
    try:
        agent = CampaignReporterAgent()
        result = await agent.generate_report(data.campaign_id, data.metrics)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
