from abc import ABC, abstractmethod
from typing import List, Optional

from src.models import Job


class BaseJobScraper(ABC):
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger

    @abstractmethod
    def search_jobs(self, titles: List[str], location: Optional[str] = None) -> List[Job]:
        """Search for jobs using the provided titles and optional location, return a list of Job objects."""
        raise NotImplementedError

    def _normalize_string(self, value: str) -> str:
        return value.strip() if value else ""
