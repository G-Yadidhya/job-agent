from datetime import datetime
from pathlib import Path

from src.csv_exporter import CSVExporter
from src.models import Job


def make_job(job_id: str) -> Job:
    return Job(
        job_id=job_id,
        platform="TestPlatform",
        title="Software Engineer",
        company="Company A",
        location="Remote",
        description="Test role",
        salary="$100k",
        url="https://example.com/job/1",
        scrape_date=datetime.utcnow(),
    )


def test_csv_exporter_writes_csv(tmp_path):
    output_path = tmp_path / "jobs.csv"
    exporter = CSVExporter(str(output_path))
    csv_path = exporter.export([make_job("1")])

    assert output_path.exists()
    assert str(output_path) == csv_path
    content = output_path.read_text(encoding="utf-8")
    assert "Software Engineer" in content
    assert "Company A" in content


from pathlib import Path


def test_csv_exporter_timestamped_output(tmp_path):
    output_path = tmp_path / "jobs.csv"
    exporter = CSVExporter(str(output_path), timestamp_output=True)
    csv_path = exporter.export([make_job("1")])

    assert csv_path != str(output_path)
    assert csv_path.endswith(".csv")
    assert Path(csv_path).exists()
