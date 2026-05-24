from src.logger import get_logger
from src.wellfound_scraper import WellfoundScraper


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

    def post(self, *args, **kwargs):
        return self._response


class CountingSession(DummySession):
    def __init__(self, response):
        super().__init__(response)
        self.call_count = 0

    def post(self, *args, **kwargs):
        self.call_count += 1
        return super().post(*args, **kwargs)


def test_wellfound_scraper_makes_single_api_call(monkeypatch):
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v1",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    payload = {
        "results": [
            {
                "id": "abc128",
                "title": "Product Manager",
                "company_name": "City Tech",
                "location": "Bangalore, India",
                "description": "Build scalable systems",
                "url": "https://wellfound.com/jobs/product-manager-abc128",
            }
        ],
    }

    counting_session = CountingSession(DummyResponse(payload))
    monkeypatch.setattr(scraper, "session", counting_session)

    scraper.search_jobs(["Product Manager"], location="bangalore")

    assert counting_session.call_count == 1


def test_wellfound_scraper_parses_api_response(monkeypatch):
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v1",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    payload = {
        "total_pages": 1,
        "results": [
            {
                "id": "abc123",
                "title": "Software Engineer",
                "company_name": "Startup X",
                "location": "Remote",
                "salary": "$140k",
                "description": "Build product infrastructure",
                "url": "https://wellfound.com/jobs/software-engineer-abc123",
            }
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Software Engineer"])

    assert len(jobs) == 1
    assert jobs[0].platform == "Wellfound"
    assert jobs[0].title == "Software Engineer"
    assert jobs[0].company == "Startup X"
    assert jobs[0].location == "Remote"
    assert jobs[0].salary == "$140k"
    assert jobs[0].url == "https://wellfound.com/jobs/software-engineer-abc123"


def test_wellfound_scraper_builds_search_payload():
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v1",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
        "wellfound_max_pages": 3,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    payload = scraper._build_request_payload("Software Engineer", "bangalore")

    assert payload["query"] == "Software Engineer"
    assert payload["location"] == "bangalore"
    assert payload["limit"] == 30
    assert payload["includeDomains"] == ["wellfound.com"]
    assert payload["sources"] == ["web"]


def test_wellfound_scraper_restricts_search_to_wellfound_domain(monkeypatch):
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v2",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    captured = {}

    class RecordingSession(DummySession):
        def post(self, *args, **kwargs):
            captured["url"] = args[0] if args else kwargs.get("url")
            captured["payload"] = kwargs.get("json")
            return super().post(*args, **kwargs)

    response_payload = {
        "success": True,
        "data": {
            "web": [
                {
                    "id": "abc123",
                    "title": "Software Engineer",
                    "company_name": "Startup X",
                    "location": "Remote",
                    "salary": "$140k",
                    "description": "Build product infrastructure",
                    "url": "https://wellfound.com/jobs/software-engineer-abc123",
                }
            ]
        },
    }
    monkeypatch.setattr(scraper, "session", RecordingSession(DummyResponse(response_payload)))

    jobs = scraper.search_jobs(["Software Engineer"])

    assert captured["payload"]["includeDomains"] == ["wellfound.com"]
    assert captured["payload"]["sources"] == ["web"]
    assert captured["url"].endswith("/search")
    assert len(jobs) == 1
    assert jobs[0].url == "https://wellfound.com/jobs/software-engineer-abc123"


def test_wellfound_scraper_builds_v2_search_url_from_base_api_url(monkeypatch):
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.dev",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    captured = {}

    class RecordingSession(DummySession):
        def post(self, *args, **kwargs):
            captured["url"] = args[0] if args else kwargs.get("url")
            captured["payload"] = kwargs.get("json")
            return super().post(*args, **kwargs)

    response_payload = {
        "success": True,
        "data": {
            "web": [
                {
                    "id": "abc128",
                    "title": "Product Manager",
                    "company_name": "City Tech",
                    "location": "Bangalore, India",
                    "description": "Build scalable systems",
                    "url": "https://wellfound.com/jobs/product-manager-abc128",
                }
            ],
        },
    }
    monkeypatch.setattr(scraper, "session", RecordingSession(DummyResponse(response_payload)))

    jobs = scraper.search_jobs(["Product Manager"], location="bangalore")

    assert captured["url"] == "https://api.firecrawl.dev/v2/search"
    assert captured["payload"]["includeDomains"] == ["wellfound.com"]
    assert captured["payload"]["sources"] == ["web"]
    assert len(jobs) == 1
    assert jobs[0].company == "City Tech"


def test_wellfound_scraper_uses_single_page_by_default():
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v1",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    payload = scraper._build_request_payload("Product Manager", "bangalore")

    assert payload["query"] == "Product Manager"
    assert payload["location"] == "bangalore"
    assert payload["limit"] == 10


def test_wellfound_scraper_filters_by_description(monkeypatch):
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v1",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    payload = {
        "total_pages": 1,
        "results": [
            {
                "id": "abc124",
                "title": "Engineering Lead",
                "company_name": "Startup Y",
                "location": "San Francisco",
                "salary": "",
                "description": "This role is focused on software engineering and backend systems",
                "url": "https://wellfound.com/jobs/engineering-lead-abc124",
            }
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Software Engineer"])

    assert len(jobs) == 1
    assert jobs[0].title == "Engineering Lead"


def test_wellfound_scraper_filters_by_exact_location(monkeypatch):
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v1",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
        "wellfound_max_pages": 2,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    payload = {
        "results": [
            {
                "id": "abc126",
                "title": "Software Engineer",
                "company_name": "City Tech",
                "location": "Bangalore, India",
                "description": "Build scalable systems",
                "url": "https://wellfound.com/jobs/software-engineer-abc126",
            },
            {
                "id": "abc127",
                "title": "Software Engineer",
                "company_name": "Remote Labs",
                "location": "Remote",
                "description": "Build scalable systems",
                "url": "https://wellfound.com/jobs/software-engineer-abc127",
            },
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Software Engineer"], location="bangalore")

    assert len(jobs) == 1
    assert jobs[0].company == "City Tech"
    assert "Bangalore" in jobs[0].location


def test_wellfound_scraper_rejects_non_wellfound_urls(monkeypatch):
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v1",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
        "wellfound_max_pages": 2,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    payload = {
        "results": [
            {
                "id": "abc126",
                "title": "Product Manager",
                "company_name": "City Tech",
                "location": "Bangalore, India",
                "description": "Build scalable systems",
                "url": "https://www.ziprecruiter.com/Jobs/Product-Manager",
            },
            {
                "id": "abc127",
                "title": "Product Manager",
                "company_name": "Remote Labs",
                "location": "Bangalore, India",
                "description": "Build scalable systems",
                "url": "https://wellfound.com/role/l/product-manager/bangalore",
            },
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Product Manager"], location="bangalore")

    assert len(jobs) == 1
    assert jobs[0].company == "Remote Labs"
    assert "wellfound.com" in jobs[0].url


def test_wellfound_scraper_deduplicates_by_url(monkeypatch):
    config = {
        "platform_urls": {"wellfound": "https://wellfound.com"},
        "firecrawl_api_url": "https://api.firecrawl.com/v1",
        "firecrawl_api_key": "test-key",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_wellfound_scraper", "DEBUG")
    scraper = WellfoundScraper(config, logger)

    payload = {
        "total_pages": 1,
        "results": [
            {
                "id": "abc125",
                "title": "Software Engineer",
                "company_name": "Startup Z",
                "location": "Remote",
                "description": "Build product features",
                "url": "https://wellfound.com/jobs/software-engineer-abc125",
            },
            {
                "id": "abc125",
                "title": "Software Engineer",
                "company_name": "Startup Z",
                "location": "Remote",
                "description": "Build product features",
                "url": "https://wellfound.com/jobs/software-engineer-abc125",
            },
        ],
    }
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Software Engineer"])

    assert len(jobs) == 1
