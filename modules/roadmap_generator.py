"""
Roadmap Generator Module
Standalone wrapper that delegates to CareerCoach.generate_learning_roadmap().
Kept as a separate file per project specification.
"""

from __future__ import annotations
import os
import json
from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


class RoadmapGenerator:
    """
    Generates 30 / 60 / 90-day personalised learning roadmaps.

    Can be used independently of CareerCoach when only roadmap
    generation is needed.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.5,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    # ------------------------------------------------------------------
    def generate(
        self,
        weak_areas: List[str | Dict],
        target_role: str,
        current_skills: Optional[List[str]] = None,
        current_level: str = "intermediate",
    ) -> Dict[str, Any]:
        """
        Generate a complete 30/60/90-day roadmap.

        Args:
            weak_areas:     List of gap strings or dicts with 'area' key.
            target_role:    Target job title.
            current_skills: Skills the candidate already has.
            current_level:  beginner | intermediate | advanced

        Returns:
            Roadmap dict with roadmap_30_day, roadmap_60_day, roadmap_90_day,
            recommended_resources keys.
        """
        # Normalise weak_areas to strings
        gaps = []
        for a in weak_areas[:6]:
            if isinstance(a, dict):
                gaps.append(f"{a.get('area', '')} — {a.get('gap', '')}")
            else:
                gaps.append(str(a))

        skills_str = ", ".join(current_skills[:15]) if current_skills else "Not specified"

        prompt = f"""You are a world-class career coach and curriculum designer.
Create a detailed, actionable learning roadmap for a candidate.

PROFILE
- Target Role   : {target_role}
- Current Level : {current_level}
- Existing Skills: {skills_str}
- Key Gaps      : {'; '.join(gaps) or 'General improvement needed'}

Return ONLY a valid JSON object with exactly this schema (no markdown fences):
{{
  "roadmap_30_day": {{
    "goal": "<what the candidate will achieve in 30 days>",
    "focus": "<primary topic>",
    "weeks": [
      {{
        "week": 1,
        "theme": "<theme>",
        "daily_tasks": ["<task>", "<task>", "<task>"],
        "resources": ["<resource with URL if possible>", "<resource>"],
        "milestone": "<end-of-week milestone>"
      }},
      {{ "week": 2, "theme": "", "daily_tasks": [], "resources": [], "milestone": "" }},
      {{ "week": 3, "theme": "", "daily_tasks": [], "resources": [], "milestone": "" }},
      {{ "week": 4, "theme": "", "daily_tasks": [], "resources": [], "milestone": "" }}
    ],
    "success_metrics": ["<metric>", "<metric>", "<metric>"]
  }},
  "roadmap_60_day": {{
    "goal": "<60-day outcome>",
    "focus": "<building on month 1>",
    "key_activities": ["<activity>", "<activity>", "<activity>", "<activity>", "<activity>"],
    "projects_to_build": [
      {{"name": "<project>", "description": "<what to build>", "skills_practiced": ["<skill>", "<skill>"]}},
      {{"name": "<project>", "description": "<what to build>", "skills_practiced": ["<skill>", "<skill>"]}}
    ],
    "certifications": ["<cert or empty string>"],
    "success_metrics": ["<metric>", "<metric>", "<metric>"]
  }},
  "roadmap_90_day": {{
    "goal": "Job-ready and applying confidently",
    "focus": "Portfolio + interview readiness",
    "key_activities": ["<activity>", "<activity>", "<activity>", "<activity>"],
    "portfolio_targets": ["<item>", "<item>", "<item>"],
    "job_application_strategy": "<2-3 sentence strategy>",
    "networking_actions": ["<action>", "<action>", "<action>"],
    "success_metrics": ["<metric>", "<metric>", "<metric>"]
  }},
  "recommended_resources": {{
    "free_courses": ["<course with platform>", "<course>", "<course>"],
    "books": ["<title — author>", "<title — author>"],
    "practice_platforms": ["<platform>", "<platform>"],
    "communities": ["<community>", "<community>"]
  }}
}}"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            # Strip markdown fences if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:
            raise RuntimeError(f"Roadmap generation failed: {e}")

    # ------------------------------------------------------------------
    def generate_topic_plan(self, topic: str, days: int = 30) -> List[Dict]:
        """
        Generate a focused day-by-day plan for a single topic.

        Returns a list of {'day': N, 'task': str, 'resource': str} dicts.
        """
        prompt = f"""Create a {days}-day learning plan for: {topic}

Return ONLY a JSON array with {min(days, 30)} entries:
[
  {{"day": 1, "task": "<specific task>", "resource": "<resource name/URL>"}},
  ...
]
Each task should be achievable in 1-2 hours."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception:
            return [{"day": i, "task": f"Study {topic} — Day {i}", "resource": ""}
                    for i in range(1, min(days, 8) + 1)]
