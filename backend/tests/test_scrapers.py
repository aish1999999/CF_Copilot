"""
Unit tests for web scraping modules.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.company_scraper import CompanyScraper
from app.scrapers.news_scraper import NewsScraper
from app.scrapers.job_scraper import JobScraper


class TestBaseScraper:
    """Tests for BaseScraper class."""

    def test_validate_data_success(self):
        """Test data validation with all required fields."""
        scraper = BaseScraper()

        data = {
            "name": "Test",
            "email": "test@example.com",
            "phone": "123-456-7890"
        }
        required_fields = ["name", "email", "phone"]

        assert scraper.validate_data(data, required_fields) is True

    def test_validate_data_missing_field(self):
        """Test data validation with missing required field."""
        scraper = BaseScraper()

        data = {
            "name": "Test",
            "email": "test@example.com"
        }
        required_fields = ["name", "email", "phone"]

        assert scraper.validate_data(data, required_fields) is False

    def test_clean_text(self):
        """Test text cleaning utility."""
        scraper = BaseScraper()

        # Test with extra whitespace
        text = "  Hello   World  "
        assert scraper.clean_text(text) == "Hello World"

        # Test with None
        assert scraper.clean_text(None) == ""

        # Test with newlines
        text = "Line1\n\nLine2"
        assert scraper.clean_text(text) == "Line1 Line2"

    @pytest.mark.asyncio
    async def test_retry_on_failure(self):
        """Test retry mechanism."""
        scraper = BaseScraper()

        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "Success"

        result = await scraper.retry_on_failure(
            failing_func,
            max_retries=3,
            delay=0.1
        )

        assert result == "Success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test retry when all attempts fail."""
        scraper = BaseScraper()

        async def always_failing():
            raise Exception("Always fails")

        result = await scraper.retry_on_failure(
            always_failing,
            max_retries=2,
            delay=0.1
        )

        assert result is None


class TestCompanyScraper:
    """Tests for CompanyScraper class."""

    @pytest.mark.asyncio
    async def test_scrape_basic_structure(self):
        """Test basic scrape result structure."""
        scraper = CompanyScraper()

        # Mock scraping to avoid actual web requests
        with patch.object(scraper, '_scrape_company_website', new=AsyncMock(return_value={})):
            result = await scraper.scrape(
                "Test Company",
                website_url="https://example.com"
            )

            assert "company_name" in result
            assert "scraped_at" in result
            assert "description" in result
            assert "success" in result
            assert result["company_name"] == "Test Company"

    def test_extract_keywords(self):
        """Test keyword extraction from company description."""
        scraper = CompanyScraper()

        text = """
        We are a leading technology company specializing in machine learning,
        cloud computing, and data science solutions. Our team builds innovative
        software using Python and modern frameworks.
        """

        keywords = scraper.extract_keywords(text)

        assert "machine learning" in keywords
        assert "cloud" in keywords
        assert "data science" in keywords

    @pytest.mark.asyncio
    async def test_scrape_multiple_companies(self):
        """Test scraping multiple companies."""
        scraper = CompanyScraper()

        companies = [
            {"name": "Company A", "website": "https://companya.com"},
            {"name": "Company B", "website": "https://companyb.com"}
        ]

        # Mock the scrape method
        with patch.object(scraper, 'scrape', new=AsyncMock(return_value={"success": True})):
            results = await scraper.scrape_multiple_companies(companies)

            assert len(results) == 2
            assert all(r.get("success") for r in results)


class TestNewsScraper:
    """Tests for NewsScraper class."""

    @pytest.mark.asyncio
    async def test_scrape_basic_structure(self):
        """Test basic news scrape structure."""
        scraper = NewsScraper()

        # Mock scraping
        with patch.object(scraper, '_scrape_google_news', new=AsyncMock(return_value=[])):
            result = await scraper.scrape("Test Company")

            assert "company_name" in result
            assert "scraped_at" in result
            assert "articles" in result
            assert "success" in result
            assert result["company_name"] == "Test Company"

    @pytest.mark.asyncio
    async def test_scrape_with_mock_articles(self, sample_news_articles):
        """Test news scraping with mock articles."""
        scraper = NewsScraper()

        # Mock the scraping method to return sample articles
        with patch.object(
            scraper,
            '_scrape_google_news',
            new=AsyncMock(return_value=sample_news_articles)
        ):
            result = await scraper.scrape("TechCorp", max_articles=5)

            assert result["success"] is True
            assert len(result["articles"]) == 2
            assert result["articles"][0]["title"] == "TechCorp Launches New AI Platform"

    def test_summarize_news(self, sample_news_articles):
        """Test news summarization."""
        scraper = NewsScraper()

        summary = scraper.summarize_news(sample_news_articles)

        assert "Found 2 recent articles" in summary
        assert "TechCorp Launches New AI Platform" in summary

    def test_summarize_empty_news(self):
        """Test summarization with no articles."""
        scraper = NewsScraper()

        summary = scraper.summarize_news([])

        assert "No recent news found" in summary


class TestJobScraper:
    """Tests for JobScraper class."""

    @pytest.mark.asyncio
    async def test_scrape_basic_structure(self):
        """Test basic job scrape structure."""
        scraper = JobScraper()

        # Mock scraping
        with patch.object(scraper, '_scrape_indeed', new=AsyncMock(return_value=[])):
            result = await scraper.scrape("Test Company")

            assert "company_name" in result
            assert "scraped_at" in result
            assert "jobs" in result
            assert "success" in result

    @pytest.mark.asyncio
    async def test_scrape_with_mock_jobs(self, sample_job_postings):
        """Test job scraping with mock data."""
        scraper = JobScraper()

        # Mock both scraping methods
        with patch.object(
            scraper,
            '_scrape_indeed',
            new=AsyncMock(return_value=sample_job_postings)
        ):
            result = await scraper.scrape("TechCorp Solutions", max_jobs=10)

            assert result["success"] is True
            assert len(result["jobs"]) == 2
            assert result["jobs"][0]["title"] == "Software Engineer Intern"

    def test_filter_by_major(self, sample_job_postings):
        """Test filtering jobs by major."""
        scraper = JobScraper()

        # Add more specific job for testing
        jobs = sample_job_postings + [
            {
                "title": "Mechanical Design Engineer",
                "company": "TechCorp",
                "location": "Houston, TX",
                "position_type": "Full-Time",
                "url": "",
                "source": "Indeed"
            }
        ]

        # Filter for software jobs
        software_jobs = scraper.filter_by_major(jobs, "Computer Science")
        assert len(software_jobs) >= 1
        assert any("Software" in job["title"] for job in software_jobs)

        # Filter for mechanical jobs
        mech_jobs = scraper.filter_by_major(jobs, "Mechanical Engineering")
        assert any("Mechanical" in job["title"] for job in mech_jobs)


@pytest.mark.asyncio
async def test_scraper_error_handling():
    """Test error handling in scrapers."""
    scraper = CompanyScraper()

    # Test with invalid URL (should not crash)
    result = await scraper.scrape(
        "Test Company",
        website_url="invalid-url"
    )

    # Should return result with success=False or handle gracefully
    assert "company_name" in result
    assert result["company_name"] == "Test Company"


def test_scraper_logging(caplog):
    """Test that scrapers log appropriately."""
    scraper = BaseScraper()

    scraper.log_scrape_metrics(
        "TestScraper",
        success=True,
        duration=1.5,
        items_scraped=10
    )

    assert "TestScraper" in caplog.text
    assert "SUCCESS" in caplog.text
