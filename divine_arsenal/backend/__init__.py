# Backend package for SMITE 2 Divine Arsenal

from .database_config import get_database_config
from .app_with_migrations import app, db, migrate

from .database import Database  # Legacy database

from .scrapers import (
    get_tracker_scraper,
    get_smite2_scraper,
    get_smitebase_scraper,
    get_smitesource_scraper,
    get_wiki_scraper,
    get_all_scrapers,
    health_check_all_scrapers,
    close_all_scrapers,
    TrackerScraper,
    Smite2Scraper,
    SmiteBaseScraper,
    SmiteSourceScraper,
    WikiSmite2Scraper,
)

__all__ = [
    'get_database_config',
    'app',
    'db',
    'migrate',
    'Database',
    'get_tracker_scraper',
    'get_smite2_scraper',
    'get_smitebase_scraper',
    'get_smitesource_scraper',
    'get_wiki_scraper',
    'get_all_scrapers',
    'health_check_all_scrapers',
    'close_all_scrapers',
    'TrackerScraper',
    'Smite2Scraper',
    'SmiteBaseScraper',
    'SmiteSourceScraper',
    'WikiSmite2Scraper',
]

# Log package initialization
print("✅ Backend package initialized")
