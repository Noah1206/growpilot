"""Query Builder Agent for generating platform-specific search queries."""
import json
from typing import Dict, Any, List
from app.agents.base import BaseAgent


class QueryBuilderAgent(BaseAgent):
    """Agent for building platform-specific search queries."""

    PROMPT_TEMPLATE = """CONTEXT: You are helping create a professional network research tool. This is a business connection discovery assistant.

You are a business research specialist. Create effective search queries for professional networking and industry research on LinkedIn, Reddit, and Facebook.

ICP Information:
{icp_json}

Target Channels: {channels}

Your task is to generate highly targeted search queries for prospect discovery on each platform:

**LinkedIn Queries** (if included):
- Use boolean search operators (AND, OR, NOT)
- Target specific job titles, industries, and keywords
- Include location filters where relevant
- Generate 3-5 varied queries

**Reddit Queries** (if included):
- Identify relevant subreddits
- Include keyword combinations for post/comment search
- Focus on pain points and discussion topics
- Generate 3-5 varied queries

**Facebook Queries** (if included):
- Target relevant groups and pages
- Include interest-based keywords
- Focus on community and discussion topics
- Generate 3-5 varied queries

Respond ONLY with valid JSON in this exact format:
{{
  "linkedin": [
    "query 1",
    "query 2",
    "query 3"
  ],
  "reddit": [
    "r/subreddit1 + keyword",
    "r/subreddit2 + keyword",
    "keyword combination"
  ],
  "facebook": [
    "group/page + keyword",
    "interest + keyword",
    "community topic"
  ]
}}

Only include platforms that are in the target channels list."""

    async def build_queries(self, icp: Dict[str, Any], channels: List[str]) -> Dict[str, List[str]]:
        """Build platform-specific search queries."""
        prompt = self._build_prompt(
            self.PROMPT_TEMPLATE,
            icp_json=json.dumps(icp, indent=2),
            channels=", ".join(channels)
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

            # Filter to only requested channels
            filtered_result = {
                channel: result.get(channel, [])
                for channel in channels
            }

            return {"queries": filtered_result}
        except json.JSONDecodeError as e:
            # Fallback
            return {
                "queries": {
                    channel: [f"Search query for {channel}"]
                    for channel in channels
                },
                "error": f"JSON parsing failed: {str(e)}"
            }
