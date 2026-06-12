"""
Scoring Engine Module
Evaluates interview answers and generates comprehensive scores.
"""

import os
import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


class ScoringEngine:
    """
    Evaluates interview performance across multiple dimensions.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        target_role: str,
        question_category: str = "technical",
    ) -> Dict[str, Any]:
        """
        Evaluate a single interview answer across multiple dimensions.
        
        Args:
            question: The interview question
            answer: The candidate's answer
            target_role: Target job role for context
            question_category: Category of question (technical/behavioral/hr)
            
        Returns:
            Detailed evaluation scores and feedback
        """
        prompt = f"""You are an expert interview evaluator. Score this interview answer objectively.

ROLE: {target_role}
QUESTION TYPE: {question_category}
QUESTION: {question}
CANDIDATE ANSWER: {answer}

Evaluate and return ONLY a JSON object:
{{
    "technical_score": <0-100, based on accuracy and depth of technical content>,
    "communication_score": <0-100, based on clarity, structure, and articulation>,
    "relevance_score": <0-100, based on how well the answer addresses the question>,
    "confidence_score": <0-100, inferred from answer completeness and specificity>,
    "overall_score": <0-100, weighted average>,
    "feedback": {{
        "positive": ["strength1", "strength2"],
        "improve": ["area1", "area2"],
        "suggestion": "One specific actionable improvement suggestion"
    }},
    "answer_quality": "excellent|good|average|needs_improvement",
    "keywords_used": ["keyword1", "keyword2"],
    "missed_keywords": ["keyword1", "keyword2"]
}}

Scoring guidelines:
- 90-100: Exceptional, exceeds expectations
- 75-89: Good, meets expectations well
- 60-74: Average, meets basic expectations
- 40-59: Below average, needs improvement
- 0-39: Poor, significant gaps

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
            return {
                "technical_score": 50,
                "communication_score": 50,
                "relevance_score": 50,
                "confidence_score": 50,
                "overall_score": 50,
                "feedback": {
                    "positive": ["Answer provided"],
                    "improve": ["Could not fully evaluate"],
                    "suggestion": "Provide more specific examples in your answers."
                },
                "answer_quality": "average",
                "keywords_used": [],
                "missed_keywords": []
            }

    def calculate_session_scores(
        self,
        responses: List[Dict[str, Any]],
        confidence_score: float = 70,
        ats_score: float = 70,
    ) -> Dict[str, float]:
        """
        Calculate aggregate scores for an entire interview session.
        
        Args:
            responses: List of evaluated answer dictionaries
            confidence_score: Score from confidence analyzer
            ats_score: ATS match score
            
        Returns:
            Aggregate scoring summary
        """
        if not responses:
            return {
                "technical_score": 0,
                "communication_score": 0,
                "confidence_score": confidence_score,
                "relevance_score": 0,
                "ats_score": ats_score,
                "interview_score": 0,
                "overall_score": 0,
            }

        # Calculate averages
        tech_scores = [r.get("technical_score", 50) for r in responses]
        comm_scores = [r.get("communication_score", 50) for r in responses]
        rel_scores = [r.get("relevance_score", 50) for r in responses]

        avg_technical = sum(tech_scores) / len(tech_scores)
        avg_communication = sum(comm_scores) / len(comm_scores)
        avg_relevance = sum(rel_scores) / len(rel_scores)

        # Interview score is weighted average of response scores
        interview_score = (avg_technical * 0.4 + avg_communication * 0.35 + avg_relevance * 0.25)

        # Overall score across all dimensions
        overall_score = (
            interview_score * 0.4 +
            confidence_score * 0.25 +
            ats_score * 0.35
        )

        return {
            "technical_score": round(avg_technical, 1),
            "communication_score": round(avg_communication, 1),
            "relevance_score": round(avg_relevance, 1),
            "confidence_score": round(confidence_score, 1),
            "ats_score": round(ats_score, 1),
            "interview_score": round(interview_score, 1),
            "overall_score": round(overall_score, 1),
        }

    def generate_interview_report(
        self,
        responses: List[Dict[str, Any]],
        scores: Dict[str, float],
        target_role: str,
    ) -> str:
        """
        Generate a narrative interview performance report.
        
        Args:
            responses: List of Q&A evaluations
            scores: Aggregate score dictionary
            target_role: Target role for context
            
        Returns:
            HTML-formatted performance report
        """
        responses_summary = "\n".join([
            f"Q: {r.get('question', 'N/A')}\nScore: {r.get('overall_score', 0)}/100"
            for r in responses[:5]
        ])

        prompt = f"""Generate a professional interview performance summary for a {target_role} candidate.

SCORES:
- Technical: {scores.get('technical_score', 0)}/100
- Communication: {scores.get('communication_score', 0)}/100
- Confidence: {scores.get('confidence_score', 0)}/100
- Overall: {scores.get('overall_score', 0)}/100

TOP RESPONSES:
{responses_summary}

Write a 3-paragraph professional assessment covering:
1. Overall performance and key strengths
2. Areas that need improvement with specific examples
3. Actionable next steps for the candidate

Keep it constructive, specific, and encouraging. Plain text only."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception:
            return f"Interview completed with an overall score of {scores.get('overall_score', 0)}/100."
