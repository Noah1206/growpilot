"""Profile Matcher Agent - Gemini AI로 LinkedIn 프로필이 ICP에 맞는지 분석"""
import json
import logging
from typing import Dict, Any, Tuple
from app.agents.base import BaseAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProfileMatcherAgent(BaseAgent):
    """LinkedIn 프로필이 ICP(Ideal Customer Profile)에 맞는지 Gemini AI로 분석하는 Agent"""

    PROMPT_TEMPLATE = """You are an expert B2B sales analyst. Analyze if this LinkedIn profile matches the Ideal Customer Profile (ICP).

**Target ICP:**
- Target Roles: {roles}
- Industries: {industries}
- Company Sizes: {company_sizes}
- Pain Points: {pain_points}
- Search Keywords: {search_keywords}

**LinkedIn Profile:**
- Name: {name}
- Title/Headline: {title}
- Company: {company}
- Location: {location}

**Your Task:**
Determine if this person is a good fit for our ICP. Consider:
1. Does their role match our target roles?
2. Is their industry relevant?
3. Would they likely have the pain points we solve?
4. Does their profile align with the search keywords?

Respond ONLY with valid JSON:
{{
    "is_match": true or false,
    "confidence": 0-100 (integer),
    "reason": "Brief explanation in 1-2 sentences"
}}

Be strict but fair. Only mark as match if confidence >= 70%.
"""

    async def analyze_profile(
        self,
        profile: Dict[str, Any],
        icp: Dict[str, Any],
        search_keywords: str
    ) -> Tuple[bool, int, str]:
        """
        프로필이 ICP에 맞는지 Gemini AI로 분석

        Args:
            profile: LinkedIn 프로필 정보 (name, title, company, location)
            icp: ICP 정보 (roles, industries, company_sizes, pain_points)
            search_keywords: 검색 키워드

        Returns:
            (is_match, confidence, reason) 튜플
        """
        try:
            # Prompt 생성
            prompt = self._build_prompt(
                self.PROMPT_TEMPLATE,
                roles=", ".join(icp.get("roles", [])),
                industries=", ".join(icp.get("industries", [])),
                company_sizes=", ".join(icp.get("company_sizes", [])),
                pain_points=", ".join(icp.get("pain_points", [])),
                search_keywords=search_keywords,
                name=profile.get('name', 'Unknown'),
                title=profile.get('title', profile.get('headline', 'Unknown')),
                company=profile.get('company', 'Unknown'),
                location=profile.get('location', 'Unknown')
            )

            # Gemini AI 호출
            response = await self.generate(prompt)

            # JSON 파싱
            result = self._parse_json_response(response)

            is_match = result.get('is_match', False)
            confidence = int(result.get('confidence', 0))
            reason = result.get('reason', 'No reason provided')

            return is_match, confidence, reason

        except Exception as e:
            logger.error(f"Error analyzing profile: {e}")
            # 에러 시 기본값 반환 (매칭 안됨)
            return False, 0, f"Analysis failed: {str(e)}"

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """JSON 응답 파싱 (markdown 코드 블록 제거)"""
        try:
            # Remove markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]

            return json.loads(clean_response.strip())

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            logger.warning(f"Response: {response}")
            # 기본값 반환
            return {
                "is_match": False,
                "confidence": 0,
                "reason": "Failed to parse AI response"
            }
