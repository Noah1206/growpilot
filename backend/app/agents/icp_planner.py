"""ICP (Ideal Customer Profile) Planner Agent."""
import json
from typing import Dict, Any
from app.agents.base import BaseAgent


class ICPPlannerAgent(BaseAgent):
    """Agent for inferring ideal customer profiles from product descriptions."""

    PROMPT_TEMPLATE = """CONTEXT: You are helping create a business communication template system. This is a professional audience analysis tool for B2B software companies.

You are a business analyst specializing in audience research and professional communication planning for software products.

Product Information:
- Product Name: {product_name}
- Description: {description}
- Target Audience Hint: {target_audience_hint}
- Target Locales: {locales}
- Language: {language_pref}

Your task is to infer a comprehensive ICP that includes:

1. **Target Roles**: Specific job titles and roles that would benefit from this product
2. **Industries**: Industries where this product would be most valuable
3. **Regions**: Geographic regions based on the provided locales
4. **Company Sizes**: Ideal company sizes (startup, SMB, enterprise)
5. **Pain Points**: Key challenges this product solves
6. **Keywords**:
   - Root keywords: Broad search terms (3-5 terms)
   - Long-tail keywords: Specific phrases prospects might use (5-8 phrases)

Respond ONLY with valid JSON in this exact format:
{{
  "icp": {{
    "roles": ["Role 1", "Role 2", "Role 3"],
    "industries": ["Industry 1", "Industry 2", "Industry 3"],
    "regions": ["Region 1", "Region 2"],
    "company_sizes": ["Size 1", "Size 2"],
    "pain_points": ["Pain 1", "Pain 2", "Pain 3"]
  }},
  "keywords": {{
    "root": ["keyword1", "keyword2", "keyword3"],
    "long_tail": ["long tail phrase 1", "long tail phrase 2", "long tail phrase 3"]
  }}
}}

Ensure all recommendations are specific, actionable, and aligned with the product value proposition."""

    async def infer_icp(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Infer ICP from product information."""
        prompt = self._build_prompt(
            self.PROMPT_TEMPLATE,
            product_name=data.get("product_name", ""),
            description=data.get("description", ""),
            target_audience_hint=data.get("target_audience_hint", "No specific hint provided"),
            locales=", ".join(data.get("locales", ["US"])),
            language_pref=data.get("language_pref", "en")
        )

        response = await self.generate(prompt)

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
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
            # Fallback: return structured error
            return {
                "icp": {
                    "roles": ["Marketing Manager", "Product Manager"],
                    "industries": ["SaaS", "Technology"],
                    "regions": data.get("locales", ["US"]),
                    "company_sizes": ["SMB", "Enterprise"],
                    "pain_points": ["Need to improve efficiency"]
                },
                "keywords": {
                    "root": ["software", "automation", "tool"],
                    "long_tail": ["best automation tool", "software for productivity"]
                },
                "error": f"JSON parsing failed: {str(e)}"
            }
