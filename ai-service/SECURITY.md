# Security Considerations

## 1. API Key Exposure
- **Threat**: Groq key in logs/responses or committed code.
- **Mitigation**: Key in .env only (.gitignore'd), no logging of keys.

## 2. Prompt Injection
- **Threat**: Malicious input manipulates LLM output.
- **Mitigation**: Input sanitization middleware, prompt templates.

## 3. Rate Limiting Bypass
- **Threat**: DDoS or excessive API calls.
- **Mitigation**: Flask-Limiter, Groq rate limits.

## 4. Data Leakage
- **Threat**: Sensitive breach data in LLM context.
- **Mitigation**: PII redaction before sending to AI.

## 5. Dependency Vulnerabilities
- **Threat**: Malicious packages in requirements.txt.
- **Mitigation**: pip-audit, pinned versions, Docker isolation.

