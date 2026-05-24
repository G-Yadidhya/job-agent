from src.logger import get_logger
from src.naukri_scraper import NaukriScraper


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class DummySession:
    def __init__(self, response):
        self._response = response

    def get(self, *args, **kwargs):
        return self._response


def test_naukri_scraper_parses_api_response(monkeypatch):
    config = {
        "platform_urls": {"naukri": "https://www.naukri.com"},
        "naukri_api_url": "https://www.naukri.com/jobapi/v2/search",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_naukri_scraper", "DEBUG")
    scraper = NaukriScraper(config, logger)

    payload = {
        "totalpages": 1,
        "list": [
            {
                "jobId": "12345",
                "post": "Software Engineer",
                "companyName": "Acme Corp",
                "cityfield": "Remote",
                "SALARY": "₹10,00,000 - ₹12,00,000",
                "jobDesc": "Build backend APIs and services",
                "urlStr": "https://www.naukri.com/job-listings/software-engineer-acme-corp-12345",
            }
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Software Engineer"])

    assert len(jobs) == 1
    assert jobs[0].platform == "Naukri"
    assert jobs[0].title == "Software Engineer"
    assert jobs[0].company == "Acme Corp"
    assert jobs[0].location == "Remote"
    assert jobs[0].salary == "₹10,00,000 - ₹12,00,000"
    assert jobs[0].description == "Build backend APIs and services"
    assert jobs[0].url == "https://www.naukri.com/job-listings/software-engineer-acme-corp-12345"


def test_naukri_scraper_filters_by_title(monkeypatch):
    config = {
        "platform_urls": {"naukri": "https://www.naukri.com"},
        "naukri_api_url": "https://www.naukri.com/jobapi/v2/search",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_naukri_scraper", "DEBUG")
    scraper = NaukriScraper(config, logger)

    payload = {
        "totalpages": 1,
        "list": [
            {
                "jobId": "54321",
                "post": "Frontend Developer",
                "companyName": "Beta Labs",
                "cityfield": "Bengaluru",
                "jobDesc": "React developer role",
                "urlStr": "https://www.naukri.com/job-listings/frontend-developer-beta-labs-54321",
            }
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Frontend"])

    assert len(jobs) == 1
    assert jobs[0].title == "Frontend Developer"


def test_naukri_scraper_normalizes_bangalore_location(monkeypatch):
    config = {
        "platform_urls": {"naukri": "https://www.naukri.com"},
        "naukri_api_url": "https://www.naukri.com/jobapi/v2/search",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_naukri_scraper", "DEBUG")
    scraper = NaukriScraper(config, logger)

    payload = {
        "totalpages": 1,
        "list": [
            {
                "jobId": "67890",
                "post": "Product Manager",
                "companyName": "Gamma Works",
                "cityfield": "Bengaluru",
                "jobDesc": "Product ownership and delivery",
                "urlStr": "https://www.naukri.com/job-listings/product-manager-gamma-works-67890",
            }
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Product Manager"], location="bangalore")

    assert len(jobs) == 1
    assert jobs[0].location == "Bengaluru"
    assert jobs[0].title == "Product Manager"


def test_naukri_scraper_deduplicates_by_url(monkeypatch):
    config = {
        "platform_urls": {"naukri": "https://www.naukri.com"},
        "naukri_api_url": "https://www.naukri.com/jobapi/v2/search",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_naukri_scraper", "DEBUG")
    scraper = NaukriScraper(config, logger)

    payload = {
        "totalpages": 1,
        "list": [
            {
                "jobId": "12345",
                "post": "Software Engineer",
                "companyName": "Acme Corp",
                "cityfield": "Remote",
                "jobDesc": "Build backend APIs",
                "urlStr": "https://www.naukri.com/job-listings/software-engineer-acme-corp-12345",
            },
            {
                "jobId": "12345",
                "post": "Software Engineer",
                "companyName": "Acme Corp",
                "cityfield": "Remote",
                "jobDesc": "Build backend APIs",
                "urlStr": "https://www.naukri.com/job-listings/software-engineer-acme-corp-12345",
            },
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Software Engineer"])

    assert len(jobs) == 1
