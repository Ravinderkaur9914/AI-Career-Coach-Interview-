"""
PDF Report Generator Module
Creates downloadable multi-section PDF reports using ReportLab.
Sections: Cover · Scores · Resume · ATS · Interview Transcript · Career Coach · Roadmap
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
    TableStyle,
)

# ── palette ───────────────────────────────────────────────────────────────────
PRIMARY   = colors.HexColor("#1E3A5F")
ACCENT    = colors.HexColor("#00B4D8")
SUCCESS   = colors.HexColor("#06D6A0")
WARNING   = colors.HexColor("#FFB703")
DANGER    = colors.HexColor("#EF476F")
LIGHT     = colors.HexColor("#F8F9FA")
DARK_TEXT = colors.HexColor("#2D3436")


class PDFReportGenerator:
    """Generates professional PDF career coaching reports."""

    def __init__(self):
        self.reports_path = os.getenv("REPORTS_PATH", "reports/")
        os.makedirs(self.reports_path, exist_ok=True)
        base = getSampleStyleSheet()

        self.title_style = ParagraphStyle(
            "CTitle", parent=base["Title"], fontSize=26, textColor=PRIMARY,
            spaceAfter=6, fontName="Helvetica-Bold", alignment=TA_CENTER)

        self.h1 = ParagraphStyle(
            "CH1", parent=base["Heading1"], fontSize=15, textColor=PRIMARY,
            spaceBefore=16, spaceAfter=8, fontName="Helvetica-Bold")

        self.h2 = ParagraphStyle(
            "CH2", parent=base["Heading2"], fontSize=12, textColor=ACCENT,
            spaceBefore=10, spaceAfter=5, fontName="Helvetica-Bold")

        self.body = ParagraphStyle(
            "CBody", parent=base["Normal"], fontSize=10, textColor=DARK_TEXT,
            spaceAfter=4, fontName="Helvetica", leading=14, alignment=TA_JUSTIFY)

        self.bullet = ParagraphStyle(
            "CBullet", parent=base["Normal"], fontSize=10, textColor=DARK_TEXT,
            spaceAfter=3, leftIndent=15, fontName="Helvetica")

        self.caption = ParagraphStyle(
            "CCaption", parent=base["Normal"], fontSize=8, textColor=colors.gray,
            alignment=TA_CENTER)

    # ── public API ────────────────────────────────────────────────────────────

    def generate_report(
        self,
        session_id: str,
        resume_data: Optional[Dict[str, Any]],
        ats_analysis: Optional[Dict[str, Any]],
        scores: Optional[Dict[str, float]],
        career_recommendations: Optional[Dict[str, Any]],
        roadmap: Optional[Dict[str, Any]],
        interview_responses: Optional[List[Dict[str, Any]]] = None,
        target_role: str = "Target Role",
        candidate_name: str = "Candidate",
    ) -> str:
        """Build and save the PDF; return the file path."""
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"career_report_{session_id[:8]}_{ts}.pdf"
        path = os.path.join(self.reports_path, name)

        doc = SimpleDocTemplate(path, pagesize=A4,
                                rightMargin=2*cm, leftMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        story: list = []

        story += self._cover(candidate_name, target_role)
        story.append(PageBreak())

        if scores:
            story += self._scores_section(scores)
            story.append(Spacer(1, .3*inch))

        if resume_data:
            story += self._resume_section(resume_data)
            story.append(Spacer(1, .3*inch))

        if ats_analysis:
            story += self._ats_section(ats_analysis)
            story.append(PageBreak())

        if interview_responses:
            story += self._interview_section(interview_responses)
            story.append(Spacer(1, .3*inch))

        if career_recommendations:
            story += self._coaching_section(career_recommendations)
            story.append(Spacer(1, .3*inch))

        if roadmap:
            story += self._roadmap_section(roadmap)

        # footer
        story += [
            Spacer(1, .5*inch),
            HRFlowable(width="100%", thickness=1, color=ACCENT),
            Spacer(1, .1*inch),
            Paragraph(
                f"Report generated {datetime.now().strftime('%B %d, %Y at %I:%M %p')} · AI Career Coach",
                self.caption),
        ]

        doc.build(story)
        return path

    # ── section builders ──────────────────────────────────────────────────────

    def _cover(self, name: str, role: str) -> list:
        e = [Spacer(1, 1.5*inch)]
        e.append(Paragraph("🎯 AI Career Coach", self.title_style))
        e.append(Paragraph("Interview Performance Report", ParagraphStyle(
            "Sub", fontSize=16, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=30)))
        e.append(HRFlowable(width="80%", thickness=2, color=ACCENT))
        e.append(Spacer(1, .5*inch))
        data = [["Candidate:", name], ["Target Role:", role],
                ["Report Date:", datetime.now().strftime("%B %d, %Y")]]
        t = Table(data, colWidths=[2*inch, 4*inch])
        t.setStyle(TableStyle([
            ("FONTNAME",  (0,0),(-1,-1),"Helvetica"),
            ("FONTSIZE",  (0,0),(-1,-1),12),
            ("FONTNAME",  (0,0),(0,-1),"Helvetica-Bold"),
            ("TEXTCOLOR", (0,0),(0,-1), PRIMARY),
            ("ALIGN",     (0,0),(-1,-1),"LEFT"),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ]))
        e.append(t)
        return e

    def _scores_section(self, scores: Dict[str, float]) -> list:
        e = [Paragraph("📊 Performance Scores", self.h1),
             HRFlowable(width="100%", thickness=1, color=colors.lightgrey),
             Spacer(1, .1*inch)]

        rows = [["Metric","Score","Rating","Description"]]
        items = [
            ("ATS Match Score",      scores.get("ats_score",0),          "Resume fit"),
            ("Technical Score",      scores.get("technical_score",0),    "Technical depth"),
            ("Communication Score",  scores.get("communication_score",0),"Clarity & structure"),
            ("Confidence Score",     scores.get("confidence_score",0),   "Delivery confidence"),
            ("Interview Score",      scores.get("interview_score",0),    "Overall interview"),
            ("Overall Score",        scores.get("overall_score",0),      "Composite rating"),
        ]
        for nm,sc,desc in items:
            rat = "Excellent" if sc>=80 else "Good" if sc>=65 else "Average" if sc>=50 else "Needs Work"
            rows.append([nm, f"{sc:.0f}/100", rat, desc])

        t = Table(rows, colWidths=[1.8*inch, .9*inch, 1.1*inch, 3*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0), PRIMARY),
            ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
            ("FONTNAME",   (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0),(-1,-1), 9),
            ("ALIGN",      (1,0),(2,-1), "CENTER"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[LIGHT, colors.white]),
            ("GRID",       (0,0),(-1,-1), .5, colors.lightgrey),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("TOPPADDING",   (0,0),(-1,-1), 6),
        ]))
        e.append(t)
        return e

    def _resume_section(self, data: Dict[str,Any]) -> list:
        e = [Paragraph("📄 Resume Analysis", self.h1),
             HRFlowable(width="100%", thickness=1, color=colors.lightgrey),
             Spacer(1, .1*inch)]

        if data.get("summary"):
            e += [Paragraph("Professional Summary", self.h2),
                  Paragraph(data["summary"], self.body)]

        if data.get("skills"):
            e.append(Paragraph("Technical Skills", self.h2))
            e.append(Paragraph(" • ".join(data["skills"]), self.body))

        if data.get("strengths"):
            e.append(Paragraph("Key Strengths", self.h2))
            for s in data["strengths"][:5]:
                e.append(Paragraph(f"✅  {s}", self.bullet))

        if data.get("weaknesses"):
            e.append(Paragraph("Improvement Areas", self.h2))
            for w in data["weaknesses"]:
                e.append(Paragraph(f"⚠  {w}", self.bullet))

        if data.get("experience"):
            e.append(Paragraph("Work Experience", self.h2))
            for exp in data["experience"][:4]:
                e.append(Paragraph(
                    f"<b>{exp.get('role','')} @ {exp.get('company','')}</b>  ({exp.get('duration','')})",
                    self.bullet))
                for r in exp.get("responsibilities",[])[:3]:
                    e.append(Paragraph(f"    • {r}", self.bullet))

        return e

    def _ats_section(self, r: Dict[str,Any]) -> list:
        e = [Paragraph("🎯 ATS & Job Fit Analysis", self.h1),
             HRFlowable(width="100%", thickness=1, color=colors.lightgrey),
             Spacer(1, .1*inch)]

        e.append(Paragraph(f"ATS Match Score: {r.get('ats_score',0):.0f}/100", self.h2))
        if r.get("summary"):
            e.append(Paragraph(r["summary"], self.body))

        if r.get("missing_skills"):
            e.append(Paragraph("Missing Skills", self.h2))
            for s in r["missing_skills"][:10]:
                e.append(Paragraph(f"❌  {s}", self.bullet))

        if r.get("recommended_skills"):
            e.append(Paragraph("Recommended Skills to Add", self.h2))
            for s in r["recommended_skills"][:8]:
                e.append(Paragraph(f"📌  {s}", self.bullet))

        if r.get("improvement_suggestions"):
            e.append(Paragraph("Resume Improvement Suggestions", self.h2))
            for i,s in enumerate(r["improvement_suggestions"][:5], 1):
                e.append(Paragraph(f"{i}.  {s}", self.bullet))

        return e

    def _interview_section(self, responses: List[Dict[str,Any]]) -> list:
        e = [Paragraph("💬 Interview Transcript & Scores", self.h1),
             HRFlowable(width="100%", thickness=1, color=colors.lightgrey),
             Spacer(1, .1*inch)]

        for i, resp in enumerate(responses[:15], 1):
            e.append(Paragraph(f"Q{i}: {resp.get('question','')}", self.h2))

            answer = resp.get("answer","")
            if answer:
                e.append(Paragraph(f"<i>Answer:</i> {answer[:400]}{'…' if len(answer)>400 else ''}",
                                   self.body))

            # Score row
            ts  = resp.get("technical_score",0)
            cs  = resp.get("communication_score", resp.get("communication_score",0))
            rs  = resp.get("relevance_score",0)
            ovr = resp.get("overall_score", round((ts+cs+rs)/3, 1) if ts+cs+rs else 0)
            score_row = [["Technical","Communication","Relevance","Overall"],
                         [f"{ts:.0f}", f"{cs:.0f}", f"{rs:.0f}", f"{ovr:.0f}"]]
            st2 = Table(score_row, colWidths=[1.3*inch]*4)
            st2.setStyle(TableStyle([
                ("BACKGROUND", (0,0),(-1,0), ACCENT),
                ("TEXTCOLOR",  (0,0),(-1,0), colors.white),
                ("FONTNAME",   (0,0),(-1,-1),"Helvetica-Bold"),
                ("FONTSIZE",   (0,0),(-1,-1), 9),
                ("ALIGN",      (0,0),(-1,-1),"CENTER"),
                ("GRID",       (0,0),(-1,-1),.5, colors.lightgrey),
                ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("TOPPADDING",   (0,0),(-1,-1),5),
            ]))
            e += [st2, Spacer(1, .15*inch)]

        return e

    def _coaching_section(self, rec: Dict[str,Any]) -> list:
        e = [Paragraph("🎓 Career Coaching Insights", self.h1),
             HRFlowable(width="100%", thickness=1, color=colors.lightgrey),
             Spacer(1, .1*inch)]

        if rec.get("overall_assessment"):
            e.append(Paragraph(rec["overall_assessment"], self.body))

        if rec.get("strong_areas"):
            e.append(Paragraph("Strong Areas", self.h2))
            for a in rec["strong_areas"][:3]:
                txt = f"✅  {a.get('area','')} — {a.get('evidence','')}" if isinstance(a,dict) else f"✅  {a}"
                e.append(Paragraph(txt, self.bullet))

        if rec.get("weak_areas"):
            e.append(Paragraph("Focus Areas", self.h2))
            for a in rec["weak_areas"][:4]:
                txt = f"📌  {a.get('area','')} [{a.get('priority','').upper()}]: {a.get('gap','')}" if isinstance(a,dict) else f"📌  {a}"
                e.append(Paragraph(txt, self.bullet))

        if rec.get("immediate_actions"):
            e.append(Paragraph("Immediate Actions", self.h2))
            for i,ac in enumerate(rec["immediate_actions"],1):
                e.append(Paragraph(f"{i}.  {ac}", self.bullet))

        if rec.get("interview_improvement_tips"):
            e.append(Paragraph("Interview Tips", self.h2))
            for tip in rec["interview_improvement_tips"][:5]:
                e.append(Paragraph(f"💡  {tip}", self.bullet))

        return e

    def _roadmap_section(self, rm: Dict[str,Any]) -> list:
        e = [Paragraph("🗺️ Learning Roadmap", self.h1),
             HRFlowable(width="100%", thickness=1, color=colors.lightgrey),
             Spacer(1, .1*inch)]

        for key, label in [("roadmap_30_day","30-Day Plan"),
                            ("roadmap_60_day","60-Day Plan"),
                            ("roadmap_90_day","90-Day Plan")]:
            plan = rm.get(key,{})
            if not plan: continue
            e.append(Paragraph(f"📅 {label}", self.h2))
            if plan.get("goal"):
                e.append(Paragraph(f"<b>Goal:</b> {plan['goal']}", self.body))
            activities = plan.get("key_activities",[])
            if not activities:
                activities = [wk.get("milestone","") for wk in plan.get("weeks",[])]
            for ac in activities[:5]:
                if ac:
                    e.append(Paragraph(f"•  {ac}", self.bullet))
            if plan.get("success_metrics"):
                for m in plan["success_metrics"][:3]:
                    e.append(Paragraph(f"✅  {m}", self.bullet))
            e.append(Spacer(1, .1*inch))

        res = rm.get("recommended_resources",{})
        if res:
            e.append(Paragraph("📚 Recommended Resources", self.h2))
            for k,lbl in [("free_courses","Courses"),("books","Books"),
                          ("practice_platforms","Practice"),("communities","Communities")]:
                items = res.get(k,[])
                if items:
                    e.append(Paragraph(f"<b>{lbl}:</b> {' · '.join(items[:3])}", self.bullet))

        return e
