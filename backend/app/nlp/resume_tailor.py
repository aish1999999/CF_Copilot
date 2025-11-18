"""
Resume tailoring engine for matching resume content with job requirements.

Features:
- Keyword matching with job descriptions
- ATS compatibility checking
- Skill gap analysis
- Resume optimization suggestions
"""

import re
import logging
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import Counter
from datetime import datetime

try:
    import spacy
    from spacy.matcher import PhraseMatcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ResumeTailor:
    """Engine for tailoring resumes to specific companies/jobs."""

    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """
        Initialize resume tailor.

        Args:
            spacy_model: spaCy model to use
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
            self.nlp = None

        # Common tech skills for matching
        self.tech_skills = {
            "programming": [
                "Python", "Java", "C++", "JavaScript", "TypeScript",
                "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin"
            ],
            "web": [
                "React", "Angular", "Vue.js", "Node.js", "Django",
                "Flask", "FastAPI", "Express", "Next.js", "HTML", "CSS"
            ],
            "database": [
                "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
                "Elasticsearch", "DynamoDB", "Cassandra"
            ],
            "cloud": [
                "AWS", "Azure", "GCP", "Docker", "Kubernetes",
                "Terraform", "Jenkins", "CircleCI"
            ],
            "ml_ai": [
                "Machine Learning", "Deep Learning", "TensorFlow",
                "PyTorch", "scikit-learn", "NLP", "Computer Vision"
            ],
            "tools": [
                "Git", "Linux", "Agile", "Scrum", "REST API",
                "GraphQL", "Microservices"
            ]
        }

    def tailor_resume(
        self,
        resume_data: Dict[str, Any],
        job_description: str,
        company_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Tailor resume to match job description and company.

        Args:
            resume_data: Parsed resume data
            job_description: Target job description
            company_info: Optional company information

        Returns:
            Dict with tailoring suggestions and analysis
        """
        start_time = datetime.now()

        result = {
            "match_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
            "keyword_matches": {},
            "suggestions": [],
            "ats_score": 0.0,
            "success": False
        }

        try:
            # Extract keywords from job description
            jd_keywords = self._extract_job_keywords(job_description)

            # Extract skills from resume
            resume_skills = set(resume_data.get("skills", []))
            resume_text = resume_data.get("raw_text", "")

            # Skill matching
            matched, missing = self._match_skills(
                resume_skills,
                jd_keywords
            )

            result["matched_skills"] = list(matched)
            result["missing_skills"] = list(missing)

            # Calculate match score
            result["match_score"] = self._calculate_match_score(
                matched,
                jd_keywords
            )

            # Keyword density analysis
            result["keyword_matches"] = self._analyze_keyword_density(
                resume_text,
                jd_keywords
            )

            # ATS compatibility check
            result["ats_score"] = self._check_ats_compatibility(
                resume_data
            )

            # Generate suggestions
            result["suggestions"] = self._generate_suggestions(
                resume_data,
                jd_keywords,
                matched,
                missing,
                company_info
            )

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error tailoring resume: {str(e)}")
            result["error"] = str(e)

        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Resume tailoring completed in {duration:.2f}s")

        return result

    def _extract_job_keywords(self, job_description: str) -> Set[str]:
        """
        Extract important keywords from job description.

        Args:
            job_description: Job description text

        Returns:
            Set of keywords
        """
        keywords = set()

        # Extract all known tech skills
        jd_lower = job_description.lower()
        for category, skills in self.tech_skills.items():
            for skill in skills:
                if skill.lower() in jd_lower:
                    keywords.add(skill)

        # Extract using NLP if available
        if self.nlp:
            doc = self.nlp(job_description)

            # Named entities
            for ent in doc.ents:
                if ent.label_ in ["PRODUCT", "ORG", "LANGUAGE"]:
                    keywords.add(ent.text)

            # Important noun chunks
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:
                    keywords.add(chunk.text.lower())

        # Common requirement keywords
        requirement_patterns = [
            r"(\d+\+?\s*years?)\s+(?:of\s+)?experience",
            r"(Bachelor|Master|PhD|B\.S\.|M\.S\.)",
            r"(proficien(?:t|cy)|expert|skilled|familiar)",
        ]

        for pattern in requirement_patterns:
            matches = re.findall(pattern, job_description, re.I)
            keywords.update(matches)

        return keywords

    def _match_skills(
        self,
        resume_skills: Set[str],
        job_keywords: Set[str]
    ) -> Tuple[Set[str], Set[str]]:
        """
        Match resume skills with job requirements.

        Args:
            resume_skills: Skills from resume
            job_keywords: Keywords from job description

        Returns:
            Tuple of (matched_skills, missing_skills)
        """
        # Normalize for comparison
        resume_lower = {s.lower() for s in resume_skills}
        job_lower = {k.lower() for k in job_keywords}

        # Find matches
        matched = set()
        for skill in resume_skills:
            if skill.lower() in job_lower:
                matched.add(skill)

        # Find missing (important job keywords not in resume)
        missing = set()
        for keyword in job_keywords:
            if keyword.lower() not in resume_lower:
                # Only include technical skills as "missing"
                if self._is_technical_skill(keyword):
                    missing.add(keyword)

        return matched, missing

    def _is_technical_skill(self, keyword: str) -> bool:
        """Check if keyword is a technical skill."""
        all_skills = []
        for skills_list in self.tech_skills.values():
            all_skills.extend([s.lower() for s in skills_list])

        return keyword.lower() in all_skills

    def _calculate_match_score(
        self,
        matched_skills: Set[str],
        job_keywords: Set[str]
    ) -> float:
        """
        Calculate match score between resume and job.

        Args:
            matched_skills: Skills that matched
            job_keywords: All job keywords

        Returns:
            Match score from 0 to 100
        """
        if not job_keywords:
            return 0.0

        # Filter job keywords to only technical skills
        tech_keywords = {
            k for k in job_keywords
            if self._is_technical_skill(k)
        }

        if not tech_keywords:
            return 50.0  # Neutral score if no tech keywords

        match_ratio = len(matched_skills) / len(tech_keywords)
        return round(match_ratio * 100, 2)

    def _analyze_keyword_density(
        self,
        resume_text: str,
        keywords: Set[str]
    ) -> Dict[str, int]:
        """
        Analyze keyword frequency in resume.

        Args:
            resume_text: Resume text
            keywords: Keywords to count

        Returns:
            Dict mapping keyword to count
        """
        text_lower = resume_text.lower()
        keyword_counts = {}

        for keyword in keywords:
            # Count occurrences
            count = len(re.findall(
                r'\b' + re.escape(keyword.lower()) + r'\b',
                text_lower
            ))
            if count > 0:
                keyword_counts[keyword] = count

        return keyword_counts

    def _check_ats_compatibility(self, resume_data: Dict[str, Any]) -> float:
        """
        Check ATS (Applicant Tracking System) compatibility.

        Args:
            resume_data: Parsed resume data

        Returns:
            ATS compatibility score from 0 to 100
        """
        score = 100.0
        issues = []

        # Check for required sections
        required_sections = ["personal_info", "education", "experience", "skills"]
        for section in required_sections:
            if not resume_data.get(section):
                score -= 15
                issues.append(f"Missing {section} section")

        # Check for contact info
        personal = resume_data.get("personal_info", {})
        if not personal.get("email"):
            score -= 10
            issues.append("Missing email")

        if not personal.get("phone"):
            score -= 5
            issues.append("Missing phone number")

        # Check skills count
        skills = resume_data.get("skills", [])
        if len(skills) < 5:
            score -= 10
            issues.append("Too few skills listed (< 5)")
        elif len(skills) > 30:
            score -= 5
            issues.append("Too many skills listed (> 30)")

        # Check experience
        experience = resume_data.get("experience", [])
        if not experience:
            score -= 20
            issues.append("No work experience listed")

        return max(0, score)

    def _generate_suggestions(
        self,
        resume_data: Dict[str, Any],
        job_keywords: Set[str],
        matched_skills: Set[str],
        missing_skills: Set[str],
        company_info: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generate tailoring suggestions.

        Args:
            resume_data: Parsed resume data
            job_keywords: Job keywords
            matched_skills: Matched skills
            missing_skills: Missing skills
            company_info: Company information

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # Missing skills suggestions
        if missing_skills:
            top_missing = list(missing_skills)[:5]
            suggestions.append(
                f"Add these skills if you have them: {', '.join(top_missing)}"
            )

        # Keyword density
        resume_text = resume_data.get("raw_text", "")
        keyword_counts = self._analyze_keyword_density(resume_text, job_keywords)

        low_frequency_keywords = [
            kw for kw, count in keyword_counts.items()
            if count == 1
        ]

        if low_frequency_keywords:
            suggestions.append(
                "Increase mentions of: " +
                ", ".join(low_frequency_keywords[:3])
            )

        # ATS compatibility
        ats_score = self._check_ats_compatibility(resume_data)
        if ats_score < 80:
            suggestions.append(
                "Improve ATS compatibility by ensuring all required "
                "sections (contact, education, experience, skills) are complete"
            )

        # Experience suggestions
        experience = resume_data.get("experience", [])
        if experience:
            # Check if experience descriptions use action verbs
            first_exp = experience[0].get("description", "")
            action_verbs = [
                "developed", "implemented", "designed", "created",
                "led", "managed", "built", "improved"
            ]

            has_action_verbs = any(
                verb in first_exp.lower()
                for verb in action_verbs
            )

            if not has_action_verbs:
                suggestions.append(
                    "Use strong action verbs in experience descriptions "
                    "(e.g., developed, implemented, led)"
                )

        # Company-specific suggestions
        if company_info:
            company_keywords = company_info.get("keywords", [])
            if company_keywords:
                suggestions.append(
                    f"Highlight experience relevant to: {', '.join(company_keywords[:3])}"
                )

        # Match score based suggestions
        match_score = self._calculate_match_score(matched_skills, job_keywords)
        if match_score < 50:
            suggestions.append(
                "Consider adding more relevant technical skills and experience "
                "to improve your match score"
            )

        return suggestions[:8]  # Top 8 suggestions

    def generate_tailored_summary(
        self,
        resume_data: Dict[str, Any],
        company_name: str,
        job_title: str,
        key_skills: List[str]
    ) -> str:
        """
        Generate a tailored resume summary/objective.

        Args:
            resume_data: Parsed resume data
            company_name: Target company name
            job_title: Target job title
            key_skills: Key skills for the role

        Returns:
            Tailored summary text
        """
        # Extract years of experience
        experience = resume_data.get("experience", [])
        years_exp = len(experience)  # Simplified

        # Extract education
        education = resume_data.get("education", [])
        degree = ""
        if education:
            degree = education[0].get("degree", "")

        # Top skills
        top_skills = key_skills[:3]

        # Generate summary
        summary = (
            f"Motivated {degree} graduate with {years_exp}+ years of experience "
            f"seeking {job_title} position at {company_name}. "
            f"Proficient in {', '.join(top_skills)}. "
            "Proven track record of delivering high-quality solutions "
            "and collaborating effectively in team environments."
        )

        return summary
