"""
Pytest configuration and fixtures for CF_Copilot tests.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_resume_data():
    """Sample parsed resume data for testing."""
    return {
        "success": True,
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "(123) 456-7890",
            "location": "Houston, TX"
        },
        "education": [
            {
                "degree": "B.S. Computer Science",
                "institution": "University of Houston",
                "graduation_year": "2024"
            }
        ],
        "experience": [
            {
                "title": "Software Engineering Intern",
                "company": "Tech Corp",
                "dates": "May 2023 - Aug 2023",
                "description": "Developed Python applications using FastAPI and React"
            }
        ],
        "skills": [
            "Python", "JavaScript", "React", "FastAPI",
            "SQL", "Git", "Docker", "AWS"
        ],
        "projects": [
            {
                "name": "Career Fair App",
                "description": "Built a career fair navigation system using React and FastAPI"
            }
        ],
        "raw_text": "John Doe\njohn.doe@email.com\n(123) 456-7890\n\nEDUCATION\nB.S. Computer Science, University of Houston, 2024\n\nEXPERIENCE\nSoftware Engineering Intern, Tech Corp\nMay 2023 - Aug 2023\nDeveloped Python applications using FastAPI and React\n\nSKILLS\nPython, JavaScript, React, FastAPI, SQL, Git, Docker, AWS"
    }


@pytest.fixture
def sample_company_info():
    """Sample company information for testing."""
    return {
        "id": 1,
        "name": "TechCorp Solutions",
        "booth_number": "101",
        "ballroom": "Waldorf",
        "recruiting_majors": ["Computer Science", "Software Engineering"],
        "position_types": ["Full-Time", "Internship"],
        "is_platinum_sponsor": True,
        "website": "https://techcorp.example.com",
        "description": "Leading technology company specializing in AI and cloud solutions",
        "keywords": ["AI", "Machine Learning", "Cloud Computing", "Python"]
    }


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
Software Engineer Intern - Summer 2025

TechCorp Solutions is seeking talented Software Engineering interns for Summer 2025.

Requirements:
- Currently pursuing Bachelor's or Master's in Computer Science or related field
- Strong programming skills in Python, Java, or C++
- Experience with web development (React, Node.js)
- Knowledge of databases (SQL, NoSQL)
- Familiarity with cloud platforms (AWS, Azure, GCP)
- 3+ years of experience preferred

Responsibilities:
- Develop and maintain web applications
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews

Technologies:
Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes, PostgreSQL

We offer competitive compensation, great benefits, and opportunities for growth.
"""


@pytest.fixture
def sample_news_articles():
    """Sample news articles for testing."""
    return [
        {
            "title": "TechCorp Launches New AI Platform",
            "source": "Tech News",
            "published_date": "2024-01-15",
            "url": "https://technews.com/techcorp-ai"
        },
        {
            "title": "TechCorp Expands Cloud Services",
            "source": "Industry Weekly",
            "published_date": "2024-01-10",
            "url": "https://industryweekly.com/techcorp-cloud"
        }
    ]


@pytest.fixture
def mock_pdf_path(tmp_path):
    """Create a temporary PDF file path for testing."""
    pdf_file = tmp_path / "test_resume.pdf"
    # Note: Actual PDF creation would require PyPDF2 or similar
    # For testing, we'll just create a placeholder
    pdf_file.write_text("Mock PDF content")
    return str(pdf_file)


@pytest.fixture
def sample_scraped_company_data():
    """Sample scraped company data."""
    return {
        "company_name": "TechCorp Solutions",
        "scraped_at": "2024-01-18T12:00:00",
        "description": "Leading technology company in AI and cloud solutions",
        "industry": "Technology",
        "size": "1000-5000 employees",
        "headquarters": "San Francisco, CA",
        "website": "https://techcorp.example.com",
        "benefits": ["Health Insurance", "401k", "Remote Work"],
        "culture": "Innovation-focused, collaborative environment",
        "recent_news": [],
        "success": True
    }


@pytest.fixture
def sample_job_postings():
    """Sample job postings data."""
    return [
        {
            "title": "Software Engineer Intern",
            "company": "TechCorp Solutions",
            "location": "Houston, TX",
            "position_type": "Internship",
            "url": "https://techcorp.example.com/careers/intern",
            "source": "Company Website"
        },
        {
            "title": "Full Stack Developer",
            "company": "TechCorp Solutions",
            "location": "Remote",
            "position_type": "Full-Time",
            "url": "https://techcorp.example.com/careers/fullstack",
            "source": "Company Website"
        }
    ]
