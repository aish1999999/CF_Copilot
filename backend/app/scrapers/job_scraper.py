"""
Job posting scraper for career fair companies.

Scrapes job postings from:
- Company career pages
- Indeed
- LinkedIn Jobs
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from urllib.parse import quote_plus

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from bs4 import BeautifulSoup
import httpx
from .base_scraper import BaseScraper


class JobScraper(BaseScraper):
    """Scraper for job postings from company career pages."""

    def __init__(self, timeout: int = 30000, headless: bool = True):
        """
        Initialize job scraper.

        Args:
            timeout: Request timeout in milliseconds
            headless: Whether to run browser in headless mode
        """
        super().__init__(timeout, headless)

    async def scrape(
        self,
        company_name: str,
        position_types: Optional[List[str]] = None,
        max_jobs: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Scrape job postings for a company.

        Args:
            company_name: Name of the company
            position_types: Filter by position types (e.g., ["Internship", "Full-Time"])
            max_jobs: Maximum number of jobs to return
            **kwargs: Additional parameters (career_page_url, location, etc.)

        Returns:
            Dict containing job postings
        """
        start_time = datetime.now()

        position_types = position_types or [
            "Full-Time",
            "Internship",
            "Co-Op"
        ]

        result = {
            "company_name": company_name,
            "scraped_at": start_time.isoformat(),
            "jobs": [],
            "success": False
        }

        try:
            jobs = []

            # Scrape from company career page if provided
            career_url = kwargs.get("career_page_url")
            if career_url:
                company_jobs = await self._scrape_company_careers(
                    career_url,
                    position_types
                )
                jobs.extend(company_jobs)

            # Scrape from Indeed
            indeed_jobs = await self._scrape_indeed(
                company_name,
                position_types,
                max_jobs=max_jobs // 2
            )
            jobs.extend(indeed_jobs)

            # Remove duplicates based on title
            seen_titles = set()
            unique_jobs = []
            for job in jobs:
                title_lower = job.get('title', '').lower()
                if title_lower not in seen_titles:
                    seen_titles.add(title_lower)
                    unique_jobs.append(job)

            result["jobs"] = unique_jobs[:max_jobs]
            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error scraping jobs for {company_name}: {str(e)}")
            result["error"] = str(e)

        duration = (datetime.now() - start_time).total_seconds()
        self.log_scrape_metrics(
            "JobScraper",
            result["success"],
            duration,
            len(result["jobs"])
        )

        return result

    async def _scrape_company_careers(
        self,
        url: str,
        position_types: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Scrape jobs from company career page.

        Args:
            url: Career page URL
            position_types: Position types to filter

        Returns:
            List of job dicts
        """
        jobs = []

        if not PLAYWRIGHT_AVAILABLE:
            return jobs

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=self.timeout)

                # Wait for content to load
                await page.wait_for_timeout(2000)

                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Common job listing selectors
                job_elements = soup.find_all(
                    ['div', 'li'],
                    class_=re.compile(r'job|position|opening', re.I)
                )

                for elem in job_elements[:20]:
                    try:
                        # Extract job title
                        title_elem = elem.find(['h2', 'h3', 'h4', 'a'])
                        if not title_elem:
                            continue

                        title = self.clean_text(title_elem.get_text())

                        # Check if position type matches
                        elem_text = elem.get_text().lower()
                        matching_type = None
                        for ptype in position_types:
                            if ptype.lower() in elem_text:
                                matching_type = ptype
                                break

                        # Extract location
                        location_elem = elem.find(
                            text=re.compile(r'location|city|remote', re.I)
                        )
                        location = ""
                        if location_elem:
                            location = self.clean_text(
                                location_elem.find_parent().get_text()
                            )

                        # Get job link
                        link_elem = elem.find('a', href=True)
                        job_url = link_elem.get('href', '') if link_elem else ""

                        if title:
                            jobs.append({
                                "title": title,
                                "company": "",  # Will be filled by caller
                                "location": location,
                                "position_type": matching_type or "Unknown",
                                "url": job_url,
                                "source": "Company Website"
                            })

                    except Exception as e:
                        self.logger.debug(f"Error parsing job element: {str(e)}")
                        continue

            except Exception as e:
                self.logger.warning(f"Error scraping {url}: {str(e)}")

            finally:
                await browser.close()

        return jobs

    async def _scrape_indeed(
        self,
        company_name: str,
        position_types: List[str],
        max_jobs: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scrape jobs from Indeed.

        Args:
            company_name: Company name to search
            position_types: Position types to include
            max_jobs: Max jobs to return

        Returns:
            List of job dicts
        """
        jobs = []

        # Build Indeed search URL
        query = quote_plus(f"{company_name}")
        url = f"https://www.indeed.com/jobs?q={query}&l=United+States"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    timeout=self.timeout / 1000,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    follow_redirects=True
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Indeed job card selector (may change)
                    job_cards = soup.find_all(
                        'div',
                        class_=re.compile(r'job_seen_beacon|jobsearch-SerpJobCard'),
                        limit=max_jobs
                    )

                    for card in job_cards:
                        try:
                            # Title
                            title_elem = card.find('h2', class_=re.compile(r'jobTitle'))
                            if not title_elem:
                                title_elem = card.find('a', class_=re.compile(r'jcs-JobTitle'))

                            title = self.clean_text(
                                title_elem.get_text()
                            ) if title_elem else ""

                            # Company (verify it matches)
                            company_elem = card.find('span', class_=re.compile(r'companyName'))
                            company = self.clean_text(
                                company_elem.get_text()
                            ) if company_elem else ""

                            # Skip if not from target company
                            if company_name.lower() not in company.lower():
                                continue

                            # Location
                            location_elem = card.find('div', class_=re.compile(r'companyLocation'))
                            location = self.clean_text(
                                location_elem.get_text()
                            ) if location_elem else ""

                            # Determine position type
                            card_text = card.get_text().lower()
                            position_type = "Unknown"
                            for ptype in position_types:
                                if ptype.lower() in card_text:
                                    position_type = ptype
                                    break

                            # Job URL
                            link_elem = card.find('a', href=True)
                            job_url = ""
                            if link_elem:
                                job_url = f"https://www.indeed.com{link_elem['href']}"

                            if title and company:
                                jobs.append({
                                    "title": title,
                                    "company": company,
                                    "location": location,
                                    "position_type": position_type,
                                    "url": job_url,
                                    "source": "Indeed"
                                })

                        except Exception as e:
                            self.logger.debug(f"Error parsing Indeed job card: {str(e)}")
                            continue

        except Exception as e:
            self.logger.warning(f"Error scraping Indeed: {str(e)}")

        return jobs

    def filter_by_major(
        self,
        jobs: List[Dict[str, Any]],
        major: str
    ) -> List[Dict[str, Any]]:
        """
        Filter jobs by major/discipline.

        Args:
            jobs: List of job dicts
            major: Major to filter by (e.g., "Computer Science", "Mechanical Engineering")

        Returns:
            Filtered list of jobs
        """
        # Keywords associated with different majors
        major_keywords = {
            "computer science": ["software", "developer", "programming", "engineer"],
            "mechanical engineering": ["mechanical", "manufacturing", "design", "cad"],
            "electrical engineering": ["electrical", "electronics", "circuit", "power"],
            "chemical engineering": ["chemical", "process", "refinery", "plant"],
            "civil engineering": ["civil", "structural", "construction", "infrastructure"],
        }

        major_lower = major.lower()
        keywords = major_keywords.get(major_lower, [major_lower])

        filtered_jobs = []
        for job in jobs:
            title_lower = job.get('title', '').lower()
            if any(kw in title_lower for kw in keywords):
                filtered_jobs.append(job)

        return filtered_jobs
