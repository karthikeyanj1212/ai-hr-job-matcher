"""
LLM Utilities v3.0 - Strict Accuracy Version
- Only extracts what's actually in the resume
- Evidence-based ATS scoring with positive/negative matches
- Realistic salary based on extracted data only
- Comprehensive hiring report
"""

import json
import re
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from datetime import datetime

# ============ MODEL CONFIGURATION ============

MODEL_CONFIG = {
    "repo_id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
    "filename": "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    "n_ctx": 8192,
    "n_gpu_layers": 0,
}

llm = None


def initialize_llm(use_gpu: bool = False, gpu_layers: int = 35):
    """Download and initialize the LLM."""
    global llm
    
    if llm is not None:
        return llm
    
    print(f"📥 Downloading model: {MODEL_CONFIG['repo_id']}")
    
    try:
        model_path = hf_hub_download(
            repo_id=MODEL_CONFIG["repo_id"],
            filename=MODEL_CONFIG["filename"]
        )
        
        print("🔄 Loading model...")
        
        llm = Llama(
            model_path=model_path,
            n_ctx=MODEL_CONFIG["n_ctx"],
            n_gpu_layers=gpu_layers if use_gpu else 0,
            n_batch=512,
            verbose=False
        )
        
        print("✅ Model loaded!")
        return llm
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


def call_llm(prompt: str, max_tokens: int = 3000, temperature: float = 0.05) -> str:
    """Generate text using local Llama model with very low temperature for accuracy."""
    global llm
    
    if llm is None:
        initialize_llm()
    
    try:
        response = llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            stop=["</s>", "[/INST]", "Human:", "User:"],
            repeat_penalty=1.1,
            echo=False
        )
        
        return response["choices"][0]["text"].strip()
        
    except Exception as e:
        return json.dumps({"error": str(e)})


def clean_json_response(response: str) -> str:
    """Extract JSON from LLM response."""
    if not response:
        return "{}"
    
    cleaned = response.strip()
    
    if "```" in cleaned:
        cleaned = re.sub(r'```json?\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)
    
    start = cleaned.find('{')
    end = cleaned.rfind('}') + 1
    
    if start != -1 and end > start:
        json_str = cleaned[start:end]
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
    """
    Parse resume with STRICT extraction - only extract what's explicitly stated.
    DO NOT infer or assume anything not written.
    """
    
    prompt = f"""<s>[INST] You are an expert resume parser. Extract ONLY information that is EXPLICITLY written in the resume.

CRITICAL RULES:
1. ONLY extract information that is EXPLICITLY STATED in the resume
2. If something is NOT mentioned, use null or "Not mentioned"
3. DO NOT assume or infer anything
4. DO NOT add information that is not in the resume
5. For education, extract EXACTLY what is written (if it says "B.Sc" don't write "B.Tech")
6. For companies, extract EXACTLY as written
7. For skills, list ONLY skills explicitly mentioned

RESUME TEXT:
{resume_text}

Extract and return ONLY valid JSON:
{{
    "personal_info": {{
        "name": "Extract exact name or null",
        "email": "Extract exact email or null",
        "phone": "Extract exact phone or null",
        "location": "Extract exact location or null",
        "linkedin": "Extract if mentioned or null",
        "github": "Extract if mentioned or null"
    }},
    "experience_summary": {{
        "total_years": "Calculate from work history or extract if stated",
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
            "duration_years": 2.5,
            "location": "If mentioned or null",
            "responsibilities": ["List exactly as written"],
            "achievements": ["List exactly as written with numbers if any"],
            "technologies": ["List only technologies explicitly mentioned"]
        }}
    ],
    "education": [
        {{
            "degree": "EXACT degree as written (B.Sc, BCA, B.Tech, MBA, etc.)",
            "field": "Field of study if mentioned",
            "institution": "Exact institution name",
            "year": "Graduation year if mentioned",
            "grade": "CGPA/Percentage if mentioned or null",
            "is_premier": false
        }}
    ],
    "skills": {{
        "technical": ["Only explicitly listed technical skills"],
        "tools": ["Only explicitly listed tools"],
        "soft_skills": ["Only if explicitly mentioned"],
        "languages": ["Programming languages only if listed"],
        "certifications": ["Only if explicitly mentioned with name"]
    }},
    "additional_info": {{
        "notice_period": "If mentioned or null",
        "current_ctc": "If mentioned or null",
        "expected_ctc": "If mentioned or null",
        "willing_to_relocate": "If mentioned or null"
    }},
    "extraction_confidence": {{
        "completeness": "High/Medium/Low based on info available",
        "missing_fields": ["List important fields not found in resume"]
    }}
}}

IMPORTANT: If the resume says "B.Sc" DO NOT write "B.Tech". Extract EXACTLY what is written.
[/INST]"""

    response = call_llm(prompt, max_tokens=3000, temperature=0.05)
    return safe_json_parse(response)


# ============ STRICT JD PARSER ============

def parse_job_description_detailed(jd_text: str) -> dict:
    """Parse JD with strict extraction."""
    
    prompt = f"""<s>[INST] You are an expert JD parser. Extract ONLY what is EXPLICITLY stated.

JOB DESCRIPTION:
{jd_text}

Return ONLY valid JSON:
{{
    "job_info": {{
        "title": "Exact title or null",
        "company": "Exact company name or null",
        "location": "Exact location or null",
        "work_mode": "Remote/Hybrid/Onsite if mentioned or null",
        "employment_type": "Full-time/Part-time/Contract if mentioned"
    }},
    "requirements": {{
        "experience_min": "Minimum years or 0",
        "experience_max": "Maximum years or null",
        "experience_text": "Exact text like '3-5 years'",
        "education_required": "Exact education requirement as written",
        "must_have_skills": ["List required skills exactly as written"],
        "good_to_have_skills": ["List nice-to-have skills"],
        "responsibilities": ["List key responsibilities"]
    }},
    "compensation": {{
        "salary_mentioned": true,
        "salary_min": "If mentioned or null",
        "salary_max": "If mentioned or null",
        "salary_text": "Exact text or null"
    }}
}}
[/INST]"""

    response = call_llm(prompt, max_tokens=2000, temperature=0.05)
    return safe_json_parse(response)


# ============ ACCURATE ATS MATCH SCORE ============

def calculate_match_score_detailed(jd_text: str, resume_text: str) -> dict:
    """
    Calculate ATS match with DETAILED positive and negative evidence.
    Each point must be backed by specific text from JD and Resume.
    """
    
    prompt = f"""<s>[INST] You are an ATS system. Analyze the match between JD and Resume with SPECIFIC EVIDENCE.

CRITICAL RULES:
1. For each skill match, quote the EXACT text from both JD and Resume
2. For missing skills, list ONLY skills required in JD but NOT found in Resume
3. Calculate scores based on ACTUAL matches, not assumptions
4. Be STRICT - if a skill is not explicitly mentioned in resume, it's missing

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Analyze and return JSON:
{{
    "match_summary": {{
        "overall_score": 75,
        "grade": "B+",
        "recommendation": "RECOMMEND",
        "confidence": "High",
        "one_line_summary": "Brief accurate summary"
    }},
    "scoring_breakdown": {{
        "skills_score": {{
            "score": 70,
            "weight": 40,
            "weighted_score": 28,
            "matched_count": 6,
            "required_count": 10,
            "calculation": "6/10 skills matched = 60%, weighted 40% = 24 points"
        }},
        "experience_score": {{
            "score": 80,
            "weight": 25,
            "weighted_score": 20,
            "jd_requires": "3-5 years",
            "candidate_has": "4 years",
            "assessment": "Within required range"
        }},
        "education_score": {{
            "score": 70,
            "weight": 15,
            "weighted_score": 10.5,
            "jd_requires": "Bachelor's degree",
            "candidate_has": "B.Sc in Computer Science",
            "assessment": "Meets requirement"
        }},
        "responsibilities_score": {{
            "score": 65,
            "weight": 15,
            "weighted_score": 9.75,
            "assessment": "Partial alignment"
        }},
        "culture_score": {{
            "score": 70,
            "weight": 5,
            "weighted_score": 3.5
        }},
        "total_weighted_score": 71.75
    }},
    "positive_matches": [
        {{
            "category": "Skill Match",
            "item": "Python",
            "jd_text": "Quote exact JD requirement",
            "resume_text": "Quote exact resume mention",
            "match_quality": "Full/Partial",
            "points": "+4"
        }},
        {{
            "category": "Experience Match",
            "item": "Years of experience",
            "jd_text": "Requires 3-5 years",
            "resume_text": "Has 4 years total experience",
            "match_quality": "Full",
            "points": "+10"
        }}
    ],
    "negative_matches": [
        {{
            "category": "Missing Skill",
            "item": "Tableau",
            "jd_text": "Quote exact JD requirement",
            "resume_text": "NOT FOUND in resume",
            "impact": "High/Medium/Low",
            "points": "-5",
            "can_learn": "Yes, 2-4 weeks"
        }},
        {{
            "category": "Experience Gap",
            "item": "Team leadership",
            "jd_text": "Quote requirement if any",
            "resume_text": "No leadership mentioned",
            "impact": "Medium",
            "points": "-3"
        }}
    ],
    "skill_analysis": {{
        "matched_skills": [
            {{
                "skill": "Python",
                "jd_requirement": "Python programming required",
                "resume_evidence": "Python mentioned in skills section",
                "proficiency": "If mentioned or Unknown"
            }}
        ],
        "missing_skills": [
            {{
                "skill": "Tableau",
                "jd_requirement": "Tableau experience required",
                "importance": "Must-have/Nice-to-have",
                "learnability": "2-4 weeks"
            }}
        ],
        "extra_skills": ["Skills in resume but not in JD"]
    }},
    "experience_analysis": {{
        "jd_requirement": {{
            "min_years": 3,
            "max_years": 5,
            "specific_experience": ["List specific experience required"]
        }},
        "candidate_experience": {{
            "total_years": 4,
            "relevant_years": 3,
            "companies": ["Company names"],
            "relevant_experience": ["Specific relevant experience"]
        }},
        "gap_analysis": "Analysis of any experience gaps"
    }},
    "education_analysis": {{
        "jd_requirement": "Exact requirement from JD",
        "candidate_has": "Exact education from resume",
        "is_match": true,
        "notes": "Any relevant notes"
    }},
    "strengths": [
        {{
            "strength": "Specific strength",
            "evidence": "Quote from resume",
            "relevance": "Why it matters for this role"
        }}
    ],
    "concerns": [
        {{
            "concern": "Specific concern",
            "evidence": "What's missing or weak",
            "severity": "High/Medium/Low",
            "mitigation": "How it could be addressed"
        }}
    ],
    "hiring_recommendation": {{
        "decision": "RECOMMEND/CONSIDER/NOT RECOMMEND",
        "priority": "High/Medium/Low",
        "reasoning": "Detailed reasoning based on analysis",
        "interview_focus": ["Areas to probe in interview"]
    }}
}}

IMPORTANT: 
- Quote EXACT text from JD and Resume for each match
- Only list skills as missing if they are REQUIRED in JD but NOT in Resume
- Be accurate with education - if resume says B.Sc, don't say B.Tech
[/INST]"""

    response = call_llm(prompt, max_tokens=4000, temperature=0.05)
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
    """Generate tailored interview questions based on actual JD and Resume content."""
    
    # Get concerns from match result if available
    concerns = []
    if match_result and "concerns" in match_result:
        concerns = [c.get("concern", "") for c in match_result.get("concerns", [])[:3]]
    
    concerns_text = ", ".join(concerns) if concerns else "General assessment needed"
    
    prompt = f"""<s>[INST] You are a senior interviewer. Generate questions based on ACTUAL JD requirements and Resume content.

AREAS TO PROBE: {concerns_text}

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Return JSON:
{{
    "interview_plan": {{
        "duration": "60-90 minutes",
        "difficulty": "Based on role level",
        "focus_areas": ["Based on JD requirements and resume gaps"]
    }},
    "technical_questions": [
        {{
            "question": "Specific question based on JD requirement",
            "tests": "What skill/knowledge it tests",
            "difficulty": "Easy/Medium/Hard",
            "time": "5-10 minutes",
            "why_asking": "Based on JD requirement or resume claim",
            "expected_answer": ["Key points to look for"],
            "followups": ["Follow-up questions"],
            "green_flags": ["Good signs"],
            "red_flags": ["Warning signs"]
        }}
    ],
    "experience_questions": [
        {{
            "question": "About specific resume claim",
            "validates": "What claim from resume",
            "probing_questions": ["Dig deeper questions"],
            "ownership_signals": ["Signs of real ownership"],
            "warning_signs": ["Signs of exaggeration"]
        }}
    ],
    "gap_probing_questions": [
        {{
            "gap": "Specific skill/experience gap identified",
            "question": "How to assess if candidate can fill gap",
            "acceptable_answers": ["What would be acceptable"],
            "concerning_answers": ["What would be concerning"]
        }}
    ],
    "behavioral_questions": [
        {{
            "question": "Behavioral question",
            "competency": "What it assesses",
            "look_for": ["What to look for in answer"]
        }}
    ],
    "scorecard": {{
        "criteria": [
            {{"name": "Technical Skills", "weight": 30}},
            {{"name": "Problem Solving", "weight": 25}},
            {{"name": "Relevant Experience", "weight": 20}},
            {{"name": "Communication", "weight": 15}},
            {{"name": "Culture Fit", "weight": 10}}
        ],
        "passing_score": "3.5/5 average",
        "strong_hire": "4.0/5 with no score below 3"
    }}
}}
[/INST]"""

    response = call_llm(prompt, max_tokens=3500, temperature=0.15)
    return safe_json_parse(response)


# ============ REALISTIC SALARY ANALYSIS ============

def recommend_salary_detailed(jd_text: str, resume_text: str) -> dict:
    """
    Provide salary recommendation based ONLY on information in resume.
    DO NOT assume premium factors not mentioned in resume.
    """
    
    prompt = f"""<s>[INST] You are a compensation analyst. Analyze salary based ONLY on what's in the resume.

CRITICAL RULES:
1. ONLY apply premium factors that are EXPLICITLY mentioned in resume
2. If education institution is not IIT/NIT/BITS, DO NOT add education premium
3. If current CTC is mentioned, use it. If NOT mentioned, state "Not provided"
4. Base salary on ACTUAL experience and skills in resume
5. DO NOT hallucinate or assume information

INDIAN TECH SALARY BENCHMARKS 2024-25 (CTC in LPA):
- Fresher (0-1 yr): 3-6 LPA (service), 6-12 LPA (product/startup)
- Junior (1-3 yrs): 5-10 LPA (service), 10-18 LPA (product)
- Mid (3-5 yrs): 8-15 LPA (service), 15-25 LPA (product)
- Senior (5-8 yrs): 12-22 LPA (service), 22-40 LPA (product)
- Lead (8-12 yrs): 18-30 LPA (service), 35-55 LPA (product)
- Manager (12+ yrs): 25-40 LPA (service), 45-70 LPA (product)

PREMIUM FACTORS (ONLY if explicitly in resume):
- IIT/NIT/BITS/IIIT education: +10-15% (ONLY if institution name matches)
- FAANG/Top startup current company: +15-25%
- Niche skills (ML/AI/Blockchain): +15-30%
- AWS/GCP/Azure certifications: +5-10%
- Management experience: +10-15%

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Analyze and return JSON:
{{
    "candidate_profile": {{
        "name": "From resume or Unknown",
        "total_experience": "Calculate from resume",
        "level": "Fresher/Junior/Mid/Senior/Lead",
        "current_company": "From resume or Not mentioned",
        "current_role": "From resume or Not mentioned",
        "current_ctc": "ONLY if mentioned in resume, else 'Not provided'",
        "expected_ctc": "ONLY if mentioned in resume, else 'Not provided'",
        "location": "From resume or Not mentioned",
        "notice_period": "ONLY if mentioned, else 'Not mentioned'"
    }},
    "job_info": {{
        "title": "From JD",
        "company": "From JD or Not mentioned",
        "company_type": "Product/Service/Startup - infer from JD",
        "location": "From JD",
        "budget_range": "From JD or Not mentioned"
    }},
    "market_rate_calculation": {{
        "base_rate": {{
            "range": "X-Y LPA",
            "basis": "Based on X years experience in Y type company"
        }},
        "applicable_premiums": [
            {{
                "factor": "Only factors FOUND in resume",
                "evidence": "Quote exact text from resume proving this",
                "premium_percent": 10,
                "premium_amount": "X LPA"
            }}
        ],
        "premiums_NOT_applicable": [
            {{
                "factor": "Premium that does NOT apply",
                "reason": "Not mentioned in resume / Institution is not premier / etc."
            }}
        ],
        "total_premium_percent": 15,
        "adjusted_market_rate": "X-Y LPA"
    }},
    "salary_recommendation": {{
        "minimum": "X LPA",
        "recommended": "Y LPA",
        "maximum": "Z LPA",
        "stretch": "W LPA (only for exceptional negotiation)"
    }},
    "offer_strategy": {{
        "initial_offer": "X LPA",
        "target_close": "Y LPA",
        "walk_away": "Z LPA",
        "reasoning": "Based on market rate and candidate profile"
    }},
    "hike_analysis": {{
        "current_ctc": "From resume or 'Not provided'",
        "recommended_offer": "X LPA",
        "hike_percent": "Y% or 'Cannot calculate - current CTC not provided'",
        "market_standard": "15-25% for lateral, 25-40% for promotion",
        "assessment": "Assessment of the offer"
    }},
    "negotiation": {{
        "candidate_leverage": "High/Medium/Low",
        "leverage_reasons": ["Based on actual resume strengths"],
        "company_leverage": "High/Medium/Low",
        "company_reasons": ["Based on JD and market"],
        "tips": ["Negotiation tips"]
    }},
    "recommendation_summary": {{
        "final_recommendation": "X LPA",
        "confidence": "High/Medium/Low",
        "key_factors": ["Factors that determined this recommendation"],
        "caveats": ["Any important notes or assumptions"]
    }}
}}

IMPORTANT: 
- If education is not from IIT/NIT/BITS/IIIT, explicitly state "Education premium NOT applicable - [Institution name] is not a premier institution"
- If current CTC is not mentioned, state clearly "Current CTC not provided in resume"
- Only list premiums that have EVIDENCE in the resume
[/INST]"""

    response = call_llm(prompt, max_tokens=3000, temperature=0.05)
    result = safe_json_parse(response)
    
    # Ensure we have proper structure even if parsing partially fails
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
    """
    Generate comprehensive hiring report with ACCURATE information.
    All details must come from actual JD and Resume content.
    """
    
    # Extract data from match result
    ats_score = 70
    grade = "B"
    recommendation = "CONSIDER"
    
    if match_result and "match_summary" in match_result:
        ats_score = match_result["match_summary"].get("overall_score", 70)
        grade = match_result["match_summary"].get("grade", "B")
        recommendation = match_result["match_summary"].get("recommendation", "CONSIDER")
    
    # Get positive and negative matches
    positive_matches = []
    negative_matches = []
    if match_result:
        positive_matches = match_result.get("positive_matches", [])[:5]
        negative_matches = match_result.get("negative_matches", [])[:5]
    
    # Get salary info
    salary_text = "Not analyzed"
    if salary_result:
        sal_rec = salary_result.get("salary_recommendation", {})
        if isinstance(sal_rec, dict):
            salary_text = sal_rec.get("recommended", "Not available")
    
    today = datetime.now().strftime("%B %d, %Y")
    
    prompt = f"""<s>[INST] You are an HR consultant creating a comprehensive hiring report.

CRITICAL RULES:
1. Use ONLY information from the actual JD and Resume
2. DO NOT add or assume any information not present
3. If education is B.Sc, write B.Sc (not B.Tech)
4. Use the exact ATS score and recommendation provided
5. Be specific with evidence from resume

PRE-CALCULATED VALUES (use these exactly):
- ATS Score: {ats_score}%
- Grade: {grade}
- Recommendation: {recommendation}
- Suggested Salary: {salary_text}

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Generate comprehensive report as JSON:
{{
    "report_header": {{
        "title": "Candidate Assessment Report",
        "date": "{today}",
        "confidentiality": "Internal Use Only",
        "report_version": "v3.0"
    }},
    "executive_summary": {{
        "recommendation": "{recommendation}",
        "ats_score": {ats_score},
        "grade": "{grade}",
        "confidence": "High/Medium/Low",
        "verdict": "One line summary using ACTUAL resume details",
        "key_decision_factors": [
            "Factor 1 with evidence from resume",
            "Factor 2 with evidence from resume",
            "Factor 3 with evidence from resume"
        ]
    }},
    "candidate_profile": {{
        "name": "EXACT name from resume",
        "email": "EXACT email from resume or Not provided",
        "phone": "EXACT phone from resume or Not provided",
        "location": "EXACT location from resume or Not provided",
        "current_company": "EXACT company from resume",
        "current_role": "EXACT role from resume",
        "total_experience": "Calculated from resume",
        "experience_level": "Junior/Mid/Senior based on years"
    }},
    "position_details": {{
        "title": "EXACT title from JD",
        "company": "EXACT company from JD or Not mentioned",
        "department": "From JD or Not specified",
        "location": "From JD",
        "level": "From JD"
    }},
    "detailed_assessment": {{
        "skills_assessment": {{
            "score": 75,
            "rating": "Good/Strong/Weak",
            "matched_skills": ["List actual matched skills"],
            "missing_skills": ["List actual missing skills"],
            "analysis": "Detailed analysis with evidence"
        }},
        "experience_assessment": {{
            "score": 80,
            "rating": "Good/Strong/Weak",
            "required": "What JD requires",
            "candidate_has": "What candidate actually has",
            "relevant_experience": ["Specific relevant experience from resume"],
            "analysis": "Detailed analysis"
        }},
        "education_assessment": {{
            "score": 70,
            "rating": "Good/Strong/Weak",
            "required": "What JD requires",
            "candidate_has": "EXACT education from resume (B.Sc/BCA/B.Tech etc.)",
            "institution": "EXACT institution name",
            "is_premier_institution": false,
            "analysis": "Assessment of education fit"
        }},
        "culture_fit_assessment": {{
            "score": 70,
            "rating": "Good/Strong/Weak",
            "indicators": ["Based on resume content"],
            "analysis": "Assessment based on available info"
        }}
    }},
    "strengths": [
        {{
            "strength": "Specific strength",
            "evidence": "Quote or reference from resume",
            "relevance_to_role": "Why it matters for this job"
        }}
    ],
    "concerns": [
        {{
            "concern": "Specific concern",
            "evidence": "What's missing or gap identified",
            "severity": "High/Medium/Low",
            "impact": "How it affects candidacy",
            "mitigation": "How it could be addressed"
        }}
    ],
    "interview_recommendation": {{
        "should_interview": true,
        "priority": "High/Medium/Low",
        "timeline": "Recommended timeline",
        "interview_rounds": [
            {{"round": 1, "type": "Screening", "duration": "30 min", "focus": "Background verification"}},
            {{"round": 2, "type": "Technical", "duration": "60 min", "focus": "Technical skills"}},
            {{"round": 3, "type": "Manager", "duration": "45 min", "focus": "Experience deep dive"}},
            {{"round": 4, "type": "HR", "duration": "30 min", "focus": "Culture fit"}}
        ],
        "key_areas_to_probe": [
            "Specific area based on identified gaps"
        ],
        "red_flags_to_watch": [
            "Specific things to verify"
        ]
    }},
    "compensation_guidance": {{
        "market_rate": "Based on analysis",
        "suggested_offer": "{salary_text}",
        "offer_range": "Min - Max",
        "candidate_expectation": "From resume or Not provided",
        "negotiation_room": "Assessment of flexibility"
    }},
    "risk_assessment": {{
        "overall_risk": "Low/Medium/High",
        "flight_risk": {{
            "level": "Low/Medium/High",
            "factors": ["Based on resume indicators"]
        }},
        "performance_risk": {{
            "level": "Low/Medium/High",
            "factors": ["Based on skill gaps or experience"]
        }},
        "culture_risk": {{
            "level": "Low/Medium/High",
            "factors": ["Based on available information"]
        }}
    }},
    "final_recommendation": {{
        "decision": "{recommendation}",
        "confidence": "High/Medium/Low",
        "reasoning": "Comprehensive reasoning using ACTUAL data from resume and JD. Reference specific skills, experience, and education as they appear in resume.",
        "next_steps": [
            {{"action": "Specific action", "owner": "Who should do it", "timeline": "When"}}
        ]
    }},
    "appendix": {{
        "score_breakdown": {{
            "skills": 75,
            "experience": 80,
            "education": 70,
            "culture": 70,
            "overall": {ats_score}
        }},
        "methodology": "Weighted scoring: Skills 40%, Experience 25%, Education 15%, Responsibilities 15%, Culture 5%"
    }}
}}

CRITICAL: 
- Use EXACT education from resume (if it says B.Sc, write B.Sc not B.Tech)
- Use EXACT company names and roles from resume
- The verdict and reasoning must reference ACTUAL resume content
[/INST]"""

    response = call_llm(prompt, max_tokens=4000, temperature=0.05)
    result = safe_json_parse(response)
    
    # Ensure consistency with provided values
    if "executive_summary" in result:
        result["executive_summary"]["recommendation"] = recommendation
        result["executive_summary"]["ats_score"] = ats_score
        result["executive_summary"]["grade"] = grade
    
    if "final_recommendation" in result:
        result["final_recommendation"]["decision"] = recommendation
    
    return result
