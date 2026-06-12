# 🎯 AI Career Coach & Interview Simulator

AI Career Coach & Interview Simulator is a production-style, GenAI-powered web application built with Streamlit that helps students and job seekers prepare for technical interviews. The platform analyzes resumes, compares them against job descriptions for ATS compatibility, generates tailored interview questions, runs AI-driven mock interviews, scores responses across multiple dimensions, and produces a complete career coaching report.
The application integrates LangChain with configurable LLM backends (OpenAI, Groq, and Amazon Bedrock), uses FAISS for vector-based similarity search, SQLite for persistence, and ReportLab/Plotly for reporting and visual analytics.


---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Resume Analyzer** | Extract skills, projects, education, experience; generate summary, strengths & weaknesses |
| 2 | **ATS Analyzer** | Compare resume vs job description; get ATS score, missing skills, improvement suggestions |
| 3 | **Question Generator** | 25+ targeted questions: Technical, Behavioral, Project, HR, Scenario-based |
| 4 | **AI Mock Interview** | Live AI interviewer with intelligent follow-up questions |
| 5 | **Voice Interview** | Record audio answers (local setup with Whisper) |
| 6 | **Confidence Analyzer** | Track filler words, specificity, response patterns |
| 7 | **Scoring Engine** | 5D scoring: Technical, Communication, Clarity, Confidence, Relevance |
| 8 | **Career Coach** | Personalized weak areas, career path options, immediate actions |
| 9 | **Company Mode** | Amazon (Leadership Principles), Google, Microsoft specific questions |
| 10 | **Learning Roadmap** | 30/60/90-day personalized learning plans |
| 11 | **Analytics Dashboard** | Plotly-powered radar charts, trend analysis, score breakdowns |
| 12 | **PDF Report** | Download complete career coaching report |

---

## 🗂️ Project Structure

```
career-coach-ai/
├── app.py                          # Main Streamlit application
├── modules/
│   ├── __init__.py
│   ├── resume_parser.py            # PDF extraction + AI analysis
│   ├── ats_analyzer.py             # ATS scoring + FAISS vector store
│   ├── interview_engine.py         # Question generation + mock interview
│   ├── scoring_engine.py           # Answer evaluation engine
│   ├── confidence_analyzer.py      # Confidence metrics from text
│   ├── career_coach.py             # Career coaching + roadmap generation
│   └── pdf_generator.py            # ReportLab PDF generation
│
├── database/
│   ├── __init__.py
│   └── db_manager.py               # SQLite CRUD operations
│
├── reports/                        # Generated PDF reports
├── uploads/                        # Uploaded resume PDFs
├── vector_store/                   # FAISS vector indices
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone / Download
```bash
cd career-coach-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate          # Linux/Mac
venv\Scripts\activate             # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Or simply enter your API key in the sidebar when the app loads.

### 5. Run the App
```bash
streamlit run app.py
```

Open: **http://localhost:8501**

---

## 🔑 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | LLM model to use | `gpt-4o` |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `DATABASE_PATH` | SQLite database path | `database/career_coach.db` |
| `UPLOADS_PATH` | Resume upload directory | `uploads/` |
| `REPORTS_PATH` | PDF report directory | `reports/` |
| `VECTOR_STORE_PATH` | FAISS store directory | `vector_store/` |

---

## 🚀 Usage Workflow

```
Step 1: Enter API Key in sidebar
         ↓
Step 2: Upload Resume PDF → Analyze
         ↓
Step 3: Paste Job Description → ATS Analysis
         ↓
Step 4: Generate Interview Questions
         ↓
Step 5: Start Mock Interview → Answer Questions
         ↓
Step 6: View Analytics Dashboard
         ↓
Step 7: Generate Career Coaching Report
         ↓
Step 8: Build 30/60/90 Day Roadmap
         ↓
Step 9: Download PDF Report
```

---

## 🏢 Company-Specific Mode

| Company | Focus |
|---------|-------|
| **Amazon** | 14 Leadership Principles, STAR method, Customer Obsession |
| **Google** | Cognitive ability, problem-solving, Googliness |
| **Microsoft** | Growth mindset, collaboration, scenario-based |

---

## 📊 Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Technical Score | 40% | Accuracy and depth of technical content |
| Communication Score | 35% | Clarity, structure, articulation |
| Relevance Score | 25% | How well answer addresses the question |
| Confidence Score | Tracked | Filler words, specificity, response time |
| ATS Score | Tracked | Resume vs job description match |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python 3.10+ |
| AI Framework | LangChain |
| LLM | OpenAI GPT-4o |
| Vector DB | FAISS |
| Database | SQLite |
| PDF Parsing | PyPDF2 |
| Visualization | Plotly |
| PDF Generation | ReportLab |

---

## 📝 Notes

- **Voice Interview**: Requires `whisper` and `pyaudio` installed locally
- **Webcam Confidence**: Requires `opencv-python` and `mediapipe` installed locally  
- **Cost**: GPT-4o is used — typical session costs ~$0.05–$0.20
- **Privacy**: All data is stored locally in SQLite; nothing is sent to external servers except OpenAI API calls

---

## 📄 License

MIT License — Free for personal and educational use.
