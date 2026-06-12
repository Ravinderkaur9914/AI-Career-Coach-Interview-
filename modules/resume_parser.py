"""
Resume Parser Module
Extracts and analyzes resume content using LangChain + Groq.
"""

import os
import json
import PyPDF2
from io import BytesIO
from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


class ResumeParser:
    """Handles resume PDF parsing and AI-powered analysis."""

    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY"),
        )

    def extract_text_from_pdf(self, pdf_file) -> str:
        """
        Extract raw text from a PDF file.
        
        Args:
            pdf_file: File-like object or bytes of the PDF
            
        Returns:
            Extracted text string
        """
        try:
            if isinstance(pdf_file, bytes):
                pdf_file = BytesIO(pdf_file)

            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract PDF text: {str(e)}")

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Use AI to analyze and structure resume content.
        
        Args:
            resume_text: Raw text extracted from resume
            
        Returns:
            Structured resume data dictionary
        """
        prompt = f"""You are an expert resume analyzer. Analyze the following resume and extract structured information.

RESUME TEXT:
{resume_text}

Extract and return a JSON object with EXACTLY this structure:
{{
    "skills": ["skill1", "skill2", ...],
    "projects": [
        {{"name": "project name", "description": "brief description", "technologies": ["tech1", "tech2"]}}
    ],
    "education": [
        {{"degree": "degree name", "institution": "university name", "year": "graduation year", "gpa": "if mentioned"}}
    ],
    "experience": [
        {{"role": "job title", "company": "company name", "duration": "time period", "responsibilities": ["resp1", "resp2"]}}
    ],
    "summary": "3-4 sentence professional summary of this candidate",
    "strengths": ["strength1", "strength2", "strength3", "strength4", "strength5"],
    "weaknesses": ["weakness1", "weakness2", "weakness3"]
}}

Return ONLY valid JSON, no markdown, no explanation."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # Clean JSON if wrapped in markdown
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            result = json.loads(content)
            result["raw_text"] = resume_text
            return result

        except json.JSONDecodeError as e:
            # Fallback: return basic structure
            return {
                "raw_text": resume_text,
                "skills": self._extract_skills_fallback(resume_text),
                "projects": [],
                "education": [],
                "experience": [],
                "summary": "Resume analysis encountered an issue. Please review manually.",
                "strengths": ["Technical background", "Project experience"],
                "weaknesses": ["Could not fully analyze resume"],
            }
        except Exception as e:
            raise RuntimeError(f"Resume analysis failed: {str(e)}")

    def _extract_skills_fallback(self, text: str) -> list:
        """Simple keyword-based skill extraction as fallback."""
        common_skills = [
            "Python", "Java", "JavaScript", "SQL", "R", "C++", "C#",
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes",
            "React", "Node.js", "Django", "Flask", "FastAPI",
            "Git", "Linux", "Agile", "Scrum",
            "Pandas", "NumPy", "Scikit-learn", "Tableau", "Power BI"
        ]
        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        return found_skills

    def save_to_uploads(self, pdf_bytes: bytes, filename: str) -> str:
        """Save uploaded PDF to the uploads directory."""
        uploads_path = os.getenv("UPLOADS_PATH", "uploads/")
        os.makedirs(uploads_path, exist_ok=True)
        filepath = os.path.join(uploads_path, filename)
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
        return filepath