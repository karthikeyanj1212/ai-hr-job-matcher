"""
LLM Utilities v1.0 - Cloud Version with Groq API
Uses FREE Groq API for fast LLM inference
Get your free API key at: https://console.groq.com/keys
"""

import json
import re
import os
import requests
from datetime import datetime

# ============ CONFIGURATION ============

# Groq API - FREE and FAST
# Get your API key at: https://console.groq.com/keys
# Set it in Streamlit Cloud secrets or environment variable

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Model Selection Strategy:
# - Use 70b for ACCURACY (ATS scoring, Salary, Reports)
# - Rate limit: 30 req/min, 6000 tokens/min for 70b
# - We add delays between requests to avoid rate limits

GROQ_MODEL = "llama-3.3-70b-versatile"  # Best accuracy for HR analysis

# Available models
AVAILABLE_MODELS = {
    "best_quality": "llama-3.3-70b-versatile",      # Best for HR analysis
    "long_context": "meta-llama/llama-4-scout-17b-16e-instruct",  # 30K context
    "balanced": "meta-llama/llama-4-maverick-17b-128e-instruct",
    "fastest": "llama-3.1-8b-instant",              # Only for quick tests
}

# Rate limit management
import time
LAST_REQUEST_TIME = 0
MIN_REQUEST_INTERVAL = 3  # Minimum seconds between requests to avoid rate limits


def get_api_key():
    """Get API key from Streamlit secrets or environment."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
            return st.secrets['GROQ_API_KEY']
    except:
        pass
    
    return os.environ.get('GROQ_API_KEY', '')


def initialize_llm(use_gpu: bool = False, gpu_layers: int = 35):
    """Initialize - verify API key exists and is valid."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError(
            "⚠️ GROQ_API_KEY not found!\n\n"
            "Get your FREE API key at: https://console.groq.com/keys\n\n"
            "For local development:\n"
            "1. Create file: .streamlit/secrets.toml\n"
            "2. Add: GROQ_API_KEY = \"gsk_your_key_here\"\n\n"
            "For Streamlit Cloud:\n"
            "1. Go to your app settings → Secrets\n"
            "2. Add: GROQ_API_KEY = \"gsk_your_key_here\""
        )
    
    # Validate API key format
    if not api_key.startswith("gsk_"):
        raise ValueError(
            "⚠️ Invalid API key format!\n\n"
            "Groq API keys should start with 'gsk_'\n"
            "Get a valid key at: https://console.groq.com/keys"
        )
    
    # Test the API key with a simple request using the same model
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        test_payload = {
            "model": GROQ_MODEL,  # Use the same 70b model for consistency
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=test_payload, timeout=15)
        
        if response.status_code == 401:
            raise ValueError(
                "⚠️ API key is invalid or expired!\n\n"
                "Please get a new key at: https://console.groq.com/keys\n"
                "Then update your .streamlit/secrets.toml file"
            )
        elif response.status_code == 429:
            print("⚠️ Rate limited during test, but key is valid")
        
        response.raise_for_status()
        print(f"✅ Groq API key verified with {GROQ_MODEL} - Ready!")
        return True
        
    except requests.exceptions.RequestException as e:
        if "401" in str(e):
            raise ValueError(
                "⚠️ API key authentication failed!\n\n"
                "Get a new key at: https://console.groq.com/keys"
            )
        print(f"⚠️ Could not verify API key: {e}")
        print("✅ Proceeding anyway - key format looks correct")
        return True


def call_llm(prompt: str, max_tokens: int = 3000, temperature: float = 0.1) -> str:
    """Call Groq API with smart rate limit handling for accurate 70b model."""
    global LAST_REQUEST_TIME
    import time
    
    api_key = get_api_key()
    
    if not api_key:
        return json.dumps({"error": "API key not configured"})
    
    # Get selected model from Streamlit session state
    selected_model = GROQ_MODEL  # Default to 70b
    try:
        import streamlit as st
        if 'selected_model' in st.session_state:
            selected_model = st.session_state['selected_model']
    except:
        pass
    
    # Smart rate limiting: wait between requests to avoid 429 errors
    current_time = time.time()
    time_since_last = current_time - LAST_REQUEST_TIME
    
    if time_since_last < MIN_REQUEST_INTERVAL:
        wait_time = MIN_REQUEST_INTERVAL - time_since_last
        print(f"⏳ Rate limit protection: waiting {wait_time:.1f}s...")
        time.sleep(wait_time)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": selected_model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert HR analyst and ATS system. You must respond with valid JSON only. Be accurate and extract only information that is explicitly stated. Do not hallucinate or assume information."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.9
    }
    
    # Retry logic for rate limits
    max_retries = 4
    retry_delays = [5, 15, 30, 60]  # Progressive delays
    
    for attempt in range(max_retries):
        try:
            LAST_REQUEST_TIME = time.time()
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=120)
            
            # Check for authentication error (401)
            if response.status_code == 401:
                return json.dumps({
                    "error": "❌ Invalid API Key (401 Unauthorized)\n\n"
                             "Please check your GROQ_API_KEY:\n"
                             "1. Go to https://console.groq.com/keys\n"
                             "2. Create a new API key\n"
                             "3. Update .streamlit/secrets.toml with:\n"
                             '   GROQ_API_KEY = "gsk_your_new_key_here"'
                })
            
            # Check for rate limit (429 error)
            if response.status_code == 429:
                wait_time = retry_delays[attempt] if attempt < len(retry_delays) else 60
                
                # Try to get retry-after header
                retry_after = response.headers.get('retry-after')
                if retry_after:
                    try:
                        wait_time = min(int(retry_after) + 2, 90)  # Add buffer, cap at 90s
                    except:
                        pass
                
                print(f"⚠️ Rate limited. Waiting {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                
                # Show warning in Streamlit
                try:
                    import streamlit as st
                    st.warning(f"⏳ Rate limited. Waiting {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                except:
                    pass
                
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"⏱️ Timeout. Retrying... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(10)
                continue
            return json.dumps({"error": "Request timed out. The 70b model may be slow. Please try again."})
            
        except requests.exceptions.RequestException as e:
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                if attempt < max_retries - 1:
                    wait_time = retry_delays[attempt]
                    print(f"⚠️ Rate limited. Waiting {wait_time} seconds...")
                    try:
                        import streamlit as st
                        st.warning(f"⏳ Rate limited. Waiting {wait_time} seconds...")
                    except:
                        pass
                    time.sleep(wait_time)
                    continue
                return json.dumps({"error": "Rate limit exceeded. Please wait 2 minutes and try again."})
            return json.dumps({"error": f"API request failed: {error_str}"})
            
        except (KeyError, IndexError) as e:
            return json.dumps({"error": f"Invalid API response: {str(e)}"})
    
    return json.dumps({"error": "Rate limit exceeded after retries. Please wait 2 minutes and try again."})


def clean_json_response(response: str) -> str:
    """Extract JSON from LLM response."""
    if not response:
        return "{}"
    
    cleaned = response.strip()
    
    # Remove markdown code blocks
    if "```" in cleaned:
        cleaned = re.sub(r'```json?\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)
    
    # Find JSON object
    start = cleaned.find('{')
    end = cleaned.rfind('}') + 1
    
    if start != -1 and end > start:
        json_str = cleaned[start:end]
        # Fix common JSON issues
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        return json_str
    
    return "{}"


def safe_json_parse(response: str, default: dict = None) -> dict:
    """Safely parse JSON from LLM response."""
    try:
        cleaned = clean_json_response(response)
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        try:
            fixed = cleaned.replace("'", '"')
            return json.loads(fixed)
        except:
            return default or {"error": f"JSON parse failed: {e}", "raw": response[:500]}


# ============ STRICT RESUME PARSER ============

def parse_resume_detailed(resume_text: str) -> dict:
    """Parse resume with STRICT extraction - only extract what's explicitly stated."""
    
    prompt = f"""You are an expert resume parser. Extract ONLY information that is EXPLICITLY written in the resume.

CRITICAL RULES:
1. ONLY extract information that is EXPLICITLY STATED in the resume
2. If something is NOT mentioned, use null or "Not mentioned"
3. DO NOT assume or infer anything
4. For education, extract EXACTLY what is written (if it says "B.Sc" don't write "B.Tech")
5. For skills, list ONLY skills explicitly mentioned

RESUME TEXT:
{resume_text}

Return ONLY valid JSON:
{{
    "personal_info": {{
        "name": "Extract exact name or null",
        "email": "Extract exact email or null",
        "phone": "Extract exact phone or null",
        "location": "Extract exact location or null"
    }},
    "experience_summary": {{
        "total_years": "Calculate from work history",
        "level": "Fresher/Junior/Mid/Senior/Lead based on years",
        "currently_employed": true,
        "current_company": "Name or null",
        "current_role": "Title or null"
    }},
    "work_history": [
        {{
            "company": "Exact company name",
            "role": "Exact job title",
            "duration": "Start - End as written",
            "achievements": ["List exactly as written"],
            "technologies": ["List only technologies mentioned"]
        }}
    ],
    "education": [
        {{
            "degree": "EXACT degree as written (B.Sc, BCA, B.Tech, etc.)",
            "field": "Field of study",
            "institution": "Exact institution name",
            "year": "Graduation year",
            "grade": "CGPA/Percentage if mentioned or null"
        }}
    ],
    "skills": {{
        "technical": ["Only explicitly listed skills"],
        "tools": ["Only explicitly listed tools"],
        "certifications": ["Only if mentioned"]
    }},
    "additional_info": {{
        "notice_period": "If mentioned or null",
        "current_ctc": "If mentioned or null",
        "expected_ctc": "If mentioned or null"
    }}
}}"""

    response = call_llm(prompt, max_tokens=2500, temperature=0.1)
    return safe_json_parse(response)


# ============ STRICT JD PARSER ============

def parse_job_description_detailed(jd_text: str) -> dict:
    """Parse JD with strict extraction."""
    
    prompt = f"""You are an expert JD parser. Extract ONLY what is EXPLICITLY stated.

JOB DESCRIPTION:
{jd_text}

Return ONLY valid JSON:
{{
    "job_info": {{
        "title": "Exact title or null",
        "company": "Exact company name or null",
        "location": "Exact location or null",
        "work_mode": "Remote/Hybrid/Onsite if mentioned",
        "employment_type": "Full-time/Part-time/Contract"
    }},
    "requirements": {{
        "experience_min": 0,
        "experience_max": 0,
        "experience_text": "Exact text like '3-5 years'",
        "education_required": "Exact education requirement",
        "must_have_skills": ["List required skills"],
        "good_to_have_skills": ["List nice-to-have skills"],
        "responsibilities": ["Key responsibilities"]
    }},
    "compensation": {{
        "salary_mentioned": true,
        "salary_text": "Exact text or null"
    }}
}}"""

    response = call_llm(prompt, max_tokens=2000, temperature=0.1)
    return safe_json_parse(response)


# ============ ACCURATE ATS MATCH SCORE ============

def calculate_match_score_detailed(jd_text: str, resume_text: str) -> dict:
    """Calculate ATS match with DETAILED positive and negative evidence."""
    
    prompt = f"""You are an ATS system. Analyze the match between JD and Resume with SPECIFIC EVIDENCE.

CRITICAL RULES:
1. For each skill match, quote the EXACT text from both JD and Resume
2. For missing skills, list ONLY skills required in JD but NOT found in Resume
3. Calculate scores based on ACTUAL matches, not assumptions
4. Be STRICT - if a skill is not explicitly mentioned in resume, it's missing

SCORING WEIGHTS:
- Skills: 40%
- Experience: 25%
- Education: 15%
- Responsibilities: 15%
- Culture: 5%

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Return ONLY valid JSON:
{{
    "match_summary": {{
        "overall_score": 75,
        "grade": "B+",
        "recommendation": "RECOMMEND",
        "confidence": "High",
        "one_line_summary": "Brief accurate summary"
    }},
    "scoring_breakdown": {{
        "skills_score": {{"score": 70, "weight": 40, "matched_count": 6, "required_count": 10}},
        "experience_score": {{"score": 80, "weight": 25, "jd_requires": "3-5 years", "candidate_has": "4 years"}},
        "education_score": {{"score": 70, "weight": 15, "jd_requires": "Bachelor's", "candidate_has": "B.Sc"}},
        "responsibilities_score": {{"score": 65, "weight": 15}},
        "culture_score": {{"score": 70, "weight": 5}}
    }},
    "positive_matches": [
        {{
            "category": "Skill Match",
            "item": "Python",
            "jd_text": "Quote exact JD requirement",
            "resume_text": "Quote exact resume mention",
            "match_quality": "Full",
            "points": "+4"
        }}
    ],
    "negative_matches": [
        {{
            "category": "Missing Skill",
            "item": "Tableau",
            "jd_text": "Quote exact JD requirement",
            "resume_text": "NOT FOUND in resume",
            "impact": "High",
            "points": "-5",
            "can_learn": "2-4 weeks"
        }}
    ],
    "skill_analysis": {{
        "matched_skills": [{{"skill": "Python", "resume_evidence": "Found in skills"}}],
        "missing_skills": [{{"skill": "Tableau", "importance": "Must-have", "learnability": "2-4 weeks"}}]
    }},
    "hiring_recommendation": {{
        "decision": "RECOMMEND FOR INTERVIEW",
        "priority": "High",
        "reasoning": "Detailed reasoning based on analysis",
        "interview_focus": ["Areas to probe"]
    }}
}}

IMPORTANT: Quote EXACT text from JD and Resume. If resume says B.Sc, don't say B.Tech."""

    response = call_llm(prompt, max_tokens=3500, temperature=0.1)
    result = safe_json_parse(response)
    
    # Ensure consistent grades based on score
    if "match_summary" in result:
        score = result["match_summary"].get("overall_score", 0)
        if isinstance(score, str):
            try:
                score = int(score.replace('%', ''))
            except:
                score = 70
        
        if score >= 85:
            result["match_summary"]["recommendation"] = "STRONGLY RECOMMEND"
            result["match_summary"]["grade"] = "A"
        elif score >= 75:
            result["match_summary"]["recommendation"] = "RECOMMEND"
            result["match_summary"]["grade"] = "B+"
        elif score >= 65:
            result["match_summary"]["recommendation"] = "CONSIDER"
            result["match_summary"]["grade"] = "B"
        elif score >= 55:
            result["match_summary"]["recommendation"] = "CONSIDER WITH RESERVATIONS"
            result["match_summary"]["grade"] = "C"
        else:
            result["match_summary"]["recommendation"] = "NOT RECOMMENDED"
            result["match_summary"]["grade"] = "D"
    
    return result


# ============ INTERVIEW QUESTIONS ============

def generate_interview_questions_detailed(jd_text: str, resume_text: str, match_result: dict = None) -> dict:
    """Generate tailored interview questions."""
    
    concerns = []
    if match_result and "concerns" in match_result:
        concerns = [c.get("concern", "") for c in match_result.get("concerns", [])[:3]]
    
    concerns_text = ", ".join(concerns) if concerns else "General assessment needed"
    
    prompt = f"""You are a senior interviewer. Generate interview questions based on ACTUAL JD and Resume.

AREAS TO PROBE: {concerns_text}

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Return ONLY valid JSON:
{{
    "interview_plan": {{
        "duration": "60-90 minutes",
        "difficulty": "Based on role level",
        "focus_areas": ["Key areas to assess"]
    }},
    "technical_questions": [
        {{
            "question": "Specific question based on JD",
            "tests": "What skill it tests",
            "difficulty": "Easy/Medium/Hard",
            "why_asking": "Based on JD requirement",
            "expected_answer": ["Key points"],
            "green_flags": ["Good signs"],
            "red_flags": ["Warning signs"]
        }}
    ],
    "experience_questions": [
        {{
            "question": "About specific resume claim",
            "validates": "What claim from resume",
            "probing_questions": ["Follow-up questions"]
        }}
    ],
    "gap_probing_questions": [
        {{
            "gap": "Specific skill gap identified",
            "question": "How to assess",
            "acceptable_answers": ["What's acceptable"]
        }}
    ],
    "behavioral_questions": [
        {{
            "question": "Behavioral question",
            "competency": "What it assesses",
            "look_for": ["What to look for"]
        }}
    ],
    "scorecard": {{
        "criteria": [
            {{"name": "Technical Skills", "weight": 30}},
            {{"name": "Problem Solving", "weight": 25}},
            {{"name": "Experience", "weight": 20}},
            {{"name": "Communication", "weight": 15}},
            {{"name": "Culture Fit", "weight": 10}}
        ],
        "passing_score": "3.5/5 average"
    }}
}}"""

    response = call_llm(prompt, max_tokens=3000, temperature=0.2)
    return safe_json_parse(response)


# ============ REALISTIC SALARY ANALYSIS ============

def recommend_salary_detailed(jd_text: str, resume_text: str) -> dict:
    """Provide salary recommendation based ONLY on resume information."""
    
    prompt = f"""You are a compensation analyst for Indian tech companies. Analyze salary based ONLY on what's in the resume.

CRITICAL RULES:
1. ONLY apply premium factors that are EXPLICITLY mentioned in resume
2. If education institution is not IIT/NIT/BITS, DO NOT add education premium
3. If current CTC is mentioned, use it. If NOT mentioned, state "Not provided"
4. DO NOT hallucinate or assume information

INDIAN TECH SALARY BENCHMARKS 2024-25 (CTC in LPA):
- Fresher (0-1 yr): 3-6 LPA (service), 6-12 LPA (product)
- Junior (1-3 yrs): 5-10 LPA (service), 10-18 LPA (product)
- Mid (3-5 yrs): 8-15 LPA (service), 15-25 LPA (product)
- Senior (5-8 yrs): 12-22 LPA (service), 22-40 LPA (product)
- Lead (8-12 yrs): 18-30 LPA (service), 35-55 LPA (product)

PREMIUM FACTORS (ONLY if explicitly in resume):
- IIT/NIT/BITS/IIIT education: +10-15%
- FAANG/Top startup current company: +15-25%
- Niche skills (ML/AI/Blockchain): +15-30%
- AWS/GCP/Azure certifications: +5-10%

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Return ONLY valid JSON:
{{
    "candidate_profile": {{
        "name": "From resume",
        "total_experience": "Calculate from resume",
        "level": "Fresher/Junior/Mid/Senior/Lead",
        "current_company": "From resume or Not mentioned",
        "current_ctc": "ONLY if mentioned, else 'Not provided'",
        "expected_ctc": "ONLY if mentioned, else 'Not provided'",
        "location": "From resume"
    }},
    "job_info": {{
        "title": "From JD",
        "company_type": "Product/Service/Startup",
        "location": "From JD",
        "budget_range": "From JD or Not mentioned"
    }},
    "market_rate_calculation": {{
        "base_rate": {{
            "range": "X-Y LPA",
            "basis": "Based on experience and company type"
        }},
        "applicable_premiums": [
            {{
                "factor": "Only factors FOUND in resume",
                "evidence": "Quote exact text from resume",
                "premium_percent": 10
            }}
        ],
        "premiums_NOT_applicable": [
            {{
                "factor": "Premium that does NOT apply",
                "reason": "Not mentioned in resume / Institution is not premier"
            }}
        ],
        "total_premium_percent": 0,
        "adjusted_market_rate": "X-Y LPA"
    }},
    "salary_recommendation": {{
        "minimum": "X LPA",
        "recommended": "Y LPA",
        "maximum": "Z LPA",
        "stretch": "W LPA"
    }},
    "offer_strategy": {{
        "initial_offer": "X LPA",
        "target_close": "Y LPA",
        "walk_away": "Z LPA"
    }},
    "hike_analysis": {{
        "current_ctc": "From resume or 'Not provided'",
        "recommended_offer": "X LPA",
        "hike_percent": "Y% or 'Cannot calculate'",
        "assessment": "Assessment of the offer"
    }},
    "negotiation": {{
        "candidate_leverage": "High/Medium/Low",
        "leverage_reasons": ["Based on actual resume"],
        "tips": ["Negotiation tips"]
    }},
    "recommendation_summary": {{
        "final_recommendation": "X LPA",
        "confidence": "High/Medium/Low",
        "key_factors": ["Key factors"],
        "caveats": ["Important notes"]
    }}
}}

IMPORTANT: If education is not from IIT/NIT/BITS/IIIT, explicitly state "Education premium NOT applicable"."""

    response = call_llm(prompt, max_tokens=2500, temperature=0.1)
    result = safe_json_parse(response)
    
    if "error" in result and "raw" in result:
        return {
            "error": "Could not parse salary analysis",
            "candidate_profile": {"current_ctc": "Not provided", "expected_ctc": "Not provided"},
            "salary_recommendation": {"minimum": "N/A", "recommended": "N/A", "maximum": "N/A", "stretch": "N/A"},
            "recommendation_summary": {"final_recommendation": "N/A", "reasoning": "Please try again"}
        }
    
    return result


# ============ COMPREHENSIVE HIRING REPORT ============

def generate_hiring_report_detailed(jd_text: str, resume_text: str, match_result: dict, salary_result: dict = None) -> dict:
    """Generate comprehensive hiring report with ACCURATE information."""
    
    # Extract data from match result
    ats_score = 70
    grade = "B"
    recommendation = "CONSIDER"
    
    if match_result and "match_summary" in match_result:
        ats_score = match_result["match_summary"].get("overall_score", 70)
        grade = match_result["match_summary"].get("grade", "B")
        recommendation = match_result["match_summary"].get("recommendation", "CONSIDER")
    
    # Get salary info
    salary_text = "Not analyzed"
    if salary_result:
        sal_rec = salary_result.get("salary_recommendation", {})
        if isinstance(sal_rec, dict):
            salary_text = sal_rec.get("recommended", "Not available")
    
    today = datetime.now().strftime("%B %d, %Y")
    
    prompt = f"""You are an HR consultant creating a comprehensive hiring report.

CRITICAL RULES:
1. Use ONLY information from the actual JD and Resume
2. DO NOT add or assume any information not present
3. If education is B.Sc, write B.Sc (not B.Tech)
4. Use the exact values provided below

PRE-CALCULATED VALUES (use these exactly):
- ATS Score: {ats_score}%
- Grade: {grade}
- Recommendation: {recommendation}
- Suggested Salary: {salary_text}

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Return ONLY valid JSON:
{{
    "report_header": {{
        "title": "Candidate Assessment Report",
        "date": "{today}",
        "confidentiality": "Internal Use Only"
    }},
    "executive_summary": {{
        "recommendation": "{recommendation}",
        "ats_score": {ats_score},
        "grade": "{grade}",
        "confidence": "High",
        "verdict": "One line using ACTUAL resume details",
        "key_decision_factors": ["Factor 1", "Factor 2", "Factor 3"]
    }},
    "candidate_profile": {{
        "name": "EXACT name from resume",
        "email": "From resume or Not provided",
        "phone": "From resume or Not provided",
        "location": "From resume",
        "current_company": "From resume",
        "current_role": "From resume",
        "total_experience": "Calculated from resume"
    }},
    "position_details": {{
        "title": "From JD",
        "company": "From JD",
        "location": "From JD"
    }},
    "detailed_assessment": {{
        "skills_assessment": {{"score": 75, "rating": "Good", "matched_skills": [], "missing_skills": []}},
        "experience_assessment": {{"score": 80, "rating": "Good", "analysis": "Details"}},
        "education_assessment": {{
            "score": 70,
            "rating": "Good",
            "required": "What JD requires",
            "candidate_has": "EXACT education from resume",
            "institution": "EXACT institution name",
            "is_premier_institution": false
        }},
        "culture_fit_assessment": {{"score": 70, "rating": "Good"}}
    }},
    "strengths": [
        {{"strength": "Specific strength", "evidence": "From resume", "relevance_to_role": "Why it matters"}}
    ],
    "concerns": [
        {{"concern": "Specific concern", "evidence": "What's missing", "severity": "High/Medium/Low", "mitigation": "How to address"}}
    ],
    "interview_recommendation": {{
        "should_interview": true,
        "priority": "High/Medium/Low",
        "timeline": "Within 1 week",
        "key_areas_to_probe": ["Area 1", "Area 2"]
    }},
    "compensation_guidance": {{
        "market_rate": "Based on analysis",
        "suggested_offer": "{salary_text}",
        "offer_range": "Min - Max",
        "candidate_expectation": "From resume or Not provided"
    }},
    "risk_assessment": {{
        "overall_risk": "Low/Medium/High",
        "flight_risk": {{"level": "Low", "factors": []}},
        "performance_risk": {{"level": "Low", "factors": []}},
        "culture_risk": {{"level": "Low", "factors": []}}
    }},
    "final_recommendation": {{
        "decision": "{recommendation}",
        "confidence": "High",
        "reasoning": "Comprehensive reasoning using ACTUAL data",
        "next_steps": [{{"action": "Action", "owner": "Owner", "timeline": "When"}}]
    }}
}}"""

    response = call_llm(prompt, max_tokens=3500, temperature=0.1)
    result = safe_json_parse(response)
    
    # Ensure consistency
    if "executive_summary" in result:
        result["executive_summary"]["recommendation"] = recommendation
        result["executive_summary"]["ats_score"] = ats_score
        result["executive_summary"]["grade"] = grade
    
    if "final_recommendation" in result:
        result["final_recommendation"]["decision"] = recommendation
    
    return result
