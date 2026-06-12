"""
Career Coach Module
Generates personalized career guidance, recommendations, and learning roadmaps.
"""

import os
import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
try:
    import importlib

    HumanMessage = importlib.import_module("langchain.schema").HumanMessage
except Exception:  # pragma: no cover - fallback for environments without langchain installed
    class HumanMessage:
        """Lightweight fallback for langchain.schema.HumanMessage used by this module."""

        def __init__(self, content: str):
            self.content = content


class CareerCoach:
    """
    AI-powered career coach that provides personalized guidance
    based on resume analysis, interview performance, and career goals.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.6,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def generate_career_analysis(
        self,
        resume_data: Dict[str, Any],
        ats_analysis: Optional[Dict[str, Any]],
        scores: Dict[str, float],
        target_role: str,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive career coaching analysis.
        
        Args:
            resume_data: Structured resume data
            ats_analysis: ATS comparison results
            scores: Interview and overall scores
            target_role: Candidate's target job role
            
        Returns:
            Detailed career coaching recommendations
        """
        skills = ", ".join(resume_data.get("skills", [])[:20])
        missing_skills = ", ".join(ats_analysis.get("missing_skills", [])[:10]) if ats_analysis else "Unknown"
        weaknesses = ", ".join(resume_data.get("weaknesses", []))

        prompt = f"""You are an expert career coach with 20+ years of experience in talent development.
Provide comprehensive career coaching for this candidate.

CANDIDATE PROFILE:
- Target Role: {target_role}
- Current Skills: {skills}
- Resume Weaknesses: {weaknesses}
- Missing Skills for Target Role: {missing_skills}

PERFORMANCE SCORES:
- ATS Match Score: {scores.get('ats_score', 0)}/100
- Interview Score: {scores.get('interview_score', 0)}/100
- Technical Score: {scores.get('technical_score', 0)}/100
- Communication Score: {scores.get('communication_score', 0)}/100
- Confidence Score: {scores.get('confidence_score', 0)}/100
- Overall Score: {scores.get('overall_score', 0)}/100

Generate a comprehensive career coaching plan as JSON:
{{
    "overall_assessment": "3-4 sentence assessment of readiness for target role",
    "strong_areas": [
        {{"area": "area name", "evidence": "why this is a strength", "leverage": "how to use it"}},
        {{"area": "area name", "evidence": "why this is a strength", "leverage": "how to use it"}},
        {{"area": "area name", "evidence": "why this is a strength", "leverage": "how to use it"}}
    ],
    "weak_areas": [
        {{"area": "area name", "gap": "specific gap", "impact": "career impact", "priority": "high|medium|low"}},
        {{"area": "area name", "gap": "specific gap", "impact": "career impact", "priority": "high|medium|low"}},
        {{"area": "area name", "gap": "specific gap", "impact": "career impact", "priority": "high|medium|low"}},
        {{"area": "area name", "gap": "specific gap", "impact": "career impact", "priority": "high|medium|low"}}
    ],
    "immediate_actions": [
        "Action 1 - do within this week",
        "Action 2 - do within this week",
        "Action 3 - do within this week"
    ],
    "career_path_options": [
        {{"role": "role name", "timeline": "X months", "fit_score": 85, "reason": "why suitable"}},
        {{"role": "role name", "timeline": "X months", "fit_score": 70, "reason": "why suitable"}},
        {{"role": "role name", "timeline": "X months", "fit_score": 60, "reason": "why suitable"}}
    ],
    "interview_improvement_tips": [
        "Tip 1 specific to their performance",
        "Tip 2 specific to their performance",
        "Tip 3 specific to their performance",
        "Tip 4 specific to their performance",
        "Tip 5 specific to their performance"
    ],
    "market_insights": {{
        "demand_level": "high|medium|low",
        "avg_salary_range": "estimated range for target role",
        "top_hiring_companies": ["company1", "company2", "company3"],
        "emerging_skills": ["skill1", "skill2", "skill3"]
    }}
}}

Return ONLY valid JSON."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            return json.loads(content)

        except Exception as e:
            raise RuntimeError(f"Career analysis failed: {str(e)}")

    def generate_learning_roadmap(
        self,
        weak_areas: List[Dict],
        target_role: str,
        current_level: str = "intermediate",
    ) -> Dict[str, Any]:
        """
        Generate 30/60/90-day learning roadmaps.
        
        Args:
            weak_areas: List of identified weak areas
            target_role: Target job role
            current_level: Current skill level (beginner/intermediate/advanced)
            
        Returns:
            Structured learning roadmap for 30, 60, and 90 days
        """
        gaps = "; ".join([a.get("area", "") + ": " + a.get("gap", "") for a in weak_areas[:5]])

        prompt = f"""Create a detailed, actionable learning roadmap for a {current_level}-level candidate targeting {target_role}.

KEY GAPS TO ADDRESS: {gaps}

Generate a structured roadmap as JSON:
{{
    "roadmap_30_day": {{
        "goal": "What will be achieved in 30 days",
        "focus": "Primary focus area",
        "weeks": [
            {{
                "week": 1,
                "theme": "week theme",
                "daily_tasks": ["task1", "task2", "task3"],
                "resources": ["resource1", "resource2"],
                "milestone": "what to achieve by end of week"
            }},
            {{
                "week": 2,
                "theme": "week theme",
                "daily_tasks": ["task1", "task2", "task3"],
                "resources": ["resource1", "resource2"],
                "milestone": "what to achieve by end of week"
            }},
            {{
                "week": 3,
                "theme": "week theme",
                "daily_tasks": ["task1", "task2", "task3"],
                "resources": ["resource1", "resource2"],
                "milestone": "what to achieve by end of week"
            }},
            {{
                "week": 4,
                "theme": "week theme",
                "daily_tasks": ["task1", "task2", "task3"],
                "resources": ["resource1", "resource2"],
                "milestone": "what to achieve by end of week"
            }}
        ],
        "success_metrics": ["metric1", "metric2", "metric3"]
    }},
    "roadmap_60_day": {{
        "goal": "What will be achieved in 60 days",
        "focus": "Building on 30-day foundation",
        "key_activities": [
            "Activity 1",
            "Activity 2",
            "Activity 3",
            "Activity 4",
            "Activity 5"
        ],
        "projects_to_build": [
            {{"name": "project name", "description": "what to build", "skills_practiced": ["skill1", "skill2"]}},
            {{"name": "project name", "description": "what to build", "skills_practiced": ["skill1", "skill2"]}}
        ],
        "certifications": ["cert1 if applicable", "cert2 if applicable"],
        "success_metrics": ["metric1", "metric2", "metric3"]
    }},
    "roadmap_90_day": {{
        "goal": "Job-ready status",
        "focus": "Portfolio and interview readiness",
        "key_activities": [
            "Activity 1",
            "Activity 2",
            "Activity 3",
            "Activity 4"
        ],
        "portfolio_targets": ["portfolio item 1", "portfolio item 2", "portfolio item 3"],
        "job_application_strategy": "specific strategy for applying to target roles",
        "networking_actions": ["action1", "action2", "action3"],
        "success_metrics": ["metric1", "metric2", "metric3"]
    }},
    "recommended_resources": {{
        "free_courses": ["resource1", "resource2", "resource3"],
        "books": ["book1", "book2"],
        "practice_platforms": ["platform1", "platform2"],
        "communities": ["community1", "community2"]
    }}
}}

Be specific, realistic, and actionable. Return ONLY valid JSON."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            return json.loads(content)

        except Exception as e:
            raise RuntimeError(f"Roadmap generation failed: {str(e)}")
