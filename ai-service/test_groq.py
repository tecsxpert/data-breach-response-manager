import os
from dotenv import load_dotenv
from services.groq_client import GroqClient

load_dotenv()

client = GroqClient()

test_data = {
    "company": "Example Inc",
    "breach_date": "2024-01-01",
    "affected_users": 10000,
    "data_types": ["emails", "passwords"],
    "attack_vector": "SQL injection"
}

try:
    analysis = client.describe_breach(test_data)
    print("Analysis:", analysis)
except Exception as e:
    print("Error:", str(e))

