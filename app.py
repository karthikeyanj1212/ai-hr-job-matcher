"""
🎯 HR Job Matcher Pro v1.0
- Strict accuracy - only uses information from actual resume
- Detailed ATS scoring with positive/negative evidence
- Comprehensive hiring report
"""

import streamlit as st
import json
from datetime import datetime

from llm_utils import (
    initialize_llm,
    parse_job_description_detailed,
    parse_resume_detailed,
    calculate_match_score_detailed,
    generate_interview_questions_detailed,
    recommend_salary_detailed,
    generate_hiring_report_detailed
)
from pdf_utils import extract_text_from_file

# ============ PAGE CONFIG ============

st.set_page_config(page_title="HR Job Matcher Pro v1", page_icon="🎯", layout="wide")

# ============ CSS ============

st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; background: linear-gradient(90deg, #1E88E5, #7C4DFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.5rem; }
    .score-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white; text-align: center; margin: 10px 0; }
    .score-big { font-size: 2.5rem; font-weight: bold; }
    .score-label { font-size: 0.9rem; opacity: 0.9; }
    .green-card { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .orange-card { background: linear-gradient(135deg, #f5af19 0%, #f12711 100%); }
    .blue-card { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
    .red-card { background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%); }
    .positive-match { background-color: #E8F5E9; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #4CAF50; }
    .negative-match { background-color: #FFEBEE; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #f44336; }
    .info-box { background-color: #E3F2FD; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #2196F3; }
    .warning-box { background-color: #FFF3E0; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #FF9800; }
    .premium-applicable { background-color: #E8F5E9; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #4CAF50; }
    .premium-not-applicable { background-color: #FFEBEE; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #f44336; }
</style>
""", unsafe_allow_html=True)

# ============ SESSION STATE ============

for key in ['model_loaded', 'global_jd_text', 'global_resume_text', 
            'tab1_result', 'tab2_result', 'tab3_result', 'tab5_result', 'tab6_result']:
    if key not in st.session_state:
        st.session_state[key] = None if 'result' in key else (False if key == 'model_loaded' else "")

@st.cache_resource
def load_model():
    return initialize_llm(use_gpu=False)

def show_retained():
    st.markdown('<div class="info-box">✅ Results retained from previous analysis</div>', unsafe_allow_html=True)

# ============ SAMPLE DATA ============

SAMPLE_JD = """Data Analyst - TechCorp Solutions
Location: Bangalore (Hybrid)
Experience: 2-4 years

Requirements:
- 2-4 years experience in data analysis
- Strong SQL and Python skills
- Experience with Tableau or Power BI
- Excel expertise
- Basic statistics knowledge

Nice-to-have:
- Machine Learning basics
- Cloud experience (AWS/GCP)

Education: Bachelor's degree in any field

Compensation: 8-15 LPA
"""

SAMPLE_RESUME = """RISHI KUMAR
Email: rishi.kumar@email.com | Phone: +91 98765 43210
Location: Bangalore

EXPERIENCE: 3 years

ABC Analytics | Data Analyst | Jan 2022 - Present (2 years)
- Analyzed sales data using SQL and Python
- Created dashboards in Excel
- Automated reports saving 10 hours/week
Technologies: SQL, Python, Excel, MySQL

XYZ Corp | Junior Analyst | Jan 2021 - Dec 2021 (1 year)
- Supported data entry and basic analysis
- Created Excel reports
Technologies: Excel, SQL basics

EDUCATION:
B.Sc Statistics, Mumbai University (2020)
Percentage: 72%

SKILLS: SQL, Python, Excel, MySQL, Basic Statistics

Notice Period: 30 days
Current CTC: 6 LPA
Expected CTC: 9-11 LPA
"""

# ============ SIDEBAR ============

with st.sidebar:
    st.title("🎯 HR Matcher Pro v1.0")
    st.caption("Strict Accuracy Version")
    st.markdown("---")
    
    if st.button("🚀 Load AI Model", type="primary", use_container_width=True):
        with st.spinner("Loading model..."):
            try:
                load_model()
                st.session_state.model_loaded = True
                st.success("✅ Model Ready!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    if st.session_state.model_loaded:
        st.success("✅ Model Loaded")
    else:
        st.warning("⚠️ Model Not Loaded")
    
    st.markdown("---")
    results = sum([1 for k in ['tab1_result', 'tab2_result', 'tab3_result', 'tab5_result', 'tab6_result'] if st.session_state.get(k)])
    st.metric("Analysis Completed", f"{results}/5")
    
    if results > 0:
        if st.button("🗑️ Clear All Results", use_container_width=True):
            for k in ['tab1_result', 'tab2_result', 'tab3_result', 'tab5_result', 'tab6_result']:
                st.session_state[k] = None
            st.rerun()
    
    st.markdown("---")
    st.caption("v1.0 - Strict Accuracy")
    st.caption("• Evidence-based scoring")
    st.caption("• No hallucination")
    st.caption("• Detailed +/- matches")

# ============ HEADER ============

st.markdown('<p class="main-header">🎯 HR Job Matcher Pro</p>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#666;">AI Recruitment Assistant | Strict Accuracy | Evidence-Based Analysis | v1.0</p>', unsafe_allow_html=True)

# ============ TABS ============

tab1, tab2, tab3, tab5, tab6 = st.tabs(["📊 ATS Score Match", "📋 Resume Parser", "📄 JD Parser", "💰 Salary Prediction", "📑 Report Generator"])

# ============ HELPER FUNCTION FOR FILE UPLOAD ============

def handle_file_upload(label, key_prefix, default_text, height=200):
    """Handle file upload with proper error handling."""
    method = st.radio(f"{label} Input:", ["Paste Text", "Upload File"], horizontal=True, key=f"{key_prefix}_method")
    
    if method == "Upload File":
        uploaded = st.file_uploader(f"Upload {label} (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], key=f"{key_prefix}_file")
        if uploaded is not None:
            with st.spinner("Extracting text..."):
                text = extract_text_from_file(uploaded, uploaded.name)
            if text and not text.startswith("Error") and not text.startswith("Could not"):
                st.success(f"✅ Extracted {len(text)} characters")
                return text
            else:
                st.error(f"❌ {text}")
                return default_text
        else:
            st.info("👆 Upload a file or switch to Paste Text")
            return default_text
    else:
        return st.text_area(f"{label}:", value=default_text, height=height, key=f"{key_prefix}_text")

# ============ TAB 1: ATS MATCH ============

with tab1:
    st.markdown("## 📊 ATS Score Match Analysis")
    st.markdown("*Evidence-based scoring with detailed positive and negative matches*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Job Description")
        jd1 = handle_file_upload("JD", "t1_jd", st.session_state.global_jd_text or SAMPLE_JD, 250)
        st.session_state.global_jd_text = jd1
    
    with col2:
        st.markdown("### 📋 Resume")
        res1 = handle_file_upload("Resume", "t1_res", st.session_state.global_resume_text or SAMPLE_RESUME, 250)
        st.session_state.global_resume_text = res1
    
    if st.button("🎯 Calculate ATS Match Score", type="primary", use_container_width=True, key="btn_match"):
        if not st.session_state.model_loaded:
            st.error("⚠️ Please load the AI model first from the sidebar")
        elif jd1 and res1:
            with st.spinner("🔍 Analyzing match... This takes 60-90 seconds"):
                load_model()
                st.session_state.tab1_result = calculate_match_score_detailed(jd1, res1)
    
    # Display Results
    if st.session_state.tab1_result:
        r = st.session_state.tab1_result
        
        if "error" in r and "match_summary" not in r:
            st.error(f"Error: {r.get('error')}")
        else:
            show_retained()
            
            # Score Cards
            summary = r.get("match_summary", {})
            score = summary.get("overall_score", 0)
            grade = summary.get("grade", "N/A")
            rec = summary.get("recommendation", "N/A")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f'<div class="score-card"><div class="score-big">{score}%</div><div class="score-label">ATS Score</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="score-card green-card"><div class="score-big">{grade}</div><div class="score-label">Grade</div></div>', unsafe_allow_html=True)
            
            rec_color = "green-card" if "RECOMMEND" in rec.upper() and "NOT" not in rec.upper() else ("orange-card" if "CONSIDER" in rec.upper() else "red-card")
            c3.markdown(f'<div class="score-card {rec_color}"><div style="font-size:1rem;font-weight:bold;">{rec}</div><div class="score-label">Decision</div></div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="score-card blue-card"><div class="score-big">{summary.get("confidence", "N/A")}</div><div class="score-label">Confidence</div></div>', unsafe_allow_html=True)
            
            # One Line Summary
            st.info(f"**Summary:** {summary.get('one_line_summary', 'Analysis complete')}")
            
            # Score Breakdown
            st.markdown("### 📊 Score Breakdown")
            breakdown = r.get("scoring_breakdown", {})
            
            cols = st.columns(5)
            metrics = [
                ("Skills", breakdown.get("skills_score", {}).get("score", 0), 40),
                ("Experience", breakdown.get("experience_score", {}).get("score", 0), 25),
                ("Education", breakdown.get("education_score", {}).get("score", 0), 15),
                ("Responsibilities", breakdown.get("responsibilities_score", {}).get("score", 0), 15),
                ("Culture", breakdown.get("culture_score", {}).get("score", 0), 5)
            ]
            
            for i, (name, sc, weight) in enumerate(metrics):
                with cols[i]:
                    st.metric(f"{name} ({weight}%)", f"{sc}%")
                    st.progress(sc/100 if isinstance(sc, (int, float)) else 0)
            
            # Positive Matches
            st.markdown("### ✅ Positive Matches")
            positive = r.get("positive_matches", [])
            if positive:
                for match in positive[:8]:
                    if isinstance(match, dict):
                        st.markdown(f"""
                        <div class="positive-match">
                            <strong>{match.get('category', 'Match')}: {match.get('item', 'N/A')}</strong> 
                            <span style="color:green;float:right;">{match.get('points', '+')}</span><br/>
                            <small><strong>JD:</strong> {match.get('jd_text', 'N/A')}</small><br/>
                            <small><strong>Resume:</strong> {match.get('resume_text', 'N/A')}</small><br/>
                            <small><strong>Match:</strong> {match.get('match_quality', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No positive matches data available")
            
            # Negative Matches
            st.markdown("### ❌ Negative Matches / Gaps")
            negative = r.get("negative_matches", [])
            if negative:
                for match in negative[:8]:
                    if isinstance(match, dict):
                        st.markdown(f"""
                        <div class="negative-match">
                            <strong>{match.get('category', 'Gap')}: {match.get('item', 'N/A')}</strong>
                            <span style="color:red;float:right;">{match.get('points', '-')}</span><br/>
                            <small><strong>JD Requires:</strong> {match.get('jd_text', 'N/A')}</small><br/>
                            <small><strong>Resume:</strong> {match.get('resume_text', 'NOT FOUND')}</small><br/>
                            <small><strong>Impact:</strong> {match.get('impact', 'N/A')} | <strong>Can Learn:</strong> {match.get('can_learn', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("No major gaps identified")
            
            # Skill Analysis
            st.markdown("### 🔧 Skill Analysis")
            skill_analysis = r.get("skill_analysis", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Matched Skills:**")
                matched = skill_analysis.get("matched_skills", [])
                if matched:
                    for s in matched[:6]:
                        if isinstance(s, dict):
                            st.markdown(f"- **{s.get('skill', 'N/A')}**: {s.get('resume_evidence', 'Found')}")
                        else:
                            st.markdown(f"- {s}")
                else:
                    st.caption("None listed")
            
            with col2:
                st.markdown("**❌ Missing Skills:**")
                missing = skill_analysis.get("missing_skills", [])
                if missing:
                    for s in missing[:6]:
                        if isinstance(s, dict):
                            st.markdown(f"- **{s.get('skill', 'N/A')}** ({s.get('importance', 'Required')}) - Learn: {s.get('learnability', 'N/A')}")
                        else:
                            st.markdown(f"- {s}")
                else:
                    st.caption("No major skills missing")
            
            # Hiring Recommendation
            st.markdown("### 🎯 Hiring Recommendation")
            hiring = r.get("hiring_recommendation", {})
            decision = hiring.get("decision", "CONSIDER")
            
            if "RECOMMEND" in decision.upper() and "NOT" not in decision.upper():
                st.success(f"**{decision}** - Priority: {hiring.get('priority', 'N/A')}")
            elif "CONSIDER" in decision.upper():
                st.warning(f"**{decision}** - Priority: {hiring.get('priority', 'N/A')}")
            else:
                st.error(f"**{decision}** - Priority: {hiring.get('priority', 'N/A')}")
            
            st.info(f"**Reasoning:** {hiring.get('reasoning', 'N/A')}")
            
            focus = hiring.get("interview_focus", [])
            if focus:
                st.markdown("**Interview Focus Areas:**")
                for f in focus[:5]:
                    st.markdown(f"- {f}")
            
            # Full JSON
            with st.expander("📄 View Full Analysis JSON"):
                st.json(r)
            
            st.download_button("📥 Download Analysis", json.dumps(r, indent=2), "ats_match_analysis.json", use_container_width=True)

# ============ TAB 2: RESUME PARSER ============

with tab2:
    st.markdown("## 📋 Resume Parser")
    st.markdown("*Strict extraction - only what's explicitly in the resume*")
    
    res2 = handle_file_upload("Resume", "t2_res", st.session_state.global_resume_text or SAMPLE_RESUME, 350)
    st.session_state.global_resume_text = res2
    
    if st.button("🔍 Parse Resume", type="primary", use_container_width=True, key="btn_resume"):
        if not st.session_state.model_loaded:
            st.error("⚠️ Please load the AI model first")
        elif res2:
            with st.spinner("Parsing resume..."):
                load_model()
                st.session_state.tab2_result = parse_resume_detailed(res2)
    
    if st.session_state.tab2_result:
        r = st.session_state.tab2_result
        if "personal_info" in r or "experience_summary" in r:
            show_retained()
            
            # Personal Info
            st.markdown("### 👤 Personal Information")
            p = r.get("personal_info", {})
            cols = st.columns(3)
            cols[0].markdown(f"**Name:** {p.get('name', 'N/A')}")
            cols[1].markdown(f"**Email:** {p.get('email', 'N/A')}")
            cols[2].markdown(f"**Phone:** {p.get('phone', 'N/A')}")
            
            # Experience Summary
            st.markdown("### 💼 Experience Summary")
            exp = r.get("experience_summary", {})
            cols = st.columns(4)
            cols[0].metric("Total Years", exp.get("total_years", "N/A"))
            cols[1].metric("Level", exp.get("level", "N/A"))
            cols[2].markdown(f"**Current Company:** {exp.get('current_company', 'N/A')}")
            cols[3].markdown(f"**Current Role:** {exp.get('current_role', 'N/A')}")
            
            # Education
            st.markdown("### 🎓 Education")
            edu = r.get("education", [])
            if edu:
                for e in edu:
                    if isinstance(e, dict):
                        st.markdown(f"**{e.get('degree', 'N/A')}** in {e.get('field', 'N/A')} - {e.get('institution', 'N/A')} ({e.get('year', 'N/A')})")
                        if e.get('grade'):
                            st.caption(f"Grade: {e.get('grade')}")
            
            # Skills
            st.markdown("### 🔧 Skills")
            skills = r.get("skills", {})
            if isinstance(skills, dict):
                for cat, items in skills.items():
                    if items and isinstance(items, list) and len(items) > 0:
                        st.markdown(f"**{cat.replace('_', ' ').title()}:** {', '.join(str(i) for i in items)}")
            
            with st.expander("📄 View Full JSON"):
                st.json(r)

# ============ TAB 3: JD PARSER ============

with tab3:
    st.markdown("## 📄 JD Parser")
    
    jd3 = handle_file_upload("JD", "t3_jd", st.session_state.global_jd_text or SAMPLE_JD, 350)
    st.session_state.global_jd_text = jd3
    
    if st.button("🔍 Parse JD", type="primary", use_container_width=True, key="btn_jd"):
        if not st.session_state.model_loaded:
            st.error("⚠️ Please load the AI model first")
        elif jd3:
            with st.spinner("Parsing JD..."):
                load_model()
                st.session_state.tab3_result = parse_job_description_detailed(jd3)
    
    if st.session_state.tab3_result:
        r = st.session_state.tab3_result
        if "job_info" in r:
            show_retained()
            
            info = r.get("job_info", {})
            st.markdown(f"### {info.get('title', 'N/A')} at {info.get('company', 'N/A')}")
            st.markdown(f"**Location:** {info.get('location', 'N/A')} | **Type:** {info.get('employment_type', 'N/A')}")
            
            reqs = r.get("requirements", {})
            st.markdown(f"**Experience:** {reqs.get('experience_text', 'N/A')}")
            st.markdown(f"**Education:** {reqs.get('education_required', 'N/A')}")
            
            st.markdown("**Must-have Skills:**")
            for s in reqs.get("must_have_skills", [])[:10]:
                st.markdown(f"- {s}")
            
            with st.expander("📄 View Full JSON"):
                st.json(r)


# ============ TAB 5: SALARY ANALYSIS ============

with tab5:
    st.markdown("## 💰 Salary Analysis")
    st.markdown("*Based ONLY on information in the resume - no assumptions*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 Job Description")
        jd5 = handle_file_upload("JD", "t5_jd", st.session_state.global_jd_text or SAMPLE_JD, 200)
        st.session_state.global_jd_text = jd5
    
    with col2:
        st.markdown("### 📋 Resume")
        res5 = handle_file_upload("Resume", "t5_res", st.session_state.global_resume_text or SAMPLE_RESUME, 200)
        st.session_state.global_resume_text = res5
    
    if st.button("💰 Analyze Salary", type="primary", use_container_width=True, key="btn_salary"):
        if not st.session_state.model_loaded:
            st.error("⚠️ Please load the AI model first")
        elif jd5 and res5:
            with st.spinner("Analyzing salary..."):
                load_model()
                st.session_state.tab5_result = recommend_salary_detailed(jd5, res5)
    
    if st.session_state.tab5_result:
        r = st.session_state.tab5_result
        
        if "error" in r and "salary_recommendation" not in r:
            st.error(f"Error: {r.get('error')}")
        else:
            show_retained()
            
            # Candidate Profile
            st.markdown("### 👤 Candidate Profile (from Resume)")
            profile = r.get("candidate_profile", {})
            cols = st.columns(4)
            cols[0].metric("Experience", profile.get("total_experience", "N/A"))
            cols[1].metric("Level", profile.get("level", "N/A"))
            cols[2].metric("Current CTC", profile.get("current_ctc", "Not provided"))
            cols[3].metric("Expected CTC", profile.get("expected_ctc", "Not provided"))
            
            # Salary Recommendation
            st.markdown("### 💵 Salary Recommendation")
            sal = r.get("salary_recommendation", {})
            
            cols = st.columns(4)
            cols[0].markdown(f'<div class="score-card"><div class="score-big">{sal.get("minimum", "N/A")}</div><div class="score-label">Minimum</div></div>', unsafe_allow_html=True)
            cols[1].markdown(f'<div class="score-card green-card"><div class="score-big">{sal.get("recommended", "N/A")}</div><div class="score-label">Recommended</div></div>', unsafe_allow_html=True)
            cols[2].markdown(f'<div class="score-card orange-card"><div class="score-big">{sal.get("maximum", "N/A")}</div><div class="score-label">Maximum</div></div>', unsafe_allow_html=True)
            cols[3].markdown(f'<div class="score-card blue-card"><div class="score-big">{sal.get("stretch", "N/A")}</div><div class="score-label">Stretch</div></div>', unsafe_allow_html=True)
            
            # Market Rate Calculation
            st.markdown("### 📊 Market Rate Calculation")
            calc = r.get("market_rate_calculation", {})
            
            base = calc.get("base_rate", {})
            st.markdown(f"**Base Market Rate:** {base.get('range', 'N/A')}")
            st.caption(base.get('basis', ''))
            
            # Applicable Premiums
            st.markdown("#### ✅ Applicable Premiums (Found in Resume)")
            premiums = calc.get("applicable_premiums", [])
            if premiums:
                for p in premiums:
                    if isinstance(p, dict):
                        st.markdown(f"""
                        <div class="premium-applicable">
                            <strong>{p.get('factor', 'N/A')}</strong>: +{p.get('premium_percent', 0)}%<br/>
                            <small>Evidence: {p.get('evidence', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No premium factors applicable based on resume")
            
            # NOT Applicable Premiums
            st.markdown("#### ❌ Premiums NOT Applicable")
            not_applicable = calc.get("premiums_NOT_applicable", [])
            if not_applicable:
                for p in not_applicable:
                    if isinstance(p, dict):
                        st.markdown(f"""
                        <div class="premium-not-applicable">
                            <strong>{p.get('factor', 'N/A')}</strong><br/>
                            <small>Reason: {p.get('reason', 'Not found in resume')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Hike Analysis
            st.markdown("### 📈 Hike Analysis")
            hike = r.get("hike_analysis", {})
            cols = st.columns(3)
            cols[0].markdown(f"**Current CTC:** {hike.get('current_ctc', 'Not provided')}")
            cols[1].markdown(f"**Recommended:** {hike.get('recommended_offer', 'N/A')}")
            cols[2].markdown(f"**Hike %:** {hike.get('hike_percent', 'N/A')}")
            st.caption(hike.get('assessment', ''))
            
            # Summary
            st.markdown("### 📝 Summary")
            summary = r.get("recommendation_summary", {})
            st.success(f"**Final Recommendation: {summary.get('final_recommendation', 'N/A')}** (Confidence: {summary.get('confidence', 'N/A')})")
            
            caveats = summary.get("caveats", [])
            if caveats:
                st.warning("**Notes:** " + " | ".join(caveats))
            
            with st.expander("📄 View Full JSON"):
                st.json(r)
            
            st.download_button("📥 Download Analysis", json.dumps(r, indent=2), "salary_analysis.json", use_container_width=True)

# ============ TAB 6: HIRING REPORT ============

with tab6:
    st.markdown("## 📑 Comprehensive Hiring Report")
    st.markdown("*Detailed assessment with accurate information from resume*")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 Job Description")
        jd6 = handle_file_upload("JD", "t6_jd", st.session_state.global_jd_text or SAMPLE_JD, 200)
        st.session_state.global_jd_text = jd6
    
    with col2:
        st.markdown("### 📋 Resume")
        res6 = handle_file_upload("Resume", "t6_res", st.session_state.global_resume_text or SAMPLE_RESUME, 200)
        st.session_state.global_resume_text = res6
    
    if st.button("📑 Generate Comprehensive Report", type="primary", use_container_width=True, key="btn_report"):
        if not st.session_state.model_loaded:
            st.error("⚠️ Please load the AI model first")
        elif jd6 and res6:
            progress = st.progress(0)
            
            with st.spinner("Step 1/3: Analyzing match..."):
                load_model()
                match = calculate_match_score_detailed(jd6, res6)
                st.session_state.tab1_result = match
                progress.progress(33)
            
            with st.spinner("Step 2/3: Analyzing salary..."):
                salary = recommend_salary_detailed(jd6, res6)
                st.session_state.tab5_result = salary
                progress.progress(66)
            
            with st.spinner("Step 3/3: Generating report..."):
                st.session_state.tab6_result = generate_hiring_report_detailed(jd6, res6, match, salary)
                progress.progress(100)
    
    if st.session_state.tab6_result:
        r = st.session_state.tab6_result
        
        if "executive_summary" in r:
            show_retained()
            
            # Executive Summary Card
            exec_sum = r.get("executive_summary", {})
            rec = exec_sum.get("recommendation", "CONSIDER")
            score = exec_sum.get("ats_score", 0)
            grade = exec_sum.get("grade", "N/A")
            
            # Color based on recommendation
            if "STRONGLY" in rec.upper():
                bg_color = "#4CAF50"
            elif "RECOMMEND" in rec.upper() and "NOT" not in rec.upper():
                bg_color = "#8BC34A"
            elif "CONSIDER" in rec.upper():
                bg_color = "#FF9800"
            else:
                bg_color = "#f44336"
            
            st.markdown(f"""
            <div style="background: {bg_color}; color: white; padding: 25px; border-radius: 15px; text-align: center; margin: 20px 0;">
                <h2 style="margin: 0;">{rec}</h2>
                <p style="margin: 10px 0 0 0; font-size: 1.2rem;">ATS Score: {score}% | Grade: {grade} | Confidence: {exec_sum.get('confidence', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info(f"**Verdict:** {exec_sum.get('verdict', 'N/A')}")
            
            # Key Decision Factors
            factors = exec_sum.get("key_decision_factors", [])
            if factors:
                st.markdown("**Key Decision Factors:**")
                for f in factors[:5]:
                    st.markdown(f"- {f}")
            
            # Candidate Profile
            st.markdown("### 👤 Candidate Profile")
            profile = r.get("candidate_profile", {})
            cols = st.columns(4)
            cols[0].markdown(f"**Name:** {profile.get('name', 'N/A')}")
            cols[1].markdown(f"**Experience:** {profile.get('total_experience', 'N/A')}")
            cols[2].markdown(f"**Current:** {profile.get('current_company', 'N/A')}")
            cols[3].markdown(f"**Location:** {profile.get('location', 'N/A')}")
            
            # Detailed Assessment
            st.markdown("### 📊 Detailed Assessment")
            assessment = r.get("detailed_assessment", {})
            
            cols = st.columns(4)
            
            skills_a = assessment.get("skills_assessment", {})
            cols[0].metric("Skills", f"{skills_a.get('score', 'N/A')}%", skills_a.get('rating', ''))
            
            exp_a = assessment.get("experience_assessment", {})
            cols[1].metric("Experience", f"{exp_a.get('score', 'N/A')}%", exp_a.get('rating', ''))
            
            edu_a = assessment.get("education_assessment", {})
            cols[2].metric("Education", f"{edu_a.get('score', 'N/A')}%", edu_a.get('rating', ''))
            
            culture_a = assessment.get("culture_fit_assessment", {})
            cols[3].metric("Culture Fit", f"{culture_a.get('score', 'N/A')}%", culture_a.get('rating', ''))
            
            # Education Details
            st.markdown("#### 🎓 Education Assessment")
            st.markdown(f"**Required:** {edu_a.get('required', 'N/A')}")
            st.markdown(f"**Candidate Has:** {edu_a.get('candidate_has', 'N/A')} from {edu_a.get('institution', 'N/A')}")
            st.caption(edu_a.get('analysis', ''))
            
            # Strengths and Concerns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ✅ Strengths")
                for s in r.get("strengths", [])[:5]:
                    if isinstance(s, dict):
                        st.markdown(f"""
                        <div class="positive-match">
                            <strong>{s.get('strength', 'N/A')}</strong><br/>
                            <small>Evidence: {s.get('evidence', 'N/A')}</small><br/>
                            <small>Relevance: {s.get('relevance_to_role', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### ⚠️ Concerns")
                for c in r.get("concerns", [])[:5]:
                    if isinstance(c, dict):
                        st.markdown(f"""
                        <div class="negative-match">
                            <strong>{c.get('concern', 'N/A')}</strong> [{c.get('severity', 'N/A')}]<br/>
                            <small>Evidence: {c.get('evidence', 'N/A')}</small><br/>
                            <small>Mitigation: {c.get('mitigation', 'N/A')}</small>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Interview Recommendation
            st.markdown("### 🗓️ Interview Recommendation")
            interview = r.get("interview_recommendation", {})
            
            if interview.get("should_interview", False):
                st.success(f"✅ **Proceed with Interview** - Priority: {interview.get('priority', 'N/A')} - Timeline: {interview.get('timeline', 'N/A')}")
            else:
                st.error("❌ **Do Not Proceed** - Candidate does not meet requirements")
            
            # Interview Rounds
            rounds = interview.get("interview_rounds", [])
            if rounds:
                st.markdown("**Recommended Interview Process:**")
                for rnd in rounds:
                    if isinstance(rnd, dict):
                        st.markdown(f"- **Round {rnd.get('round', 'N/A')}:** {rnd.get('type', 'N/A')} ({rnd.get('duration', 'N/A')}) - Focus: {rnd.get('focus', 'N/A')}")
            
            # Areas to Probe
            probe = interview.get("key_areas_to_probe", [])
            if probe:
                st.markdown("**Key Areas to Probe:**")
                for p in probe[:5]:
                    st.markdown(f"- {p}")
            
            # Compensation Guidance
            st.markdown("### 💰 Compensation Guidance")
            comp = r.get("compensation_guidance", {})
            cols = st.columns(3)
            cols[0].metric("Suggested Offer", comp.get("suggested_offer", "N/A"))
            cols[1].metric("Offer Range", comp.get("offer_range", "N/A"))
            cols[2].metric("Candidate Expects", comp.get("candidate_expectation", "Not provided"))
            
            # Risk Assessment
            st.markdown("### ⚠️ Risk Assessment")
            risk = r.get("risk_assessment", {})
            cols = st.columns(4)
            cols[0].metric("Overall Risk", risk.get("overall_risk", "N/A"))
            
            flight = risk.get("flight_risk", {})
            cols[1].metric("Flight Risk", flight.get("level", "N/A") if isinstance(flight, dict) else flight)
            
            perf = risk.get("performance_risk", {})
            cols[2].metric("Performance Risk", perf.get("level", "N/A") if isinstance(perf, dict) else perf)
            
            culture = risk.get("culture_risk", {})
            cols[3].metric("Culture Risk", culture.get("level", "N/A") if isinstance(culture, dict) else culture)
            
            # Final Recommendation
            st.markdown("### 🎯 Final Recommendation")
            final = r.get("final_recommendation", {})
            
            decision = final.get("decision", "CONSIDER")
            if "RECOMMEND" in decision.upper() and "NOT" not in decision.upper():
                st.success(f"**{decision}** (Confidence: {final.get('confidence', 'N/A')})")
            elif "CONSIDER" in decision.upper():
                st.warning(f"**{decision}** (Confidence: {final.get('confidence', 'N/A')})")
            else:
                st.error(f"**{decision}** (Confidence: {final.get('confidence', 'N/A')})")
            
            st.info(f"**Reasoning:** {final.get('reasoning', 'N/A')}")
            
            # Next Steps
            steps = final.get("next_steps", [])
            if steps:
                st.markdown("**Next Steps:**")
                for s in steps[:5]:
                    if isinstance(s, dict):
                        st.markdown(f"- {s.get('action', 'N/A')} - Owner: {s.get('owner', 'N/A')} - Timeline: {s.get('timeline', 'N/A')}")
            
            # Download
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Download Full Report (JSON)", json.dumps(r, indent=2), f"hiring_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json", use_container_width=True)
            
            with col2:
                # Create text summary
                summary_text = f"""
HIRING REPORT - {datetime.now().strftime('%B %d, %Y')}
{'='*50}

RECOMMENDATION: {rec}
ATS SCORE: {score}% | GRADE: {grade}

CANDIDATE: {profile.get('name', 'N/A')}
EXPERIENCE: {profile.get('total_experience', 'N/A')}
CURRENT: {profile.get('current_company', 'N/A')} - {profile.get('current_role', 'N/A')}

VERDICT: {exec_sum.get('verdict', 'N/A')}

SUGGESTED OFFER: {comp.get('suggested_offer', 'N/A')}

INTERVIEW: {'Yes' if interview.get('should_interview') else 'No'} - Priority: {interview.get('priority', 'N/A')}
"""
                st.download_button("📥 Download Summary (TXT)", summary_text, f"hiring_summary_{datetime.now().strftime('%Y%m%d')}.txt", use_container_width=True)
            
            with st.expander("📄 View Full Report JSON"):
                st.json(r)

# ============ FOOTER ============

st.markdown("---")
st.markdown("""
<p style="text-align:center;color:#666;">
    🎯 HR Job Matcher Pro v1.0 | Strict Accuracy Edition<br/>
    <small>Evidence-based scoring • No hallucination • Detailed analysis</small><br/>
</p>
""", unsafe_allow_html=True)
