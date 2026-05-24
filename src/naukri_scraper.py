import time
from datetime import datetime
from typing import List, Optional

import requests

from src.base_scraper import BaseJobScraper
from src.models import Job


class NaukriScraper(BaseJobScraper):
    LOCATION_ALIASES = {
        "bangalore": "bengaluru",
        "bengaluru": "bengaluru",
        "bombay": "mumbai",
        "mumbai": "mumbai",
        "new delhi": "delhi",
        "delhi": "delhi",
        "gurgaon": "gurugram",
        "gurugram": "gurugram",
        "noida": "noida",
    }

    def __init__(self, config: dict, logger):
        super().__init__(config, logger)
        self.base_url = config.get("platform_urls", {}).get("naukri", "https://www.naukri.com")
        self.api_url = config.get("naukri_api_url", "https://www.naukri.com/jobapi/v2/search")
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
        }
        self.rate_limit = float(config.get("rate_limit_seconds", 2))
        self.max_pages = int(config.get("naukri_max_pages", 3))

    def search_jobs(self, titles: List[str], location: Optional[str] = None) -> List[Job]:
        self.logger.info(f"Fetching Naukri jobs using API integration (location: {location or 'any'})")
        titles = [title.strip() for title in titles if title]
        if not titles:
            self.logger.warning("No job titles configured for Naukri search")
            return []

        found_jobs = []
        seen_urls = set()
        queries = [title.lower() for title in titles]
        location_lower = location.lower() if location else None

        for title in titles:
            page = 1
            while page <= self.max_pages:
                params = {"keyword": title, "page": page, "src": "searchapi"}
                if location:
                    params["location"] = location
                response = self.session.get(
                    self.api_url,
                    headers=self.headers,
                    params=params,
                    timeout=20,
                )
                response.raise_for_status()
                data = response.json()

                items = data.get("list", [])
                total_pages = int(data.get("totalpages", 1) or 1)
                self.logger.debug(f"Naukri API returned {len(items)} jobs for title '{title}' page {page}/{total_pages}")

                if not items:
                    break

                for item in items:
                    job = self._parse_job_item(item)
                    if not job:
                        continue
                    if job.url in seen_urls:
                        continue
                    if not self._matches_title(job.title, queries, job.description or ""):
                        continue
                    if location_lower and not self._matches_location(job.location or "", location_lower):
                        continue
                    found_jobs.append(job)
                    seen_urls.add(job.url)

                if page >= total_pages:
                    break
                page += 1
                time.sleep(self.rate_limit)

        self.logger.info(f"Extracted {len(found_jobs)} Naukri jobs")
        return found_jobs

    def _parse_job_item(self, item: dict) -> Optional[Job]:
        title = self._normalize_string(item.get("post") or item.get("CONTDESIG") or item.get("jobTitle") or item.get("title") or "")
        company = self._normalize_string(item.get("companyName") or item.get("CONTCOM") or item.get("staticCompanyName") or "")
        location = self._normalize_string(self._extract_location(item))
        salary = self._normalize_string(item.get("SALARY") or self._format_salary(item))
        url = self._normalize_url(item)
        description = self._normalize_string(item.get("jobDesc") or item.get("jobSpec") or item.get("JOB_SPEC") or item.get("tupleDesc") or "")

        if not title or not url:
            return None

        return Job(
            job_id=f"naukri-{item.get('jobId', '')}",
            platform="Naukri",
            title=title,
            company=company,
            location=location,
            description=description,
            salary=salary,
            url=url,
            scrape_date=datetime.utcnow(),
            extra={"source": self.api_url, "job_id": item.get("jobId")},
        )

    def _extract_location(self, item: dict) -> str:
        if item.get("locality"):
            locality = item.get("locality")
            if isinstance(locality, list) and locality:
                first = locality[0]
                if isinstance(first, dict):
                    loc_name = first.get("city") or first.get("localities")
                    if loc_name:
                        if isinstance(loc_name, list):
                            return ", ".join(str(x) for x in loc_name if x)
                        return str(loc_name)
        if item.get("cityfield"):
            return item.get("cityfield")
        if item.get("CONTCITY"):
            return item.get("CONTCITY")
        return ""

    def _normalize_url(self, item: dict) -> str:
        url = item.get("urlStr") or item.get("nonStaticUrlFor") or item.get("RP_URL") or ""
        if url and not url.startswith("http"):
            url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        return self._normalize_string(url)

    def _format_salary(self, item: dict) -> str:
        min_sal = item.get("minSal")
        max_sal = item.get("maxSal")
        currency = item.get("currencySal") or ""
        if min_sal and max_sal and min_sal != "0" and max_sal != "0":
            return f"{currency} {min_sal} - {max_sal}".strip()
        if min_sal and min_sal != "0":
            return f"{currency} {min_sal}".strip()
        if max_sal and max_sal != "0":
            return f"{currency} {max_sal}".strip()
        return ""

    def _matches_title(self, title: str, queries: List[str], description: str) -> bool:
        if not queries:
            return True

        title_lower = title.lower()
        if any(query in title_lower for query in queries):
            return True
        if description and any(query in description.lower() for query in queries):
            return True
        return False

    def _matches_location(self, job_location: str, query_location: str) -> bool:
        """Check if job location matches the query location."""
        if not query_location or not job_location:
            return True

        normalized_query_location = self._normalize_string(query_location)
        job_loc_lower = job_location.lower()

        if normalized_query_location == "remote":
            return any(
                keyword in job_loc_lower
                for keyword in ["remote", "work from home", "wfh", "home"]
            )

        alias = self.LOCATION_ALIASES.get(normalized_query_location, normalized_query_location)
        candidates = {alias}
        candidates.update(
            key for key, value in self.LOCATION_ALIASES.items() if value == alias
        )

        return any(candidate in job_loc_lower for candidate in candidates)
