from datetime import datetime

from src.aggregator import JobAggregator
from src.models import Job


def make_job(job_id: str, url: str, title: str, company: str, location: str) -> Job:
    return Job(
        job_id=job_id,
        platform="TestPlatform",
        title=title,
        company=company,
        location=location,
        description="Description",
        salary="$100k",
        url=url,
        scrape_date=datetime.utcnow(),
    )


def test_job_aggregator_deduplicates_same_url():
    aggregator = JobAggregator()
    jobs = [
        make_job("1", "https://example.com/job/1", "Software Engineer", "Company A", "Remote"),
        make_job("2", "https://example.com/job/1", "Software Engineer", "Company A", "Remote"),
    ]

    result = aggregator.aggregate([jobs])

    assert len(result) == 1
    assert result[0].url == "https://example.com/job/1"
    assert result[0].title == "Software Engineer"


def test_job_aggregator_deduplicates_missing_url_using_fallback():
    aggregator = JobAggregator()
    jobs = [
        make_job("1", "", "Data Scientist", "Company B", "Bangalore"),
        make_job("2", "", "Data Scientist", "Company B", "Bangalore"),
    ]

    result = aggregator.aggregate([jobs])

    assert len(result) == 1
    assert result[0].company == "Company B"


def test_job_aggregator_normalizes_text_fields():
    aggregator = JobAggregator()
    jobs = [
        make_job("1", " https://example.com/job/1 ", " Software Engineer ", " Company A ", " Remote ")
    ]

    result = aggregator.aggregate([jobs])

    assert result[0].title == "Software Engineer"
    assert result[0].company == "Company A"
    assert result[0].url == "https://example.com/job/1"
