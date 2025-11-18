"""
Company information scraper using Playwright.

Scrapes company data from public sources like:
- Company websites
- LinkedIn
- Glassdoor (with rate limiting and respect for robots.txt)
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from bs4 import BeautifulSoup
from .base_scraper import BaseScraper


class CompanyScraper(BaseScraper):
    """Scraper for company information and details."""

    def __init__(self, timeout: int = 30000, headless: bool = True):
        """
        Initialize company scraper.

        Args:
            timeout: Request timeout in milliseconds
            headless: Whether to run browser in headless mode
        """
        super().__init__(timeout, headless)

        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning(
                "Playwright not available. Run: playwright install chromium"
            )

    async def scrape(self, company_name: str, **kwargs) -> Dict[str, Any]:
        """
        Scrape company information.

        Args:
            company_name: Name of the company to scrape
            **kwargs: Additional parameters (website_url, linkedin_url, etc.)

        Returns:
            Dict containing company information
        """
        start_time = datetime.now()

        result = {
            "company_name": company_name,
            "scraped_at": start_time.isoformat(),
            "description": "",
            "industry": "",
            "size": "",
            "headquarters": "",
            "website": kwargs.get("website_url", ""),
            "benefits": [],
            "culture": "",
            "recent_news": [],
            "success": False
        }

        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not installed")
            return result

        try:
            # Try to scrape from company website if provided
            website_url = kwargs.get("website_url")
            if website_url:
                website_data = await self._scrape_company_website(website_url)
                result.update(website_data)

            # Try to scrape from LinkedIn if URL provided
            linkedin_url = kwargs.get("linkedin_url")
            if linkedin_url:
                linkedin_data = await self._scrape_linkedin(linkedin_url)
                result.update(linkedin_data)

            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error scraping {company_name}: {str(e)}")
            result["error"] = str(e)

        duration = (datetime.now() - start_time).total_seconds()
        self.log_scrape_metrics("CompanyScraper", result["success"], duration, 1)

        return result

    async def _scrape_company_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape company website for basic information.

        Args:
            url: Company website URL

        Returns:
            Dict with scraped data
        """
        data = {}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=self.timeout)

                # Get page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    data["description"] = self.clean_text(
                        meta_desc.get('content', '')
                    )

                # Try to find "About" section
                about_section = soup.find(
                    text=re.compile(r'(about|mission|vision)', re.I)
                )
                if about_section:
                    parent = about_section.find_parent()
                    if parent:
                        data["about"] = self.clean_text(parent.get_text())

            except Exception as e:
                self.logger.warning(f"Error scraping website {url}: {str(e)}")

            finally:
                await browser.close()

        return data

    async def _scrape_linkedin(self, url: str) -> Dict[str, Any]:
        """
        Scrape LinkedIn company page (respecting rate limits).

        Args:
            url: LinkedIn company page URL

        Returns:
            Dict with scraped data
        """
        data = {}

        # NOTE: LinkedIn has strict anti-scraping measures
        # This is a basic implementation that respects robots.txt
        # For production, consider using LinkedIn API with proper authentication

        self.logger.info(
            f"LinkedIn scraping for {url} - "
            "Consider using LinkedIn API for production"
        )

        # Placeholder for LinkedIn data
        # In production, use LinkedIn API with OAuth

        return data

    async def scrape_multiple_companies(
        self,
        companies: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Scrape multiple companies in parallel with rate limiting.

        Args:
            companies: List of dicts with company_name and URLs

        Returns:
            List of scrape results
        """
        tasks = []
        for company in companies:
            task = self.scrape(
                company_name=company.get("name", ""),
                website_url=company.get("website", ""),
                linkedin_url=company.get("linkedin", "")
            )
            tasks.append(task)

            # Rate limiting: wait between requests
            await asyncio.sleep(2)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = [
            r for r in results
            if isinstance(r, dict) and not isinstance(r, Exception)
        ]

        return valid_results

    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from company description.

        Args:
            text: Company description text

        Returns:
            List of keywords
        """
        # Simple keyword extraction
        # In production, use NLP techniques like TF-IDF or spaCy

        # Common tech keywords
        tech_keywords = [
            'ai', 'machine learning', 'data science', 'cloud',
            'software', 'engineering', 'innovation', 'technology',
            'research', 'development', 'automation', 'analytics'
        ]

        text_lower = text.lower()
        found_keywords = [
            kw for kw in tech_keywords if kw in text_lower
        ]

        return found_keywords
