"""
ATS Analyzer Module
Compares resume with job description and generates ATS match scores.

Uses Groq (via langchain_groq) for LLM analysis and a local
HuggingFace sentence-transformer model for embeddings, so no
OpenAI API key is required.
"""

import importlib
import os
import json
from typing import Dict, Any, List

try:
    ChatGroq = importlib.import_module("langchain_groq").ChatGroq
except ImportError:
    ChatGroq = None

try:
    HumanMessage = importlib.import_module("langchain.schema").HumanMessage
except ImportError:
    HumanMessage = importlib.import_module("langchain.schema.messages").HumanMessage

try:
    RecursiveCharacterTextSplitter = importlib.import_module("langchain.text_splitter").RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = importlib.import_module("langchain.text_splitter.text_splitter").RecursiveCharacterTextSplitter

from langchain_community.vectorstores import FAISS

try:
    HuggingFaceEmbeddings = importlib.import_module("langchain_huggingface").HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = importlib.import_module("langchain_community.embeddings").HuggingFaceEmbeddings


class ATSAnalyzer:
    """
    Applicant Tracking System analyzer.
    Compares resume content against job descriptions.
    """

    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            temperature=0.2,
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )

    def analyze(self, resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """
        Perform full ATS analysis comparing resume to job description.

        Args:
            resume_data: Structured resume data from ResumeParser
            job_description: Raw job description text

        Returns:
            ATS analysis results with score and recommendations
        """
        resume_text = self._build_resume_summary(resume_data)

        prompt = f"""You are an expert ATS (Applicant Tracking System) analyzer. 
Analyze the compatibility between this resume and job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide a detailed analysis and return ONLY a JSON object with this structure:
{{
    "ats_score": <number 0-100>,
    "match_percentage": <number 0-100>,
    "matched_skills": ["skill1", "skill2", ...],
    "missing_skills": ["skill1", "skill2", ...],
    "recommended_skills": ["skill1", "skill2", ...],
    "improvement_suggestions": [
        "suggestion1",
        "suggestion2",
        "suggestion3",
        "suggestion4",
        "suggestion5"
    ],
    "keyword_analysis": {{
        "present": ["keyword1", "keyword2"],
        "absent": ["keyword1", "keyword2"]
    }},
    "section_scores": {{
        "skills_match": <0-100>,
        "experience_match": <0-100>,
        "education_match": <0-100>,
        "overall_fit": <0-100>
    }},
    "summary": "2-3 sentence overall assessment"
}}

Be realistic and specific. Return ONLY valid JSON."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            result = json.loads(content)
            result["job_description"] = job_description
            return result

        except Exception as e:
            raise RuntimeError(f"ATS analysis failed: {str(e)}")

    def _build_resume_summary(self, resume_data: Dict[str, Any]) -> str:
        """Convert structured resume data to readable text for comparison."""
        lines = []

        if resume_data.get("skills"):
            lines.append(f"SKILLS: {', '.join(resume_data['skills'])}")

        if resume_data.get("experience"):
            lines.append("\nEXPERIENCE:")
            for exp in resume_data["experience"]:
                lines.append(f"- {exp.get('role', '')} at {exp.get('company', '')} ({exp.get('duration', '')})")
                for resp in exp.get("responsibilities", [])[:3]:
                    lines.append(f"  • {resp}")

        if resume_data.get("education"):
            lines.append("\nEDUCATION:")
            for edu in resume_data["education"]:
                lines.append(f"- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('year', '')})")

        if resume_data.get("projects"):
            lines.append("\nPROJECTS:")
            for proj in resume_data["projects"]:
                lines.append(f"- {proj.get('name', '')}: {proj.get('description', '')}")
                techs = proj.get("technologies", [])
                if techs:
                    lines.append(f"  Technologies: {', '.join(techs)}")

        return "\n".join(lines)

    def build_vector_store(self, resume_text: str, session_id: str) -> bool:
        """
        Build FAISS vector store from resume text for semantic search.

        Args:
            resume_text: Full resume text
            session_id: Session identifier for storing vectors

        Returns:
            True if successful
        """
        try:
            chunks = self.text_splitter.split_text(resume_text)
            vector_store = FAISS.from_texts(chunks, self.embeddings)

            store_path = os.path.join(
                os.getenv("VECTOR_STORE_PATH", "vector_store/"),
                session_id
            )
            os.makedirs(store_path, exist_ok=True)
            vector_store.save_local(store_path)
            return True
        except Exception as e:
            print(f"Vector store creation failed: {e}")
            return False

    def semantic_skill_match(self, skills: List[str], job_description: str) -> float:
        """
        Calculate semantic similarity between resume skills and job requirements.

        Returns:
            Similarity score 0-100
        """
        try:
            skills_text = " ".join(skills)
            skill_embedding = self.embeddings.embed_query(skills_text)
            job_embedding = self.embeddings.embed_query(job_description[:2000])

            import numpy as np
            skill_vec = np.array(skill_embedding)
            job_vec = np.array(job_embedding)
            cosine_sim = np.dot(skill_vec, job_vec) / (
                np.linalg.norm(skill_vec) * np.linalg.norm(job_vec)
            )
            return round(float(cosine_sim) * 100, 1)
        except Exception:
            return 0.0