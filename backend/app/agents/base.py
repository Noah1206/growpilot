"""Base agent class for Gemini-powered AI agents."""
import google.generativeai as genai
from typing import Dict, Any, Optional
from app.core.config import settings


class BaseAgent:
    """Base class for all AI agents using Google Gemini."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """Initialize the agent with Gemini API."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(model_name)
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

    async def generate(self, prompt: str, generation_config: Optional[Dict[str, Any]] = None) -> str:
        """Generate response from Gemini with safety filter handling."""
        config = generation_config or self.generation_config

        # Configure safety settings to be less restrictive
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = await self.model.generate_content_async(
            prompt,
            generation_config=config,
            safety_settings=safety_settings
        )

        # Handle safety filter blocks
        if not response.parts:
            # If blocked by safety filter, try to get the finish reason
            finish_reason = getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None
            if finish_reason == 2:  # SAFETY
                raise ValueError("Content was blocked by Gemini safety filters. Please try rephrasing your input.")
            else:
                raise ValueError(f"No response generated. Finish reason: {finish_reason}")

        return response.text

    def _build_prompt(self, template: str, **kwargs) -> str:
        """Build prompt from template and variables."""
        return template.format(**kwargs)
