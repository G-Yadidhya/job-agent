import time
from datetime import datetime
import re
from typing import List, Optional

import requests

from src.base_scraper import BaseJobScraper
from src.models import Job


class RemoteOKScraper(BaseJobScraper):
    def __init__(self, config: dict, logger):
        super().__init__(config, logger)
        self.api_url = config.get("remoteok_api_url", "https://remoteok.com/api")
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "JobAgent/1.0 (+https://example.com)",
            "Accept": "application/json",
        }
        self.rate_limit = float(config.get("rate_limit_seconds", 1))

    def search_jobs(self, titles: List[str], location: Optional[str] = None) -> List[Job]:
        self.logger.info(f"Fetching RemoteOK jobs from API (location: {location or 'any'})")
        response = self.session.get(self.api_url, headers=self.headers, timeout=15)
        response.raise_for_status()

        raw_jobs = response.json()
        titles = [title.strip().lower() for title in titles if title]

        extracted_jobs = []
        for item in raw_jobs:
            if not isinstance(item, dict):
                continue

            if not self._is_remoteok_job_item(item):
                continue

            title = self._normalize_string(item.get("position") or item.get("title") or "")
            if not self._matches_title(title, titles, item):
                continue

            if location:
                self.logger.debug(f"Ignoring RemoteOK location filter for '{location}'; matching by role only")

            job = Job(
                job_id=self._build_job_id(item),
                platform="RemoteOK",
                title=title,
                company=self._normalize_string(item.get("company")),
                location=self._normalize_string(item.get("location")),
                description=self._normalize_string(item.get("description")),
                salary=self._normalize_string(item.get("salary")),
                url=self._normalize_url(item),
                scrape_date=datetime.utcnow(),
                extra={
                    "tags": item.get("tags", []),
                    "remote": item.get("remote", True),
                },
            )
            extracted_jobs.append(job)

        time.sleep(self.rate_limit)

        self.logger.info(f"Extracted {len(extracted_jobs)} RemoteOK jobs")
        return extracted_jobs

    def _is_remoteok_job_item(self, item: dict) -> bool:
        return bool(item.get("company") and (item.get("position") or item.get("title")))

    def _build_job_id(self, item: dict) -> str:
        return f"remoteok-{item.get('id') or item.get('slug') or item.get('date', '')}"

    def _normalize_url(self, item: dict) -> str:
        url = item.get("url") or item.get("apply_url") or ""
        return url if url.startswith("http") else f"https://remoteok.com{url}"

    def _matches_title(self, title: str, titles: List[str], item: dict) -> bool:
        if not titles:
            return True

        title_lower = title.lower()
        description_lower = self._normalize_string(item.get("description", "")).lower()
        tags = [str(tag).lower() for tag in (item.get("tags") or [])]
        combined_text = " ".join([title_lower, description_lower] + tags)

        for query in titles:
            query_lower = query.lower()
            if query_lower in title_lower:
                continue
            if query_lower in description_lower:
                continue
            if any(query_lower in tag for tag in tags):
                continue

            query_words = re.findall(r"\w+", query_lower)
            if query_words and all(word in combined_text for word in query_words):
                continue

            return False

        return True

    def _matches_location(self, job_location: str, query_location: str) -> bool:
        """Check if job location matches the query location. Allow missing locations."""
        if not query_location:
            return True
        
        job_location = self._normalize_string(job_location)
        if not job_location:
            return True  # Allow jobs with missing location

        job_loc_lower = job_location.lower()
        if query_location == "remote":
            return any(
                keyword in job_loc_lower
                for keyword in ["remote", "work from home", "wfh", "worldwide", "global"]
            )

        return bool(re.search(rf"\b{re.escape(query_location)}\b", job_loc_lower))

