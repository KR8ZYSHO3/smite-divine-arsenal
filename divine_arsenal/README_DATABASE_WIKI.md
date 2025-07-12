# Smite 2 Wiki Scraper & Database Integration

This document explains how to use the new Smite 2 Wiki scraper with the enhanced database system.

## Overview

We now have a comprehensive system that includes:

1. **WikiSmite2Scraper** - Scrapes data from the official Smite 2 Wiki
2. **Enhanced Database** - Supports gods, items, and patch notes with full relational structure
3. **Integration Methods** - Easy import/export between wiki data and database

## Database Schema

### Gods Data
- **Main Table**: `gods` - Core god information (name, role, damage_type, pantheon, stats, etc.)
- **Abilities**: `god_abilities` - God abilities with descriptions and scaling
- **Relationships**: `god_relationships` - Counter relationships, strong/weak against
- **Playstyles**: `god_playstyles` - God playstyle tags

### Items Data
- **Main Table**: `items` - Core item information (name, cost, stats, passive/active effects)
- **Tags**: `item_tags` - Item category tags
- **Dynamic Stats**: `item_stats` - Additional stats that don't fit in main table

### Patch Notes
- **Main Table**: `patches` - Version, title, content, date, URL, source

## Usage Examples

### Basic Wiki Scraping

```python
from backend.scrapers.wiki_smite2 import WikiSmite2Scraper

# Initialize scraper
scraper = WikiSmite2Scraper()

# Scrape all gods
gods_data = scraper.get_all_gods()
print(f"Found {len(gods_data)} gods")

# Scrape all items
items_data = scraper.get_all_items()
print(f"Found {len(items_data)} items")

# Scrape patch notes
patches_data = scraper.get_patch_notes()
print(f"Found {len(patches_data)} patches")

# Search wiki
search_results = scraper.search_wiki("Zeus", limit=5)
for result in search_results:
    print(f"- {result['title']}: {result['snippet']}")
```

### Database Operations

```python
from backend.database import Database

# Initialize database
db = Database("divine_arsenal.db")

# Add a god manually
god_data = {
    'name': 'Zeus',
    'role': 'Mage',
    'damage_type': 'Magical',
    'pantheon': 'Greek',
    'health': 400,
    'mana': 280,
    'abilities': [
        {'name': 'Chain Lightning', 'description': 'Throws lightning', 'type': 'Damage'}
    ],
    'playstyle': ['Burst', 'Area Control']
}
god_id = db.add_god(god_data)

# Retrieve god
zeus = db.get_god('Zeus')
print(f"Zeus role: {zeus['role']}")
print(f"Zeus abilities: {len(zeus['abilities'])}")

# Get all gods
all_gods = db.get_all_gods()
print(f"Database contains {len(all_gods)} gods")
```

### Complete Integration Workflow

```python
from backend.database import Database
from backend.scrapers.wiki_smite2 import WikiSmite2Scraper

def sync_wiki_to_database():
    """Complete workflow to sync wiki data to database."""
    
    # Initialize components
    db = Database("divine_arsenal_wiki.db")
    scraper = WikiSmite2Scraper()
    
    print("🔄 Starting wiki synchronization...")
    
    # Scrape all data
    print("📊 Scraping gods...")
    gods_data = scraper.get_all_gods()
    
    print("⚔️ Scraping items...")
    items_data = scraper.get_all_items()
    
    print("📝 Scraping patch notes...")
    patches_data = scraper.get_patch_notes()
    
    # Import to database
    print("💾 Importing to database...")
    db.import_wiki_data(gods_data, items_data, patches_data)
    
    print(f"✅ Successfully imported:")
    print(f"   - {len(gods_data)} gods")
    print(f"   - {len(items_data)} items") 
    print(f"   - {len(patches_data)} patches")
    
    return db

# Run the sync
database = sync_wiki_to_database()
```

## Wiki Scraper Features

### God Data Extraction
- Name, role, damage type, pantheon
- Base stats (health, mana, attack speed, etc.)
- Abilities with descriptions
- Lore and background information
- Extracts from MediaWiki infoboxes

### Item Data Extraction  
- Name, type, tier, cost
- All item stats (power, protection, etc.)
- Passive and active effects
- Category and description information

### Patch Notes Extraction
- Version numbers and titles
- Release dates and content
- Direct links to wiki pages
- Automatic version sorting

### Search Capabilities
- Full-text search across wiki
- Results with snippets and URLs
- Configurable result limits

## Database Features

### Advanced Queries

```python
# Get gods by role
mages = [god for god in db.get_all_gods() if god['role'] == 'Mage']

# Get items by category
physical_items = [item for item in db.get_all_items() 
                  if item.get('category') == 'Physical']

# Get recent patches
recent_patches = db.get_patches(limit=10)
```

### Relationship Tracking

```python
# Gods store counter relationships
zeus = db.get_god('Zeus')
counters = zeus.get('counter_gods', [])  # Gods that counter Zeus
strong_against = zeus.get('strong_against', [])  # Gods Zeus counters
```

### Stats History

```python
# Track god stat changes over time
db.add_god_stats('Zeus', {
    'health': 400,
    'mana': 280,
    'magical_power': 45
})

# Get historical data
history = db.get_god_stats_history('Zeus', 'health', days=30)
```

## Data Schema Compatibility

The system is designed to work with multiple data sources:

1. **Wiki Data** - Comprehensive, official information
2. **JSON Files** - Your existing data files in `/data/`
3. **Manual Entry** - Direct database operations
4. **Other Scrapers** - Tracker.gg, SmiteBase, etc.

All sources use compatible data schemas for seamless integration.

## Performance Considerations

- **Indexes** - Database includes indexes on commonly queried fields
- **Batch Operations** - `import_wiki_data()` handles bulk imports efficiently
- **Caching** - Wiki responses can be cached to reduce API calls
- **Rate Limiting** - Scraper includes appropriate delays

## Error Handling

Both the scraper and database include comprehensive error handling:

- Network timeouts and retries
- Invalid wiki page handling
- Database constraint violations
- Logging for debugging

## Future Enhancements

Planned improvements include:

1. **Incremental Updates** - Only scrape changed pages
2. **Image Downloads** - Cache god/item images locally
3. **Build Integration** - Connect with build optimizer
4. **Real-time Sync** - Automatic periodic updates
5. **Data Validation** - Cross-reference multiple sources

## Getting Started

1. Install dependencies: `pip install requests beautifulsoup4`
2. Initialize database: `db = Database("your_database.db")`
3. Run scraper: `scraper = WikiSmite2Scraper()`
4. Import data: `db.import_wiki_data(gods, items, patches)`

The system is now ready for production use with comprehensive god and item data from the official Smite 2 Wiki! 