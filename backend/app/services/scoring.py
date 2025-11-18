"""
Company scoring service.

Scores companies based on user profile using multiple factors:
- Major alignment
- Role alignment
- User interest
- Recency/relevance
"""
from typing import Dict, List
from ..config import get_settings

settings = get_settings()


class CompanyScorer:
    """Score companies based on user profile."""

    def __init__(
        self,
        weight_major: float = None,
        weight_role: float = None,
        weight_interest: float = None,
        weight_recency: float = None,
    ):
        """
        Initialize scorer with weights.

        Args:
            weight_major: Weight for major alignment (default from settings)
            weight_role: Weight for role alignment (default from settings)
            weight_interest: Weight for user interest (default from settings)
            weight_recency: Weight for news recency (default from settings)
        """
        self.w_major = weight_major or settings.weight_major
        self.w_role = weight_role or settings.weight_role
        self.w_interest = weight_interest or settings.weight_interest
        self.w_recency = weight_recency or settings.weight_recency

    def score_major_alignment(self, user_major: str, company_majors: List[str]) -> float:
        """
        Score major alignment.

        Args:
            user_major: User's major
            company_majors: List of majors company recruits

        Returns:
            Score between 0 and 1
        """
        if not user_major or not company_majors:
            return 0.5  # Neutral score

        # Exact match
        if user_major in company_majors:
            return 1.0

        # Check for "All Majors"
        if "All Majors" in company_majors:
            return 0.9

        # Partial match (simple keyword matching)
        user_keywords = set(user_major.lower().split())
        for major in company_majors:
            major_keywords = set(major.lower().split())
            overlap = user_keywords & major_keywords
            if overlap:
                return 0.7  # Partial match

        return 0.3  # No match

    def score_role_alignment(
        self,
        user_experience: str,
        company_position_types: List[str]
    ) -> float:
        """
        Score role/position alignment.

        Args:
            user_experience: User's experience level (e.g., "Entry-Level", "Experienced")
            company_position_types: List of position types company offers

        Returns:
            Score between 0 and 1
        """
        if not company_position_types:
            return 0.5

        # Entry-level students
        if user_experience in ["Entry-Level", "Freshman", "Sophomore"]:
            if any("Internship" in pt for pt in company_position_types):
                return 1.0
            if any("Co-Op" in pt for pt in company_position_types):
                return 0.9
            if any("Entry-Level" in pt or "Full-Time" in pt for pt in company_position_types):
                return 0.7
            return 0.4

        # Senior/Graduate students
        elif user_experience in ["Senior", "Graduate", "Experienced"]:
            if any("Entry-Level" in pt or "Full-Time" in pt for pt in company_position_types):
                return 1.0
            if any("Internship" in pt for pt in company_position_types):
                return 0.8
            return 0.5

        return 0.5  # Default

    def score_company(
        self,
        user_profile: Dict,
        company: Dict,
    ) -> float:
        """
        Calculate overall company score.

        Args:
            user_profile: Dictionary with user info (major, experience_level, etc.)
            company: Dictionary with company info (majors, position_types, etc.)

        Returns:
            Overall score (0-1)
        """
        # Major alignment
        major_score = self.score_major_alignment(
            user_profile.get("major", ""),
            company.get("majors", [])
        )

        # Role alignment
        role_score = self.score_role_alignment(
            user_profile.get("experience_level", "Entry-Level"),
            company.get("position_types", [])
        )

        # Interest score (default to 0.5, can be customized)
        interest_score = user_profile.get("interest", 0.5)

        # Recency score (default to 0.5, would use news data in production)
        recency_score = 0.5

        # Weighted sum
        total_score = (
            self.w_major * major_score +
            self.w_role * role_score +
            self.w_interest * interest_score +
            self.w_recency * recency_score
        )

        return total_score

    def score_companies(
        self,
        user_profile: Dict,
        companies: List[Dict],
    ) -> List[Dict]:
        """
        Score a list of companies and return sorted by score.

        Args:
            user_profile: User profile dictionary
            companies: List of company dictionaries

        Returns:
            List of companies with added 'score' field, sorted by score descending
        """
        scored_companies = []

        for company in companies:
            score = self.score_company(user_profile, company)
            company_with_score = company.copy()
            company_with_score["score"] = score
            scored_companies.append(company_with_score)

        # Sort by score descending
        scored_companies.sort(key=lambda x: x["score"], reverse=True)

        return scored_companies
