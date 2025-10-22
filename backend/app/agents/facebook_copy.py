"""Facebook Copy Generator Agent."""
import json
from typing import Dict, Any
from app.agents.base import BaseAgent


class FacebookCopyAgent(BaseAgent):
    """Agent for generating Facebook post/comment copy variants."""

    PROMPT_TEMPLATE = """CONTEXT: You are helping create social discussion templates. This is a discussion content assistant for Facebook business communities.

You are a social discussion writer. Create friendly, helpful discussion templates for Facebook business groups.

Product Information:
- Product Name: {product_name}
- Description: {description}
- Tone: {tone}
- CTA: {cta}

ICP Information:
{icp_json}

Platform Rules for Facebook:
- Maximum 6 sentences
- One link maximum
- Friendly, approachable tone
- Community and relationship focused
- No aggressive selling
- Avoid misleading claims or clickbait
- Authentic engagement

Your task is to generate 2-3 post/comment variants for Facebook groups:

Variant A: Story/Experience Based
- Share a relatable story or experience
- Connect emotionally with the audience
- Natural product integration

Variant B: Question/Engagement Based
- Ask engaging questions
- Invite community participation
- Position product as helpful resource

Variant C (optional): Value/Education Based
- Share helpful tips or insights
- Provide genuine value
- Mention product as supporting tool

Each variant must:
- Be 6 sentences or less
- Use friendly, conversational language
- Focus on building relationships
- Include product mention naturally
- Invite engagement or conversation

Respond ONLY with valid JSON in this exact format:
{{
  "variants": [
    {{
      "variant": "A",
      "copy": "Hey everyone! I wanted to share...",
      "tone": "friendly"
    }},
    {{
      "variant": "B",
      "copy": "Quick question for the group...",
      "tone": "engaging"
    }}
  ]
}}"""

    async def generate_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Facebook copy variants."""
        prompt = self._build_prompt(
            self.PROMPT_TEMPLATE,
            product_name=data.get("product_name", ""),
            description=data.get("description", ""),
            tone=data.get("tone", "friendly"),
            cta=data.get("cta", "Would love to hear your thoughts!"),
            icp_json=json.dumps(data.get("icp", {}), indent=2)
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
                "variants": [
                    {
                        "variant": "A",
                        "copy": f"Hey everyone! I've been using {data.get('product_name')} and wanted to share. {data.get('description', '')} {data.get('cta', 'Would love to hear your thoughts!')}",
                        "tone": "friendly"
                    }
                ],
                "error": f"JSON parsing failed: {str(e)}"
            }
