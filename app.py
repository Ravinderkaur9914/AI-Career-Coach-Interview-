"""
AI Career Coach & Interview Simulator  –  app.py
All 12 features fully implemented:
  1  Resume Analyzer        7  Interview Scoring Engine
  2  ATS Analyzer           8  AI Career Coach
  3  Question Generator     9  Company-Specific Mode
  4  AI Mock Interview     10  Personalized Roadmap
  5  Voice Interview       11  Analytics Dashboard
  6  Confidence Analysis   12  PDF Report
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import (
    get_career_recommendations,
    get_interview_responses,
    get_resume_data,
    get_scores,
    initialize_database,
    save_ats_analysis,
    save_career_recommendations,
    save_interview_response,
    save_resume_data,
    save_scores,
)

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
#MainMenu,footer,header{visibility:hidden;}

/* sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0A1628 0%,#162947 100%);}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label{color:#CBD5E1!important;}

/* header */
.app-header{background:linear-gradient(135deg,#0A1628 0%,#1E3A5F 55%,#0077B6 100%);
  padding:2rem 2.5rem;border-radius:16px;margin-bottom:1.5rem;color:#fff;position:relative;overflow:hidden;}
.app-header::after{content:'';position:absolute;top:-60%;right:-5%;width:420px;height:420px;
  background:radial-gradient(circle,rgba(0,180,216,.18) 0%,transparent 70%);border-radius:50%;}
.app-header h1{font-size:2.1rem;font-weight:700;margin:0;letter-spacing:-.4px;}
.app-header p{font-size:.95rem;opacity:.82;margin:.5rem 0 0;}

/* score card */
.score-card{padding:1.1rem;border-radius:12px;text-align:center;color:#fff;
  box-shadow:0 4px 18px rgba(0,0,0,.18);transition:transform .2s;}
.score-card:hover{transform:translateY(-2px);}
.score-card .num{font-size:2.3rem;font-weight:700;line-height:1;}
.score-card .lbl{font-size:.72rem;opacity:.88;margin-top:.3rem;text-transform:uppercase;letter-spacing:.5px;}

/* section title */
.sec-title{font-size:1.3rem;font-weight:700;color:#1E3A5F;border-left:4px solid #00B4D8;
  padding-left:.75rem;margin:1rem 0 .75rem;}

/* feature card */
.fcard{background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:1.1rem;
  margin-bottom:.7rem;transition:box-shadow .2s,border-color .2s;}
.fcard:hover{box-shadow:0 4px 18px rgba(0,119,182,.12);border-color:#00B4D8;}

/* badges */
.badge{display:inline-block;padding:.18rem .6rem;border-radius:999px;font-size:.73rem;font-weight:600;margin:.12rem;}
.bg{background:#D1FAE5;color:#065F46;}   /* green  */
.bb{background:#DBEAFE;color:#1E40AF;}   /* blue   */
.ba{background:#FEF3C7;color:#92400E;}   /* amber  */
.br{background:#FEE2E2;color:#991B1B;}   /* red    */
.bp{background:#EDE9FE;color:#5B21B6;}   /* purple */

/* chat bubbles */
.chat-ai{background:linear-gradient(135deg,#EFF6FF,#DBEAFE);border-left:4px solid #3B82F6;
  padding:.9rem 1.1rem;border-radius:0 12px 12px 0;margin-bottom:.65rem;}
.chat-user{background:#F8FAFC;border-left:4px solid #10B981;
  padding:.9rem 1.1rem;border-radius:0 12px 12px 0;margin-bottom:.65rem;}
.chat-lbl{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.8px;margin-bottom:.35rem;}
.chat-ai .chat-lbl{color:#1D4ED8;} .chat-user .chat-lbl{color:#059669;}

/* progress bar */
.pw{background:#E2E8F0;border-radius:999px;height:9px;overflow:hidden;}
.pf{height:100%;border-radius:999px;transition:width .4s;}

/* roadmap cards */
.rm{border:2px solid;border-radius:12px;padding:1.2rem;margin-bottom:1rem;}
.rm30{border-color:#10B981;background:#F0FDF4;}
.rm60{border-color:#F59E0B;background:#FFFBEB;}
.rm90{border-color:#8B5CF6;background:#F5F3FF;}

/* voice record area */
.rec-panel{background:#F0F9FF;border:2px dashed #0077B6;border-radius:12px;padding:1.5rem;text-align:center;}

/* buttons */
.stButton>button{background:linear-gradient(135deg,#1E3A5F,#0077B6);color:#fff;
  border:none;border-radius:8px;padding:.5rem 1.4rem;font-weight:600;letter-spacing:.3px;}
.stButton>button:hover{opacity:.9;transform:translateY(-1px);}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────────────────────
_DEFAULTS: Dict[str, Any] = {
    "session_id": str(uuid.uuid4()),
    "api_key_set": False,
    "resume_data": None,
    "ats_analysis": None,
    "questions": None,
    "target_role": "",
    "selected_company": None,
    # mock interview
    "interview_active": False,
    "interview_messages": [],
    "current_question": None,
    "current_question_idx": 0,
    "answer_evaluations": [],
    "question_start_time": 0.0,
    # voice interview
    "voice_active": False,
    "voice_messages": [],
    "voice_current_question": None,
    "voice_question_idx": 0,
    # scores & coaching
    "scores": {},
    "career_recommendations": None,
    "roadmap": None,
    "confidence_metrics": [],
    # lazy-loaded modules
    "interview_engine": None,
    "scoring_engine": None,
    "confidence_analyzer": None,
    "voice_module": None,
    # misc
    "pdf_path": None,
    "page": "🏠 Home",
}

def _init():
    for k, v in _DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def score_color(s: float) -> str:
    if s >= 80: return "#10B981"
    if s >= 65: return "#F59E0B"
    if s >= 50: return "#EF4444"
    return "#6B7280"

def score_label(s: float) -> str:
    if s >= 80: return "Excellent"
    if s >= 65: return "Good"
    if s >= 50: return "Average"
    return "Needs Work"

def score_card(label: str, score: float, emoji: str = "📊"):
    c = score_color(score)
    st.markdown(f"""
    <div class="score-card" style="background:linear-gradient(135deg,{c}CC,{c});">
        <div class="num">{score:.0f}</div>
        <div class="lbl">{emoji} {label}</div>
    </div>""", unsafe_allow_html=True)

def progress_bar(label: str, value: float):
    c = score_color(value)
    pct = min(100, value)
    st.markdown(f"""
    <div style="margin-bottom:.55rem;">
      <div style="display:flex;justify-content:space-between;font-size:.84rem;margin-bottom:2px;">
        <span style="font-weight:600;color:#334155;">{label}</span>
        <span style="color:{c};font-weight:700;">{value:.0f}/100</span>
      </div>
      <div class="pw"><div class="pf" style="width:{pct}%;background:{c};"></div></div>
    </div>""", unsafe_allow_html=True)

def check_api() -> bool:
    return bool(os.getenv("OPENAI_API_KEY")) or st.session_state.api_key_set

def lazy_load():
    """Initialise AI modules only when API key is present."""
    if st.session_state.interview_engine is None:
        try:
            from modules.interview_engine import InterviewEngine
            from modules.scoring_engine import ScoringEngine
            from modules.confidence_analyzer import ConfidenceAnalyzer
            from modules.voice_module import VoiceModule
            st.session_state.interview_engine = InterviewEngine()
            st.session_state.scoring_engine = ScoringEngine()
            st.session_state.confidence_analyzer = ConfidenceAnalyzer()
            st.session_state.voice_module = VoiceModule()
        except Exception as e:
            st.error(f"Failed to load AI modules: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:.8rem 0 1rem;">
          <div style="font-size:2.4rem;">🎯</div>
          <div style="font-weight:700;font-size:1.05rem;color:#fff;">AI Career Coach</div>
          <div style="font-size:.72rem;color:#94A3B8;">Interview Simulator</div>
        </div>""", unsafe_allow_html=True)

        # API key
        st.markdown('<p style="color:#94A3B8;font-size:.78rem;font-weight:600;margin-bottom:2px;">🔑 OPENAI API KEY</p>', unsafe_allow_html=True)
        key = st.text_input("", type="password", placeholder="sk-...",
                            key="api_key_input", label_visibility="collapsed")
        if key:
            os.environ["OPENAI_API_KEY"] = key
            st.session_state.api_key_set = True
            st.success("✅ Key saved")

        st.markdown("---")

        # Navigation — all 12 features
        pages = [
            "🏠 Home",
            "📄 Resume Analyzer",
            "🎯 ATS Analyzer",
            "❓ Question Generator",
            "🤖 Mock Interview",
            "🔊 Voice Interview",
            "📸 Confidence Analysis",
            "⭐ Interview Scoring",
            "🏢 Company Mode",
            "🎓 Career Coach",
            "🗺️ Learning Roadmap",
            "📊 Analytics Dashboard",
            "📥 PDF Report",
        ]
        st.markdown('<p style="color:#94A3B8;font-size:.78rem;font-weight:600;">📍 NAVIGATION</p>', unsafe_allow_html=True)
        sel = st.radio("", pages,
                       index=pages.index(st.session_state.page) if st.session_state.page in pages else 0,
                       label_visibility="collapsed")
        st.session_state.page = sel

        st.markdown("---")

        # Target role & company
        st.markdown('<p style="color:#94A3B8;font-size:.78rem;font-weight:600;">💼 TARGET ROLE</p>', unsafe_allow_html=True)
        role = st.text_input("", value=st.session_state.target_role,
                             placeholder="e.g. Data Scientist", label_visibility="collapsed")
        st.session_state.target_role = role

        st.markdown('<p style="color:#94A3B8;font-size:.78rem;font-weight:600;margin-top:6px;">🏢 COMPANY MODE</p>', unsafe_allow_html=True)
        co = st.selectbox("", ["None","Amazon","Google","Microsoft"], label_visibility="collapsed")
        st.session_state.selected_company = None if co == "None" else co

        # Progress checklist
        st.markdown("---")
        checks = {
            "Resume uploaded": st.session_state.resume_data is not None,
            "ATS analysed":    st.session_state.ats_analysis is not None,
            "Questions ready": st.session_state.questions is not None,
            "Interview done":  len(st.session_state.answer_evaluations) > 0,
            "Report generated":st.session_state.pdf_path is not None,
        }
        st.markdown('<p style="color:#94A3B8;font-size:.78rem;font-weight:600;">✅ PROGRESS</p>', unsafe_allow_html=True)
        for item, done in checks.items():
            icon = "✅" if done else "⬜"
            st.markdown(f'<p style="color:#CBD5E1;font-size:.78rem;margin:2px 0;">{icon} {item}</p>',
                        unsafe_allow_html=True)

        st.markdown(f'<p style="color:#475569;font-size:.68rem;margin-top:8px;">ID: {st.session_state.session_id[:8]}…</p>',
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 1 — RESUME ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
def page_resume():
    st.markdown('<div class="sec-title">📄 Resume Analyzer</div>', unsafe_allow_html=True)
    if not check_api():
        st.warning("⚠️ Enter your OpenAI API key in the sidebar."); return

    uploaded = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

    if uploaded:
        st.success(f"✅ {uploaded.name}  ({uploaded.size/1024:.1f} KB)")
        if st.button("🔍 Analyze Resume", use_container_width=True):
            with st.spinner("Extracting & analysing…"):
                try:
                    from modules.resume_parser import ResumeParser
                    p = ResumeParser()
                    raw = uploaded.read()
                    text = p.extract_text_from_pdf(raw)
                    if not text.strip():
                        st.error("No text found — use a text-based PDF."); return
                    p.save_to_uploads(raw, uploaded.name)
                    bar = st.progress(30, "AI analysing…")
                    data = p.analyze_resume(text)
                    bar.progress(100, "Done!")
                    st.session_state.resume_data = data
                    save_resume_data(st.session_state.session_id, data)
                    st.success("✅ Resume analysed!")
                except Exception as e:
                    st.error(f"Error: {e}"); return

    data = st.session_state.resume_data
    if not data: return

    st.markdown("---")
    st.markdown('<div class="sec-title">Analysis Results</div>', unsafe_allow_html=True)

    if data.get("summary"):
        st.info(f"**📝 Summary**\n\n{data['summary']}")

    # Skills
    if data.get("skills"):
        st.markdown("**🛠️ Skills Detected**")
        for sk in data["skills"]:
            st.markdown(f'<span class="badge bb">{sk}</span>', unsafe_allow_html=True)
        st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        if data.get("experience"):
            st.markdown("**💼 Experience**")
            for exp in data["experience"]:
                with st.expander(f"{exp.get('role','')} @ {exp.get('company','')}"):
                    st.caption(f"📅 {exp.get('duration','N/A')}")
                    for r in exp.get("responsibilities", [])[:4]:
                        st.markdown(f"• {r}")

        if data.get("education"):
            st.markdown("**🎓 Education**")
            for edu in data["education"]:
                st.markdown(f"""<div class="fcard" style="padding:.75rem;">
                    <b>{edu.get('degree','')}</b> — {edu.get('institution','')}<br>
                    <small style="color:#64748B;">Graduated {edu.get('year','N/A')}</small>
                </div>""", unsafe_allow_html=True)

    with col2:
        if data.get("projects"):
            st.markdown("**🚀 Projects**")
            for proj in data["projects"]:
                with st.expander(proj.get("name", "Project")):
                    st.write(proj.get("description", ""))
                    for t in proj.get("technologies", []):
                        st.markdown(f'<span class="badge bg">{t}</span>', unsafe_allow_html=True)

        if data.get("strengths"):
            st.markdown("**💪 Strengths**")
            for s in data["strengths"]:
                st.markdown(f'<span class="badge bg">✅ {s}</span>', unsafe_allow_html=True)
            st.markdown("")

        if data.get("weaknesses"):
            st.markdown("**⚠️ Improvement Areas**")
            for w in data["weaknesses"]:
                st.markdown(f'<span class="badge ba">⚠ {w}</span>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 2 — ATS ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
def page_ats():
    st.markdown('<div class="sec-title">🎯 ATS Job-Fit Analyzer</div>', unsafe_allow_html=True)
    if not check_api(): st.warning("⚠️ Enter API key in sidebar."); return
    if not st.session_state.resume_data:
        st.warning("⚠️ Analyse your resume first."); return

    jd = st.text_area("Paste the Job Description", height=220,
                      placeholder="Full job posting text…")

    if st.button("🎯 Run ATS Analysis", use_container_width=True) and jd.strip():
        with st.spinner("Comparing resume ↔ job description…"):
            try:
                from modules.ats_analyzer import ATSAnalyzer
                a = ATSAnalyzer()
                result = a.analyze(st.session_state.resume_data, jd)
                raw = st.session_state.resume_data.get("raw_text","")
                if raw:
                    a.build_vector_store(raw, st.session_state.session_id)
                st.session_state.ats_analysis = result
                st.session_state.scores["ats_score"] = result.get("ats_score", 0)
                save_ats_analysis(st.session_state.session_id, result)
                st.success("✅ ATS analysis complete!")
            except Exception as e:
                st.error(f"ATS error: {e}")

    r = st.session_state.ats_analysis
    if not r: return

    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    sec = r.get("section_scores", {})
    with c1: score_card("ATS Match",  r.get("ats_score",0), "🎯")
    with c2: score_card("Skills",     sec.get("skills_match",0), "🛠️")
    with c3: score_card("Experience", sec.get("experience_match",0), "💼")
    with c4: score_card("Overall Fit",sec.get("overall_fit",0), "⭐")

    if r.get("summary"):
        st.info(r["summary"])
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**✅ Matched Skills**")
        for sk in r.get("matched_skills",[])[:12]:
            st.markdown(f'<span class="badge bg">{sk}</span>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("**❌ Missing Skills**")
        for sk in r.get("missing_skills",[])[:12]:
            st.markdown(f'<span class="badge br">{sk}</span>', unsafe_allow_html=True)
    with col2:
        st.markdown("**📈 Recommended to Add**")
        for sk in r.get("recommended_skills",[])[:10]:
            st.markdown(f'<span class="badge bb">{sk}</span>', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("**💡 Resume Improvements**")
        for i,s in enumerate(r.get("improvement_suggestions",[])[:5], 1):
            st.markdown(f'<div class="fcard" style="padding:.65rem;"><b style="color:#0077B6;">{i}.</b> {s}</div>',
                        unsafe_allow_html=True)

    # Skill gap pie chart
    matched = len(r.get("matched_skills",[]))
    missing = len(r.get("missing_skills",[]))
    if matched + missing > 0:
        st.markdown("---")
        st.markdown("**📊 Skill Gap Overview**")
        fig = go.Figure(go.Pie(
            labels=["Matched","Missing"],
            values=[matched, missing],
            hole=.55,
            marker_colors=["#10B981","#EF4444"],
        ))
        fig.update_layout(height=280, margin=dict(t=10,b=10,l=10,r=10),
                          showlegend=True)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 3 — QUESTION GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def page_questions():
    st.markdown('<div class="sec-title">❓ Interview Question Generator</div>', unsafe_allow_html=True)
    if not check_api(): st.warning("⚠️ Enter API key."); return
    if not st.session_state.resume_data: st.warning("⚠️ Analyse resume first."); return

    col1, col2 = st.columns([2,1])
    with col1:
        role = st.text_input("Target Role", value=st.session_state.target_role,
                             placeholder="e.g. Senior Data Scientist")
        jd   = st.text_area("Job Description (optional)", height=90,
                             placeholder="Paste JD for targeted questions…")
    with col2:
        co   = st.selectbox("Company Mode", ["None","Amazon","Google","Microsoft"])
        diff = st.select_slider("Difficulty", ["Entry","Mid","Senior","Lead"])

    if st.button("⚡ Generate Questions", use_container_width=True):
        if not role: st.warning("Enter a target role."); return
        st.session_state.target_role = role
        lazy_load()
        with st.spinner("Generating 30+ personalised questions…"):
            try:
                co_val = None if co=="None" else co
                qs = st.session_state.interview_engine.generate_questions(
                    st.session_state.resume_data, jd or "General", role, co_val
                )
                st.session_state.questions = qs
                st.session_state.selected_company = co_val
                total = sum(len(v) for v in qs.values())
                st.success(f"✅ {total} questions generated!")
            except Exception as e:
                st.error(f"Error: {e}")

    q = st.session_state.questions
    if not q: return
    st.markdown("---")

    cats = {
        "🔧 Technical (10)":          q.get("technical",[]),
        "📁 Project-Based (5)":       q.get("project_based",[]),
        "🧠 Behavioral (10)":         q.get("behavioral",[]),
        "👔 HR (5)":                  q.get("hr",[]),
        "🎭 Scenario-Based (5)":      q.get("scenario_based",[]),
        "🏢 Company-Specific":        q.get("company_specific",[]),
    }
    for cname, cqs in cats.items():
        if cqs:
            with st.expander(f"{cname}  ({len(cqs)} questions)",
                             expanded="Technical" in cname):
                for i, qtext in enumerate(cqs, 1):
                    st.markdown(
                        f'<div class="fcard" style="padding:.65rem;"><span style="color:#0077B6;font-weight:700;">Q{i}.</span> {qtext}</div>',
                        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 4 — AI MOCK INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_mock_interview():
    st.markdown('<div class="sec-title">🤖 AI Mock Interview</div>', unsafe_allow_html=True)
    if not check_api(): st.warning("⚠️ Enter API key."); return
    if not st.session_state.resume_data: st.warning("⚠️ Analyse resume first."); return
    if not st.session_state.questions:  st.warning("⚠️ Generate questions first."); return

    # ── Controls ──
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("▶️ Start New Interview", use_container_width=True):
            lazy_load()
            eng = st.session_state.interview_engine
            eng.start_interview(st.session_state.questions,
                                st.session_state.target_role or "Target Role")
            st.session_state.update({
                "interview_active": True,
                "interview_messages": [],
                "answer_evaluations": [],
                "current_question": eng.get_next_question(),
                "current_question_idx": 1,
                "question_start_time": time.time(),
            })
            st.session_state.confidence_analyzer.reset_session()
            st.rerun()

    with c2:
        if st.session_state.interview_active and st.button("⏹️ End & Save", use_container_width=True):
            _finish_interview()
            st.rerun()

    with c3:
        eng = st.session_state.interview_engine
        total   = len(eng.all_questions) if eng and hasattr(eng, "all_questions") else 12
        answered = len(st.session_state.answer_evaluations)
        pct = int(answered / max(total, 1) * 100)
        st.markdown(f"""
        <div style="text-align:center;padding:.5rem;background:#F1F5F9;border-radius:8px;">
          <b style="color:#1E3A5F;font-size:1.1rem;">{answered}/{total}</b>
          <div style="font-size:.72rem;color:#64748B;">answered  ({pct}%)</div>
          <div class="pw" style="margin-top:4px;"><div class="pf" style="width:{pct}%;background:#0077B6;"></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Conversation history ──
    for msg in st.session_state.interview_messages[-10:]:
        if msg["role"] == "ai":
            st.markdown(f'<div class="chat-ai"><div class="chat-lbl">🤖 AI Interviewer</div>{msg["content"]}</div>',
                        unsafe_allow_html=True)
        else:
            score_html = ""
            if msg.get("score") is not None:
                sc = msg["score"]
                score_html = f'<span style="float:right;color:{score_color(sc)};font-weight:700;">{sc:.0f}/100</span>'
            st.markdown(f'<div class="chat-user"><div class="chat-lbl">👤 You{score_html}</div>{msg["content"]}</div>',
                        unsafe_allow_html=True)

    # ── Current question & answer box ──
    if st.session_state.interview_active and st.session_state.current_question:
        q = st.session_state.current_question
        idx = st.session_state.current_question_idx

        st.markdown(f"""
        <div class="chat-ai" style="border-left-color:#1D4ED8;border-left-width:4px;">
          <div class="chat-lbl">🤖 Question #{idx}</div>
          <b>{q}</b>
        </div>""", unsafe_allow_html=True)

        answer = st.text_area("Your Answer", height=130,
            placeholder="Be specific. STAR method works well for behavioural questions.",
            key=f"ans_{idx}")

        ca, cb = st.columns([4,1])
        with ca:
            if st.button("📤 Submit Answer", use_container_width=True) and answer.strip():
                _submit_answer(q, answer)
                st.rerun()
        with cb:
            if st.session_state.answer_evaluations:
                last_sc = st.session_state.answer_evaluations[-1].get("overall_score", 0)
                st.markdown(f"""
                <div style="text-align:center;padding:.6rem;border-radius:8px;
                  background:linear-gradient(135deg,{score_color(last_sc)},{score_color(last_sc)}AA);color:#fff;">
                  <b style="font-size:1.5rem;">{last_sc:.0f}</b><br>
                  <small>last score</small>
                </div>""", unsafe_allow_html=True)

    elif not st.session_state.interview_active and st.session_state.answer_evaluations:
        st.success("✅ Interview saved. Go to **⭐ Interview Scoring** or **📊 Analytics** for results.")


def _submit_answer(question: str, answer: str):
    """Score answer, get AI follow-up, advance to next question."""
    resp_time = time.time() - st.session_state.get("question_start_time", time.time())
    st.session_state.question_start_time = time.time()

    eng  = st.session_state.interview_engine
    scor = st.session_state.scoring_engine
    conf = st.session_state.confidence_analyzer

    with st.spinner("Evaluating…"):
        # Score
        ev = scor.evaluate_answer(question, answer,
                                  st.session_state.target_role or "Target Role") if scor else {}
        ev["question"] = question
        ev["answer"]   = answer
        st.session_state.answer_evaluations.append(ev)

        # Confidence
        if conf:
            cm = conf.analyze_text_confidence(answer, resp_time)
            st.session_state.confidence_metrics.append(cm)
            st.session_state.scores["confidence_score"] = cm["confidence_score"]

        # AI follow-up
        follow_up = eng.process_answer(question, answer) if eng else "Thank you. Moving on."

        # Save to DB
        save_interview_response(st.session_state.session_id, {
            "question": question, "answer": answer, "follow_up": follow_up,
            "technical_score":    ev.get("technical_score", 0),
            "communication_score":ev.get("communication_score", 0),
            "relevance_score":    ev.get("relevance_score", 0),
        })

        # Update messages
        st.session_state.interview_messages.append(
            {"role": "user", "content": answer, "score": ev.get("overall_score")})
        st.session_state.interview_messages.append(
            {"role": "ai",   "content": follow_up})

        # Advance
        nxt = eng.get_next_question() if eng else None
        if nxt:
            st.session_state.current_question = nxt
            st.session_state.current_question_idx += 1
        else:
            st.session_state.interview_messages.append({
                "role":"ai",
                "content":"🎉 That completes the interview! Click <b>End & Save</b> to see your results."
            })
            st.session_state.current_question = None


def _finish_interview():
    """Compute final scores and persist."""
    st.session_state.interview_active = False
    evs = st.session_state.answer_evaluations
    if evs and st.session_state.scoring_engine:
        final = st.session_state.scoring_engine.calculate_session_scores(
            evs,
            confidence_score=st.session_state.scores.get("confidence_score", 70),
            ats_score=st.session_state.scores.get("ats_score", 70),
        )
        st.session_state.scores.update(final)
        save_scores(st.session_state.session_id, st.session_state.scores)
    st.success("✅ Interview saved!")


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 5 — VOICE INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
def page_voice_interview():
    st.markdown('<div class="sec-title">🔊 Voice Interview</div>', unsafe_allow_html=True)
    if not check_api(): st.warning("⚠️ Enter API key."); return
    if not st.session_state.resume_data: st.warning("⚠️ Analyse resume first."); return
    if not st.session_state.questions:  st.warning("⚠️ Generate questions first."); return

    lazy_load()
    vm   = st.session_state.voice_module
    eng  = st.session_state.interview_engine
    scor = st.session_state.scoring_engine

    st.markdown("""
    <div class="fcard">
      <b>How Voice Interview Works</b><br>
      <small style="color:#64748B;">
        1️⃣ Click <b>Start Voice Session</b> — the AI reads the question aloud.<br>
        2️⃣ Record your answer using the microphone widget below.<br>
        3️⃣ The audio is auto-transcribed by <b>OpenAI Whisper</b>.<br>
        4️⃣ Your answer is scored and the next question is read out.
      </small>
    </div>""", unsafe_allow_html=True)

    # ── Start / End buttons ──
    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Start Voice Session", use_container_width=True):
            if not hasattr(eng, "all_questions") or not eng.all_questions:
                eng.start_interview(st.session_state.questions,
                                    st.session_state.target_role or "Target Role")
            q = eng.all_questions[0] if eng.all_questions else "Tell me about yourself."
            st.session_state.voice_active = True
            st.session_state.voice_messages = []
            st.session_state.voice_current_question = q
            st.session_state.voice_question_idx = 1
            vm.reset()
            st.rerun()
    with c2:
        if st.session_state.voice_active and st.button("⏹️ End Voice Session", use_container_width=True):
            st.session_state.voice_active = False
            st.success("Voice session ended. History saved below.")
            st.rerun()

    st.markdown("---")

    # ── Active voice session ──
    if st.session_state.voice_active and st.session_state.voice_current_question:
        q   = st.session_state.voice_current_question
        idx = st.session_state.voice_question_idx

        # TTS: speak the question
        st.markdown(f"""
        <div class="chat-ai">
          <div class="chat-lbl">🔊 Question #{idx} — AI is speaking</div>
          <b>{q}</b>
        </div>""", unsafe_allow_html=True)

        audio_b64 = vm.text_to_speech_b64(q)
        if audio_b64:
            st.markdown(vm.audio_autoplay_html(audio_b64), unsafe_allow_html=True)
        else:
            st.warning("TTS unavailable — question shown as text above.")

        # ── Microphone input ──
        st.markdown('<div class="rec-panel">🎙️ Record your answer using the audio widget below</div>',
                    unsafe_allow_html=True)
        audio_val = st.audio_input("🎙️ Record your answer", key=f"voice_rec_{idx}")

        if audio_val is not None:
            st.audio(audio_val, format="audio/wav")
            if st.button("📤 Transcribe & Submit", use_container_width=True, key=f"vsub_{idx}"):
                with st.spinner("Transcribing with Whisper…"):
                    raw_bytes = audio_val.read() if hasattr(audio_val, "read") else bytes(audio_val)
                    transcript = vm.transcribe_audio_bytes(raw_bytes, "answer.wav")

                if transcript.startswith("[Transcription failed"):
                    st.error(transcript)
                else:
                    st.markdown(f'<div class="chat-user"><div class="chat-lbl">👤 Transcribed Answer</div>{transcript}</div>',
                                unsafe_allow_html=True)

                    # Score transcribed answer
                    ev = scor.evaluate_answer(q, transcript,
                                              st.session_state.target_role or "Role") if scor else {}
                    ev["question"] = q; ev["answer"] = transcript
                    st.session_state.answer_evaluations.append(ev)

                    # Persist
                    follow_up = eng.process_answer(q, transcript) if eng else "Thank you."
                    save_interview_response(st.session_state.session_id, {
                        "question": q, "answer": transcript, "follow_up": follow_up,
                        "technical_score": ev.get("technical_score",0),
                        "communication_score": ev.get("communication_score",0),
                        "relevance_score": ev.get("relevance_score",0),
                    })
                    vm.add_to_history("ai", q)
                    vm.add_to_history("candidate", transcript)
                    st.session_state.voice_messages.append({"role":"ai","content":q})
                    st.session_state.voice_messages.append({"role":"user","content":transcript,
                                                             "score":ev.get("overall_score",0)})

                    # Advance question
                    if eng and hasattr(eng, "all_questions"):
                        if idx < len(eng.all_questions):
                            st.session_state.voice_current_question = eng.all_questions[idx]
                            st.session_state.voice_question_idx = idx + 1
                        else:
                            st.session_state.voice_current_question = None
                            st.session_state.voice_active = False
                            st.success("🎉 Voice interview complete!")
                    st.rerun()

    # ── Conversation history ──
    if st.session_state.voice_messages:
        st.markdown('<div class="sec-title">Conversation History</div>', unsafe_allow_html=True)
        for msg in st.session_state.voice_messages:
            if msg["role"] == "ai":
                st.markdown(f'<div class="chat-ai"><div class="chat-lbl">🔊 AI Question</div>{msg["content"]}</div>',
                            unsafe_allow_html=True)
            else:
                sc = msg.get("score", 0)
                st.markdown(f'<div class="chat-user"><div class="chat-lbl">🎙️ Your Answer — Score {sc:.0f}/100</div>{msg["content"]}</div>',
                            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 6 — CONFIDENCE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def page_confidence():
    st.markdown('<div class="sec-title">📸 Confidence Analysis</div>', unsafe_allow_html=True)

    metrics = st.session_state.confidence_metrics
    evs     = st.session_state.answer_evaluations

    if not metrics:
        st.info("Complete a Mock Interview or Voice Interview to see your confidence analysis.")

        st.markdown("---")
        st.markdown('<div class="sec-title">What We Measure</div>', unsafe_allow_html=True)
        items = [
            ("🔡", "Filler Word Detection",
             "Counts 'um', 'uh', 'like', 'you know' and similar hesitation words per answer."),
            ("📝", "Answer Specificity",
             "Detects numbers/metrics, concrete examples, and action-oriented language."),
            ("📏", "Response Length",
             "Checks whether answers are in the ideal 80–300 word range."),
            ("⏱️", "Response Time",
             "Measures how quickly you begin answering after the question appears."),
            ("📷", "Webcam Tracking (local only)",
             "Eye contact, head movement, and face visibility via OpenCV + MediaPipe."),
        ]
        c1, c2 = st.columns(2)
        for i,(icon,title,desc) in enumerate(items):
            col = c1 if i%2==0 else c2
            with col:
                st.markdown(f"""
                <div class="fcard">
                  <div style="font-size:1.5rem;">{icon}</div>
                  <b>{title}</b>
                  <div style="font-size:.82rem;color:#64748B;margin-top:.25rem;">{desc}</div>
                </div>""", unsafe_allow_html=True)
        return

    # ── Session summary ──
    lazy_load()
    conf = st.session_state.confidence_analyzer
    summary = conf.get_session_confidence_score() if conf else {}
    overall = summary.get("overall_score", 0)

    c1,c2,c3,c4 = st.columns(4)
    with c1: score_card("Confidence Score", overall, "💪")
    with c2: score_card("Responses Analysed", len(metrics), "📝")
    with c3: score_card("Avg Filler Ratio",
                        summary.get("avg_filler_word_ratio",0), "🔡")
    with c4:
        trend = summary.get("trend","stable")
        trend_icon = "📈" if trend=="improving" else "📉" if trend=="declining" else "➡️"
        score_card(f"Trend: {trend.title()}", overall, trend_icon)

    st.markdown("---")

    # ── Feedback list ──
    for fb in summary.get("feedback",[]):
        st.markdown(f"{'✅' if fb.startswith('✅') else '⚠️' if fb.startswith('⚠️') else '📈'} {fb}")

    # ── Per-answer breakdown ──
    st.markdown('<div class="sec-title">Per-Answer Confidence Breakdown</div>', unsafe_allow_html=True)
    for i, m in enumerate(metrics, 1):
        cs = m.get("confidence_score", 0)
        with st.expander(f"Answer #{i} — Confidence {cs:.0f}/100", expanded=i==1):
            c1,c2,c3 = st.columns(3)
            with c1:
                progress_bar("Filler Word Score",    m["sub_scores"]["filler_word_score"])
                progress_bar("Specificity Score",    m["sub_scores"]["specificity_score"])
            with c2:
                progress_bar("Length Score",         m["sub_scores"]["length_score"])
                progress_bar("Response Time Score",  m["sub_scores"]["response_time_score"])
            with c3:
                st.metric("Word Count",      m.get("word_count",0))
                st.metric("Filler Words",    m.get("filler_words_detected",0))
                has_ex = m.get("has_specific_examples", False)
                has_num = m.get("has_metrics_numbers", False)
                st.markdown(f'<span class="badge {"bg" if has_ex else "br"}">{"✅" if has_ex else "❌"} Examples</span>'
                            f'<span class="badge {"bg" if has_num else "ba"}">{"✅" if has_num else "⚠️"} Metrics</span>',
                            unsafe_allow_html=True)
            for fb in m.get("feedback",[]):
                st.markdown(f"• {fb}")

    # ── Confidence trend chart ──
    scores_over_time = [m.get("confidence_score",0) for m in metrics]
    if len(scores_over_time) > 1:
        st.markdown('<div class="sec-title">Confidence Trend</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Scatter(
            x=[f"Q{i}" for i in range(1,len(scores_over_time)+1)],
            y=scores_over_time,
            mode="lines+markers",
            fill="tozeroy",
            fillcolor="rgba(0,119,182,0.1)",
            line=dict(color="#0077B6", width=2.5),
            marker=dict(size=8),
        ))
        fig.add_hline(y=70, line_dash="dash", line_color="#F59E0B",
                      annotation_text="Target 70")
        fig.update_layout(height=280, yaxis=dict(range=[0,100]),
                          margin=dict(t=20,b=20,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Webcam section ──
    st.markdown("---")
    st.markdown('<div class="sec-title">📷 Webcam Confidence (local only)</div>', unsafe_allow_html=True)
    lazy_load()
    wc = st.session_state.confidence_analyzer.analyze_webcam_confidence() if conf else {}
    if not wc.get("available", False):
        st.warning(wc.get("message","Webcam not available in this environment."))
        with st.expander("Setup Instructions"):
            for step in wc.get("setup_instructions",[]):
                st.markdown(f"• {step}")
    else:
        st.success(f"Webcam connected — Estimated confidence: {wc.get('simulated_score',0)}/100")


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 7 — INTERVIEW SCORING ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def page_scoring():
    st.markdown('<div class="sec-title">⭐ Interview Scoring Engine</div>', unsafe_allow_html=True)

    evs = st.session_state.answer_evaluations
    if not evs:
        st.info("Complete a Mock Interview or Voice Interview first.")
        st.markdown("""
        <div class="fcard">
          <b>Scoring Dimensions</b>
          <table style="width:100%;font-size:.85rem;margin-top:.5rem;">
            <tr><th align="left">Dimension</th><th align="left">Weight</th><th align="left">What it measures</th></tr>
            <tr><td>🔧 Technical Accuracy</td><td>40%</td><td>Correctness & depth of technical content</td></tr>
            <tr><td>💬 Communication</td><td>35%</td><td>Clarity, structure, articulation</td></tr>
            <tr><td>🎯 Relevance</td><td>25%</td><td>How well the answer addresses the question</td></tr>
            <tr><td>💪 Confidence</td><td>tracked</td><td>Filler words, specificity, response time</td></tr>
            <tr><td>🎯 ATS Match</td><td>tracked</td><td>Resume ↔ job description alignment</td></tr>
          </table>
        </div>""", unsafe_allow_html=True)
        return

    scores = st.session_state.scores

    # ── Aggregate score cards ──
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: score_card("Technical",    scores.get("technical_score",0),    "🔧")
    with c2: score_card("Communication",scores.get("communication_score",0),"💬")
    with c3: score_card("Confidence",   scores.get("confidence_score",0),   "💪")
    with c4: score_card("Interview",    scores.get("interview_score",0),    "🤖")
    with c5: score_card("Overall",      scores.get("overall_score",0),      "⭐")

    st.markdown("---")

    # ── Progress bars ──
    col1, col2 = st.columns(2)
    with col1:
        progress_bar("Technical Accuracy",    scores.get("technical_score",0))
        progress_bar("Communication",         scores.get("communication_score",0))
        progress_bar("Confidence",            scores.get("confidence_score",0))
    with col2:
        progress_bar("Relevance",             scores.get("relevance_score",0))
        progress_bar("ATS Match",             scores.get("ats_score",0))
        progress_bar("Overall Score",         scores.get("overall_score",0))

    # ── Narrative report ──
    if scores and st.button("📝 Generate Detailed Report Narrative", use_container_width=True):
        lazy_load()
        with st.spinner("Generating performance report…"):
            try:
                report = st.session_state.scoring_engine.generate_interview_report(
                    evs, scores, st.session_state.target_role or "Target Role")
                st.markdown("---")
                st.markdown('<div class="sec-title">Performance Report</div>', unsafe_allow_html=True)
                st.write(report)
            except Exception as e:
                st.error(f"Report error: {e}")

    # ── Per-answer table ──
    st.markdown("---")
    st.markdown('<div class="sec-title">Answer-by-Answer Results</div>', unsafe_allow_html=True)
    for i, ev in enumerate(evs, 1):
        overall_sc = ev.get("overall_score", 0)
        quality = ev.get("answer_quality","average")
        badge_cl = "bg" if quality=="excellent" else "bb" if quality=="good" else "ba" if quality=="average" else "br"
        with st.expander(f"Q{i}: {ev.get('question','')[:65]}…  │  {overall_sc:.0f}/100"):
            c1,c2,c3 = st.columns([2,2,1])
            with c1:
                progress_bar("Technical",     ev.get("technical_score",0))
                progress_bar("Communication", ev.get("communication_score",0))
            with c2:
                progress_bar("Relevance",     ev.get("relevance_score",0))
                progress_bar("Confidence",    ev.get("confidence_score",0))
            with c3:
                st.markdown(f'<span class="badge {badge_cl}" style="font-size:.9rem;">{quality.title()}</span>',
                            unsafe_allow_html=True)
                kw = ev.get("keywords_used",[])
                if kw:
                    st.markdown("**Keywords used:**")
                    for k in kw[:4]:
                        st.markdown(f'<span class="badge bg">{k}</span>', unsafe_allow_html=True)
            fb = ev.get("feedback",{})
            for p in fb.get("positive",[]):
                st.markdown(f"✅ {p}")
            for im in fb.get("improve",[]):
                st.markdown(f"📌 {im}")
            if fb.get("suggestion"):
                st.info(f"💡 {fb['suggestion']}")
            st.markdown(f"**Your Answer:** {ev.get('answer','')}")


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 8 — AI CAREER COACH
# ══════════════════════════════════════════════════════════════════════════════
def page_career_coach():
    st.markdown('<div class="sec-title">🎓 AI Career Coach</div>', unsafe_allow_html=True)
    if not check_api(): st.warning("⚠️ Enter API key."); return
    if not st.session_state.resume_data: st.warning("⚠️ Analyse resume first."); return

    if st.button("🎓 Generate Career Coaching Analysis", use_container_width=True):
        with st.spinner("Generating personalised career insights…"):
            try:
                from modules.career_coach import CareerCoach
                coach = CareerCoach()
                rec = coach.generate_career_analysis(
                    resume_data=st.session_state.resume_data,
                    ats_analysis=st.session_state.ats_analysis,
                    scores=st.session_state.scores,
                    target_role=st.session_state.target_role or "Target Role",
                )
                st.session_state.career_recommendations = rec
                save_career_recommendations(st.session_state.session_id, {
                    "weak_areas":  [a.get("area","") if isinstance(a,dict) else a for a in rec.get("weak_areas",[])],
                    "strong_areas":[a.get("area","") if isinstance(a,dict) else a for a in rec.get("strong_areas",[])],
                    "recommendations": rec.get("immediate_actions",[]),
                })
                st.success("✅ Career coaching report generated!")
            except Exception as e:
                st.error(f"Error: {e}")

    rec = st.session_state.career_recommendations
    if not rec: return

    if rec.get("overall_assessment"):
        st.info(rec["overall_assessment"])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**💪 Strong Areas**")
        for a in rec.get("strong_areas",[])[:3]:
            if isinstance(a,dict):
                st.markdown(f"""<div class="fcard" style="border-left:3px solid #10B981;">
                    <b>✅ {a.get('area','')}</b><br>
                    <small style="color:#64748B;">{a.get('evidence','')}</small><br>
                    <small style="color:#0077B6;">→ {a.get('leverage','')}</small>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="badge bg">✅ {a}</span>', unsafe_allow_html=True)

    with c2:
        priority_color = {"high":"#EF4444","medium":"#F59E0B","low":"#10B981"}
        st.markdown("**📌 Focus Areas**")
        for a in rec.get("weak_areas",[])[:4]:
            if isinstance(a,dict):
                pr = a.get("priority","medium")
                st.markdown(f"""<div class="fcard" style="border-left:3px solid {priority_color.get(pr,'#F59E0B')};">
                    <b>⚠️ {a.get('area','')}</b>
                    <span class="badge ba" style="float:right;">{pr}</span><br>
                    <small style="color:#64748B;">{a.get('gap','')}</small>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="badge ba">⚠️ {a}</span>', unsafe_allow_html=True)

    if rec.get("immediate_actions"):
        st.markdown("**⚡ This Week's Actions**")
        for i,ac in enumerate(rec["immediate_actions"],1):
            st.markdown(f'<div class="fcard" style="padding:.65rem;"><b style="color:#0077B6;">{i}.</b> {ac}</div>',
                        unsafe_allow_html=True)

    if rec.get("career_path_options"):
        st.markdown("**🛤️ Career Path Options**")
        for p in rec["career_path_options"]:
            fit = p.get("fit_score",0)
            st.markdown(f"""<div class="fcard">
              <div style="display:flex;justify-content:space-between;">
                <b>{p.get('role','')}</b>
                <span style="color:{score_color(fit)};font-weight:700;">{fit}% fit</span>
              </div>
              <small style="color:#64748B;">⏱ {p.get('timeline','')} — {p.get('reason','')}</small>
            </div>""", unsafe_allow_html=True)

    if rec.get("interview_improvement_tips"):
        st.markdown("**🎤 Interview Tips**")
        for tip in rec["interview_improvement_tips"]:
            st.markdown(f"💡 {tip}")

    ins = rec.get("market_insights",{})
    if ins:
        st.markdown("---")
        st.markdown("**📊 Market Insights**")
        mc1,mc2,mc3 = st.columns(3)
        with mc1: st.metric("Demand Level", ins.get("demand_level","N/A").title())
        with mc2: st.metric("Salary Range", ins.get("avg_salary_range","N/A"))
        with mc3:
            em = ins.get("emerging_skills",[])
            st.markdown("**Emerging Skills:**")
            for e in em[:4]:
                st.markdown(f'<span class="badge bp">{e}</span>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 9 — COMPANY-SPECIFIC MODE
# ══════════════════════════════════════════════════════════════════════════════
COMPANY_INFO = {
    "Amazon": {
        "color": "#FF9900",
        "icon": "🛒",
        "style": "STAR method (Situation, Task, Action, Result)",
        "principles": [
            "Customer Obsession","Ownership","Invent and Simplify",
            "Are Right A Lot","Learn and Be Curious","Hire and Develop the Best",
            "Insist on the Highest Standards","Think Big","Bias for Action",
            "Frugality","Earn Trust","Dive Deep","Have Backbone; Disagree and Commit",
            "Deliver Results",
        ],
        "tips": [
            "Every answer should map to ≥1 Leadership Principle.",
            "Use STAR format strictly — quantify results whenever possible.",
            "Show customer impact in every technical decision.",
            "Demonstrate long-term thinking, not just quick fixes.",
        ],
    },
    "Google": {
        "color": "#4285F4",
        "icon": "🔵",
        "style": "Structured + data-driven + Googliness",
        "principles": ["Googliness","Leadership","Cognitive Ability","Role-Related Knowledge"],
        "tips": [
            "Quantify impact with data ('reduced latency by 40%').",
            "Show structured problem decomposition.",
            "Demonstrate cross-functional collaboration.",
            "Googleyness = intellectual humility + enthusiasm + teamwork.",
        ],
    },
    "Microsoft": {
        "color": "#00A4EF",
        "icon": "🪟",
        "style": "Growth mindset + scenario-based",
        "principles": ["Growth Mindset","Collaboration","Customer Focus","Diversity & Inclusion"],
        "tips": [
            "Frame failures as learning opportunities (growth mindset).",
            "Show how you've helped others grow.",
            "Connect technical decisions to customer outcomes.",
            "Demonstrate inclusive leadership behaviour.",
        ],
    },
}

def page_company_mode():
    st.markdown('<div class="sec-title">🏢 Company-Specific Mode</div>', unsafe_allow_html=True)
    if not check_api(): st.warning("⚠️ Enter API key."); return

    company = st.selectbox("Select Company", ["Amazon","Google","Microsoft"],
                           index=["Amazon","Google","Microsoft"].index(
                               st.session_state.selected_company)
                           if st.session_state.selected_company else 0)

    info = COMPANY_INFO[company]

    # Company banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{info['color']}22,{info['color']}11);
                border:2px solid {info['color']}44;border-radius:14px;padding:1.3rem;margin-bottom:1rem;">
      <h3 style="color:{info['color']};margin:0;">{info['icon']} {company} Interview Preparation</h3>
      <p style="color:#475569;margin:.4rem 0 0;font-size:.9rem;">Question style: <b>{info['style']}</b></p>
    </div>""", unsafe_allow_html=True)

    # Leadership Principles
    st.markdown(f"**{company} Core Principles / Values**")
    cols = st.columns(3)
    for i, p in enumerate(info["principles"]):
        with cols[i % 3]:
            st.markdown(f'<span class="badge bb">{p}</span>', unsafe_allow_html=True)

    # Interview tips
    st.markdown("---")
    st.markdown(f"**💡 {company} Interview Tips**")
    for tip in info["tips"]:
        st.markdown(f"✅ {tip}")

    st.markdown("---")
    role = st.text_input("Role you're applying for",
                         value=st.session_state.target_role,
                         placeholder="e.g. Software Development Engineer")

    if st.button(f"⚡ Generate {company} Questions", use_container_width=True):
        if not role: st.warning("Enter a target role."); return
        st.session_state.target_role = role
        st.session_state.selected_company = company
        lazy_load()
        with st.spinner(f"Generating {company}-style questions…"):
            try:
                qs = st.session_state.interview_engine.get_company_questions(company, role)
                # Also generate full set if resume available
                if st.session_state.resume_data:
                    full = st.session_state.interview_engine.generate_questions(
                        st.session_state.resume_data, "", role, company)
                    st.session_state.questions = full

                st.session_state[f"company_qs_{company}"] = qs
                st.success(f"✅ {len(qs)} {company}-specific questions generated!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Display company questions
    key = f"company_qs_{company}"
    if st.session_state.get(key):
        st.markdown(f"**{info['icon']} {company}-Specific Questions**")
        for i, q in enumerate(st.session_state[key], 1):
            st.markdown(
                f'<div class="fcard" style="border-left:3px solid {info["color"]};padding:.7rem;">'
                f'<b style="color:{info["color"]};">Q{i}.</b> {q}</div>',
                unsafe_allow_html=True)

        # STAR method helper for Amazon
        if company == "Amazon":
            st.markdown("---")
            st.markdown("**📋 STAR Method Template**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="fcard">
                  <b>S — Situation</b><br>
                  <small>Set the scene. What was the context? What challenge existed?</small>
                </div>
                <div class="fcard">
                  <b>T — Task</b><br>
                  <small>What was your specific responsibility or goal?</small>
                </div>""", unsafe_allow_html=True)
            with col2:
                st.markdown("""
                <div class="fcard">
                  <b>A — Action</b><br>
                  <small>What steps did YOU personally take? Use "I", not "we".</small>
                </div>
                <div class="fcard">
                  <b>R — Result</b><br>
                  <small>What was the measurable outcome? Quantify whenever possible.</small>
                </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 10 — PERSONALIZED ROADMAP
# ══════════════════════════════════════════════════════════════════════════════
def page_roadmap():
    st.markdown('<div class="sec-title">🗺️ Personalised Learning Roadmap</div>', unsafe_allow_html=True)
    if not check_api(): st.warning("⚠️ Enter API key."); return

    if not st.session_state.career_recommendations:
        st.warning("⚠️ Generate the Career Coaching report first (🎓 Career Coach page).")
        return

    col1, col2 = st.columns([2,1])
    with col1:
        role  = st.text_input("Target Role", value=st.session_state.target_role)
    with col2:
        level = st.selectbox("Current Level", ["Beginner","Intermediate","Advanced"])

    if st.button("🗺️ Generate 30/60/90-Day Roadmap", use_container_width=True):
        with st.spinner("Building your personalised learning roadmap…"):
            try:
                from modules.roadmap_generator import RoadmapGenerator
                gen = RoadmapGenerator()
                weak = st.session_state.career_recommendations.get("weak_areas", [])
                skills = st.session_state.resume_data.get("skills",[]) \
                         if st.session_state.resume_data else []
                roadmap = gen.generate(weak, role or "Target Role", skills, level.lower())
                st.session_state.roadmap = roadmap
                st.success("✅ Roadmap generated!")
            except Exception as e:
                st.error(f"Error: {e}")

    rm = st.session_state.roadmap
    if not rm: return
    st.markdown("---")

    plans = [
        ("roadmap_30_day","30 Days","rm30","#10B981"),
        ("roadmap_60_day","60 Days","rm60","#F59E0B"),
        ("roadmap_90_day","90 Days","rm90","#8B5CF6"),
    ]
    for key, label, css, color in plans:
        plan = rm.get(key,{})
        if not plan: continue
        st.markdown(f"""
        <div class="rm {css}">
          <h3 style="margin:0 0 .4rem;color:{color};">📅 {label}</h3>
          <b>Goal:</b> {plan.get('goal','')}
        </div>""", unsafe_allow_html=True)

        with st.expander(f"View {label} detailed plan"):
            # Week-by-week (30-day)
            for wk in plan.get("weeks",[]):
                st.markdown(f"**Week {wk.get('week','')}: {wk.get('theme','')}**")
                for task in wk.get("daily_tasks",[]):
                    st.markdown(f"  • {task}")
                for res in wk.get("resources",[]):
                    st.markdown(f'  📚 <a href="#" style="color:#0077B6;">{res}</a>',
                                unsafe_allow_html=True)
                if wk.get("milestone"):
                    st.success(f"🏆 Milestone: {wk['milestone']}")
                st.markdown("")

            # Key activities (60/90-day)
            for ac in plan.get("key_activities",[]):
                st.markdown(f"→ {ac}")

            # Projects
            for proj in plan.get("projects_to_build",[]):
                st.markdown(f"""<div class="fcard" style="padding:.65rem;">
                  🚀 <b>{proj.get('name','')}</b> — {proj.get('description','')}<br>
                  <small>Skills: {', '.join(proj.get('skills_practiced',[]))}</small>
                </div>""", unsafe_allow_html=True)

            # Portfolio
            for pt in plan.get("portfolio_targets",[]):
                st.markdown(f"📁 {pt}")

            # Success metrics
            if plan.get("success_metrics"):
                st.markdown("**✅ Success Metrics:**")
                for m in plan["success_metrics"]:
                    st.markdown(f"• {m}")

    # Resources
    res = rm.get("recommended_resources",{})
    if res:
        st.markdown("---")
        st.markdown('<div class="sec-title">📚 Recommended Resources</div>', unsafe_allow_html=True)
        rc1,rc2,rc3,rc4 = st.columns(4)
        sections = [
            (rc1,"free_courses","🎓 Free Courses"),
            (rc2,"books","📖 Books"),
            (rc3,"practice_platforms","💻 Practice"),
            (rc4,"communities","👥 Communities"),
        ]
        for col,k,lbl in sections:
            with col:
                st.markdown(f"**{lbl}**")
                for r in res.get(k,[])[:5]:
                    st.markdown(f"• {r}")


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 11 — ANALYTICS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    st.markdown('<div class="sec-title">📊 Analytics Dashboard</div>', unsafe_allow_html=True)

    scores = st.session_state.scores
    evs    = st.session_state.answer_evaluations
    metrics= st.session_state.confidence_metrics

    if not scores and not evs:
        st.info("Complete resume analysis and a mock interview to populate the dashboard.")
        return

    # ── Top KPI row ──
    kpis = [
        ("ATS Score",    "ats_score",    "🎯"),
        ("Interview",    "interview_score","🤖"),
        ("Technical",    "technical_score","🔧"),
        ("Communication","communication_score","💬"),
        ("Confidence",   "confidence_score","💪"),
        ("Overall",      "overall_score", "⭐"),
    ]
    cols = st.columns(len(kpis))
    for col,(lbl,key,icon) in zip(cols,kpis):
        with col: score_card(lbl, scores.get(key,0), icon)

    st.markdown("---")

    # ── Radar + Bar ──
    c1, c2 = st.columns(2)
    cats_r = ["Technical","Communication","Confidence","ATS Match","Relevance"]
    vals_r = [scores.get("technical_score",0), scores.get("communication_score",0),
              scores.get("confidence_score",0), scores.get("ats_score",0),
              scores.get("relevance_score",0)]

    with c1:
        fig = go.Figure(go.Scatterpolar(
            r=vals_r+[vals_r[0]], theta=cats_r+[cats_r[0]],
            fill="toself", fillcolor="rgba(0,119,182,.18)",
            line=dict(color="#0077B6",width=2.5),
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),
                          showlegend=False, title="Performance Radar",
                          height=340, margin=dict(t=45,b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        bar_colors = [score_color(v) for v in vals_r]
        fig2 = go.Figure(go.Bar(
            x=vals_r, y=cats_r, orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{v:.0f}" for v in vals_r], textposition="outside",
        ))
        fig2.update_layout(title="Score Breakdown", xaxis=dict(range=[0,115],showgrid=False),
                           yaxis=dict(showgrid=False), height=340,
                           margin=dict(t=45,b=10,l=10,r=40),
                           plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Answer score trend ──
    if evs:
        st.markdown('<div class="sec-title">Answer Score Progression</div>', unsafe_allow_html=True)
        overall_sc  = [e.get("overall_score",0)       for e in evs]
        tech_sc     = [e.get("technical_score",0)      for e in evs]
        comm_sc     = [e.get("communication_score",0)  for e in evs]
        xlabels     = [f"Q{i}" for i in range(1,len(evs)+1)]

        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=xlabels,y=overall_sc,name="Overall",
            line=dict(color="#0077B6",width=2.5),mode="lines+markers",marker=dict(size=7)))
        fig3.add_trace(go.Scatter(x=xlabels,y=tech_sc,name="Technical",
            line=dict(color="#10B981",width=2,dash="dot"),mode="lines+markers",marker=dict(size=6)))
        fig3.add_trace(go.Scatter(x=xlabels,y=comm_sc,name="Communication",
            line=dict(color="#F59E0B",width=2,dash="dot"),mode="lines+markers",marker=dict(size=6)))
        fig3.update_layout(yaxis=dict(range=[0,100]),height=280,
                           margin=dict(t=20,b=20),legend=dict(orientation="h",y=-0.25))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Confidence trend ──
    if metrics:
        conf_scores = [m.get("confidence_score",0) for m in metrics]
        st.markdown('<div class="sec-title">Confidence Trend</div>', unsafe_allow_html=True)
        fig4 = go.Figure(go.Scatter(
            x=[f"Q{i}" for i in range(1,len(conf_scores)+1)],
            y=conf_scores, fill="tozeroy",
            fillcolor="rgba(16,185,129,.12)",
            line=dict(color="#10B981",width=2.5), mode="lines+markers",
        ))
        fig4.add_hline(y=70,line_dash="dash",line_color="#F59E0B",annotation_text="Target")
        fig4.update_layout(yaxis=dict(range=[0,100]),height=250,margin=dict(t=20,b=20))
        st.plotly_chart(fig4, use_container_width=True)

    # ── Skill gap donut ──
    ats = st.session_state.ats_analysis
    if ats:
        matched = len(ats.get("matched_skills",[]))
        missing = len(ats.get("missing_skills",[]))
        if matched+missing > 0:
            st.markdown('<div class="sec-title">Skill Gap Overview</div>', unsafe_allow_html=True)
            dc1, dc2 = st.columns(2)
            with dc1:
                fig5 = go.Figure(go.Pie(
                    labels=["Matched","Missing"],
                    values=[matched,missing], hole=.6,
                    marker_colors=["#10B981","#EF4444"],
                ))
                fig5.update_layout(height=260,margin=dict(t=10,b=10,l=10,r=10))
                st.plotly_chart(fig5, use_container_width=True)
            with dc2:
                st.metric("Matched Skills", matched)
                st.metric("Missing Skills", missing)
                coverage = round(matched/(matched+missing)*100,1)
                progress_bar("Skill Coverage", coverage)

    # ── Answer quality distribution ──
    if evs:
        quality_counts: Dict[str,int] = {}
        for ev in evs:
            q = ev.get("answer_quality","average")
            quality_counts[q] = quality_counts.get(q,0)+1
        if quality_counts:
            st.markdown('<div class="sec-title">Answer Quality Distribution</div>', unsafe_allow_html=True)
            fig6 = go.Figure(go.Bar(
                x=list(quality_counts.keys()),
                y=list(quality_counts.values()),
                marker_color=["#10B981","#3B82F6","#F59E0B","#EF4444"],
            ))
            fig6.update_layout(height=240,yaxis_title="Count",margin=dict(t=20,b=20))
            st.plotly_chart(fig6, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 12 — PDF REPORT
# ══════════════════════════════════════════════════════════════════════════════
def page_pdf():
    st.markdown('<div class="sec-title">📥 PDF Career Report</div>', unsafe_allow_html=True)
    if not st.session_state.resume_data:
        st.warning("⚠️ Analyse your resume first."); return

    # Checklist
    checks = {
        "Resume Analysis":         st.session_state.resume_data is not None,
        "ATS Analysis":            st.session_state.ats_analysis is not None,
        "Interview Scores":        len(st.session_state.answer_evaluations) > 0,
        "Career Coaching Insights":st.session_state.career_recommendations is not None,
        "Learning Roadmap":        st.session_state.roadmap is not None,
    }
    st.markdown("**📋 Report will include:**")
    for item, done in checks.items():
        st.markdown(f"{'✅' if done else '⬜'} {item}")

    st.markdown("---")
    candidate_name = st.text_input("Your Full Name",
                                   placeholder="e.g. Priya Sharma")

    if st.button("📥 Generate PDF Report", use_container_width=True):
        with st.spinner("Building your professional report…"):
            try:
                from modules.pdf_generator import PDFReportGenerator
                gen = PDFReportGenerator()
                path = gen.generate_report(
                    session_id=st.session_state.session_id,
                    resume_data=st.session_state.resume_data,
                    ats_analysis=st.session_state.ats_analysis,
                    scores=st.session_state.scores or None,
                    career_recommendations=st.session_state.career_recommendations,
                    roadmap=st.session_state.roadmap,
                    interview_responses=st.session_state.answer_evaluations,
                    target_role=st.session_state.target_role or "Target Role",
                    candidate_name=candidate_name or "Candidate",
                )
                st.session_state.pdf_path = path
                with open(path,"rb") as f:
                    pdf_bytes = f.read()
                st.success(f"✅ Report ready: {os.path.basename(path)}")
                st.download_button(
                    "⬇️ Download PDF Report",
                    data=pdf_bytes,
                    file_name=os.path.basename(path),
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    st.markdown("""
    <div class="app-header">
      <h1>🎯 AI Career Coach & Interview Simulator</h1>
      <p>GPT-4o · LangChain · FAISS · OpenAI Whisper · ReportLab · Plotly</p>
    </div>""", unsafe_allow_html=True)

    features = [
        ("📄","Resume Analyzer","Extract skills, projects, education. Get AI-powered strengths & weaknesses."),
        ("🎯","ATS Analyzer","Match score against any JD. Identify skill gaps. Get improvement suggestions."),
        ("❓","Question Generator","30+ personalised questions: Technical, Behavioral, HR, Scenario, Project."),
        ("🤖","Mock Interview","AI interviewer with intelligent follow-up questions after every answer."),
        ("🔊","Voice Interview","Record audio answers — auto-transcribed by OpenAI Whisper."),
        ("📸","Confidence Analysis","Track filler words, specificity, response time per answer."),
        ("⭐","Interview Scoring","5-dimension scoring: Technical, Communication, Relevance, Confidence, ATS."),
        ("🎓","Career Coach","Personalised weak/strong areas, career paths, immediate actions."),
        ("🏢","Company Mode","Amazon (Leadership Principles), Google, Microsoft — authentic question sets."),
        ("🗺️","Learning Roadmap","30/60/90-day plans with weekly tasks, projects, and resources."),
        ("📊","Analytics Dashboard","Radar, trend, skill-gap, and quality charts powered by Plotly."),
        ("📥","PDF Report","Download a complete multi-section coaching report via ReportLab."),
    ]
    cols = st.columns(3)
    for i,(icon,name,desc) in enumerate(features):
        with cols[i%3]:
            st.markdown(f"""
            <div class="fcard">
              <div style="font-size:1.7rem;">{icon}</div>
              <b style="color:#1E3A5F;">{name}</b>
              <div style="color:#64748B;font-size:.81rem;margin-top:.25rem;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="sec-title">🚀 Quick Start</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1: st.info("**Step 1**\nEnter your OpenAI API key in the sidebar, then go to **📄 Resume Analyzer** and upload your PDF.")
    with c2: st.info("**Step 2**\nPaste a job description in **🎯 ATS Analyzer**, run the analysis, then generate questions.")
    with c3: st.info("**Step 3**\nPractice in **🤖 Mock Interview**, review results in **📊 Analytics**, download your **📥 PDF Report**.")


# ──────────────────────────────────────────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────────────────────────────────────────
PAGE_MAP = {
    "🏠 Home":              page_home,
    "📄 Resume Analyzer":   page_resume,
    "🎯 ATS Analyzer":      page_ats,
    "❓ Question Generator":page_questions,
    "🤖 Mock Interview":    page_mock_interview,
    "🔊 Voice Interview":   page_voice_interview,
    "📸 Confidence Analysis":page_confidence,
    "⭐ Interview Scoring": page_scoring,
    "🏢 Company Mode":      page_company_mode,
    "🎓 Career Coach":      page_career_coach,
    "🗺️ Learning Roadmap":  page_roadmap,
    "📊 Analytics Dashboard":page_analytics,
    "📥 PDF Report":        page_pdf,
}

def main():
    try:
        initialize_database()
    except Exception:
        pass
    _init()
    sidebar()
    handler = PAGE_MAP.get(st.session_state.page, page_home)
    handler()

if __name__ == "__main__":
    main()
