from src.config import load_config
from src.main import main

import argparse


def _parse_cli_args():
    parser = argparse.ArgumentParser(description="Job agent for multi-platform scraping and CSV export")
    parser.add_argument("-q", "--query", help="Natural language job search query")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser windows")
    parser.add_argument("--platforms", help="Comma-separated list of platforms to scrape (naukri,remoteok,wellfound)")
    parser.add_argument("--output-path", help="Override the CSV output path")
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
    )
