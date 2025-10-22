"""Conversation Analyst Agent for analyzing prospect responses."""
import json
from typing import Dict, Any
from app.agents.base import BaseAgent


class ConversationAnalystAgent(BaseAgent):
    """Agent for analyzing prospect responses and suggesting follow-ups."""

    PROMPT_TEMPLATE = """You are an expert sales conversation analyst specializing in prospect engagement analysis.

Original Message:
{original_message}

Prospect Reply:
{prospect_reply}

Channel: {channel}

Your task is to analyze the prospect's reply and provide actionable insights:

1. **Classification**: Categorize the reply
   - "positive": Interested, wants more information
   - "neutral": Acknowledges but non-committal
   - "negative": Not interested, dismissive
   - "question": Asking questions, seeking clarification
   - "objection": Expressing concerns or objections

2. **Sentiment Score**: Rate from -1.0 (very negative) to 1.0 (very positive)

3. **Suggested Follow-up**: Provide a contextual, appropriate follow-up message based on the classification

4. **Reasoning**: Brief explanation of your analysis

Respond ONLY with valid JSON in this exact format:
{{
  "classification": "positive|neutral|negative|question|objection",
  "sentiment_score": 0.0,
  "suggested_followup": "Your suggested follow-up message here",
  "reasoning": "Brief explanation of classification and sentiment"
}}

Be nuanced and context-aware. Consider cultural and communication style differences."""

    async def analyze_conversation(
        self,
        prospect_reply: str,
        original_message: str,
        channel: str
    ) -> Dict[str, Any]:
        """Analyze prospect response and suggest follow-up."""
        prompt = self._build_prompt(
            self.PROMPT_TEMPLATE,
            prospect_reply=prospect_reply,
            original_message=original_message,
            channel=channel
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
                "classification": "neutral",
                "sentiment_score": 0.0,
                "suggested_followup": "Thank you for your response. Would you like to learn more?",
                "reasoning": "Unable to parse response - defaulting to neutral classification",
                "error": f"JSON parsing failed: {str(e)}"
            }
