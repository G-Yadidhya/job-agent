try:
    from src.config import load_config
    from src.logger import get_logger
    from src.csv_exporter import CSVExporter
    from src.naukri_scraper import NaukriScraper
    from src.remoteok_scraper import RemoteOKScraper
    from src.wellfound_scraper import WellfoundScraper
    from src.query_parser import QueryParser
    from src.aggregator import JobAggregator
    from src.url_builder import NaukriURLBuilder, RemoteOKURLBuilder, WellfoundURLBuilder
except ImportError:
    from config import load_config
    from logger import get_logger
    from csv_exporter import CSVExporter
    from naukri_scraper import NaukriScraper
    from remoteok_scraper import RemoteOKScraper
    from wellfound_scraper import WellfoundScraper
    from query_parser import QueryParser
    from aggregator import JobAggregator
    from url_builder import NaukriURLBuilder, RemoteOKURLBuilder, WellfoundURLBuilder

import argparse
import webbrowser


def main(
    user_query: str = None,
    open_browser: bool = True,
    platforms: list = None,
    config: dict = None,
    log_to_console: bool = None,
    timestamped_output: bool = None,
) -> None:
    """
    Main job agent orchestrator.
    
    Args:
        user_query: Natural language query (e.g., "Find Product Manager roles in bangalore")
        open_browser: Whether to open search URLs in browser
        platforms: List of platforms to scrape (["naukri", "remoteok", "wellfound"]). If None, uses config.
        config: Optional loaded config dictionary.
        log_to_console: Whether to output logs to the terminal.
    """
    config = config or load_config()
    if log_to_console is None:
        log_to_console = config.get("log_to_console", True)
    if timestamped_output is None:
        timestamped_output = config.get("timestamped_output", False)
    logger = get_logger("job_agent", config.get("log_level", "INFO"), console=log_to_console)

    logger.info("Job Agent initialized")
    logger.info(f"Loaded config for platforms: {config.get('platforms')}")

    # Parse user query or use configured titles
    if user_query:
        logger.info(f"Parsing user query: {user_query}")
        parsed = QueryParser.parse(user_query)
        job_titles = [parsed["title"]] if parsed["title"] else []
        location = parsed["location"]
        logger.info(f"Extracted title: {parsed['title']}, location: {parsed['location']}")

        # Open browser windows with search URLs if requested
        if open_browser:
            _open_search_urls(job_titles[0] if job_titles else None, location, logger)
    else:
        job_titles = config.get("job_titles", [])
        location = None
        logger.info(f"Using configured job titles: {job_titles}")
        if open_browser and job_titles:
            _open_search_urls(job_titles[0], location, logger)

    # Determine which platforms to scrape
    platforms_to_scrape = platforms or config.get("platforms", [])

    platform_results = {}
    for platform in platforms_to_scrape:
        platform_key = platform.lower()
        try:
            if platform_key == "remoteok":
                jobs = scrape_remoteok(job_titles, location, config, logger)
                platform_results[platform_key] = jobs
            elif platform_key == "naukri":
                jobs = scrape_naukri(job_titles, location, config, logger)
                platform_results[platform_key] = jobs
            elif platform_key == "wellfound":
                jobs = scrape_wellfound(job_titles, location, config, logger)
                platform_results[platform_key] = jobs
        except Exception as exc:
            logger.error(f"Failed to scrape {platform}: {exc}")
            platform_results[platform_key] = []

    aggregator = JobAggregator(logger)
    all_jobs = aggregator.aggregate(platform_results.values())

    exporter = CSVExporter(
        config.get("output_path"),
        timestamp_output=timestamped_output,
    )
    csv_path = exporter.export(all_jobs)

    logger.info(f"Exported {len(all_jobs)} jobs to {csv_path}")


def scrape_naukri(titles: list, location: str = None, config: dict = None, logger = None):
    """Scrape jobs from Naukri."""
    if not logger:
        logger = get_logger("naukri_scraper")
    if not config:
        config = load_config()
    
    scraper = NaukriScraper(config, logger)
    return scraper.search_jobs(titles, location=location)


def scrape_remoteok(titles: list, location: str = None, config: dict = None, logger = None):
    """Scrape jobs from RemoteOK."""
    if not logger:
        logger = get_logger("remoteok_scraper")
    if not config:
        config = load_config()
    
    scraper = RemoteOKScraper(config, logger)
    return scraper.search_jobs(titles, location=location)


def scrape_wellfound(titles: list, location: str = None, config: dict = None, logger = None):
    """Scrape jobs from Wellfound."""
    if not logger:
        logger = get_logger("wellfound_scraper")
    if not config:
        config = load_config()
    
    scraper = WellfoundScraper(config, logger)
    return scraper.search_jobs(titles, location=location)



def _open_search_urls(job_title: str, location: str, logger) -> None:
    """Open browser windows with job search URLs for all platforms."""
    if not job_title:
        logger.warning("No job title to open browser URLs")
        return

    urls = {
        "Naukri": NaukriURLBuilder.build_search_url(job_title, location),
        "RemoteOK": RemoteOKURLBuilder.build_search_url(job_title, location),
        "Wellfound": WellfoundURLBuilder.build_search_url(job_title, location),
    }

    logger.info("Opening browser windows with search URLs:")
    for platform, url in urls.items():
        logger.info(f"  {platform}: {url}")
        try:
            webbrowser.open(url, new=1)
        except Exception as e:
            logger.error(f"Failed to open {platform} URL: {e}")




def _parse_cli_args():
    parser = argparse.ArgumentParser(description="Job agent for multi-platform scraping and CSV export")
    parser.add_argument("-q", "--query", help="Natural language job search query")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser windows")
    parser.add_argument("--platforms", help="Comma-separated list of platforms to scrape (naukri,remoteok,wellfound)")
    parser.add_argument("--output-path", help="Override the CSV output path")
    parser.add_argument("--timestamped-output", action="store_true", help="Append timestamp to CSV filename output")
    parser.add_argument("--quiet", action="store_true", help="Disable console logging")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_cli_args()
    config = load_config()
    if args.output_path:
        config["output_path"] = args.output_path
    selected_platforms = (
        [platform.strip() for platform in args.platforms.split(",") if platform.strip()]
        if args.platforms
        else None
    )
    main(
        user_query=args.query,
        open_browser=not args.no_browser,
        platforms=selected_platforms,
        config=config,
        log_to_console=not args.quiet,
        timestamped_output=args.timestamped_output,
    )
