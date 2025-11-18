"""
Talking points generator for career fair conversations.

Generates personalized talking points for each company based on:
- Company information
- Job requirements
- Resume experience
- Recent news
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class TalkingPointsGenerator:
    """Generator for personalized talking points."""

    def __init__(self):
        """Initialize talking points generator."""
        self.logger = logger

        # Question templates
        self.question_templates = {
            "technical": [
                "What technologies does your team use for {topic}?",
                "How does {company} approach {topic}?",
                "Can you tell me about the tech stack for {topic}?",
                "What are the biggest technical challenges in {topic}?",
            ],
            "company_culture": [
                "What's the engineering culture like at {company}?",
                "How does {company} support professional development?",
                "What's a typical day like for a {role}?",
                "How does {company} promote work-life balance?",
            ],
            "role_specific": [
                "What projects would I work on as a {role}?",
                "What skills are most important for this {role} position?",
                "How is the {role} team structured?",
                "What's the onboarding process for new {role}s?",
            ],
            "growth": [
                "What career growth opportunities exist for {role}s?",
                "How does {company} support continuing education?",
                "Are there mentorship programs for new hires?",
                "What's the typical career path for a {role}?",
            ],
            "news_based": [
                "I read about {news_topic}. How will this impact the team?",
                "I saw that {company} recently {news_topic}. Can you tell me more?",
                "How does {news_topic} align with {company}'s goals?",
            ]
        }

        # Conversation starters
        self.conversation_starters = [
            "I'm particularly interested in {interest} and noticed that {company} {relevance}.",
            "I have experience with {skill} and I'm excited about {company}'s work in {area}.",
            "I'm impressed by {company}'s {achievement}.",
        ]

    def generate_talking_points(
        self,
        company_info: Dict[str, Any],
        resume_data: Dict[str, Any],
        job_description: Optional[str] = None,
        news_articles: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized talking points for a company.

        Args:
            company_info: Company information
            resume_data: Parsed resume data
            job_description: Optional job description
            news_articles: Optional recent news articles

        Returns:
            Dict with talking points, questions, and conversation starters
        """
        start_time = datetime.now()

        result = {
            "company_name": company_info.get("name", ""),
            "talking_points": [],
            "questions_to_ask": [],
            "conversation_starters": [],
            "key_topics": [],
            "success": False
        }

        try:
            # Extract key information
            company_name = company_info.get("name", "")
            majors = company_info.get("recruiting_majors", [])
            position_types = company_info.get("position_types", [])

            # Generate talking points from resume
            resume_points = self._generate_resume_talking_points(
                resume_data,
                company_info
            )
            result["talking_points"].extend(resume_points)

            # Generate questions
            questions = self._generate_questions(
                company_name,
                majors,
                position_types,
                news_articles
            )
            result["questions_to_ask"] = questions

            # Generate conversation starters
            starters = self._generate_conversation_starters(
                company_info,
                resume_data
            )
            result["conversation_starters"] = starters

            # Identify key topics to discuss
            result["key_topics"] = self._identify_key_topics(
                company_info,
                resume_data,
                job_description
            )

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error generating talking points: {str(e)}")
            result["error"] = str(e)

        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Talking points generation completed in {duration:.2f}s")

        return result

    def _generate_resume_talking_points(
        self,
        resume_data: Dict[str, Any],
        company_info: Dict[str, Any]
    ) -> List[str]:
        """
        Generate talking points based on resume experience.

        Args:
            resume_data: Parsed resume data
            company_info: Company information

        Returns:
            List of talking points
        """
        points = []

        # Experience-based points
        experience = resume_data.get("experience", [])
        if experience:
            latest_exp = experience[0]
            title = latest_exp.get("title", "")
            company = latest_exp.get("company", "")

            if title and company:
                points.append(
                    f"Currently/Previously worked as {title} at {company}, "
                    f"where I gained experience in relevant technologies"
                )

        # Skills-based points
        skills = resume_data.get("skills", [])
        company_keywords = company_info.get("keywords", [])

        # Find matching skills
        matching_skills = [
            s for s in skills
            if any(kw.lower() in s.lower() for kw in company_keywords)
        ]

        if matching_skills:
            points.append(
                f"Proficient in {', '.join(matching_skills[:3])}, "
                f"which aligns with your tech stack"
            )

        # Projects-based points
        projects = resume_data.get("projects", [])
        if projects:
            top_project = projects[0]
            project_name = top_project.get("name", "")
            if project_name:
                points.append(
                    f"Built {project_name}, demonstrating hands-on experience "
                    f"with relevant technologies"
                )

        # Education-based points
        education = resume_data.get("education", [])
        if education:
            degree_info = education[0]
            degree = degree_info.get("degree", "")
            if degree:
                points.append(
                    f"Pursuing/Completed {degree}, providing strong "
                    f"foundation in technical concepts"
                )

        return points[:4]  # Top 4 points

    def _generate_questions(
        self,
        company_name: str,
        majors: List[str],
        position_types: List[str],
        news_articles: Optional[List[Dict[str, str]]] = None
    ) -> List[str]:
        """
        Generate thoughtful questions to ask recruiters.

        Args:
            company_name: Company name
            majors: Recruiting majors
            position_types: Position types
            news_articles: Recent news

        Returns:
            List of questions
        """
        questions = []

        # Technical questions
        if majors:
            major = majors[0]
            topic = self._major_to_topic(major)

            tech_questions = [
                q.format(topic=topic, company=company_name)
                for q in self.question_templates["technical"][:2]
            ]
            questions.extend(tech_questions)

        # Role-specific questions
        if position_types:
            role = position_types[0]
            role_questions = [
                q.format(role=role, company=company_name)
                for q in self.question_templates["role_specific"][:2]
            ]
            questions.extend(role_questions)

        # Company culture questions
        culture_questions = [
            q.format(company=company_name, role=position_types[0] if position_types else "engineer")
            for q in self.question_templates["company_culture"][:2]
        ]
        questions.extend(culture_questions)

        # Growth questions
        growth_questions = [
            q.format(role=position_types[0] if position_types else "engineer", company=company_name)
            for q in self.question_templates["growth"][:1]
        ]
        questions.extend(growth_questions)

        # News-based questions
        if news_articles and len(news_articles) > 0:
            article = news_articles[0]
            news_topic = article.get("title", "")
            if news_topic:
                news_q = random.choice(self.question_templates["news_based"])
                questions.append(
                    news_q.format(
                        company=company_name,
                        news_topic=news_topic[:50]
                    )
                )

        return questions[:8]  # Top 8 questions

    def _generate_conversation_starters(
        self,
        company_info: Dict[str, Any],
        resume_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate conversation starters.

        Args:
            company_info: Company information
            resume_data: Resume data

        Returns:
            List of conversation starters
        """
        starters = []

        company_name = company_info.get("name", "")
        skills = resume_data.get("skills", [])

        if skills and company_name:
            # Skill-based starter
            top_skill = skills[0]
            starters.append(
                f"I'm particularly interested in working with {top_skill} "
                f"and I noticed that {company_name} uses cutting-edge technologies."
            )

        # Major-based starter
        majors = company_info.get("recruiting_majors", [])
        if majors:
            major = majors[0]
            starters.append(
                f"As a {major} student, I'm excited about {company_name}'s "
                f"innovative work in the field."
            )

        # Company achievement starter
        if company_info.get("is_platinum_sponsor"):
            starters.append(
                f"I'm impressed by {company_name}'s commitment to engineering "
                f"talent, especially as a platinum sponsor."
            )

        # General starter
        starters.append(
            f"I've been following {company_name} and I'm really interested "
            f"in learning more about the team and opportunities."
        )

        return starters[:3]

    def _identify_key_topics(
        self,
        company_info: Dict[str, Any],
        resume_data: Dict[str, Any],
        job_description: Optional[str] = None
    ) -> List[str]:
        """
        Identify key topics to discuss.

        Args:
            company_info: Company information
            resume_data: Resume data
            job_description: Job description

        Returns:
            List of key topics
        """
        topics = []

        # Technology topics
        skills = resume_data.get("skills", [])
        if skills:
            topics.extend(skills[:3])

        # Industry topics
        majors = company_info.get("recruiting_majors", [])
        if majors:
            topics.extend([self._major_to_topic(m) for m in majors[:2]])

        # Company-specific topics
        if company_info.get("keywords"):
            topics.extend(company_info["keywords"][:2])

        # Remove duplicates
        topics = list(set(topics))

        return topics[:6]

    def _major_to_topic(self, major: str) -> str:
        """Convert major to discussion topic."""
        major_topics = {
            "computer science": "software development",
            "mechanical engineering": "mechanical design",
            "electrical engineering": "electrical systems",
            "chemical engineering": "chemical processes",
            "civil engineering": "infrastructure",
            "software engineering": "software architecture",
        }

        major_lower = major.lower()
        for key, topic in major_topics.items():
            if key in major_lower:
                return topic

        return major

    def format_for_display(
        self,
        talking_points_data: Dict[str, Any]
    ) -> str:
        """
        Format talking points for display/printing.

        Args:
            talking_points_data: Generated talking points data

        Returns:
            Formatted string
        """
        output = []

        company = talking_points_data.get("company_name", "Company")
        output.append(f"=== TALKING POINTS FOR {company.upper()} ===\n")

        # Conversation starters
        starters = talking_points_data.get("conversation_starters", [])
        if starters:
            output.append("🗣️ CONVERSATION STARTERS:")
            for i, starter in enumerate(starters, 1):
                output.append(f"  {i}. {starter}")
            output.append("")

        # Talking points
        points = talking_points_data.get("talking_points", [])
        if points:
            output.append("💡 KEY POINTS TO MENTION:")
            for i, point in enumerate(points, 1):
                output.append(f"  {i}. {point}")
            output.append("")

        # Questions
        questions = talking_points_data.get("questions_to_ask", [])
        if questions:
            output.append("❓ QUESTIONS TO ASK:")
            for i, question in enumerate(questions, 1):
                output.append(f"  {i}. {question}")
            output.append("")

        # Key topics
        topics = talking_points_data.get("key_topics", [])
        if topics:
            output.append("📌 KEY TOPICS:")
            output.append(f"  {', '.join(topics)}")

        return "\n".join(output)
