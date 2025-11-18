"""
API routes for web scraping services.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

from app.scrapers.company_scraper import CompanyScraper
from app.scrapers.news_scraper import NewsScraper
from app.scrapers.job_scraper import JobScraper

router = APIRouter(prefix="/api/v1/scraping", tags=["Scraping"])

# Initialize scrapers
company_scraper = CompanyScraper()
news_scraper = NewsScraper()
job_scraper = JobScraper()


class CompanyScrapeRequest(BaseModel):
    """Request model for company scraping."""
    company_name: str
    website_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None


class NewsScrapeRequest(BaseModel):
    """Request model for news scraping."""
    company_name: str
    days_back: int = 30
    max_articles: int = 10


class JobScrapeRequest(BaseModel):
    """Request model for job scraping."""
    company_name: str
    position_types: Optional[List[str]] = None
    max_jobs: int = 20
    career_page_url: Optional[HttpUrl] = None


@router.post("/scrape-company")
async def scrape_company(request: CompanyScrapeRequest):
    """
    Scrape company information from public sources.

    Args:
        request: Company scrape request

    Returns:
        Scraped company data
    """
    result = await company_scraper.scrape(
        company_name=request.company_name,
        website_url=str(request.website_url) if request.website_url else None,
        linkedin_url=str(request.linkedin_url) if request.linkedin_url else None
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to scrape company data")
        )

    return result


@router.post("/scrape-news")
async def scrape_news(request: NewsScrapeRequest):
    """
    Scrape recent news articles about a company.

    Args:
        request: News scrape request

    Returns:
        News articles
    """
    result = await news_scraper.scrape(
        company_name=request.company_name,
        days_back=request.days_back,
        max_articles=request.max_articles
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to scrape news")
        )

    return result


@router.post("/scrape-jobs")
async def scrape_jobs(request: JobScrapeRequest):
    """
    Scrape job postings for a company.

    Args:
        request: Job scrape request

    Returns:
        Job postings
    """
    result = await job_scraper.scrape(
        company_name=request.company_name,
        position_types=request.position_types,
        max_jobs=request.max_jobs,
        career_page_url=str(request.career_page_url) if request.career_page_url else None
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to scrape jobs")
        )

    return result


@router.get("/scrape-multiple-companies")
async def scrape_multiple_companies(
    company_names: List[str] = Query(..., description="List of company names")
):
    """
    Scrape multiple companies in batch.

    Args:
        company_names: List of company names

    Returns:
        List of scrape results
    """
    companies_data = [
        {"name": name, "website": "", "linkedin": ""}
        for name in company_names
    ]

    results = await company_scraper.scrape_multiple_companies(companies_data)

    return {
        "companies": results,
        "total": len(results),
        "successful": sum(1 for r in results if r.get("success"))
    }
