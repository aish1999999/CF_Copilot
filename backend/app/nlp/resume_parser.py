"""
Resume parsing module using spaCy and PDF extraction.

Extracts structured information from PDF resumes:
- Personal information (name, email, phone)
- Education
- Work experience
- Skills
- Projects
"""

import re
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pdfplumber
from pathlib import Path

try:
    import spacy
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parser for extracting structured data from resumes."""

    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """
        Initialize resume parser.

        Args:
            spacy_model: spaCy model to use for NLP
        """
        self.logger = logger

        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(spacy_model)
            except OSError:
                self.logger.warning(
                    f"spaCy model '{spacy_model}' not found. "
                    "Run: python -m spacy download en_core_web_sm"
                )
                self.nlp = None
        else:
            self.logger.warning("spaCy not installed")
            self.nlp = None

    def parse_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Parse a PDF resume and extract structured information.

        Args:
            pdf_path: Path to PDF resume file

        Returns:
            Dict with parsed resume data
        """
        start_time = datetime.now()

        result = {
            "success": False,
            "parsed_at": start_time.isoformat(),
            "personal_info": {},
            "education": [],
            "experience": [],
            "skills": [],
            "projects": [],
            "raw_text": ""
        }

        try:
            # Extract text from PDF
            text = self._extract_text_from_pdf(pdf_path)
            result["raw_text"] = text

            if not text:
                result["error"] = "No text extracted from PDF"
                return result

            # Parse sections
            result["personal_info"] = self._extract_personal_info(text)
            result["education"] = self._extract_education(text)
            result["experience"] = self._extract_experience(text)
            result["skills"] = self._extract_skills(text)
            result["projects"] = self._extract_projects(text)

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error parsing resume: {str(e)}")
            result["error"] = str(e)

        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Resume parsing completed in {duration:.2f}s")

        return result

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        text = ""

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

        except Exception as e:
            self.logger.error(f"Error extracting PDF text: {str(e)}")

        return text.strip()

    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """
        Extract personal information (name, email, phone).

        Args:
            text: Resume text

        Returns:
            Dict with personal info
        """
        info = {
            "name": "",
            "email": "",
            "phone": "",
            "location": ""
        }

        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            info["email"] = email_match.group(0)

        # Extract phone
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            info["phone"] = phone_match.group(0)

        # Extract name (first line usually)
        lines = text.split('\n')
        if lines:
            # First non-empty line is often the name
            for line in lines:
                line = line.strip()
                if line and len(line) < 50 and not '@' in line:
                    info["name"] = line
                    break

        return info

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """
        Extract education information.

        Args:
            text: Resume text

        Returns:
            List of education entries
        """
        education = []

        # Common degree patterns
        degree_patterns = [
            r"(Bachelor|B\.S\.|B\.A\.|Master|M\.S\.|M\.A\.|Ph\.D\.|MBA)",
            r"(Computer Science|Engineering|Business|Mathematics|Physics)",
        ]

        # Common university patterns
        university_pattern = r"University|College|Institute"

        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Check if line contains education keywords
            if any(re.search(pattern, line, re.I) for pattern in degree_patterns):
                # Look for university in nearby lines
                context_lines = lines[max(0, i-1):min(len(lines), i+3)]
                context = ' '.join(context_lines)

                uni_match = re.search(university_pattern, context, re.I)

                education.append({
                    "degree": line.strip(),
                    "institution": uni_match.group(0) if uni_match else "",
                    "graduation_year": self._extract_year(context)
                })

        return education

    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """
        Extract work experience.

        Args:
            text: Resume text

        Returns:
            List of experience entries
        """
        experience = []

        # Find "Experience" section
        exp_section = self._extract_section(text, ["experience", "work history"])

        if exp_section:
            # Split by job entries (often marked by dates)
            entries = re.split(r'\n(?=\d{4}|\w+\s+\d{4})', exp_section)

            for entry in entries:
                if len(entry.strip()) < 20:
                    continue

                lines = entry.split('\n')
                if lines:
                    experience.append({
                        "title": lines[0].strip() if lines else "",
                        "company": lines[1].strip() if len(lines) > 1 else "",
                        "dates": self._extract_date_range(entry),
                        "description": entry.strip()
                    })

        return experience[:5]  # Limit to 5 entries

    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract skills and technologies.

        Args:
            text: Resume text

        Returns:
            List of skills
        """
        skills = []

        # Find "Skills" section
        skills_section = self._extract_section(
            text,
            ["skills", "technical skills", "technologies"]
        )

        if skills_section:
            # Common skill keywords
            tech_skills = [
                "Python", "Java", "C++", "JavaScript", "React", "Node.js",
                "SQL", "MongoDB", "AWS", "Docker", "Kubernetes",
                "Machine Learning", "Data Analysis", "Git", "Linux",
                "TensorFlow", "PyTorch", "FastAPI", "Django", "Flask"
            ]

            # Extract matching skills
            text_lower = skills_section.lower()
            for skill in tech_skills:
                if skill.lower() in text_lower:
                    skills.append(skill)

            # Also extract from bullet points
            bullets = re.findall(r'[•\-\*]\s*([^\n]+)', skills_section)
            for bullet in bullets:
                cleaned = bullet.strip()
                if cleaned and len(cleaned) < 50:
                    # Extract individual skills from comma-separated lists
                    items = [s.strip() for s in cleaned.split(',')]
                    skills.extend(items)

        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)

        return unique_skills[:20]  # Limit to top 20

    def _extract_projects(self, text: str) -> List[Dict[str, str]]:
        """
        Extract project information.

        Args:
            text: Resume text

        Returns:
            List of projects
        """
        projects = []

        # Find "Projects" section
        projects_section = self._extract_section(text, ["projects", "personal projects"])

        if projects_section:
            # Split by project entries
            entries = re.split(r'\n(?=[A-Z][^a-z\n]{10,})', projects_section)

            for entry in entries:
                if len(entry.strip()) < 20:
                    continue

                lines = entry.split('\n')
                projects.append({
                    "name": lines[0].strip() if lines else "",
                    "description": entry.strip(),
                    "technologies": []  # Could extract from description
                })

        return projects[:5]

    def _extract_section(self, text: str, section_headers: List[str]) -> str:
        """
        Extract a specific section from resume text.

        Args:
            text: Full resume text
            section_headers: Possible section header names

        Returns:
            Section text
        """
        # Create pattern for section headers
        pattern = r'\b(' + '|'.join(section_headers) + r')\b'

        # Find section start
        match = re.search(pattern, text, re.I)
        if not match:
            return ""

        start_idx = match.start()

        # Find next section (common headers)
        next_sections = [
            "education", "experience", "skills", "projects",
            "certifications", "awards", "references"
        ]

        next_pattern = r'\n\s*\b(' + '|'.join(next_sections) + r')\b'
        next_match = re.search(next_pattern, text[start_idx + 50:], re.I)

        if next_match:
            end_idx = start_idx + 50 + next_match.start()
            return text[start_idx:end_idx]

        return text[start_idx:]

    def _extract_year(self, text: str) -> str:
        """Extract 4-digit year from text."""
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        return year_match.group(0) if year_match else ""

    def _extract_date_range(self, text: str) -> str:
        """Extract date range like 'Jan 2020 - Dec 2022'."""
        date_pattern = r'(\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4}|\w+\s+\d{4}\s*[-–]\s*Present)'
        match = re.search(date_pattern, text)
        return match.group(0) if match else ""

    def extract_keywords(self, text: str, top_n: int = 20) -> List[str]:
        """
        Extract important keywords using NLP.

        Args:
            text: Resume text
            top_n: Number of top keywords to return

        Returns:
            List of keywords
        """
        if not self.nlp:
            return []

        doc = self.nlp(text.lower())

        # Extract noun phrases and key entities
        keywords = []

        # Named entities
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE", "NORP"]:
                keywords.append(ent.text)

        # Noun chunks
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 3:
                keywords.append(chunk.text)

        # Remove duplicates
        keywords = list(set(keywords))

        return keywords[:top_n]
