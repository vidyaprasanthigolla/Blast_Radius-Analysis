import os
import json
import urllib.request

def generate_ai_explanation(changed_node, impacted_node, intent, impact_distance, category):
    """
    Connects to Gemini API to generate explanation.
    Fallback deterministically if no key exists.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return _fallback_explanation(changed_node, impacted_node, impact_distance, category)

    prompt = f"""
    You are an AI code analyst for BlastScope.
    A developer modified component `{changed_node}` with intent: "{intent}"
    This impacted component `{impacted_node}` (dependency distance: {impact_distance}, category: {category}).
    
    Write a specific, technical 1-2 sentence explanation of WHY this is affected and what to verify. Look at node names to infer relationships.
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 150}
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return _fallback_explanation(changed_node, impacted_node, impact_distance, category)

def _fallback_explanation(changed_node, impacted_node, distance, category):
    reasoning = f"Because {impacted_node} depends on {changed_node} (distance: {distance})."
    if distance == 1:
        reasoning = f"Directly calls or imports the modified component. Verify {category} constraints."
    return reasoning
