# Job Agent — Project Context and Overview

## Overview

This repository is a multi-platform job scraping agent designed to aggregate job listings from Naukri, RemoteOK, and Wellfound into a single structured dataset. It includes natural language query parsing, URL-driven browser integration, platform-specific scraping, aggregation, deduplication, and CSV export.

## Problem Statement

Searching for jobs across multiple job portals is time-consuming and inefficient. Users face:
- Fragmented information across sites
- Duplicate effort for the same job title
- Missed opportunities due to scattered listings
- No centralized way to track or analyze job results

## Solution

This Job Agent automates job discovery by:
- parsing natural language queries for title and location
- opening platform-specific search URLs in a browser
- scraping jobs from multiple sources
- aggregating results into a unified dataset
- deduplicating overlapping listings
- exporting clean CSV files for analysis

## Why this is best

- **Unified workflow**: one query gathers data from three platforms.
- **Flexible search**: supports query phrases like "Product Manager in bangalore" and remote searches.
- **Resilient output**: data is normalized, deduplicated, and exported in CSV format.
- **Minimal disruption**: documentation changes only, no runtime or output behavior changes.
- **Extensible design**: scraper classes and config-driven URLs make future platforms easy to add.

## Objectives

- Scrape jobs from Naukri, RemoteOK, and Wellfound
- Support natural language queries for title and location
- Filter and normalize results across platforms
- Deduplicate duplicate postings
- Export a consistent CSV dataset
- Preserve project workflow and output format

## Features

- Multi-platform scraping (Naukri, RemoteOK, Wellfound)
- Natural language query parsing
- Browser integration for search URLs
- Aggregation and deduplication of results
- CSV export with optional timestamping
- Environment-based API key support for Wellfound/FireCrawl
- Config-driven platform URLs and settings

## Requirements

- Python 3.10+ recommended
- Install dependencies with `python -m pip install -r requirements.txt`
- Optional: `.env` file with `FIRECRAWL_API_KEY` for Wellfound scraping

## Architecture

The project is organized in phases and modules.

### Phase 1: Foundation
- `src/base_scraper.py` - base scraper contract
- `src/config.py` - loads JSON config and `.env` values
- `src/logger.py` - logger factory
- `src/models.py` - `Job` data model
- `src/csv_exporter.py` - CSV export utility

### Phase 2: RemoteOK Integration
- `src/remoteok_scraper.py` - integrates with RemoteOK API
- filters by query terms and tags
- exports standard job model fields

### Phase 3: Naukri Integration
- `src/naukri_scraper.py` - Naukri API search
- location alias normalization
- job parsing and filtering logic

### Phase 4: Wellfound Integration
- `src/wellfound_scraper.py` - FireCrawl-based Wellfound search
- API key authentication and request payload handling
- result extraction and filtering

### Phase 5: Aggregation & Deduplication
- `src/aggregator.py` - combines results and removes duplicates
- normalizes text fields for clean output

### Phase 6: CSV Output Management
- `src/csv_exporter.py` - writes job results to CSV
- supports timestamped filenames if enabled

### Phase 7: CLI & Orchestrator
- `src/main.py` - main entrypoint and orchestrator
- parses queries, runs scrapers, aggregates results, and exports CSV

## Usage

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Run with a natural language query

```bash
python -c "from src.main import main; main(user_query='Find Product Manager roles in bangalore')"
```

### Run without browser opening

```bash
python -c "from src.main import main; main(user_query='Product Manager in bangalore', open_browser=False)"
```

### Run default configured titles

```bash
python -m src.main
```

## Project Files

- `context.md` — full project context, architecture, problem statement, and solution
- `README.md` — lightweight pointer to `context.md`
- `config/config.json` — platform URLs and endpoints
- `src/` — scraper and orchestration code
- `tests/` — unit tests and regression coverage
- `requirements.txt` — Python dependencies

## Notes

- `context.md` is now the main documentation file for this repository.
- `README.md` exists to keep the repository accessible, but `context.md` contains the full project overview and architecture.
- No code behavior, CSV output, or scraping workflow has changed.
