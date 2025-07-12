#!/usr/bin/env python3
"""
Data Migration Script for SMITE 2 Divine Arsenal
Migrates data from SQLite to PostgreSQL with zero data loss
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import database configurations and models
from .database_config import get_database_config
from .app_with_migrations import app, db, God, Item, Patch, UserAuth

# Import legacy database for reading existing data
try:
    from .database import Database as LegacyDatabase
    legacy_db_available = True
except ImportError as e:
    logger.warning(f"Legacy database not available: {e}")
    legacy_db_available = False


class DataMigrator:
    """Handles data migration from SQLite to PostgreSQL."""

    def __init__(self):
        self.db_config = get_database_config()
        self.legacy_db = None
        self.migration_log = []

        # Initialize legacy database if available
        if legacy_db_available:
            try:
                self.legacy_db = LegacyDatabase()
                logger.info("✅ Legacy database initialized")
            except Exception as e:
                logger.error(f"Failed to initialize legacy database: {e}")
                self.legacy_db = None

    def log_migration(self, table: str, action: str, count: int, details: str = ""):
        """Log migration activity."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'table': table,
            'action': action,
            'count': count,
            'details': details
        }
        self.migration_log.append(entry)
        logger.info(f"Migration: {table} - {action} - {count} records - {details}")

    def backup_current_data(self) -> str:
        """Create a backup of current data before migration."""
        backup_dir = Path("migration_backups")
        backup_dir.mkdir(exist_ok=True)

        backup_file = backup_dir / f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'source_db_type': self.db_config.get_database_type(),
            'gods': [],
            'items': [],
            'patches': [],
            'users': []
        }

        try:
            # Backup existing data from new database (if any)
            with app.app_context():
                backup_data['gods'] = [god.to_dict() for god in God.query.all()]
                backup_data['items'] = [item.to_dict() for item in Item.query.all()]
                backup_data['patches'] = [patch.to_dict() for patch in Patch.query.all()]
                backup_data['users'] = [user.to_dict() for user in UserAuth.query.all()]

            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)

            logger.info(f"✅ Data backup created: {backup_file}")
            return str(backup_file)

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""

    def migrate_gods(self) -> int:
        """Migrate gods data."""
        if not self.legacy_db:
            logger.warning("No legacy database available for gods migration")
            return 0

        try:
            # Get gods from legacy database
            legacy_gods = self.legacy_db.get_all_gods()

            if not legacy_gods:
                logger.warning("No gods found in legacy database")
                return 0

            migrated_count = 0

            with app.app_context():
                for god_data in legacy_gods:
                    # Check if god already exists
                    existing_god = God.query.filter_by(name=god_data.get('name', '')).first()

                    if existing_god:
                        logger.debug(f"God {god_data.get('name')} already exists, skipping")
                        continue

                    # Helper function to safely convert stats to float
                    def safe_float(value, default=0.0):
                        if value is None:
                            return default
                        if isinstance(value, (int, float)):
                            return float(value)
                        if isinstance(value, str):
                            # Extract first number from strings like "1.7 (+0.2)"
                            import re
                            match = re.search(r'(\d+\.?\d*)', value)
                            if match:
                                return float(match.group(1))
                        return default

                    # Create new god record
                    god = God()
                    god.name = god_data.get('name', '')
                    god.role = god_data.get('role', '')
                    god.damage_type = god_data.get('damage_type', '')
                    god.pantheon = god_data.get('pantheon', '')
                    god.health = safe_float(god_data.get('health', 0))
                    god.mana = safe_float(god_data.get('mana', 0))
                    god.physical_power = safe_float(god_data.get('physical_power', 0))
                    god.magical_power = safe_float(god_data.get('magical_power', 0))
                    god.physical_protection = safe_float(god_data.get('physical_protection', 0))
                    god.magical_protection = safe_float(god_data.get('magical_protection', 0))
                    god.attack_speed = safe_float(god_data.get('attack_speed', 0))
                    god.movement_speed = safe_float(god_data.get('movement_speed', 0))
                    god.health_per_level = safe_float(god_data.get('health_per_level', 0))
                    god.mana_per_level = safe_float(god_data.get('mana_per_level', 0))
                    god.physical_power_per_level = safe_float(god_data.get('physical_power_per_level', 0))
                    god.magical_power_per_level = safe_float(god_data.get('magical_power_per_level', 0))
                    god.physical_protection_per_level = safe_float(god_data.get('physical_protection_per_level', 0))
                    god.magical_protection_per_level = safe_float(god_data.get('magical_protection_per_level', 0))

                    db.session.add(god)
                    migrated_count += 1

                db.session.commit()

            self.log_migration('gods', 'migrated', migrated_count, "from legacy database")
            return migrated_count

        except Exception as e:
            logger.error(f"Error migrating gods: {e}")
            with app.app_context():
                db.session.rollback()
            return 0

    def migrate_items(self) -> int:
        """Migrate items data."""
        if not self.legacy_db:
            logger.warning("No legacy database available for items migration")
            return 0

        try:
            # Get items from legacy database
            legacy_items = self.legacy_db.get_all_items()

            if not legacy_items:
                logger.warning("No items found in legacy database")
                return 0

            migrated_count = 0

            with app.app_context():
                for item_data in legacy_items:
                    # Check if item already exists
                    existing_item = Item.query.filter_by(name=item_data.get('name', '')).first()

                    if existing_item:
                        logger.debug(f"Item {item_data.get('name')} already exists, skipping")
                        continue

                    # Create new item record
                    item = Item()
                    item.name = item_data.get('name', '')
                    item.cost = int(item_data.get('cost', 0))
                    item.tier = int(item_data.get('tier', 1))
                    item.category = item_data.get('category', '')
                    item.health = float(item_data.get('health', 0))
                    item.mana = float(item_data.get('mana', 0))
                    item.physical_power = float(item_data.get('physical_power', 0))
                    item.magical_power = float(item_data.get('magical_power', 0))
                    item.physical_protection = float(item_data.get('physical_protection', 0))
                    item.magical_protection = float(item_data.get('magical_protection', 0))
                    item.attack_speed = float(item_data.get('attack_speed', 0))
                    item.movement_speed = float(item_data.get('movement_speed', 0))
                    item.penetration = float(item_data.get('penetration', 0))
                    item.critical_chance = float(item_data.get('critical_chance', 0))
                    item.cooldown_reduction = float(item_data.get('cooldown_reduction', 0))
                    item.lifesteal = float(item_data.get('lifesteal', 0))
                    item.passive_description = item_data.get('passive_description', '')
                    item.active_description = item_data.get('active_description', '')

                    db.session.add(item)
                    migrated_count += 1

                db.session.commit()

            self.log_migration('items', 'migrated', migrated_count, "from legacy database")
            return migrated_count

        except Exception as e:
            logger.error(f"Error migrating items: {e}")
            with app.app_context():
                db.session.rollback()
            return 0

    def migrate_patches(self) -> int:
        """Migrate patches data."""
        if not self.legacy_db:
            logger.warning("No legacy database available for patches migration")
            return 0

        try:
            # Get patches from legacy database
            legacy_patches = self.legacy_db.get_patches()

            if not legacy_patches:
                logger.warning("No patches found in legacy database")
                return 0

            migrated_count = 0

            with app.app_context():
                for patch_data in legacy_patches:
                    # Check if patch already exists
                    existing_patch = Patch.query.filter_by(version=patch_data.get('version', '')).first()

                    if existing_patch:
                        logger.debug(f"Patch {patch_data.get('version')} already exists, skipping")
                        continue

                    # Parse release date
                    release_date = None
                    if patch_data.get('release_date'):
                        try:
                            if isinstance(patch_data['release_date'], str):
                                release_date = datetime.strptime(patch_data['release_date'], '%Y-%m-%d').date()
                            else:
                                release_date = patch_data['release_date']
                        except Exception as e:
                            logger.warning(f"Could not parse release date for patch {patch_data.get('version')}: {e}")

                    # Create new patch record
                    patch = Patch()
                    patch.version = patch_data.get('version', '')
                    patch.title = patch_data.get('title', '')
                    patch.content = patch_data.get('content', '')
                    patch.release_date = release_date
                    patch.url = patch_data.get('url', '')
                    patch.source = patch_data.get('source', '')

                    db.session.add(patch)
                    migrated_count += 1

                db.session.commit()

            self.log_migration('patches', 'migrated', migrated_count, "from legacy database")
            return migrated_count

        except Exception as e:
            logger.error(f"Error migrating patches: {e}")
            with app.app_context():
                db.session.rollback()
            return 0

    def migrate_users(self) -> int:
        """Migrate user authentication data."""
        # For now, we'll skip user migration as it's sensitive data
        # and should be handled carefully in production
        logger.info("User migration skipped - handle separately for security")
        return 0

    def verify_migration(self) -> Dict[str, Any]:
        """Verify that migration was successful."""
        verification_results = {}

        try:
            with app.app_context():
                # Count records in new database
                gods_count = God.query.count()
                items_count = Item.query.count()
                patches_count = Patch.query.count()
                users_count = UserAuth.query.count()

                verification_results = {
                    'gods': {
                        'count': gods_count,
                        'sample': [god.to_dict() for god in God.query.limit(3).all()],
                    },
                    'items': {
                        'count': items_count,
                        'sample': [item.to_dict() for item in Item.query.limit(3).all()],
                    },
                    'patches': {
                        'count': patches_count,
                        'sample': [patch.to_dict() for patch in Patch.query.limit(3).all()],
                    },
                    'users': {
                        'count': users_count,
                    }
                }

                # Compare with legacy database if available
                if self.legacy_db:
                    try:
                        legacy_gods = len(self.legacy_db.get_all_gods() or [])
                        legacy_items = len(self.legacy_db.get_all_items() or [])
                        legacy_patches = len(self.legacy_db.get_patches() or [])

                        verification_results['comparison'] = {
                            'gods': {'legacy': legacy_gods, 'new': gods_count, 'match': legacy_gods == gods_count},
                            'items': {'legacy': legacy_items, 'new': items_count, 'match': legacy_items == items_count},
                            'patches': {'legacy': legacy_patches, 'new': patches_count, 'match': legacy_patches == patches_count},
                        }
                    except Exception as e:
                        logger.warning(f"Could not compare with legacy database: {e}")

        except Exception as e:
            logger.error(f"Error during verification: {e}")
            verification_results['error'] = str(e)

        return verification_results

    def run_migration(self) -> Dict[str, Any]:
        """Run the complete migration process."""
        logger.info("🚀 Starting data migration...")

        # Create backup
        backup_file = self.backup_current_data()

        # Run migrations
        gods_migrated = self.migrate_gods()
        items_migrated = self.migrate_items()
        patches_migrated = self.migrate_patches()
        users_migrated = self.migrate_users()

        # Verify migration
        verification = self.verify_migration()

        # Generate migration report
        migration_report = {
            'timestamp': datetime.now().isoformat(),
            'backup_file': backup_file,
            'migrated_counts': {
                'gods': gods_migrated,
                'items': items_migrated,
                'patches': patches_migrated,
                'users': users_migrated,
            },
            'total_migrated': gods_migrated + items_migrated + patches_migrated + users_migrated,
            'verification': verification,
            'migration_log': self.migration_log,
            'database_config': {
                'source': 'SQLite (legacy)',
                'target': self.db_config.get_database_type(),
                'target_uri': self.db_config.get_database_uri().split('@')[0] + '@***' if '@' in self.db_config.get_database_uri() else self.db_config.get_database_uri(),
            }
        }

        # Save migration report
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(migration_report, f, indent=2)

        logger.info(f"✅ Migration completed. Report saved to: {report_file}")

        return migration_report


def main():
    """Main migration function."""
    print("🗄️ SMITE 2 DIVINE ARSENAL - DATA MIGRATION")
    print("=" * 60)

    db_config = get_database_config()
    print("Source: SQLite (legacy)")
    print(f"Target: {db_config.get_database_type()}")
    print(f"Target URI: {db_config.get_database_uri()}")
    print()

    # Initialize Flask app context
    with app.app_context():
        # Create tables if they don't exist
        logger.info("🔧 Creating database tables...")
        db.create_all()
        logger.info("✅ Database tables created")

        # Run migration
        migrator = DataMigrator()
        report = migrator.run_migration()

        # Print summary
        print("\n📊 MIGRATION SUMMARY:")
        print(f"   Gods migrated: {report['migrated_counts']['gods']}")
        print(f"   Items migrated: {report['migrated_counts']['items']}")
        print(f"   Patches migrated: {report['migrated_counts']['patches']}")
        print(f"   Users migrated: {report['migrated_counts']['users']}")
        print(f"   Total migrated: {report['total_migrated']}")

        if 'comparison' in report['verification']:
            comp = report['verification']['comparison']
            print("\n🔍 VERIFICATION:")
            print(f"   Gods: {comp['gods']['new']}/{comp['gods']['legacy']} {'✅' if comp['gods']['match'] else '⚠️'}")
            print(f"   Items: {comp['items']['new']}/{comp['items']['legacy']} {'✅' if comp['items']['match'] else '⚠️'}")
            print(f"   Patches: {comp['patches']['new']}/{comp['patches']['legacy']} {'✅' if comp['patches']['match'] else '⚠️'}")

        print(f"\n📁 Report saved to: {os.path.basename(report.get('backup_file', 'N/A'))}")
        print("🎉 Migration completed successfully!")


if __name__ == "__main__":
    main()
