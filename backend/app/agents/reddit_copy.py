"""Reddit Copy Generator Agent."""
import json
from typing import Dict, Any
from app.agents.base import BaseAgent


class RedditCopyAgent(BaseAgent):
    """Agent for generating Reddit comment copy variants."""

    PROMPT_TEMPLATE = """CONTEXT: You are helping create community discussion templates. This is a discussion participation assistant for Reddit communities.

You are a community discussion writer. Create authentic, helpful discussion templates for Reddit community engagement.

Product Information:
- Product Name: {product_name}
- Description: {description}
- Tone: {tone}
- CTA: {cta}

ICP Information:
{icp_json}

Platform Rules for Reddit:
- Maximum 5 sentences
- One link maximum
- Conversational, authentic tone
- Must provide value to the discussion
- No pure self-promotion
- Community-first mindset
- Avoid multi-link dumping

Your task is to generate 2-3 comment variants for relevant Reddit discussions:

Variant A: Helpful Experience Share
- Share relevant personal/professional experience
- Naturally mention the product as a solution
- Provide additional value beyond product mention

Variant B: Technical/Detailed Response
- Answer the question or add to discussion
- Include product as one option among others
- Show expertise and helpfulness

Variant C (optional): Community-Focused
- Contribute to the conversation genuinely
- Subtle product mention if relevant
- Focus on solving the community member's problem

Each variant must:
- Be 5 sentences or less
- Sound natural and conversational
- Provide real value to the discussion
- Include product mention organically
- Avoid aggressive selling

Respond ONLY with valid JSON in this exact format:
{{
  "variants": [
    {{
      "variant": "A",
      "copy": "I've been in a similar situation...",
      "tone": "conversational"
    }},
    {{
      "variant": "B",
      "copy": "Here's what worked for me...",
      "tone": "helpful"
    }}
  ]
}}"""

    async def generate_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Reddit copy variants."""
        prompt = self._build_prompt(
            self.PROMPT_TEMPLATE,
            product_name=data.get("product_name", ""),
            description=data.get("description", ""),
            tone=data.get("tone", "friendly"),
            cta=data.get("cta", "happy to share more if helpful"),
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
                        "copy": f"I've had success with {data.get('product_name')} for this. {data.get('description', '')} {data.get('cta', 'Happy to share more.')}",
                        "tone": "conversational"
                    }
                ],
                "error": f"JSON parsing failed: {str(e)}"
            }
