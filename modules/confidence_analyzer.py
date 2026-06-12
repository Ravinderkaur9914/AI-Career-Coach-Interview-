"""
Confidence Analyzer Module
Analyzes speaking confidence through text-based indicators.
Note: Full webcam analysis requires OpenCV/MediaPipe in local environment.
This module provides text-based confidence scoring + webcam stub.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage


class ConfidenceAnalyzer:
    """
    Analyzes interview confidence through multiple signals:
    - Text analysis (answer length, specificity, filler words)
    - Response time patterns
    - Optional: Webcam-based face/eye tracking (requires local setup)
    """

    # Filler words that indicate nervousness or lack of confidence
    FILLER_WORDS = [
        "um", "uh", "like", "you know", "basically", "literally",
        "actually", "honestly", "sort of", "kind of", "i think",
        "i guess", "maybe", "probably", "i mean"
    ]

    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.session_metrics: List[Dict] = []

    def analyze_text_confidence(self, answer: str, response_time_seconds: float = 30) -> Dict[str, Any]:
        """
        Analyze confidence signals from text answer.
        
        Args:
            answer: The candidate's answer text
            response_time_seconds: Time taken to respond
            
        Returns:
            Confidence metrics and score
        """
        word_count = len(answer.split())
        filler_count = sum(answer.lower().count(fw) for fw in self.FILLER_WORDS)
        filler_ratio = filler_count / max(word_count, 1)

        # Specificity signals
        has_numbers = any(char.isdigit() for char in answer)
        has_examples = any(word in answer.lower() for word in ["example", "instance", "specifically", "for instance", "such as"])
        has_action_words = any(word in answer.lower() for word in ["implemented", "built", "led", "achieved", "designed", "created"])

        # Length appropriateness (ideal: 100-300 words)
        length_score = min(100, max(20, word_count / 2)) if word_count < 50 else min(100, 100 - max(0, (word_count - 300) / 5))

        # Calculate sub-scores
        filler_score = max(0, 100 - (filler_ratio * 500))
        specificity_score = (
            (30 if has_numbers else 0) +
            (30 if has_examples else 0) +
            (40 if has_action_words else 0)
        )
        response_time_score = self._score_response_time(response_time_seconds)

        # Weighted confidence score
        confidence_score = (
            filler_score * 0.25 +
            specificity_score * 0.35 +
            length_score * 0.20 +
            response_time_score * 0.20
        )

        metrics = {
            "confidence_score": round(confidence_score, 1),
            "word_count": word_count,
            "filler_words_detected": filler_count,
            "filler_ratio": round(filler_ratio * 100, 1),
            "has_specific_examples": has_examples,
            "has_metrics_numbers": has_numbers,
            "has_action_words": has_action_words,
            "response_time_seconds": response_time_seconds,
            "sub_scores": {
                "filler_word_score": round(filler_score, 1),
                "specificity_score": round(specificity_score, 1),
                "length_score": round(length_score, 1),
                "response_time_score": round(response_time_score, 1),
            },
            "feedback": self._generate_text_feedback(filler_score, specificity_score, length_score, word_count)
        }

        self.session_metrics.append(metrics)
        return metrics

    def _score_response_time(self, seconds: float) -> float:
        """Score response time (ideal: 30-120 seconds for most questions)."""
        if seconds < 5:
            return 30   # Too quick, likely not thought through
        elif seconds < 15:
            return 60
        elif seconds <= 90:
            return 100  # Ideal range
        elif seconds <= 180:
            return 80
        else:
            return 50   # Too long

    def _generate_text_feedback(
        self,
        filler_score: float,
        specificity_score: float,
        length_score: float,
        word_count: int,
    ) -> List[str]:
        """Generate specific, actionable feedback items."""
        feedback = []

        if filler_score < 60:
            feedback.append("⚠️ Reduce filler words (um, uh, like) — practice pausing instead")
        else:
            feedback.append("✅ Good control of filler words")

        if specificity_score < 50:
            feedback.append("⚠️ Include specific examples, numbers, and measurable outcomes")
        elif specificity_score >= 80:
            feedback.append("✅ Excellent use of specific examples and metrics")
        else:
            feedback.append("✅ Reasonable level of specificity in answers")

        if word_count < 50:
            feedback.append("⚠️ Answers are too brief — elaborate more with context and details")
        elif word_count > 400:
            feedback.append("⚠️ Answers are too long — focus on the most relevant points")
        else:
            feedback.append("✅ Good answer length and detail level")

        return feedback

    def get_session_confidence_score(self) -> Dict[str, Any]:
        """
        Calculate aggregate confidence score for the entire session.
        
        Returns:
            Session-level confidence summary
        """
        if not self.session_metrics:
            return {"overall_score": 70, "trend": "neutral", "feedback": []}

        scores = [m["confidence_score"] for m in self.session_metrics]
        avg_score = sum(scores) / len(scores)

        # Calculate trend (improving, declining, or stable)
        if len(scores) >= 3:
            early_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
            late_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
            if late_avg > early_avg + 10:
                trend = "improving"
            elif late_avg < early_avg - 10:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"

        avg_filler = sum(m["filler_ratio"] for m in self.session_metrics) / len(self.session_metrics)
        specificity_count = sum(1 for m in self.session_metrics if m["has_specific_examples"])

        return {
            "overall_score": round(avg_score, 1),
            "trend": trend,
            "total_responses": len(self.session_metrics),
            "avg_filler_word_ratio": round(avg_filler, 1),
            "responses_with_examples": specificity_count,
            "score_progression": scores,
            "feedback": self._generate_session_feedback(avg_score, trend, avg_filler)
        }

    def _generate_session_feedback(self, score: float, trend: str, filler_ratio: float) -> List[str]:
        """Generate session-level confidence feedback."""
        feedback = []

        if score >= 80:
            feedback.append("🌟 Excellent overall confidence throughout the interview")
        elif score >= 65:
            feedback.append("✅ Good confidence level with room for improvement")
        else:
            feedback.append("📈 Work on building more confident communication patterns")

        if trend == "improving":
            feedback.append("📈 Your confidence improved as the interview progressed — great adaptation!")
        elif trend == "declining":
            feedback.append("⚠️ Confidence decreased later — practice managing interview fatigue")

        if filler_ratio < 2:
            feedback.append("✅ Minimal filler words — very professional communication")
        elif filler_ratio > 10:
            feedback.append("⚠️ High filler word usage — practice the pause instead of 'um'")

        return feedback

    def analyze_webcam_confidence(self) -> Dict[str, Any]:
        """
        Webcam-based confidence analysis.
        Returns simulated data in cloud environment.
        For production: requires OpenCV + MediaPipe.
        """
        # In cloud/Streamlit Cloud environment, return guidance
        return {
            "available": False,
            "message": "Webcam analysis requires local installation with OpenCV and MediaPipe.",
            "setup_instructions": [
                "Install: pip install opencv-python mediapipe",
                "Run the app locally (not on Streamlit Cloud)",
                "Grant camera permissions when prompted",
                "The app will automatically detect eye contact and head movement"
            ],
            "simulated_score": 75,
        }

    def reset_session(self):
        """Reset metrics for a new interview session."""
        self.session_metrics = []
