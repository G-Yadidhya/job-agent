import urllib.parse
from typing import Optional


class NaukriURLBuilder:
    """Build properly formatted Naukri search URLs."""

    BASE_URL = "https://www.naukri.com"

    @staticmethod
    def build_search_url(job_title: Optional[str] = None, location: Optional[str] = None) -> str:
        """
        Build a Naukri search URL from job title and location.

        Examples:
            - "Product Manager" + "bangalore" -> https://www.naukri.com/product-manager-jobs-in-bangalore-city
            - "Software Engineer" + "remote" -> https://www.naukri.com/software-engineer-jobs
            - "Data Scientist" + None -> https://www.naukri.com/data-scientist-jobs

        Args:
            job_title: Job title (e.g., "Product Manager")
            location: Location (e.g., "bangalore", "remote")

        Returns:
            Complete Naukri search URL
        """
        if not job_title:
            return NaukriURLBuilder.BASE_URL

        # Normalize title to URL format
        title_slug = NaukriURLBuilder._slugify(job_title)

        # Handle location
        if location:
            location_lower = location.lower()
            if location_lower == "remote" or location_lower == "wfh" or location_lower == "work from home":
                # Remote jobs don't use location in URL, just add -remote to title
                return f"{NaukriURLBuilder.BASE_URL}/{title_slug}-jobs"
            else:
                # Add location suffix for specific cities
                location_slug = NaukriURLBuilder._slugify(location)
                # Naukri uses city names with -city suffix
                location_slug = f"{location_slug}-city"
                return f"{NaukriURLBuilder.BASE_URL}/{title_slug}-jobs-in-{location_slug}"
        else:
            # No location specified
            return f"{NaukriURLBuilder.BASE_URL}/{title_slug}-jobs"

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL-friendly slug."""
        if not text:
            return ""

        # Convert to lowercase
        slug = text.lower()

        # Replace spaces and special chars with hyphens
        slug = slug.replace(" ", "-")
        slug = slug.replace("/", "-")
        slug = slug.replace("&", "and")

        # Remove any remaining special characters
        slug = "".join(c if c.isalnum() or c == "-" else "" for c in slug)

        # Remove consecutive hyphens
        while "--" in slug:
            slug = slug.replace("--", "-")

        # Strip leading/trailing hyphens
        slug = slug.strip("-")

        return slug


class RemoteOKURLBuilder:
    """Build RemoteOK search URLs."""

    BASE_URL = "https://remoteok.io"

    @staticmethod
    def build_search_url(job_title: Optional[str] = None, location: Optional[str] = None) -> str:
        """
        Build a RemoteOK search URL.

        Args:
            job_title: Job title (used as search query)
            location: Location (not used as RemoteOK is for remote jobs)

        Returns:
            Complete RemoteOK search URL
        """
        if not job_title:
            return RemoteOKURLBuilder.BASE_URL

        # RemoteOK uses query parameter for search
        query = urllib.parse.quote(job_title)
        return f"{RemoteOKURLBuilder.BASE_URL}?q={query}"


class WellfoundURLBuilder:
    """Build Wellfound search URLs."""

    BASE_URL = "https://wellfound.com"

    @staticmethod
    def build_search_url(job_title: Optional[str] = None, location: Optional[str] = None) -> str:
        """
        Build a Wellfound search URL.

        Args:
            job_title: Job title (used as search query)
            location: Location (optional, used in search)

        Returns:
            Complete Wellfound search URL
        """
        if not job_title:
            return f"{WellfoundURLBuilder.BASE_URL}/jobs"

        query = urllib.parse.quote(job_title)
        search_url = f"{WellfoundURLBuilder.BASE_URL}/jobs?query={query}"

        if location:
            location_query = urllib.parse.quote(location)
            search_url += f"&location={location_query}"

        return search_url
