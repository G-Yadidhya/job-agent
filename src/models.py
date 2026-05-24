from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class Job:
    job_id: str
    platform: str
    title: str
    company: Optional[str]
    location: Optional[str]
    description: Optional[str]
    salary: Optional[str]
    url: str
    scrape_date: datetime
    extra: Optional[dict] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["scrape_date"] = self.scrape_date.isoformat()
        return data
