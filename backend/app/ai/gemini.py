import json
import time
import logging
from typing import Optional
from dataclasses import dataclass
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class GeminiResponse:
    text: str
    parsed: Optional[dict] = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    success: bool = False
    error: Optional[str] = None


class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self.max_retries = settings.gemini_max_retries
        self.timeout = settings.gemini_request_timeout
        self._model = None
        self._initialized = False

    def _initialize(self):
        if not self.api_key:
            logger.warning("Gemini API key not configured")
            return False
        try:
            genai.configure(api_key=self.api_key)
            generation_config = {
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            self._model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return False

    def is_available(self) -> bool:
        if not self._initialized:
            return self._initialize()
        return self._model is not None

    def generate(self, prompt: str, response_schema: Optional[dict] = None) -> GeminiResponse:
        if not self.is_available():
            return GeminiResponse(success=False, error="Gemini API not configured")

        start_time = time.time()
        last_error = None

        for attempt in range(self.max_retries):
            try:
                if response_schema:
                    full_prompt = f"{prompt}\n\nRespond in valid JSON matching this schema:\n{json.dumps(response_schema, indent=2)}"
                else:
                    full_prompt = prompt

                response = self._model.generate_content(full_prompt)

                latency_ms = int((time.time() - start_time) * 1000)

                usage = getattr(response, "usage_metadata", None)
                input_tokens = usage.prompt_token_count if usage else 0
                output_tokens = usage.candidates_token_count if usage else 0
                total_tokens = input_tokens + output_tokens

                text = response.text if hasattr(response, "text") else ""

                parsed = None
                if response_schema and text:
                    try:
                        cleaned = text.strip()
                        if cleaned.startswith("```json"):
                            cleaned = cleaned[7:]
                        if cleaned.startswith("```"):
                            cleaned = cleaned[3:]
                        if cleaned.endswith("```"):
                            cleaned = cleaned[:-3]
                        cleaned = cleaned.strip()
                        parsed = json.loads(cleaned)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON response: {e}")
                        parsed = {"raw_response": text}

                return GeminiResponse(
                    text=text,
                    parsed=parsed,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    latency_ms=latency_ms,
                    success=True,
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(f"Gemini attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)

        return GeminiResponse(success=False, error=last_error or "Unknown error")


gemini_service = GeminiService()
