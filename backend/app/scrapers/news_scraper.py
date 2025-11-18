"""
News aggregation scraper for company-related news.

Scrapes recent news articles about companies from:
- Google News
- Company press releases
- Industry news sites
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
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


class NewsScraper(BaseScraper):
    """Scraper for company news and press releases."""

    def __init__(self, timeout: int = 30000, headless: bool = True):
        """
        Initialize news scraper.

        Args:
            timeout: Request timeout in milliseconds
            headless: Whether to run browser in headless mode
        """
        super().__init__(timeout, headless)

    async def scrape(
        self,
        company_name: str,
        days_back: int = 30,
        max_articles: int = 10,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Scrape recent news about a company.

        Args:
            company_name: Name of the company
            days_back: How many days back to search for news
            max_articles: Maximum number of articles to return
            **kwargs: Additional parameters

        Returns:
            Dict containing news articles
        """
        start_time = datetime.now()

        result = {
            "company_name": company_name,
            "scraped_at": start_time.isoformat(),
            "articles": [],
            "success": False
        }

        try:
            # Scrape from multiple sources
            articles = []

            # Google News
            google_articles = await self._scrape_google_news(
                company_name,
                max_articles
            )
            articles.extend(google_articles)

            # Sort by date (most recent first)
            articles.sort(
                key=lambda x: x.get('published_date', ''),
                reverse=True
            )

            result["articles"] = articles[:max_articles]
            result["success"] = True

        except Exception as e:
            self.logger.error(f"Error scraping news for {company_name}: {str(e)}")
            result["error"] = str(e)

        duration = (datetime.now() - start_time).total_seconds()
        self.log_scrape_metrics(
            "NewsScraper",
            result["success"],
            duration,
            len(result["articles"])
        )

        return result

    async def _scrape_google_news(
        self,
        company_name: str,
        max_articles: int = 10
    ) -> List[Dict[str, str]]:
        """
        Scrape Google News for company articles.

        Args:
            company_name: Company name to search
            max_articles: Max articles to return

        Returns:
            List of article dicts
        """
        articles = []

        # Build Google News search URL
        query = quote_plus(f"{company_name} company")
        url = f"https://news.google.com/search?q={query}&hl=en-US&gl=US&ceid=US:en"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    timeout=self.timeout / 1000,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Parse article elements
                    # Note: Google News HTML structure may change
                    article_elements = soup.find_all('article', limit=max_articles)

                    for elem in article_elements:
                        try:
                            title_elem = elem.find('a')
                            title = self.clean_text(
                                title_elem.get_text()
                            ) if title_elem else ""

                            # Get time (relative format like "2 hours ago")
                            time_elem = elem.find('time')
                            published = time_elem.get('datetime', '') if time_elem else ""

                            # Get source
                            source_elem = elem.find('a', {'data-n-tid': True})
                            source = self.clean_text(
                                source_elem.get_text()
                            ) if source_elem else "Unknown"

                            if title:
                                articles.append({
                                    "title": title,
                                    "source": source,
                                    "published_date": published,
                                    "url": ""  # Google News uses redirect URLs
                                })

                        except Exception as e:
                            self.logger.debug(f"Error parsing article: {str(e)}")
                            continue

        except Exception as e:
            self.logger.warning(f"Error scraping Google News: {str(e)}")

        return articles

    async def scrape_company_press_releases(
        self,
        company_website: str
    ) -> List[Dict[str, str]]:
        """
        Scrape press releases from company website.

        Args:
            company_website: Company website URL

        Returns:
            List of press release dicts
        """
        press_releases = []

        # Common press release page patterns
        press_urls = [
            f"{company_website}/news",
            f"{company_website}/press",
            f"{company_website}/newsroom",
            f"{company_website}/media",
        ]

        for url in press_urls:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        timeout=self.timeout / 1000,
                        follow_redirects=True
                    )

                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # Look for press release links
                        # This is a generic implementation
                        articles = soup.find_all('article')
                        if not articles:
                            articles = soup.find_all('div', class_=re.compile(r'news|press'))

                        for article in articles[:5]:  # Limit to 5 per page
                            title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                            if title_elem:
                                press_releases.append({
                                    "title": self.clean_text(title_elem.get_text()),
                                    "source": "Company Press Release",
                                    "published_date": "",
                                    "url": url
                                })

                        # If we found press releases, stop searching
                        if press_releases:
                            break

            except Exception as e:
                self.logger.debug(f"Error checking {url}: {str(e)}")
                continue

        return press_releases

    def summarize_news(self, articles: List[Dict[str, str]]) -> str:
        """
        Create a brief summary of news articles.

        Args:
            articles: List of article dicts

        Returns:
            Summary text
        """
        if not articles:
            return "No recent news found."

        summary_parts = [
            f"Found {len(articles)} recent articles:"
        ]

        for i, article in enumerate(articles[:3], 1):
            title = article.get('title', 'Untitled')
            source = article.get('source', 'Unknown')
            summary_parts.append(f"{i}. {title} ({source})")

        return "\n".join(summary_parts)
