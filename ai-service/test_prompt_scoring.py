"""
Real Prompt Tuning Test - 10 Real Inputs
Evaluate actual scoring accuracy with Groq API
"""

import re
import os
import json
from dotenv import load_dotenv
from services.groq_client import GroqClient

load_dotenv()


def check_response_format(response):
    """Parse and validate response format"""
    result = {
        'has_severity': False,
        'has_affected': False,
        'has_impact': False,
        'has_steps': False,
        'has_timeline': False,
        'valid': False
    }
    
    if not response:
        return result
    
    result['has_severity'] = bool(re.search(r'SEVERITY:\s*\w+', response, re.I))
    result['has_affected'] = bool(re.search(r'AFFECTED_DATA:', response, re.I))
    result['has_impact'] = bool(re.search(r'IMPACT_SUMMARY:', response, re.I))
    result['has_steps'] = bool(re.search(r'IMMEDIATE_STEPS:', response, re.I))
    result['has_timeline'] = bool(re.search(r'REMEDIATION[_ ]TIMELINE:', response, re.I))
    
    result['valid'] = all([
        result['has_severity'],
        result['has_affected'],
        result['has_impact'],
        result['has_steps'],
        result['has_timeline']
    ])
    
    return result


def score_response(result):
    """Score out of 10 based on valid format"""
    score = 0
    if result['has_severity']:
        score += 2
    if result['has_affected']:
        score += 2
    if result['has_impact']:
        score += 2
    if result['has_steps']:
        score += 2
    if result['has_timeline']:
        score += 2
    return score


# 10 Real Test Cases
test_cases = [
    {
        "description": "Test 1: Medical records breach",
        "data": {"breach_data": {"company": "HealthFirst", "records": 5000, "data_type": "medical"}}
    },
    {
        "description": "Test 2: Credit card breach",
        "data": {"breach_data": {"company": "ShopFast", "records": 50000, "data_type": "credit_card"}}
    },
    {
        "description": "Test 3: SSN breach",
        "data": {"breach_data": {"company": "BankSecure", "records": 1000, "data_type": "ssn"}}
    },
    {
        "description": "Test 4: Email breach",
        "data": {"breach_data": {"company": "EmailCo", "records": 100000, "data_type": "email"}}
    },
    {
        "description": "Test 5: Patient diagnosis breach",
        "data": {"breach_data": {"company": "DoctorPlus", "records": 2000, "data_type": "patient_diagnosis"}}
    },
    {
        "description": "Test 6: Username/password breach",
        "data": {"breach_data": {"company": "GamePortal", "records": 500, "data_type": "username_password"}}
    },
    {
        "description": "Test 7: Student grades breach",
        "data": {"breach_data": {"company": "SchoolDistrict", "records": 8000, "data_type": "student_grades"}}
    },
    {
        "description": "Test 8: Address breach",
        "data": {"breach_data": {"company": "RetailGiant", "records": 200000, "data_type": "addresses"}}
    },
    {
        "description": "Test 9: Insurance medical breach",
        "data": {"breach_data": {"company": "InsuranceCorp", "records": 3000, "data_type": "medical"}}
    },
    {
        "description": "Test 10: Phone number breach",
        "data": {"breach_data": {"company": "SocialApp", "records": 50000, "data_type": "phone_number"}}
    }
]


def run_real_tests():
    """Run all 10 real inputs through Groq API and score"""
    client = GroqClient()
    
    print("=" * 60)
    print("PROMPT TUNING - 10 REAL INPUTS TEST")
    print("=" * 60)
    
    total_score = 0
    failed_cases = []
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            print(f"\n{test_case['description']}")
            print("-" * 40)
            
            response = client.describe_breach(test_case['data'])
            result = check_response_format(response)
            test_score = score_response(result)
            total_score += test_score
            
            print(f"Response:\n{response[:200]}...")
            print(f"Valid format: {result['valid']}")
            print(f"Score: {test_score}/10")
            
            if test_score < 7:
                failed_cases.append((i, test_case['description'], test_score))
                
        except Exception as e:
            print(f"Error: {str(e)}")
            failed_cases.append((i, test_case['description'], 0))
    
    # Summary
    accuracy = (total_score / 100) * 100
    print("\n" + "=" * 60)
    print("SCORING SUMMARY")
    print("=" * 60)
    print(f"Total score: {total_score}/100")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Failed cases (< 7/10): {len(failed_cases)}")
    
    if failed_cases:
        print("\nFailed cases:")
        for case_num, desc, score in failed_cases:
            print(f"  {desc}: {score}/10")
    
    return total_score, accuracy, failed_cases


if __name__ == '__main__':
    run_real_tests()
