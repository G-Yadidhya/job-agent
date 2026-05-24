import re
from typing import Dict, Optional


class QueryParser:
    """Parse natural language queries to extract job title and location."""

    # Common location keywords
    LOCATION_KEYWORDS = {
        "remote": "remote",
        "work from home": "remote",
        "wfh": "remote",
        "bangalore": "bangalore",
        "bengaluru": "bangalore",
        "pune": "pune",
        "mumbai": "mumbai",
        "delhi": "delhi",
        "hyderabad": "hyderabad",
        "chennai": "chennai",
        "kolkata": "kolkata",
        "jaipur": "jaipur",
        "ahmedabad": "ahmedabad",
        "indore": "indore",
        "surat": "surat",
        "lucknow": "lucknow",
        "kanpur": "kanpur",
        "nagpur": "nagpur",
        "visakhapatnam": "visakhapatnam",
        "worldwide": "worldwide",
        "global": "worldwide",
        "any location": None,
        "all locations": None,
    }

    # Job titles that should be recognized
    COMMON_TITLES = {
        "software engineer",
        "data scientist",
        "product manager",
        "backend engineer",
        "frontend engineer",
        "full stack engineer",
        "devops engineer",
        "machine learning engineer",
        "senior engineer",
        "lead engineer",
        "architect",
        "data analyst",
        "business analyst",
        "qa engineer",
        "product designer",
        "ux designer",
        "ui designer",
        "growth hacker",
        "marketing manager",
        "sales executive",
        "account executive",
        "hr manager",
        "finance manager",
        "operations manager",
        "project manager",
    }

    @staticmethod
    def parse(query: str) -> Dict[str, Optional[str]]:
        """
        Parse a natural language query to extract job title and location.

        Args:
            query: User query string (e.g., "Find Product Manager roles in bangalore")

        Returns:
            Dictionary with 'title' and 'location' keys
        """
        if not query or not isinstance(query, str):
            return {"title": None, "location": None}

        query_lower = query.lower().strip()

        # Extract location
        location = QueryParser._extract_location(query_lower)

        # Remove location-related keywords from query to isolate title
        query_for_title = QueryParser._remove_location_keywords(query_lower)

        # Extract job title
        title = QueryParser._extract_title(query_for_title)

        return {"title": title, "location": location}

    @staticmethod
    def _extract_location(query_lower: str) -> Optional[str]:
        """Extract location from query."""
        for keyword, location in QueryParser.LOCATION_KEYWORDS.items():
            if keyword in query_lower:
                return location
        return None

    @staticmethod
    def _remove_location_keywords(query_lower: str) -> str:
        """Remove location keywords and common prepositions from query."""
        result = query_lower

        # Remove location keywords
        for keyword in QueryParser.LOCATION_KEYWORDS.keys():
            result = re.sub(rf"\b{re.escape(keyword)}\b", " ", result)

        # Remove common prepositions and words
        for word in [
            "find",
            "search",
            "looking for",
            "get",
            "show me",
            "roles",
            "jobs",
            "positions",
            "openings",
            "in",
            "at",
            "for",
            "and",
            "or",
        ]:
            result = re.sub(rf"\b{re.escape(word)}\b", " ", result)

        # Clean up whitespace
        result = re.sub(r"\s+", " ", result).strip()
        return result

    @staticmethod
    def _extract_title(query_for_title: str) -> Optional[str]:
        """Extract job title from cleaned query."""
        if not query_for_title:
            return None

        query_lower = query_for_title.lower()

        # Check for exact matches with common titles
        for title in QueryParser.COMMON_TITLES:
            if title in query_lower:
                return title.title()

        # If no exact match, return the entire cleaned query as title
        if query_for_title:
            return query_for_title.title()

        return None
