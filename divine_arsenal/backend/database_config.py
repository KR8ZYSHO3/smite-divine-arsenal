"""
Database Configuration for SMITE 2 Divine Arsenal - PostgreSQL Only
Supports only PostgreSQL (production-ready)
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class - PostgreSQL only."""

    def __init__(self):
        """Initialize database configuration."""
        self.config = {}
        
    def get_database_uri(self) -> str:
        """Get PostgreSQL database URI."""
        # Force PostgreSQL only - no SQLite fallback
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            raise ValueError(
                "DATABASE_URL environment variable is required for PostgreSQL connection. "
                "SQLite fallback has been removed for production consistency."
            )
        
        logger.info("Using DATABASE_URL for production")
        return database_url
    
    def get_database_type(self) -> str:
        """Get the database type (always postgresql)."""
        return 'postgresql'
    
    def get_flask_config(self) -> Dict[str, Any]:
        """Get Flask configuration for PostgreSQL."""
        database_uri = self.get_database_uri()
        
        return {
            'SQLALCHEMY_DATABASE_URI': database_uri,
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'pool_pre_ping': True,
                'pool_recycle': 3600,
                'pool_size': 10,
                'max_overflow': 20
            }
        }


def get_database_config() -> DatabaseConfig:
    """Get database configuration instance."""
    return DatabaseConfig()
