"""
API routes for NLP services (resume parsing, tailoring, talking points).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os

from app.nlp.resume_parser import ResumeParser
from app.nlp.resume_tailor import ResumeTailor
from app.nlp.talking_points import TalkingPointsGenerator

router = APIRouter(prefix="/api/v1/nlp", tags=["NLP"])

# Initialize services
resume_parser = ResumeParser()
resume_tailor = ResumeTailor()
talking_points_gen = TalkingPointsGenerator()


class TailoringRequest(BaseModel):
    """Request model for resume tailoring."""
    resume_text: str
    job_description: str
    company_name: Optional[str] = None


class TalkingPointsRequest(BaseModel):
    """Request model for talking points generation."""
    company_name: str
    company_info: dict
    resume_data: dict
    job_description: Optional[str] = None
    news_articles: Optional[List[dict]] = None


@router.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse resume PDF and extract structured information.

    Args:
        file: PDF resume file

    Returns:
        Parsed resume data
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Parse resume
        result = resume_parser.parse_pdf(temp_path)

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to parse resume")
            )

        return result

    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/tailor-resume")
async def tailor_resume(request: TailoringRequest):
    """
    Tailor resume to match job description.

    Args:
        request: Tailoring request with resume text and job description

    Returns:
        Tailoring analysis and suggestions
    """
    # Parse resume text
    resume_data = {
        "raw_text": request.resume_text,
        "skills": [],  # Would be extracted from text
        "experience": [],
        "education": [],
        "personal_info": {}
    }

    # Perform tailoring
    result = resume_tailor.tailor_resume(
        resume_data,
        request.job_description,
        {"name": request.company_name} if request.company_name else None
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to tailor resume")
        )

    return result


@router.post("/generate-talking-points")
async def generate_talking_points(request: TalkingPointsRequest):
    """
    Generate personalized talking points for a company.

    Args:
        request: Request with company and resume data

    Returns:
        Talking points, questions, and conversation starters
    """
    result = talking_points_gen.generate_talking_points(
        request.company_info,
        request.resume_data,
        request.job_description,
        request.news_articles
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to generate talking points")
        )

    return result


@router.get("/extract-keywords")
async def extract_keywords(text: str, top_n: int = 20):
    """
    Extract keywords from text using NLP.

    Args:
        text: Input text
        top_n: Number of top keywords to return

    Returns:
        List of keywords
    """
    keywords = resume_parser.extract_keywords(text, top_n)

    return {
        "keywords": keywords,
        "count": len(keywords)
    }
