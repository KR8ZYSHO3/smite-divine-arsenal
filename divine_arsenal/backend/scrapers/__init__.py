"""
Enhanced Scrapers Module with Playwright Integration
Lazy loading prevents WebDriver processes from spawning on import
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Global scraper instances (lazy loaded)
_tracker_scraper = None
_smite2_scraper = None
_smitebase_scraper = None
_smitesource_scraper = None
_wiki_scraper = None


def get_tracker_scraper(use_playwright: bool = True, headless: bool = True):
    """Get TrackerScraper instance with lazy loading."""
    global _tracker_scraper
    
    if _tracker_scraper is None:
        try:
            # Try to use new Playwright-based scraper first
            from .tracker_playwright import TrackerPlaywrightScraper
            _tracker_scraper = TrackerPlaywrightScraper(
                use_playwright=use_playwright, 
                headless=headless
            )
            logger.info("✅ TrackerPlaywrightScraper loaded successfully")
        except ImportError as e:
            logger.warning(f"Playwright scraper not available: {e}")
            try:
                # Fallback to original scraper but with Selenium disabled
                from .tracker import TrackerScraper
                _tracker_scraper = TrackerScraper(use_selenium=False)
                logger.info("✅ TrackerScraper loaded (Selenium disabled)")
            except Exception as e2:
                logger.error(f"Could not load any tracker scraper: {e2}")
                _tracker_scraper = None
    
    return _tracker_scraper


def get_smite2_scraper():
    """Get Smite2Scraper instance with lazy loading."""
    global _smite2_scraper
    
    if _smite2_scraper is None:
        try:
            from .smite2 import Smite2Scraper
            _smite2_scraper = Smite2Scraper()
            logger.info("✅ Smite2Scraper loaded successfully")
        except Exception as e:
            logger.error(f"Could not load Smite2Scraper: {e}")
            _smite2_scraper = None
    
    return _smite2_scraper


def get_smitebase_scraper():
    """Get SmiteBaseScraper instance with lazy loading."""
    global _smitebase_scraper
    
    if _smitebase_scraper is None:
        try:
            from .smitebase import SmiteBaseScraper
            _smitebase_scraper = SmiteBaseScraper()
            logger.info("✅ SmiteBaseScraper loaded successfully")
        except Exception as e:
            logger.error(f"Could not load SmiteBaseScraper: {e}")
            _smitebase_scraper = None
    
    return _smitebase_scraper


def get_smitesource_scraper():
    """Get SmiteSourceScraper instance with lazy loading."""
    global _smitesource_scraper
    
    if _smitesource_scraper is None:
        try:
            from .smitesource import SmiteSourceScraper
            _smitesource_scraper = SmiteSourceScraper()
            logger.info("✅ SmiteSourceScraper loaded successfully")
        except Exception as e:
            logger.error(f"Could not load SmiteSourceScraper: {e}")
            _smitesource_scraper = None
    
    return _smitesource_scraper


def get_wiki_scraper():
    """Get WikiSmite2Scraper instance with lazy loading."""
    global _wiki_scraper
    
    if _wiki_scraper is None:
        try:
            from .wiki_smite2 import WikiSmite2Scraper
            _wiki_scraper = WikiSmite2Scraper()
            logger.info("✅ WikiSmite2Scraper loaded successfully")
        except Exception as e:
            logger.error(f"Could not load WikiSmite2Scraper: {e}")
            _wiki_scraper = None
    
    return _wiki_scraper


def get_all_scrapers() -> Dict[str, Any]:
    """Get all available scrapers."""
    return {
        "tracker": get_tracker_scraper(),
        "smite2": get_smite2_scraper(),
        "smitebase": get_smitebase_scraper(),
        "smitesource": get_smitesource_scraper(),
        "wiki": get_wiki_scraper(),
    }


def health_check_all_scrapers() -> Dict[str, Any]:
    """Perform health check on all scrapers."""
    health_results = {}
    
    # Check tracker scraper
    tracker = get_tracker_scraper()
    if tracker and hasattr(tracker, 'get_health_check'):
        try:
            health_results["tracker"] = tracker.get_health_check()
        except Exception as e:
            health_results["tracker"] = {"status": "error", "error": str(e)}
    else:
        health_results["tracker"] = {"status": "unavailable"}
    
    # Check other scrapers (basic connectivity)
    for name, scraper in get_all_scrapers().items():
        if name != "tracker":  # Already checked above
            if scraper:
                health_results[name] = {"status": "available"}
            else:
                health_results[name] = {"status": "unavailable"}
    
    return health_results


def close_all_scrapers():
    """Close all scrapers and clean up resources."""
    global _tracker_scraper, _smite2_scraper, _smitebase_scraper, _smitesource_scraper, _wiki_scraper
    
    scrapers = [
        ("tracker", _tracker_scraper),
        ("smite2", _smite2_scraper),
        ("smitebase", _smitebase_scraper),
        ("smitesource", _smitesource_scraper),
        ("wiki", _wiki_scraper),
    ]
    
    for name, scraper in scrapers:
        if scraper and hasattr(scraper, 'close'):
            try:
                scraper.close()
                logger.info(f"✅ {name} scraper closed successfully")
            except Exception as e:
                logger.warning(f"Error closing {name} scraper: {e}")
    
    # Reset global instances
    _tracker_scraper = None
    _smite2_scraper = None
    _smitebase_scraper = None
    _smitesource_scraper = None
    _wiki_scraper = None
    
    logger.info("All scrapers closed and cleaned up")


# For backward compatibility, provide the old imports but with lazy loading
class LazyTrackerScraper:
    """Lazy wrapper for TrackerScraper."""
    def __getattr__(self, name):
        scraper = get_tracker_scraper()
        if scraper:
            return getattr(scraper, name)
        raise AttributeError(f"TrackerScraper not available or missing attribute: {name}")


class LazySmite2Scraper:
    """Lazy wrapper for Smite2Scraper."""
    def __getattr__(self, name):
        scraper = get_smite2_scraper()
        if scraper:
            return getattr(scraper, name)
        raise AttributeError(f"Smite2Scraper not available or missing attribute: {name}")


class LazySmiteBaseScraper:
    """Lazy wrapper for SmiteBaseScraper."""
    def __getattr__(self, name):
        scraper = get_smitebase_scraper()
        if scraper:
            return getattr(scraper, name)
        raise AttributeError(f"SmiteBaseScraper not available or missing attribute: {name}")


class LazySmiteSourceScraper:
    """Lazy wrapper for SmiteSourceScraper."""
    def __getattr__(self, name):
        scraper = get_smitesource_scraper()
        if scraper:
            return getattr(scraper, name)
        raise AttributeError(f"SmiteSourceScraper not available or missing attribute: {name}")


class LazyWikiSmite2Scraper:
    """Lazy wrapper for WikiSmite2Scraper."""
    def __getattr__(self, name):
        scraper = get_wiki_scraper()
        if scraper:
            return getattr(scraper, name)
        raise AttributeError(f"WikiSmite2Scraper not available or missing attribute: {name}")


# Backward compatibility instances
TrackerScraper = LazyTrackerScraper()
Smite2Scraper = LazySmite2Scraper()
SmiteBaseScraper = LazySmiteBaseScraper()
SmiteSourceScraper = LazySmiteSourceScraper()
WikiSmite2Scraper = LazyWikiSmite2Scraper()


# Export all the lazy loading functions and classes
__all__ = [
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
