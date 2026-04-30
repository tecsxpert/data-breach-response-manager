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
                    temperature=0.0,  # Deterministic for consistent scoring
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
        """Build optimized prompt for breach analysis with structured output format."""
        prompt = """
You are a cybersecurity incident response analyst. Classify breach severity STRICTLY.

DATA TYPE TO SEVERITY MAPPING (MUST FOLLOW EXACTLY):
- "ssn" → CRITICAL
- "credit_card" → CRITICAL  
- "financial" → CRITICAL
- "medical" → HIGH
- "patient_diagnosis" → HIGH
- "medical_insurance" → HIGH
- "credentials" or "username_password" → HIGH
- "password" → HIGH
- "email" → MEDIUM
- "addresses" → MEDIUM
- "student_grades" → MEDIUM
- "phone_number" → LOW
- "anonymized" → LOW

Breach details:
{}

Respond in EXACT format (no extra text):
SEVERITY: [Critical|High|Medium|Low]
AFFECTED_DATA: [what was exposed]
IMPACT_SUMMARY: [1-2 sentences on impact]
IMMEDIATE_STEPS: [1. first action, 2. second action]
REMEDIATION_TIMELINE: [timeframe]

CRITICAL = identity theft, financial fraud risks
HIGH = HIPAA violations, medical PHI exposed
MEDIUM = privacy breaches, phishing risk
LOW = spam risk, minimal PII

First step: ISOLATE or FREEZE affected systems.""".format(json.dumps(breach_data, indent=2))
        return prompt
