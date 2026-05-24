import re
import time
from datetime import datetime
from typing import List, Optional

import requests

from src.base_scraper import BaseJobScraper
from src.models import Job


class WellfoundScraper(BaseJobScraper):
    def __init__(self, config: dict, logger):
        super().__init__(config, logger)
        self.base_url = config.get("platform_urls", {}).get("wellfound", "https://wellfound.com")
        self.api_url = config.get("firecrawl_api_url", "https://api.firecrawl.dev/v2")
        self.api_key = config.get("firecrawl_api_key")
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "JobAgent/1.0 (+https://example.com)",
            "Accept": "application/json",
        }
        self._search_cache = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        self.rate_limit = float(config.get("rate_limit_seconds", 2))
        self.max_pages = int(config.get("wellfound_max_pages", 1))

    def search_jobs(self, titles: List[str], location: Optional[str] = None) -> List[Job]:
        self.logger.info(f"Fetching Wellfound jobs using FireCrawl integration (location: {location or 'any'})")
        titles = [title.strip() for title in titles if title]
        if not titles:
            self.logger.warning("No job titles configured for Wellfound search")
            return []

        if not self.api_key:
            self.logger.warning("No FireCrawl API key configured; skipping Wellfound scraping")
            return []

        found_jobs = []
        seen_urls = set()
        queries = [title.lower() for title in titles]
        location_lower = location.lower() if location else None

        search_url = self.api_url.rstrip('/')

        title = titles[0]
        cache_key = (title.lower(), location_lower)
        if cache_key in self._search_cache:
            self.logger.debug(f"Using cached Wellfound results for query={title} location={location_lower}")
            return self._search_cache[cache_key]

        payload = self._build_request_payload(title, location_lower)
        if search_url.endswith("/search"):
            request_url = search_url
        elif search_url.endswith("/v1") or search_url.endswith("/v2"):
            request_url = f"{search_url}/search"
        else:
            request_url = f"{search_url}/v2/search"
        self.logger.debug(f"Wellfound FireCrawl request POST {request_url} payload={payload}")
        response = self.session.post(
            request_url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        items = self._extract_items(data)
        self.logger.debug(
            f"Wellfound FireCrawl returned {len(items)} results for title '{title}'"
        )

        if items:
            for item in items:
                job = self._parse_job_item(item)
                if not job:
                    continue
                if job.url in seen_urls:
                    continue
                if not self._is_job_url(job.url):
                    continue
                if not self._matches_title(job.title, queries, job.description or ""):
                    continue
                if location_lower and not self._matches_location(job.location or "", location_lower):
                    continue
                found_jobs.append(job)
                seen_urls.add(job.url)

        self.logger.info(f"Extracted {len(found_jobs)} Wellfound jobs")
        self._search_cache[cache_key] = found_jobs
        return found_jobs

    def _build_request_payload(self, title: str, location: Optional[str]) -> dict:
        payload = {
            "query": title,
            "limit": min(self.max_pages * 10, 100),
            "sources": ["web"],
            "includeDomains": ["wellfound.com"],
        }

        if location:
            payload["location"] = location

        return payload

    def _extract_items(self, data: dict) -> List[dict]:
        if not isinstance(data, dict):
            return []

        # Handle the nested FireCrawl search response format.
        if isinstance(data.get("data"), dict):
            nested = data["data"].get("web") or data["data"].get("results") or data["data"].get("items")
            if isinstance(nested, list):
                return nested

        for key in ("results", "jobs", "items", "data", "searchResults", "web"):
            if isinstance(data.get(key), list):
                return data.get(key)

        return []

    def _parse_job_item(self, item: dict) -> Optional[Job]:
        if hasattr(item, "dict"):
            item = item.dict(by_alias=True, exclude_none=True)

        title = self._normalize_string(
            item.get("title") or item.get("job_title") or item.get("position") or ""
        )
        company = self._normalize_string(
            item.get("company") or item.get("company_name") or item.get("startup") or ""
        )
        location = self._normalize_string(
            item.get("location") or item.get("city") or item.get("remote") or ""
        )
        salary = self._normalize_string(item.get("salary") or item.get("compensation") or "")
        url = self._normalize_url(item)
        description = self._normalize_string(
            item.get("description") or item.get("summary") or item.get("details") or ""
        )

        if not title or not url:
            return None

        return Job(
            job_id=f"wellfound-{item.get('id') or item.get('job_id') or hash(url)}",
            platform="Wellfound",
            title=title,
            company=company,
            location=location,
            description=description,
            salary=salary,
            url=url,
            scrape_date=datetime.utcnow(),
            extra={"source": self.api_url, "job_id": item.get("id") or item.get("job_id")},
        )

    def _normalize_url(self, item: dict) -> str:
        url = item.get("url") or item.get("job_url") or item.get("apply_url") or ""
        url = self._normalize_string(url)
        if url and not url.startswith("http"):
            url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        return url

    def _is_job_url(self, url: str) -> bool:
        """Check if URL is an actual Wellfound job posting or role page."""
        if not url:
            return False

        url_lower = url.lower()
        if "wellfound.com" not in url_lower:
            return False

        # Reject generic content pages and external resources.
        non_job_patterns = [
            "reddit.com",
            "medium.com",
            "coursera.org",
            "youtube.com",
            "atlassian.com",
            "intercom.com",
            "indeed.com",
            "builtinla.com",
            "productfocus.com",
            "productplan.com",
            "ikmultimedia.com",
            ".pdf",
            ".doc",
            ".docx",
        ]
        for pattern in non_job_patterns:
            if pattern in url_lower:
                return False

        # Accept wellfound role/job URLs only.
        return "/role/" in url_lower or "/jobs/" in url_lower

    def _matches_title(self, title: str, queries: List[str], description: str) -> bool:
        if not queries:
            return True

        title_lower = title.lower()
        description_lower = description.lower() if description else ""

        for query in queries:
            if query in title_lower:
                continue
            if query in description_lower:
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
