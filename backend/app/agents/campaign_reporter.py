"""Campaign Reporter Agent for performance analysis and recommendations."""
import json
from typing import Dict, Any
from app.agents.base import BaseAgent


class CampaignReporterAgent(BaseAgent):
    """Agent for analyzing campaign performance and providing strategic recommendations."""

    PROMPT_TEMPLATE = """You are an expert marketing analytics consultant specializing in outreach campaign optimization.

Campaign Metrics:
{metrics}

Your task is to analyze the campaign performance and provide actionable insights:

1. **Performance Summary**: High-level overview of campaign results
   - Key metrics (sends, opens, replies, conversions)
   - Channel comparison
   - Standout results or concerns

2. **Strategic Recommendations**: 3-5 specific, actionable recommendations
   - What's working and should be scaled
   - What needs improvement
   - Tactical adjustments to test
   - Priority order for implementation

3. **Insights**: 2-4 key insights from the data
   - Pattern recognition
   - Unexpected findings
   - Opportunity identification
   - Risk areas

Respond ONLY with valid JSON in this exact format:
{{
  "summary": {{
    "overall_performance": "Brief performance overview",
    "key_metrics": {{
      "sends": 0,
      "reply_rate": 0.0,
      "conversion_rate": 0.0
    }},
    "top_channel": "channel name",
    "concerns": ["Concern 1 if any"]
  }},
  "recommendations": [
    "Recommendation 1: Specific action to take",
    "Recommendation 2: Another specific action",
    "Recommendation 3: Priority improvement area"
  ],
  "insights": [
    "Insight 1: Pattern or finding from data",
    "Insight 2: Opportunity or risk identified"
  ]
}}

Be data-driven, specific, and actionable. Focus on ROI and efficiency improvements."""

    async def generate_report(
        self,
        campaign_id: int,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate campaign performance report and recommendations."""
        prompt = self._build_prompt(
            self.PROMPT_TEMPLATE,
            metrics=json.dumps(metrics, indent=2)
        )

        response = await self.generate(prompt)

        # Parse JSON response
        try:
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]

            result = json.loads(clean_response.strip())
            return result
        except json.JSONDecodeError as e:
            # Fallback
            return {
                "summary": {
                    "overall_performance": "Campaign data received, analysis in progress",
                    "key_metrics": metrics,
                    "top_channel": "linkedin",
                    "concerns": []
                },
                "recommendations": [
                    "Continue monitoring campaign performance",
                    "Test different messaging variants",
                    "Analyze response patterns by channel"
                ],
                "insights": [
                    "Initial data collected successfully",
                    "Recommend longer data collection period for accurate analysis"
                ],
                "error": f"JSON parsing failed: {str(e)}"
            }
