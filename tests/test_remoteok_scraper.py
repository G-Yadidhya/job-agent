from datetime import datetime

from src.remoteok_scraper import RemoteOKScraper
from src.logger import get_logger


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


def make_remoteok_item(id_, title, tags, description, location="Remote", company="Acme Corp"):
    return {
        "id": id_,
        "company": company,
        "position": title,
        "location": location,
        "description": description,
        "salary": "$120000",
        "url": f"https://remoteok.com/remote-jobs/{id_}",
        "tags": tags,
    }


def test_remoteok_scraper_extracts_matching_jobs(monkeypatch):
    config = {
        "remoteok_api_url": "https://remoteok.com/api",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_remoteok_scraper", "DEBUG")
    scraper = RemoteOKScraper(config, logger)

    payload = [
        {"id": 1, "company": "Acme Corp", "position": "Software Engineer", "location": "Remote", "description": "Build APIs", "salary": "$120000", "url": "https://remoteok.com/remote-jobs/1", "tags": ["python", "backend"]},
        {"id": 2, "company": "Other Inc", "position": "Marketing Manager", "location": "Remote", "description": "Lead campaigns", "salary": "$90000", "url": "https://remoteok.com/remote-jobs/2", "tags": ["marketing"]},
    ]
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Software Engineer"])

    assert len(jobs) == 1
    assert jobs[0].platform == "RemoteOK"
    assert jobs[0].title == "Software Engineer"
    assert jobs[0].company == "Acme Corp"
    assert jobs[0].job_id == "remoteok-1"
    assert jobs[0].url == "https://remoteok.com/remote-jobs/1"


def test_remoteok_scraper_filters_by_tags(monkeypatch):
    config = {
        "remoteok_api_url": "https://remoteok.com/api",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_remoteok_scraper", "DEBUG")
    scraper = RemoteOKScraper(config, logger)

    payload = [
        {"id": 3, "company": "Startup X", "position": "Product Designer", "location": "Remote", "description": "Design SaaS products", "salary": "", "url": "https://remoteok.com/remote-jobs/3", "tags": ["product manager", "design"]},
    ]
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Product Manager"])

    assert len(jobs) == 1
    assert "Product" in jobs[0].title or "product manager" in jobs[0].extra["tags"]


def test_remoteok_scraper_word_split_matching(monkeypatch):
    config = {
        "remoteok_api_url": "https://remoteok.com/api",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_remoteok_scraper", "DEBUG")
    scraper = RemoteOKScraper(config, logger)

    payload = [
        make_remoteok_item(6, "Product Designer", ["product"], "This role works with manager teams"),
    ]
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Product Manager"])

    assert len(jobs) == 1
    assert jobs[0].title == "Product Designer"


def test_remoteok_scraper_ignores_location_filter(monkeypatch):
    config = {
        "remoteok_api_url": "https://remoteok.com/api",
        "rate_limit_seconds": 0,
    }
    logger = get_logger("test_remoteok_scraper", "DEBUG")
    scraper = RemoteOKScraper(config, logger)

    payload = [
        {"id": 4, "company": "City Tech", "position": "Software Engineer", "location": "Bangalore, India", "description": "Build APIs", "salary": "$120000", "url": "https://remoteok.com/jobs/4", "tags": ["python"]},
        {"id": 5, "company": "Remote Labs", "position": "Software Engineer", "location": "Remote", "description": "Build APIs", "salary": "$120000", "url": "https://remoteok.com/remote-jobs/5", "tags": ["remote"]},
    ]
    monkeypatch.setattr(scraper, "session", DummySession(DummyResponse(payload)))

    jobs = scraper.search_jobs(["Software Engineer"], location="bangalore")

    assert len(jobs) == 2
    assert any(job.company == "City Tech" for job in jobs)
    assert any(job.company == "Remote Labs" for job in jobs)
