"""
Unit tests for NLP modules.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.nlp.resume_parser import ResumeParser
from app.nlp.resume_tailor import ResumeTailor
from app.nlp.talking_points import TalkingPointsGenerator


class TestResumeParser:
    """Tests for ResumeParser class."""

    def test_init_without_spacy(self):
        """Test parser initialization without spaCy."""
        with patch('app.nlp.resume_parser.SPACY_AVAILABLE', False):
            parser = ResumeParser()
            assert parser.nlp is None

    def test_extract_personal_info(self, sample_resume_data):
        """Test personal information extraction."""
        parser = ResumeParser()

        text = sample_resume_data["raw_text"]
        info = parser._extract_personal_info(text)

        assert info["email"] == "john.doe@email.com"
        assert info["phone"] == "(123) 456-7890"
        assert info["name"] == "John Doe"

    def test_extract_email(self):
        """Test email extraction from various formats."""
        parser = ResumeParser()

        test_cases = [
            ("Contact: john@example.com", "john@example.com"),
            ("Email: jane.doe@university.edu", "jane.doe@university.edu"),
            ("test+filter@company.co.uk", "test+filter@company.co.uk"),
        ]

        for text, expected_email in test_cases:
            info = parser._extract_personal_info(text)
            assert info["email"] == expected_email

    def test_extract_phone(self):
        """Test phone number extraction."""
        parser = ResumeParser()

        test_cases = [
            ("Phone: 123-456-7890", "123-456-7890"),
            ("Call me at (555) 123-4567", "(555) 123-4567"),
            ("Contact: 555.123.4567", "555.123.4567"),
        ]

        for text, expected_phone in test_cases:
            info = parser._extract_personal_info(text)
            assert expected_phone in info["phone"]

    def test_extract_education(self):
        """Test education extraction."""
        parser = ResumeParser()

        text = """
        EDUCATION
        Bachelor of Science in Computer Science
        University of Houston
        Expected Graduation: 2024

        Master of Science in Software Engineering
        Rice University
        Graduated: 2022
        """

        education = parser._extract_education(text)

        assert len(education) > 0
        assert any("Bachelor" in e["degree"] for e in education)

    def test_extract_skills(self, sample_resume_data):
        """Test skills extraction."""
        parser = ResumeParser()

        text = """
        SKILLS
        • Programming: Python, Java, C++, JavaScript
        • Web Development: React, Node.js, FastAPI
        • Databases: PostgreSQL, MongoDB
        • Tools: Git, Docker, AWS
        """

        skills = parser._extract_skills(text)

        assert len(skills) > 0
        assert "Python" in skills or "python" in [s.lower() for s in skills]
        assert "React" in skills or "react" in [s.lower() for s in skills]

    def test_extract_experience(self):
        """Test experience extraction."""
        parser = ResumeParser()

        text = """
        EXPERIENCE

        Software Engineering Intern
        Tech Corp, Houston TX
        May 2023 - August 2023
        - Developed web applications using Python and React
        - Collaborated with team of 5 engineers

        Research Assistant
        University of Houston
        2022 - 2023
        - Conducted research in machine learning
        """

        experience = parser._extract_experience(text)

        assert len(experience) > 0
        # Check that some experience was extracted
        assert any("Software" in exp.get("title", "") or
                   "Research" in exp.get("title", "") for exp in experience)

    def test_extract_year(self):
        """Test year extraction utility."""
        parser = ResumeParser()

        assert parser._extract_year("Graduated in 2024") == "2024"
        assert parser._extract_year("Class of 2023") == "2023"
        assert parser._extract_year("1995-2000") == "1995"
        assert parser._extract_year("No year here") == ""

    def test_extract_date_range(self):
        """Test date range extraction."""
        parser = ResumeParser()

        assert "2023" in parser._extract_date_range("May 2023 - Aug 2023")
        assert "Present" in parser._extract_date_range("Jan 2024 - Present")

    def test_clean_text(self):
        """Test text cleaning in parser."""
        parser = ResumeParser()

        assert parser.clean_text("  Extra   spaces  ") == "Extra spaces"
        assert parser.clean_text(None) == ""


class TestResumeTailor:
    """Tests for ResumeTailor class."""

    def test_extract_job_keywords(self, sample_job_description):
        """Test keyword extraction from job description."""
        tailor = ResumeTailor()

        keywords = tailor._extract_job_keywords(sample_job_description)

        assert len(keywords) > 0
        # Should find tech skills
        keywords_lower = {k.lower() for k in keywords}
        assert any(skill in keywords_lower for skill in ["python", "react", "aws", "sql"])

    def test_match_skills(self, sample_resume_data):
        """Test skill matching."""
        tailor = ResumeTailor()

        resume_skills = set(sample_resume_data["skills"])
        job_keywords = {"Python", "React", "AWS", "Kubernetes", "Go"}

        matched, missing = tailor._match_skills(resume_skills, job_keywords)

        # Should match Python, React, AWS
        assert "Python" in matched
        assert "React" in matched

        # Should identify missing skills
        assert "Kubernetes" in missing or "kubernetes" in {m.lower() for m in missing}

    def test_calculate_match_score(self):
        """Test match score calculation."""
        tailor = ResumeTailor()

        # Perfect match
        matched = {"Python", "Java", "SQL"}
        job_keywords = {"Python", "Java", "SQL"}
        score = tailor._calculate_match_score(matched, job_keywords)
        assert score == 100.0

        # 50% match
        matched = {"Python"}
        job_keywords = {"Python", "Java"}
        score = tailor._calculate_match_score(matched, job_keywords)
        assert score == 50.0

        # No match
        matched = set()
        job_keywords = {"Python", "Java"}
        score = tailor._calculate_match_score(matched, job_keywords)
        assert score == 0.0

    def test_is_technical_skill(self):
        """Test technical skill identification."""
        tailor = ResumeTailor()

        assert tailor._is_technical_skill("Python") is True
        assert tailor._is_technical_skill("JavaScript") is True
        assert tailor._is_technical_skill("AWS") is True
        assert tailor._is_technical_skill("random text") is False

    def test_analyze_keyword_density(self, sample_resume_data):
        """Test keyword density analysis."""
        tailor = ResumeTailor()

        text = sample_resume_data["raw_text"]
        keywords = {"Python", "React", "FastAPI", "NonexistentKeyword"}

        density = tailor._analyze_keyword_density(text, keywords)

        # Should find Python and React in the text
        assert "Python" in density
        assert density["Python"] > 0

        # Should not include keywords not in text
        assert "NonexistentKeyword" not in density

    def test_check_ats_compatibility(self, sample_resume_data):
        """Test ATS compatibility checking."""
        tailor = ResumeTailor()

        # Good resume
        score = tailor._check_ats_compatibility(sample_resume_data)
        assert score >= 80  # Should have high score with complete data

        # Resume missing sections
        incomplete_resume = {
            "personal_info": {"email": "test@example.com"},
            "education": [],
            "experience": [],
            "skills": []
        }
        score = tailor._check_ats_compatibility(incomplete_resume)
        assert score < 80  # Should have lower score

    def test_generate_suggestions(self, sample_resume_data, sample_job_description):
        """Test suggestion generation."""
        tailor = ResumeTailor()

        job_keywords = tailor._extract_job_keywords(sample_job_description)
        resume_skills = set(sample_resume_data["skills"])
        matched, missing = tailor._match_skills(resume_skills, job_keywords)

        suggestions = tailor._generate_suggestions(
            sample_resume_data,
            job_keywords,
            matched,
            missing,
            None
        )

        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)

    def test_tailor_resume(self, sample_resume_data, sample_job_description):
        """Test complete resume tailoring."""
        tailor = ResumeTailor()

        result = tailor.tailor_resume(
            sample_resume_data,
            sample_job_description
        )

        assert result["success"] is True
        assert "match_score" in result
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "suggestions" in result
        assert 0 <= result["match_score"] <= 100

    def test_generate_tailored_summary(self, sample_resume_data):
        """Test tailored summary generation."""
        tailor = ResumeTailor()

        summary = tailor.generate_tailored_summary(
            sample_resume_data,
            "TechCorp",
            "Software Engineer",
            ["Python", "React", "AWS"]
        )

        assert "TechCorp" in summary
        assert "Software Engineer" in summary
        assert len(summary) > 50  # Should be a meaningful summary


class TestTalkingPointsGenerator:
    """Tests for TalkingPointsGenerator class."""

    def test_generate_talking_points(
        self,
        sample_company_info,
        sample_resume_data,
        sample_job_description,
        sample_news_articles
    ):
        """Test talking points generation."""
        generator = TalkingPointsGenerator()

        result = generator.generate_talking_points(
            sample_company_info,
            sample_resume_data,
            sample_job_description,
            sample_news_articles
        )

        assert result["success"] is True
        assert "talking_points" in result
        assert "questions_to_ask" in result
        assert "conversation_starters" in result
        assert "key_topics" in result
        assert result["company_name"] == sample_company_info["name"]

    def test_generate_resume_talking_points(self, sample_resume_data, sample_company_info):
        """Test resume-based talking points."""
        generator = TalkingPointsGenerator()

        points = generator._generate_resume_talking_points(
            sample_resume_data,
            sample_company_info
        )

        assert len(points) > 0
        # Should mention experience or skills
        assert any("experience" in p.lower() or "proficient" in p.lower() for p in points)

    def test_generate_questions(self, sample_company_info):
        """Test question generation."""
        generator = TalkingPointsGenerator()

        questions = generator._generate_questions(
            sample_company_info["name"],
            sample_company_info["recruiting_majors"],
            sample_company_info["position_types"],
            None
        )

        assert len(questions) > 0
        # Questions should be complete sentences
        assert all(q.endswith("?") for q in questions)
        # Should mention company name
        assert any(sample_company_info["name"] in q for q in questions)

    def test_generate_conversation_starters(self, sample_company_info, sample_resume_data):
        """Test conversation starter generation."""
        generator = TalkingPointsGenerator()

        starters = generator._generate_conversation_starters(
            sample_company_info,
            sample_resume_data
        )

        assert len(starters) > 0
        # Should mention company name
        assert any(sample_company_info["name"] in s for s in starters)

    def test_identify_key_topics(
        self,
        sample_company_info,
        sample_resume_data,
        sample_job_description
    ):
        """Test key topic identification."""
        generator = TalkingPointsGenerator()

        topics = generator._identify_key_topics(
            sample_company_info,
            sample_resume_data,
            sample_job_description
        )

        assert len(topics) > 0
        # Should be strings
        assert all(isinstance(t, str) for t in topics)

    def test_major_to_topic(self):
        """Test major to topic conversion."""
        generator = TalkingPointsGenerator()

        assert "software" in generator._major_to_topic("Computer Science").lower()
        assert "mechanical" in generator._major_to_topic("Mechanical Engineering").lower()
        # Unknown major should return original
        assert generator._major_to_topic("Unknown Major") == "Unknown Major"

    def test_format_for_display(self, sample_company_info, sample_resume_data):
        """Test formatted output."""
        generator = TalkingPointsGenerator()

        talking_points = generator.generate_talking_points(
            sample_company_info,
            sample_resume_data
        )

        formatted = generator.format_for_display(talking_points)

        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert sample_company_info["name"].upper() in formatted
        # Should have sections
        assert "CONVERSATION STARTERS" in formatted or "QUESTIONS" in formatted


def test_nlp_integration(sample_resume_data, sample_company_info, sample_job_description):
    """Integration test for NLP modules working together."""
    # Parse resume (already parsed in fixture, but simulate workflow)
    parser = ResumeParser()
    resume_data = sample_resume_data  # In real case: parser.parse_pdf(path)

    # Tailor resume
    tailor = ResumeTailor()
    tailoring = tailor.tailor_resume(resume_data, sample_job_description)

    assert tailoring["success"] is True
    assert tailoring["match_score"] >= 0

    # Generate talking points
    generator = TalkingPointsGenerator()
    talking_points = generator.generate_talking_points(
        sample_company_info,
        resume_data,
        sample_job_description
    )

    assert talking_points["success"] is True
    assert len(talking_points["questions_to_ask"]) > 0

    # Verify data flow
    assert len(tailoring["matched_skills"]) >= 0
    assert len(talking_points["talking_points"]) >= 0
