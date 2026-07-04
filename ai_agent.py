import os
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Try to configure Gemini API if key is present and SDK is available
API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
API_AVAILABLE = False

if API_KEY and genai is not None:
    try:
        genai.configure(api_key=API_KEY)
        API_AVAILABLE = True
    except Exception as e:
        print(f"Failed to configure Gemini API: {e}")
        API_AVAILABLE = False
else:
    if API_KEY and genai is None:
        print("Gemini SDK not installed; falling back to local AI rules.")
    API_AVAILABLE = False

def rule_based_analysis(employee_name, leave_type, duration_days, reason, remaining_balance):
    """
    Local heuristic rule-based fallback when the Gemini API is unavailable.
    """
    reason_lower = reason.lower().strip()
    
    # Rule 1: Zero or Negative duration check
    if duration_days <= 0:
        return 'Reject', "Invalid leave duration (must be 1 or more days)."
        
    # Rule 2: Over limit balance check
    if duration_days > remaining_balance:
        return 'Reject', f"Requested leave duration ({duration_days} days) exceeds the remaining {leave_type} balance ({remaining_balance} days)."
    
    # Rule 3: Sick Leave Evaluation
    if leave_type == 'Sick':
        medical_keywords = ['medical', 'hospital', 'surgery', 'doctor', 'fever', 'flu', 'covid', 'accident', 'emergency', 'pain', 'sick', 'dental', 'checkup', 'treatment']
        if any(kw in reason_lower for kw in medical_keywords):
            return 'Approve', "AI Heuristic: Automatic Approval recommendation for documented health/medical conditions."
        return 'Approve', "AI Heuristic: Standard sick leave recommendation (sufficient balance)."
        
    # Rule 4: Vacation / Long Leave checks
    if duration_days > 10:
        return 'Escalate', f"AI Heuristic: Large leave block ({duration_days} days) requested. Escalating to Admin for team coverage planning."
        
    # Rule 5: Vague reason check
    if len(reason_lower) < 10:
        return 'Escalate', "AI Heuristic: Vague or extremely brief description. Escalating to Admin for manual review."
        
    # Rule 6: Informal / Red flag terms
    informal_keywords = ['party', 'hangout', 'lazy', 'sleep in', 'hangover', 'bored', 'chill', 'gaming']
    if any(kw in reason_lower for kw in informal_keywords):
        return 'Escalate', "AI Heuristic: Reason contains terms that may indicate non-standard leave usage. Escalating to Admin."
        
    # Rule 7: Family emergencies or life events
    priority_keywords = ['family emergency', 'funeral', 'bereavement', 'wedding', 'marriage', 'spouse', 'child', 'death', 'parent']
    if any(kw in reason_lower for kw in priority_keywords):
        return 'Approve', "AI Heuristic: Recommended for Approval (valid personal/family priority context)."
        
    # Default approval if balance is fine and reason looks typical
    return 'Approve', "AI Heuristic: Recommended for Approval (within policy limits, sufficient balance)."

def analyze_leave_request(employee_name: str, leave_type: str, duration_days: int, reason: str, remaining_balance: int) -> tuple[str, str]:
    """
    Main entrypoint to analyze a leave request.
    Uses Gemini API if configured, otherwise falls back to local heuristic rules.
    Returns:
        (recommendation, reasoning) where recommendation is 'Approve', 'Escalate', or 'Reject'
    """
    if not API_AVAILABLE:
        return rule_based_analysis(employee_name, leave_type, duration_days, reason, remaining_balance)
        
    try:
        # Prompt definition
        prompt = f"""
        You are an intelligent HR Leave Approval AI Assistant. 
        Analyze the following leave request details and make a recommendation.
        
        Details:
        - Employee Name: {employee_name}
        - Leave Type: {leave_type} (Casual, Sick, or Paid)
        - Duration: {duration_days} day(s)
        - Remaining Balance for this leave type: {remaining_balance} day(s)
        - Employee's Reason: "{reason}"
        
        Evaluation Guidelines:
        1. If duration_days > remaining_balance, recommend 'Reject' with an explanation of insufficient balance.
        2. If duration_days is negative or zero, recommend 'Reject'.
        3. If leave_type is 'Sick' and the reason details a medical issue, emergency, or hospital visit, recommend 'Approve'.
        4. If the duration is greater than 10 days, recommend 'Escalate' to check coverage.
        5. If the reason is extremely vague (e.g., "personal", "stuff") or seems unprofessional (e.g., "hangover", "party", "bored"), recommend 'Escalate'.
        6. Otherwise, if the reason is reasonable and the balance is sufficient, recommend 'Approve'.
        
        You must respond with a JSON object containing exactly two keys:
        1. "recommendation": must be one of the strings: "Approve", "Escalate", or "Reject"
        2. "reason": a concise explanation (1-2 sentences) of why you chose this recommendation.
        
        Do not include any markdown styling like ```json or anything else. Just return the raw JSON object string.
        """
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse JSON response
        result = json.loads(response.text.strip())
        recommendation = result.get("recommendation", "Escalate")
        reasoning = result.get("reason", "Parsed response from AI.")
        
        # Validate recommendation value
        if recommendation not in ['Approve', 'Escalate', 'Reject']:
            recommendation = 'Escalate'
            
        return recommendation, reasoning
        
    except Exception as e:
        # Gracefully handle API failures by falling back to rules
        print(f"Gemini API call failed, falling back to local rule-based engine: {e}")
        return rule_based_analysis(employee_name, leave_type, duration_days, reason, remaining_balance)
