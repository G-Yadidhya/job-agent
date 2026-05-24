import json
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.json"


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    config["firecrawl_api_key"] = os.getenv("FIRECRAWL_API_KEY")
    config["remoteok_api_key"] = os.getenv("REMOTEOK_API_KEY")
    config["job_titles"] = os.getenv("JOB_TITLES", ",".join(config.get("search_titles", []))).split(",")
    config["output_path"] = os.getenv("OUTPUT_PATH", config.get("output_path"))
    config["log_level"] = os.getenv("LOG_LEVEL", "INFO")
    config["log_to_console"] = os.getenv("LOG_TO_CONSOLE", "true").lower() in ("1", "true", "yes")

    return config
