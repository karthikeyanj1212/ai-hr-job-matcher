# 🎯 HR Job Matcher Pro v1

> **AI-Powered Recruitment Assistant with Strict Accuracy**
> 
> Evidence-based ATS scoring, realistic salary analysis, and comprehensive hiring reports - all running 100% locally on your machine.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![AI](https://img.shields.io/badge/AI-Mistral%207B-purple)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Modules](#-modules)
- [Technical Details](#-technical-details)
- [API Reference](#-api-reference)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

HR Job Matcher Pro is an intelligent recruitment assistant that helps HR professionals and hiring managers evaluate candidates accurately and efficiently. Unlike cloud-based solutions, this tool runs **entirely on your local machine**, ensuring complete data privacy.

### What Makes v1.0 Special?

- **🎯 Strict Accuracy**: Only extracts and uses information explicitly stated in resumes
- **📊 Evidence-Based Scoring**: Every match point is backed by quoted text from JD and resume
- **💰 Realistic Salary Analysis**: Based on actual Indian tech market data (2024-25)
- **🔒 100% Private**: No data leaves your machine - runs completely offline
- **🆓 Completely Free**: Uses open-source Mistral 7B model

---

## ✨ Key Features

### 1. 📊 ATS Match Analysis

Comprehensive job-candidate matching with detailed scoring breakdown.

| Feature | Description |
|---------|-------------|
| **Overall Score** | Weighted percentage (0-100%) based on multiple factors |
| **Grade System** | A, B+, B, C, D grades for quick assessment |
| **Positive Matches** | Skills/experience found with exact evidence from both documents |
| **Negative Matches** | Gaps identified with impact assessment and learnability timeline |
| **Score Breakdown** | Skills (40%), Experience (25%), Education (15%), Responsibilities (15%), Culture (5%) |

**Sample Output:**
```
✅ Positive Match: Python
   JD: "Strong Python programming required"
   Resume: "Python (3 years experience)"
   Points: +4

❌ Negative Match: Tableau
   JD: "Experience with Tableau required"
   Resume: NOT FOUND
   Impact: Medium | Can Learn: 2-4 weeks
   Points: -5
```

### 2. 📋 Resume Parser

Intelligent extraction of candidate information with strict accuracy.

**Extracts:**
- Personal Information (Name, Email, Phone, Location)
- Experience Summary (Total Years, Level, Current Role)
- Work History (Companies, Roles, Achievements, Technologies)
- Education (Exact degree as written - B.Sc, BCA, B.Tech, etc.)
- Skills (Technical, Tools, Languages, Certifications)
- Additional Info (Notice Period, Current CTC, Expected CTC)

**Strict Accuracy Guarantee:**
- If resume says "B.Sc", output shows "B.Sc" (never assumed as B.Tech)
- If CTC not mentioned, shows "Not provided" (never guessed)
- Only lists skills explicitly mentioned in resume

### 3. 📄 JD Parser

Structured extraction of job requirements.

**Extracts:**
- Job Information (Title, Company, Location, Work Mode)
- Experience Requirements (Min-Max Years, Level)
- Technical Requirements (Must-have, Nice-to-have Skills)
- Education Requirements (As specified in JD)
- Compensation (If mentioned)

### 4. 💰 Salary Analysis

Realistic salary recommendations based on actual market data.

**Features:**
- **Candidate Profile**: Extracted from resume (not assumed)
- **Market Rate Calculation**: Based on experience level and company type
- **Premium Factors**: Only applied if evidence found in resume
- **Non-Applicable Premiums**: Explicitly shown with reasons
- **Offer Strategy**: Initial, Target, Walk-away amounts
- **Hike Analysis**: Current vs Recommended with percentage

**Salary Benchmarks (2024-25 Indian Tech Market):**

| Level | Service Companies | Product Companies | FAANG/Top Startups |
|-------|------------------|-------------------|-------------------|
| Fresher (0-1 yr) | 3-6 LPA | 6-12 LPA | 12-20 LPA |
| Junior (1-3 yrs) | 5-10 LPA | 10-18 LPA | 18-30 LPA |
| Mid (3-5 yrs) | 8-15 LPA | 15-25 LPA | 25-40 LPA |
| Senior (5-8 yrs) | 12-22 LPA | 22-40 LPA | 40-65 LPA |
| Lead (8-12 yrs) | 18-30 LPA | 35-55 LPA | 55-90 LPA |

**Premium Factors (Only if in resume):**
- IIT/NIT/BITS/IIIT: +10-15%
- FAANG Experience: +15-25%
- Niche Skills (ML/AI): +15-30%
- Certifications (AWS/GCP): +5-10%

### 5. 📑 Comprehensive Hiring Report

Executive-level assessment report with all details.

**Report Sections:**

1. **Executive Summary**
   - Recommendation (Strongly Recommend / Recommend / Consider / Not Recommend)
   - ATS Score and Grade
   - One-line Verdict
   - Key Decision Factors

2. **Candidate Profile**
   - Extracted accurately from resume
   - Current company and role
   - Experience level

3. **Detailed Assessment**
   - Skills Score with matched/missing analysis
   - Experience Score with gap analysis
   - Education Score with exact qualification
   - Culture Fit Score

4. **Strengths & Concerns**
   - Each with evidence from resume
   - Severity levels for concerns
   - Mitigation suggestions

5. **Interview Recommendation**
   - Should interview (Yes/No)
   - Priority level
   - Recommended interview rounds
   - Key areas to probe

6. **Compensation Guidance**
   - Suggested offer
   - Offer range
   - Candidate expectations

7. **Risk Assessment**
   - Flight Risk
   - Performance Risk
   - Culture Risk

8. **Final Recommendation**
   - Decision with confidence level
   - Detailed reasoning
   - Next steps with owners and timelines

---

## 📸 Screenshots

### ATS Match Analysis
```
┌─────────────────────────────────────────────────────────┐
│  📊 ATS Match Analysis                                  │
├─────────────┬─────────────┬─────────────┬──────────────┤
│   75%       │    B+       │  RECOMMEND  │    High      │
│   Score     │   Grade     │  Decision   │  Confidence  │
├─────────────┴─────────────┴─────────────┴──────────────┤
│  ✅ Positive Matches                                    │
│  ├── Python: Full match (+4 pts)                       │
│  ├── SQL: Full match (+4 pts)                          │
│  └── Excel: Full match (+3 pts)                        │
├─────────────────────────────────────────────────────────┤
│  ❌ Negative Matches                                    │
│  ├── Tableau: NOT FOUND (-5 pts) [Can learn: 2-4 wks]  │
│  └── Power BI: NOT FOUND (-3 pts) [Can learn: 2 wks]   │
└─────────────────────────────────────────────────────────┘
```

### Salary Analysis
```
┌─────────────────────────────────────────────────────────┐
│  💰 Salary Recommendation                               │
├─────────────┬─────────────┬─────────────┬──────────────┤
│   8 LPA     │   9.5 LPA   │   11 LPA    │   12 LPA     │
│  Minimum    │ Recommended │  Maximum    │   Stretch    │
├─────────────────────────────────────────────────────────┤
│  ✅ Applicable Premiums                                 │
│  └── (None found in resume)                            │
├─────────────────────────────────────────────────────────┤
│  ❌ Premiums NOT Applicable                             │
│  ├── IIT/NIT/BITS: Mumbai University is not premier    │
│  └── FAANG Exp: No FAANG companies in work history     │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- 5GB disk space for model

### Step 1: Clone/Download

```bash
# Option 1: Extract from ZIP
unzip hr_job_matcher_v3.zip
cd hr_job_matcher_v3

# Option 2: Create directory and add files
mkdir hr_job_matcher
cd hr_job_matcher
# Add app.py, llm_utils.py, pdf_utils.py, requirements.txt
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### First Run

On first run, the application will:
1. Download Mistral 7B model (~4GB) from Hugging Face
2. Cache it locally (~/.cache/huggingface/)
3. Subsequent runs will be instant

---

## 📖 Usage

### Quick Start

1. **Load Model**: Click "🚀 Load AI Model" in sidebar (first time takes 2-3 minutes)
2. **Input Data**: Paste or upload JD and Resume
3. **Analyze**: Click the analysis button
4. **Review**: Check results with evidence
5. **Download**: Export reports as JSON or TXT

### Input Methods

| Method | Supported Formats | Best For |
|--------|------------------|----------|
| Paste Text | Plain text | Quick testing |
| Upload File | PDF, DOCX, TXT | Real documents |

### Workflow Recommendation

```
1. ATS Match Analysis    → Get overall fit score
         ↓
2. Review +/- Matches    → Understand gaps
         ↓
3. Salary Analysis       → Determine offer range
         ↓
4. Hiring Report         → Generate final recommendation
```

---

## 📦 Modules

### File Structure

```
hr_job_matcher_v3/
├── app.py              # Main Streamlit application
├── llm_utils.py        # LLM functions and prompts
├── pdf_utils.py        # PDF/DOCX text extraction
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

### Module Descriptions

#### `app.py`
Main application with Streamlit UI.
- Page configuration and styling
- Session state management
- Tab-based interface
- Result display with formatting

#### `llm_utils.py`
Core AI functions with strict accuracy prompts.

| Function | Purpose |
|----------|---------|
| `initialize_llm()` | Download and load Mistral 7B model |
| `parse_resume_detailed()` | Extract resume information |
| `parse_job_description_detailed()` | Extract JD requirements |
| `calculate_match_score_detailed()` | Calculate ATS match with evidence |
| `recommend_salary_detailed()` | Analyze salary with market data |
| `generate_hiring_report_detailed()` | Create comprehensive report |

#### `pdf_utils.py`
Document text extraction utilities.

| Function | Purpose |
|----------|---------|
| `extract_text_from_pdf()` | Extract text from PDF files |
| `extract_text_from_docx()` | Extract text from Word documents |
| `extract_text_from_txt()` | Read plain text files |
| `extract_text_from_file()` | Auto-detect and extract |

---

## 🔧 Technical Details

### Model Information

| Property | Value |
|----------|-------|
| Model | Mistral-7B-Instruct-v0.2 |
| Quantization | Q4_K_M (4-bit) |
| Size | ~4GB |
| Context Window | 8192 tokens |
| Source | TheBloke/Mistral-7B-Instruct-v0.2-GGUF |

### Performance

| Metric | Value |
|--------|-------|
| Model Load Time | 30-60 seconds (first time) |
| Analysis Time | 60-90 seconds per request |
| Memory Usage | 4-6 GB RAM |
| GPU Support | Optional (CUDA) |

### Scoring Methodology

```
Overall Score = (Skills × 0.40) + (Experience × 0.25) + 
                (Education × 0.15) + (Responsibilities × 0.15) + 
                (Culture × 0.05)

Grade Mapping:
- 85%+ → A (Strongly Recommend)
- 75-84% → B+ (Recommend)
- 65-74% → B (Consider)
- 55-64% → C (Consider with Reservations)
- <55% → D (Not Recommended)
```

---

## 📚 API Reference

### `calculate_match_score_detailed(jd_text, resume_text)`

Calculates ATS match score with detailed evidence.

**Parameters:**
- `jd_text` (str): Job description text
- `resume_text` (str): Resume text

**Returns:**
```python
{
    "match_summary": {
        "overall_score": 75,
        "grade": "B+",
        "recommendation": "RECOMMEND",
        "confidence": "High"
    },
    "positive_matches": [...],
    "negative_matches": [...],
    "skill_analysis": {...},
    "hiring_recommendation": {...}
}
```

### `recommend_salary_detailed(jd_text, resume_text)`

Provides salary recommendation based on market data.

**Parameters:**
- `jd_text` (str): Job description text
- `resume_text` (str): Resume text

**Returns:**
```python
{
    "candidate_profile": {...},
    "market_rate_calculation": {
        "applicable_premiums": [...],
        "premiums_NOT_applicable": [...]
    },
    "salary_recommendation": {
        "minimum": "8 LPA",
        "recommended": "9.5 LPA",
        "maximum": "11 LPA"
    }
}
```

---

## ❓ Troubleshooting

### Common Issues

#### Model Download Fails
```
Error: Connection timeout during model download
```
**Solution:**
- Check internet connection
- Try again (downloads resume from where it stopped)
- Manually download from Hugging Face and place in cache

#### Out of Memory
```
Error: CUDA out of memory / System out of memory
```
**Solution:**
- Close other applications
- Use CPU mode (default)
- Reduce context window in `llm_utils.py`

#### PDF Extraction Fails
```
Error: Could not extract text from PDF
```
**Solution:**
- Ensure PDF is not scanned image
- Install all PDF libraries: `pip install pdfplumber PyPDF2 pymupdf`
- Try converting to DOCX first

#### Slow Performance
**Solution:**
- First run downloads model (~4GB) - be patient
- Subsequent runs use cached model
- Consider GPU acceleration if available

### Getting Help

1. Check the error message in the terminal
2. Verify all dependencies are installed
3. Ensure sufficient RAM (8GB+)
4. Try with sample data first

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue with details
2. **Suggest Features**: Describe your idea
3. **Submit PRs**: Fork, modify, and submit pull request

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd hr_job_matcher

# Install dev dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run app.py --server.runOnSave true
```

---

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
```

---

## 🙏 Acknowledgments

- **Mistral AI** - For the excellent Mistral 7B model
- **TheBloke** - For GGUF quantized models
- **Streamlit** - For the amazing web framework
- **Hugging Face** - For model hosting

---

## 📞 Support

For questions or support:
- Open an issue on GitHub
- Check existing issues for solutions

---

<p align="center">
  Made with ❤️ for HR Professionals
  <br>
  <strong>HR Job Matcher Pro v1.0</strong>
  <br>
  <em>Strict Accuracy • Evidence-Based • 100% Private</em>
</p>
