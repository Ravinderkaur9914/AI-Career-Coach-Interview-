"""
Database Module - SQLite setup and operations
Handles all database operations for the AI Career Coach application.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List


DATABASE_PATH = os.getenv("DATABASE_PATH", "database/career_coach.db")


def get_connection() -> sqlite3.Connection:
    """Create and return a database connection."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Initialize all database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Resume data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            raw_text TEXT,
            skills TEXT,
            projects TEXT,
            education TEXT,
            experience TEXT,
            summary TEXT,
            strengths TEXT,
            weaknesses TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    # ATS analysis table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ats_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            job_description TEXT,
            ats_score REAL,
            missing_skills TEXT,
            recommended_skills TEXT,
            improvement_suggestions TEXT,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    # Interview questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            category TEXT,
            question TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    # Interview responses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            question TEXT,
            answer TEXT,
            follow_up TEXT,
            technical_score REAL,
            communication_score REAL,
            relevance_score REAL,
            responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    # Scores table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            ats_score REAL DEFAULT 0,
            interview_score REAL DEFAULT 0,
            confidence_score REAL DEFAULT 0,
            technical_score REAL DEFAULT 0,
            communication_score REAL DEFAULT 0,
            overall_score REAL DEFAULT 0,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    # Career recommendations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            weak_areas TEXT,
            strong_areas TEXT,
            recommendations TEXT,
            roadmap_30 TEXT,
            roadmap_60 TEXT,
            roadmap_90 TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


def save_resume_data(session_id: str, data: Dict[str, Any]) -> bool:
    """Save resume analysis data to database."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO resume_data 
            (session_id, raw_text, skills, projects, education, experience, summary, strengths, weaknesses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            data.get("raw_text", ""),
            json.dumps(data.get("skills", [])),
            json.dumps(data.get("projects", [])),
            json.dumps(data.get("education", [])),
            json.dumps(data.get("experience", [])),
            data.get("summary", ""),
            json.dumps(data.get("strengths", [])),
            json.dumps(data.get("weaknesses", [])),
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving resume data: {e}")
        return False


def get_resume_data(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve resume data for a session."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resume_data WHERE session_id = ? ORDER BY id DESC LIMIT 1", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "raw_text": row["raw_text"],
                "skills": json.loads(row["skills"] or "[]"),
                "projects": json.loads(row["projects"] or "[]"),
                "education": json.loads(row["education"] or "[]"),
                "experience": json.loads(row["experience"] or "[]"),
                "summary": row["summary"],
                "strengths": json.loads(row["strengths"] or "[]"),
                "weaknesses": json.loads(row["weaknesses"] or "[]"),
            }
        return None
    except Exception as e:
        print(f"Error retrieving resume data: {e}")
        return None


def save_ats_analysis(session_id: str, data: Dict[str, Any]) -> bool:
    """Save ATS analysis results."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ats_analysis 
            (session_id, job_description, ats_score, missing_skills, recommended_skills, improvement_suggestions)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            data.get("job_description", ""),
            data.get("ats_score", 0),
            json.dumps(data.get("missing_skills", [])),
            json.dumps(data.get("recommended_skills", [])),
            json.dumps(data.get("improvement_suggestions", [])),
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving ATS analysis: {e}")
        return False


def save_interview_response(session_id: str, data: Dict[str, Any]) -> bool:
    """Save an interview Q&A pair with scores."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO interview_responses 
            (session_id, question, answer, follow_up, technical_score, communication_score, relevance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            data.get("question", ""),
            data.get("answer", ""),
            data.get("follow_up", ""),
            data.get("technical_score", 0),
            data.get("communication_score", 0),
            data.get("relevance_score", 0),
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving interview response: {e}")
        return False


def get_interview_responses(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve all interview responses for a session."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interview_responses WHERE session_id = ? ORDER BY responded_at", (session_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error retrieving responses: {e}")
        return []


def save_scores(session_id: str, scores: Dict[str, float]) -> bool:
    """Save scoring results."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO scores 
            (session_id, ats_score, interview_score, confidence_score, technical_score, communication_score, overall_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            scores.get("ats_score", 0),
            scores.get("interview_score", 0),
            scores.get("confidence_score", 0),
            scores.get("technical_score", 0),
            scores.get("communication_score", 0),
            scores.get("overall_score", 0),
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving scores: {e}")
        return False


def get_scores(session_id: str) -> Optional[Dict[str, float]]:
    """Retrieve scores for a session."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM scores WHERE session_id = ? ORDER BY id DESC LIMIT 1", (session_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error retrieving scores: {e}")
        return None


def save_career_recommendations(session_id: str, data: Dict[str, Any]) -> bool:
    """Save career coaching recommendations."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO career_recommendations 
            (session_id, weak_areas, strong_areas, recommendations, roadmap_30, roadmap_60, roadmap_90)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            json.dumps(data.get("weak_areas", [])),
            json.dumps(data.get("strong_areas", [])),
            json.dumps(data.get("recommendations", [])),
            json.dumps(data.get("roadmap_30", [])),
            json.dumps(data.get("roadmap_60", [])),
            json.dumps(data.get("roadmap_90", [])),
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving recommendations: {e}")
        return False


def get_career_recommendations(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve career recommendations for a session."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM career_recommendations WHERE session_id = ? ORDER BY id DESC LIMIT 1", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "weak_areas": json.loads(row["weak_areas"] or "[]"),
                "strong_areas": json.loads(row["strong_areas"] or "[]"),
                "recommendations": json.loads(row["recommendations"] or "[]"),
                "roadmap_30": json.loads(row["roadmap_30"] or "[]"),
                "roadmap_60": json.loads(row["roadmap_60"] or "[]"),
                "roadmap_90": json.loads(row["roadmap_90"] or "[]"),
            }
        return None
    except Exception as e:
        print(f"Error retrieving recommendations: {e}")
        return None
