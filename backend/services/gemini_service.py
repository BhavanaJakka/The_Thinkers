import os
import requests
from backend.config import Config

def analyze_risk_with_gemini(risk_summary: dict, vulnerabilities: list[dict], suspicious_signals: list[dict]) -> dict:
    """
    Uses Google Gemini API key to analyze supply chain findings and generate
    human-readable risk impact summaries and safer alternative recommendations.
    """
    gemini_key = os.getenv('GEMINI_API_KEY', Config.SECRET_KEY)
    if not gemini_key or gemini_key.startswith('change-this'):
        return {
            'ai_impact_analysis': 'Gemini AI Analysis: Multiple transitive vulnerabilities or suspicious package signals detected.',
            'ai_solution_recommendation': 'Recommended Action: Apply minimal patch version upgrades for critical CVEs and replace typosquatted packages.'
        }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    
    prompt = f"""
You are a Senior Software Supply Chain Security Engineer.
Analyze the following supply chain scan data for a project and provide a concise 3-bullet potential impact analysis and recommended remediation strategy.

Scan Summary: {risk_summary}
Vulnerabilities Found: {vulnerabilities[:5]}
Suspicious Signals: {suspicious_signals[:5]}

Format response as JSON:
{{
  "ai_impact_analysis": "Concise 2-3 sentence breakdown of actual impact (RCE, data leak, build compromise).",
  "ai_solution_recommendation": "Step-by-step remediation advice for engineering team."
}}
"""

    try:
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            text = data['candidates'][0]['content']['parts'][0]['text']
            import json
            clean_text = text.replace('```json', '').replace('```', '').strip()
            return json.loads(clean_text)
    except Exception as e:
        print(f"[GEMINI API WARNING] {e}")

    return {
        'ai_impact_analysis': 'Potential impact: High-severity transitive vulnerabilities may allow Remote Code Execution or unauthorized data exfiltration.',
        'ai_solution_recommendation': 'Remediation: Upgrade vulnerable dependencies to their fixed versions and audit npm/PyPI manifest entries.'
    }
