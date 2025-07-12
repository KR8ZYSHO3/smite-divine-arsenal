
from pathlib import Path

# Base directory for the backend
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
BACKEND_DIR = BASE_DIR / 'backend'

# Data files
GODS_WITH_SCALING = DATA_DIR / 'gods_with_scaling.json'
ITEMS_OFFICIAL_DIRECT = DATA_DIR / 'smite2_items_official_direct.json'
ITEMS_OFFICIAL = DATA_DIR / 'smite2_items_official.json'
ITEMS_JSON = DATA_DIR / 'items.json'
GODS_JSON = DATA_DIR / 'gods.json'
UPDATE_LOG = DATA_DIR / 'update_log.json'
DATABASE_VERSION = DATA_DIR / 'database_version.json'

# Database files
DIVINE_ARSENAL_DB = BACKEND_DIR / 'divine_arsenal.db'
PLAYER_PERFORMANCE_DB = BACKEND_DIR / 'player_performance.db'
ENHANCED_DATA_CACHE_DB = BACKEND_DIR / 'enhanced_data_cache.db'
SMITE_STATS_DB = BACKEND_DIR / 'smite_stats.db'
STATISTICAL_ANALYSIS_DB = BACKEND_DIR / 'statistical_analysis.db'

# Log files
SCALING_DEBUG_LOG = BACKEND_DIR / 'scaling_debug.log'
DIVINE_ARSENAL_LOG = BACKEND_DIR / 'divine_arsenal.log'

# Add more as needed
