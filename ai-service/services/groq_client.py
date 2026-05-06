import os
import time
import json
import logging
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, api_key: str = None):
        self.client = Groq(api_key=api_key or os.getenv('GROQ_API_KEY'))
        self.model = "llama-3.1-8b-instant"
        self.max_retries = 3

    def describe_breach(self, breach_data: Dict[str, Any]) -> str:
        """Describe breach using Groq LLM with retry logic."""
        prompt = self._build_prompt(breach_data)
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1000
                )
                analysis = response.choices[0].message.content.strip()
                logger.info(f"Groq analysis success on attempt {attempt + 1}")
                return analysis
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        return ""

    def _build_prompt(self, breach_data: Dict[str, Any]) -> str:
        """Build detailed prompt for breach analysis."""
        prompt = """
Analyze this data breach incident and provide:
1. Severity level (Low/Med/High/Critical)
2. Affected data types
3. Potential impact
4. Immediate response steps
5. Remediation timeline

Breach details: {}
        """.format(json.dumps(breach_data, indent=2))
        return prompt

