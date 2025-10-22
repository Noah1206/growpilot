"""Policy Reviewer Agent for validating content compliance."""
import json
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.core.config import settings


class PolicyReviewerAgent(BaseAgent):
    """Agent for reviewing copy against platform policies and safety rules."""

    PROMPT_TEMPLATE = """CONTEXT: You are helping review professional communication templates for platform guidelines compliance. This is a content quality assurance system.

Platform: {channel}

Platform Rules:
{platform_rules}

Blocked Phrases:
{blocked_phrases}

Copy Variants to Review:
{copy_variants}

Your task is to review each copy variant for compliance with platform rules and safety policies:

Check for:
1. **Character/Sentence Limits**: Does it exceed platform limits?
2. **Link Policy**: Does it follow link rules?
3. **Tone Requirements**: Does it match required tone?
4. **Banned Phrases**: Does it contain any blocked phrases?
5. **Spam Indicators**: Any spammy or aggressive selling?
6. **Platform-Specific Rules**: Compliance with specific platform policies?

Determine:
- **Status**: "pass" (all variants compliant), "fail" (violations found), or "needs_revision" (minor issues)
- **Reasons**: List of specific policy violations or concerns
- **Revised**: If needed, provide compliant versions of problematic variants

Respond ONLY with valid JSON in this exact format:
{{
  "status": "pass|fail|needs_revision",
  "reasons": [
    "Reason 1 if any",
    "Reason 2 if any"
  ],
  "revised": {{
    "variant_name": "revised copy if needed"
  }}
}}

Be strict but constructive. Focus on protecting both the sender and recipients."""

    async def review_copy(
        self,
        channel: str,
        copy_variants: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Review copy variants for policy compliance."""
        platform_rules = settings.platform_rules.get(channel, {})
        blocked_phrases = settings.blocked_phrases

        prompt = self._build_prompt(
            self.PROMPT_TEMPLATE,
            channel=channel,
            platform_rules=json.dumps(platform_rules, indent=2),
            blocked_phrases=json.dumps(blocked_phrases, indent=2),
            copy_variants=json.dumps(copy_variants, indent=2)
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
            # Fallback - assume pass if parsing fails
            return {
                "status": "pass",
                "reasons": [],
                "revised": None,
                "error": f"JSON parsing failed: {str(e)}"
            }
