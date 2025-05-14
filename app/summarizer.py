import json
import re
from typing import List
import openai
import google.generativeai as genai
import structlog
from app.models import NewsItem, SummarySchema
from app.config import settings

logger = structlog.get_logger()

class Summarizer:
    """Класс для обработки новостей через LLM"""
    
    def __init__(self):
        # OpenAI
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.openai_model = getattr(settings, 'OPENAI_MODEL', 'gpt-4')
        self.openai_temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.2)
        
        # Gemini
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        self.gemini_temperature = getattr(settings, 'GEMINI_TEMPERATURE', 0.2)
    
    async def process_batch(self, items: List[NewsItem]) -> List[NewsItem]:
        """Обработать пакет новостей"""
        results = []
        for item in items:
            try:
                # Сначала пробуем Gemini
                try:
                    summary = await self._process_with_gemini(item)
                    item.llm_model = "gemini-1.5-flash"
                    item.cost_usd = 0.0001  # примерная оценка
                except Exception as e:
                    logger.warning("gemini_failed", error=str(e), url=item.url)
                    # Если Gemini не справился, пробуем OpenAI
                    summary = await self._process_with_openai(item)
                    item.llm_model = "openai"
                    item.cost_usd = 0.002  # примерная оценка
                
                item.summary = summary.summary
                item.why_matters = summary.why
                item.impact = summary.impact
                results.append(item)
            except Exception as e:
                logger.error("error_processing_item", error=str(e), url=item.url)
                continue
        return results

    async def _process_with_gemini(self, item: NewsItem) -> SummarySchema:
        """Обработать новость через Gemini"""
        prompt = self._create_prompt(item)
        response = await self.gemini_model.generate_content_async(
            prompt,
            generation_config={
                'temperature': self.gemini_temperature,
                'max_output_tokens': 512,
            }
        )
        text = response.text
        return self._parse_llm_response(text)

    async def _process_with_openai(self, item: NewsItem) -> SummarySchema:
        """Обработать новость через OpenAI"""
        prompt = self._create_prompt(item)
        response = await self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=[{"role": "system", "content": "You are an expert AI news editor."},
                      {"role": "user", "content": prompt}],
            temperature=self.openai_temperature,
            max_tokens=512,
        )
        text = response.choices[0].message.content
        return self._parse_llm_response(text)

    def _create_prompt(self, item: NewsItem) -> str:
        """Создать промпт для LLM"""
        return f'''You are an expert AI news editor.
Return ONLY valid JSON, without any explanation, markdown, or formatting. Do not write anything except the JSON object.

Title: {item.title}
Content: {item.content[:4000]}

Your task:
- Write a short, but high-quality, informative, and clear summary of the news for a non-technical audience.
- Add context and background if needed, so the news is understandable even for those who are not experts.
- Explain why this news matters and what its possible impact is.
- Be concise, but make the summary meaningful and useful.

Format example:
{{
  "summary": "short summary here",
  "why": "why it matters here",
  "impact": 3
}}
Return ONLY valid JSON as shown above. Do not use markdown, do not add any text before or after the JSON.'''
    
    def _parse_llm_response(self, response: str) -> SummarySchema:
        try:
            data = json.loads(response)
            return SummarySchema(**data)
        except Exception as e:
            print(f"Primary JSON parse failed: {e}. Trying fallback regex.")
            # Сначала ищем JSON в markdown-блоке
            match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if not match:
                match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1) if match.lastindex else match.group(0))
                    return SummarySchema(**data)
                except Exception as e2:
                    logger.error("error_parsing_llm_response_fallback", error=str(e2), response=response)
            logger.error("error_parsing_llm_response", error=str(e), response=response)
            raise 