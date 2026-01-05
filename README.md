# 🎯 HR Job Matcher Pro v1.0

> **AI-Powered Recruitment Assistant** - ATS scoring, salary recommendations, and hiring reports powered by Groq's free LLM API.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![AI](https://img.shields.io/badge/AI-Llama%203.3%2070B-purple)
![API](https://img.shields.io/badge/API-Groq%20(Free)-brightgreen)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **📊 ATS Match** | Score candidates 0-100% with positive/negative match evidence |
| **📋 Resume Parser** | Extract skills, experience, education (strict accuracy) |
| **📄 JD Parser** | Parse job requirements and must-have skills |
| **💰 Salary Analysis** | Market-based recommendations with premium factors |
| **📑 Hiring Report** | Comprehensive assessment with interview guidance |

### Key Highlights

- ✅ **100% Free** - Uses Groq's free API
- ✅ **Accurate** - Powered by Llama 3.3 70B model
- ✅ **Evidence-Based** - Every score backed by specific matches
- ✅ **No Hallucination** - Only extracts what's in the resume

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ai-hr-job-matcher
pip install -r requirements.txt
```

### 2. Get FREE Groq API Key

1. Go to: **https://console.groq.com/keys**
2. Sign up (free, no credit card)
3. Create and copy API key (starts with `gsk_`)

### 3. Configure API Key

```bash
mkdir -p .streamlit
echo 'GROQ_API_KEY = "gsk_your_api_key_here"' > .streamlit/secrets.toml
```

### 4. Run

```bash
streamlit run app.py
```

Open: **http://localhost:8501**

---

## 📁 Project Structure

```
ai-hr-job-matcher/
├── .streamlit/
│   └── secrets.toml      # API key (create this)
├── app.py                # Main Streamlit app
├── llm_utils.py          # Groq API & prompts
├── pdf_utils.py          # PDF/DOCX extraction
├── requirements.txt      # Dependencies
└── README.md
```

---

## 🤖 Model Selection

| Model | Accuracy | Speed | Use For |
|-------|----------|-------|---------|
| **llama-3.3-70b-versatile** ✅ | Best | 10-20s | All HR analysis |
| llama-4-scout-17b | Good | 5-10s | Long documents |
| llama-3.1-8b-instant | Fair | 2-5s | Quick tests only |

---

## ❓ Troubleshooting

| Error | Solution |
|-------|----------|
| "GROQ_API_KEY not found" | Create `.streamlit/secrets.toml` with your key |
| "401 Unauthorized" | Get new key at console.groq.com/keys |
| "429 Too Many Requests" | Wait 1-2 minutes, app will auto-retry |

---

## 🌐 Deploy to Streamlit Cloud

1. Push to GitHub (don't commit `secrets.toml`)
2. Go to share.streamlit.io
3. Connect repo & add secret: `GROQ_API_KEY = "gsk_xxx"`

---

## 📄 License

MIT License - Free to use and modify.

---

<p align="center">
  <strong>HR Job Matcher Pro v1.0</strong><br>
  <em>Accurate • Evidence-Based • Free</em>
</p>