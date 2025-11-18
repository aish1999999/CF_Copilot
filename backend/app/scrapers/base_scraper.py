"""
Base scraper class with common utilities and error handling.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    def __init__(self, timeout: int = 30000, headless: bool = True):
        """
        Initialize base scraper.

        Args:
            timeout: Request timeout in milliseconds
            headless: Whether to run browser in headless mode
        """
        self.timeout = timeout
        self.headless = headless
        self.logger = logger

    @abstractmethod
    async def scrape(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Abstract scrape method to be implemented by subclasses.

        Args:
            query: Search query or company name
            **kwargs: Additional scraping parameters

        Returns:
            Dict containing scraped data
        """
        pass

    def validate_data(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate scraped data has required fields.

        Args:
            data: Scraped data dictionary
            required_fields: List of required field names

        Returns:
            True if all required fields present, False otherwise
        """
        return all(field in data and data[field] for field in required_fields)

    def clean_text(self, text: Optional[str]) -> str:
        """
        Clean and normalize text data.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = " ".join(text.split())
        # Remove special characters
        text = text.strip()

        return text

    async def retry_on_failure(
        self,
        func,
        max_retries: int = 3,
        delay: float = 1.0,
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        Retry a function on failure with exponential backoff.

        Args:
            func: Async function to retry
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries in seconds
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Function result or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"All retries failed: {str(e)}")
                    return None

                wait_time = delay * (2 ** attempt)
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

        return None

    def log_scrape_metrics(
        self,
        scraper_name: str,
        success: bool,
        duration: float,
        items_scraped: int = 0
    ):
        """
        Log scraping metrics for monitoring.

        Args:
            scraper_name: Name of the scraper
            success: Whether scraping was successful
            duration: Time taken in seconds
            items_scraped: Number of items successfully scraped
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"[{scraper_name}] {status} - "
            f"Duration: {duration:.2f}s, Items: {items_scraped}"
        )
