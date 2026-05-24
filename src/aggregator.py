from typing import Iterable, List

from src.models import Job


class JobAggregator:
    def __init__(self, logger=None):
        self.logger = logger

    def aggregate(self, job_collections: Iterable[List[Job]]) -> List[Job]:
        all_jobs: List[Job] = []
        for collection in job_collections:
            all_jobs.extend(collection or [])

        if self.logger:
            self.logger.info(f"Aggregating {len(all_jobs)} jobs across platforms")

        unique_jobs = []
        seen_keys = set()
        for job in all_jobs:
            key = self._job_key(job)
            if key in seen_keys:
                if self.logger:
                    self.logger.debug(f"Skipping duplicate job: {job.title} ({job.url})")
                continue

            seen_keys.add(key)
            self._normalize_job(job)
            unique_jobs.append(job)

        if self.logger:
            self.logger.info(f"Aggregated {len(unique_jobs)} unique jobs")

        return unique_jobs

    def _job_key(self, job: Job) -> str:
        if job.url:
            return job.url.strip().lower()

        title = job.title or ""
        company = job.company or ""
        location = job.location or ""
        return f"{title.strip().lower()}|{company.strip().lower()}|{location.strip().lower()}"

    def _normalize_job(self, job: Job) -> None:
        job.title = self._normalize_text(job.title)
        job.company = self._normalize_text(job.company)
        job.location = self._normalize_text(job.location)
        job.description = self._normalize_text(job.description)
        job.salary = self._normalize_text(job.salary)
        job.url = self._normalize_text(job.url)

    def _normalize_text(self, value: str) -> str:
        return value.strip() if isinstance(value, str) else ""
