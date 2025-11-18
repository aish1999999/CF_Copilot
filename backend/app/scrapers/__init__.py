"""
Web scraping modules for CF_Copilot.

This package contains scrapers for:
- Company information (LinkedIn, Glassdoor)
- Job postings
- News aggregation
"""

from .company_scraper import CompanyScraper
from .news_scraper import NewsScraper
from .job_scraper import JobScraper

__all__ = ["CompanyScraper", "NewsScraper", "JobScraper"]
