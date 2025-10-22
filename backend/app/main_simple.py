"""Simple FastAPI application without database."""
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Create FastAPI app
app = FastAPI(
    title="GrowthPilot API",
    description="AI-Powered SaaS Outreach Automation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9000",
        "http://127.0.0.1:9000",
        "http://localhost:6000",
        "http://127.0.0.1:6000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class CampaignInput(BaseModel):
    """Input schema for campaign generation."""
    product_name: str
    product_description: str
    target_audience: str
    platforms: list[str]


class CampaignOutput(BaseModel):
    """Output schema for campaign generation."""
    campaign_id: str
    icp: dict
    queries: dict
    copy: dict
    policy_review: dict
    status: str
    message: str


def generate_with_gemini(prompt: str) -> str:
    """Generate content using Gemini AI."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": "development",
        "version": "1.0.0",
        "gemini_configured": bool(GEMINI_API_KEY),
        "note": "Running in simple mode without database"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to GrowthPilot API",
        "docs": "/docs",
        "health": "/health",
        "note": "Please configure .env file and install all dependencies for full functionality"
    }


@app.post("/api/campaigns/generate", response_model=CampaignOutput)
async def generate_campaign(campaign_input: CampaignInput):
    """Generate a complete outreach campaign using AI agents."""

    # Generate ICP
    icp_prompt = f"""Generate an Ideal Customer Profile (ICP) for the following product:

Product: {campaign_input.product_name}
Description: {campaign_input.product_description}
Target Audience: {campaign_input.target_audience}

Provide a detailed ICP in JSON format with the following structure:
{{
    "demographics": {{"company_size": "", "industry": "", "job_titles": []}},
    "psychographics": {{"pain_points": [], "goals": [], "values": []}},
    "behavioral": {{"buying_behavior": "", "preferred_channels": [], "decision_factors": []}}
}}"""

    icp_text = await generate_with_gemini(icp_prompt)

    # Generate search queries
    queries_prompt = f"""Generate platform-specific search queries for finding prospects matching this ICP:

Product: {campaign_input.product_name}
Target Audience: {campaign_input.target_audience}
Platforms: {', '.join(campaign_input.platforms)}

ICP: {icp_text}

Provide search queries in JSON format:
{{
    "linkedin": ["query1", "query2", "query3"],
    "reddit": ["query1", "query2"],
    "facebook": ["query1", "query2"]
}}"""

    queries_text = await generate_with_gemini(queries_prompt)

    # Generate outreach copy
    copy_prompt = f"""Generate platform-specific outreach copy for:

Product: {campaign_input.product_name}
Description: {campaign_input.product_description}
Platforms: {', '.join(campaign_input.platforms)}

Provide outreach messages in JSON format:
{{
    "linkedin": {{"subject": "", "body": "", "cta": ""}},
    "reddit": {{"title": "", "body": "", "cta": ""}},
    "facebook": {{"post": "", "cta": ""}}
}}"""

    copy_text = await generate_with_gemini(copy_prompt)

    # Generate policy review
    policy_prompt = f"""Review the following outreach copy for platform policy compliance:

Copy: {copy_text}
Platforms: {', '.join(campaign_input.platforms)}

Provide a compliance review in JSON format:
{{
    "compliant": true/false,
    "issues": [],
    "recommendations": [],
    "risk_level": "low/medium/high"
}}"""

    policy_text = await generate_with_gemini(policy_prompt)

    return CampaignOutput(
        campaign_id=f"camp_{hash(campaign_input.product_name) % 100000}",
        icp={"raw": icp_text},
        queries={"raw": queries_text},
        copy={"raw": copy_text},
        policy_review={"raw": policy_text},
        status="generated",
        message="Campaign generated successfully using AI agents"
    )
