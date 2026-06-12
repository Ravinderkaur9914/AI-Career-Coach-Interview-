"""
Interview Engine Module
Generates questions and manages AI mock interview conversations.
"""

import os
import json
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferMemory


# Company-specific interview frameworks
COMPANY_FRAMEWORKS = {
    "Amazon": {
        "principles": [
            "Customer Obsession", "Ownership", "Invent and Simplify",
            "Are Right A Lot", "Learn and Be Curious", "Hire and Develop the Best",
            "Insist on the Highest Standards", "Think Big", "Bias for Action",
            "Frugality", "Earn Trust", "Dive Deep", "Have Backbone",
            "Deliver Results"
        ],
        "question_style": "STAR method (Situation, Task, Action, Result)",
        "focus": "Leadership Principles with behavioral evidence"
    },
    "Google": {
        "principles": ["Googliness", "Leadership", "Cognitive Ability", "Role-Related Knowledge"],
        "question_style": "Behavioral + Technical + Case studies",
        "focus": "Structured problem-solving and data-driven thinking"
    },
    "Microsoft": {
        "principles": ["Growth Mindset", "Collaboration", "Customer Focus", "Diversity & Inclusion"],
        "question_style": "Scenario-based + Technical + Culture fit",
        "focus": "Problem-solving, collaboration, and growth mindset"
    },
}


class InterviewEngine:
    """
    Manages interview question generation and mock interview conversations.
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        self.conversation_history: List = []
        self.current_question_index = 0
        self.questions_asked: List[str] = []

    def generate_questions(
        self,
        resume_data: Dict[str, Any],
        job_description: str,
        target_role: str,
        company: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """
        Generate comprehensive interview questions based on resume and role.
        
        Args:
            resume_data: Structured resume analysis
            job_description: Target job description
            target_role: Target job role/title
            company: Optional company for company-specific questions
            
        Returns:
            Dictionary with categorized questions
        """
        skills = ", ".join(resume_data.get("skills", [])[:15])
        projects = "; ".join([p.get("name", "") for p in resume_data.get("projects", [])[:5]])
        experience = "; ".join([
            f"{e.get('role', '')} at {e.get('company', '')}"
            for e in resume_data.get("experience", [])[:3]
        ])

        company_context = ""
        if company and company in COMPANY_FRAMEWORKS:
            fw = COMPANY_FRAMEWORKS[company]
            company_context = f"""
COMPANY: {company}
Focus on: {fw['focus']}
Question style: {fw['question_style']}
Key principles: {', '.join(fw['principles'][:6])}
"""

        prompt = f"""You are a senior technical interviewer. Generate comprehensive interview questions.

CANDIDATE PROFILE:
- Target Role: {target_role}
- Key Skills: {skills}
- Projects: {projects}
- Experience: {experience}

JOB DESCRIPTION SUMMARY:
{job_description[:1000]}

{company_context}

Generate interview questions in JSON format with EXACTLY this structure:
{{
    "technical": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5",
        "Question 6",
        "Question 7",
        "Question 8",
        "Question 9",
        "Question 10"
    ],
    "project_based": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5"
    ],
    "behavioral": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5",
        "Question 6",
        "Question 7",
        "Question 8",
        "Question 9",
        "Question 10"
    ],
    "hr": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5"
    ],
    "scenario_based": [
        "Question 1",
        "Question 2",
        "Question 3",
        "Question 4",
        "Question 5"
    ],
    "company_specific": [
        "Question 1",
        "Question 2",
        "Question 3"
    ]
}}

Make questions specific to the candidate's background and the target role.
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
            raise RuntimeError(f"Question generation failed: {str(e)}")

    def start_interview(self, questions: Dict[str, List[str]], target_role: str):
        """Initialize a new mock interview session."""
        self.conversation_history = []
        self.questions_asked = []
        self.all_questions = (
            questions.get("technical", [])[:5] +
            questions.get("behavioral", [])[:3] +
            questions.get("project_based", [])[:2] +
            questions.get("hr", [])[:2]
        )
        self.current_question_index = 0
        self.target_role = target_role

        # System prompt for the AI interviewer
        self.system_prompt = f"""You are a professional interviewer conducting a mock interview for a {target_role} position.

Your role:
1. Ask interview questions naturally and professionally
2. Listen carefully to answers
3. Ask intelligent follow-up questions to dig deeper
4. Be encouraging but maintain professional standards
5. Ask 1-3 follow-up questions before moving to the next main question

Follow-up question triggers:
- If the candidate mentions a technology: ask HOW they used it
- If they describe a project: ask about challenges, results, metrics
- If they give a vague answer: ask for specific examples
- If they mention an achievement: ask about their specific contribution

Keep responses concise. Only ask ONE question at a time."""

    def get_next_question(self) -> Optional[str]:
        """Get the next main interview question."""
        if self.current_question_index < len(self.all_questions):
            question = self.all_questions[self.current_question_index]
            self.current_question_index += 1
            self.questions_asked.append(question)
            return question
        return None

    def process_answer(self, question: str, answer: str) -> str:
        """
        Process candidate's answer and generate intelligent follow-up.
        
        Args:
            question: The question that was asked
            answer: The candidate's answer
            
        Returns:
            AI interviewer's follow-up response
        """
        # Build conversation context
        messages = [SystemMessage(content=self.system_prompt)]

        # Add conversation history
        for msg in self.conversation_history[-6:]:  # Keep last 6 exchanges
            if msg["role"] == "interviewer":
                messages.append(AIMessage(content=msg["content"]))
            else:
                messages.append(HumanMessage(content=msg["content"]))

        # Add current exchange
        messages.append(AIMessage(content=f"Interview question: {question}"))
        messages.append(HumanMessage(content=answer))

        follow_up_prompt = """Based on the candidate's answer, decide:
1. If the answer needs more depth → ask ONE specific follow-up question
2. If the answer was complete → acknowledge briefly and say you'll move to the next question

Example follow-ups:
- "That's interesting. Which specific algorithm did you use and why?"
- "Can you share the metrics or results from that project?"
- "How did you handle a situation where that approach didn't work?"

Keep your response under 3 sentences. Ask only ONE question."""

        messages.append(HumanMessage(content=follow_up_prompt))

        try:
            response = self.llm.invoke(messages)
            follow_up = response.content.strip()

            # Update conversation history
            self.conversation_history.append({"role": "interviewer", "content": question})
            self.conversation_history.append({"role": "candidate", "content": answer})
            self.conversation_history.append({"role": "interviewer", "content": follow_up})

            return follow_up

        except Exception as e:
            return f"Thank you for that answer. Let's move on to the next question."

    def get_company_questions(self, company: str, role: str) -> List[str]:
        """Generate company-specific interview questions."""
        if company not in COMPANY_FRAMEWORKS:
            return []

        fw = COMPANY_FRAMEWORKS[company]
        prompt = f"""Generate 10 {company}-specific interview questions for a {role} candidate.

Focus on {company}'s values: {', '.join(fw['principles'][:8])}
Style: {fw['question_style']}

Return a JSON array of 10 questions:
["question1", "question2", ..., "question10"]

Make questions authentic to {company}'s actual interview style.
Return ONLY valid JSON array."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception:
            return [f"Tell me about a time you demonstrated {p}." for p in fw["principles"][:5]]
