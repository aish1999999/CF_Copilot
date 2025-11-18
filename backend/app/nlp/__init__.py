"""
NLP modules for CF_Copilot.

This package contains:
- Resume parsing
- Resume tailoring
- Talking points generation
- Keyword extraction
"""

from .resume_parser import ResumeParser
from .resume_tailor import ResumeTailor
from .talking_points import TalkingPointsGenerator

__all__ = ["ResumeParser", "ResumeTailor", "TalkingPointsGenerator"]
