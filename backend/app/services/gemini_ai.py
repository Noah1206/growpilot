"""Gemini AI service for profile filtering and message generation."""
import logging
from typing import Dict, Tuple
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiAI:
    """Gemini AI service for ICP matching and message generation."""

    def __init__(self):
        """Initialize Gemini AI with API key from settings."""
        try:
            api_key = settings.gemini_api_key
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini AI initialized successfully")
            else:
                self.model = None
                logger.warning("⚠️ Gemini API key not found - using mock mode")
        except Exception as e:
            self.model = None
            logger.warning(f"⚠️ Gemini API key not configured - using mock mode: {e}")

    async def check_icp_match(
        self,
        campaign_data: Dict,
        profile_description: str
    ) -> Tuple[bool, str]:
        """
        Check if a LinkedIn profile matches the campaign's ICP.

        Args:
            campaign_data: Campaign information (product_name, description, etc.)
            profile_description: Profile details (name, title, company)

        Returns:
            Tuple of (is_match: bool, reason: str)
        """
        try:
            if not self.model:
                # Mock mode - approve all profiles
                return True, "Mock mode - auto-approved"

            prompt = f"""
You are an expert at identifying ideal customer profiles (ICP) for B2B sales.

Product: {campaign_data['product_name']}
Description: {campaign_data['description']}
Target Audience: {campaign_data.get('target_audience_hint', 'Not specified')}

Profile to evaluate:
{profile_description}

Does this profile match the ideal customer profile? Respond with:
1. YES or NO
2. Brief reason (one sentence)

Format: YES/NO | Reason
"""

            response = self.model.generate_content(prompt)
            result = response.text.strip()

            # Parse response
            parts = result.split('|')
            is_match = parts[0].strip().upper() == 'YES'
            reason = parts[1].strip() if len(parts) > 1 else "No reason provided"

            return is_match, reason

        except Exception as e:
            logger.error(f"Error in check_icp_match: {e}")
            # On error, approve to avoid blocking
            return True, f"Error during check: {str(e)}"

    async def generate_personalized_message(
        self,
        campaign_data: Dict,
        profile_data: Dict
    ) -> str:
        """
        Generate a personalized LinkedIn message for a profile.

        Args:
            campaign_data: Campaign information (product_name, description, tone, cta)
            profile_data: Profile details (name, title, company)

        Returns:
            Personalized message string
        """
        try:
            if not self.model:
                # Mock mode - return template message
                return self._generate_mock_message(campaign_data, profile_data)

            prompt = f"""
You are an expert at writing personalized LinkedIn connection request messages.

Product: {campaign_data['product_name']}
Description: {campaign_data['description']}
Tone: {campaign_data.get('tone', 'professional')}
Call to Action: {campaign_data.get('cta', 'interested in learning more?')}

Recipient:
Name: {profile_data['name']}
Title: {profile_data['title']}
Company: {profile_data['company']}

Write a personalized LinkedIn message (max 300 characters) that:
1. References their role/company
2. Explains value proposition briefly
3. Includes the call to action
4. Matches the specified tone

Return ONLY the message text, no extra formatting.
"""

            response = self.model.generate_content(prompt)
            message = response.text.strip()

            # Ensure message is within LinkedIn's character limit
            if len(message) > 300:
                message = message[:297] + "..."

            return message

        except Exception as e:
            logger.error(f"Error in generate_personalized_message: {e}")
            return self._generate_mock_message(campaign_data, profile_data)

    async def generate_message_template(
        self,
        campaign_data: Dict
    ) -> str:
        """
        Generate a general LinkedIn message template for a campaign.

        This template includes placeholders like {name}, {title}, {company}
        that will be personalized for each prospect.

        Args:
            campaign_data: Campaign information (product_name, description, tone, cta)

        Returns:
            Message template string with placeholders
        """
        try:
            if not self.model:
                # Mock mode - return template message
                return self._generate_mock_template(campaign_data)

            prompt = f"""
You are an expert at writing LinkedIn outreach message templates.

Product: {campaign_data['product_name']}
Description: {campaign_data['description']}
Tone: {campaign_data.get('tone', 'professional')}
Call to Action: {campaign_data.get('cta', 'interested in learning more?')}

Write a LinkedIn message template (max 300 characters) that:
1. Uses placeholders: {{name}}, {{title}}, {{company}}
2. References the recipient's role/company using placeholders
3. Explains the value proposition briefly
4. Includes the call to action
5. Matches the specified tone

Example format:
Hi {{name}}, I noticed your expertise in {{title}} at {{company}}. Our [product] helps [value proposition]. Would you be {{cta}}?

Return ONLY the message template text, no extra formatting or explanations.
"""

            response = self.model.generate_content(prompt)
            template = response.text.strip()

            # Ensure template is within LinkedIn's character limit
            if len(template) > 300:
                template = template[:297] + "..."

            logger.info(f"Generated message template: {template[:50]}...")
            return template

        except Exception as e:
            logger.error(f"Error in generate_message_template: {e}")
            return self._generate_mock_template(campaign_data)

    def _generate_mock_template(self, campaign_data: Dict) -> str:
        """Generate a simple template message with placeholders for mock mode."""
        product = campaign_data['product_name']
        description = campaign_data['description'][:100]  # Limit description length
        cta = campaign_data.get('cta', 'interested in learning more?')

        return f"Hi {{name}}, I noticed your expertise in {{title}} at {{company}}. Our {product} helps with {description}. Are you {cta}"

    def _generate_mock_message(self, campaign_data: Dict, profile_data: Dict) -> str:
        """Generate a simple template message for mock mode."""
        name = profile_data['name'].split()[0]  # First name only
        product = campaign_data['product_name']
        cta = campaign_data.get('cta', 'interested in learning more?')

        return f"Hi {name}, I noticed your work at {profile_data['company']}. I think {product} could help. Are you {cta}"
