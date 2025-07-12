"""Tests for the build optimizer module."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from divine_arsenal.backend.build import Build
from divine_arsenal.backend.build_optimizer import BuildOptimizer
from divine_arsenal.backend.database import Database
from divine_arsenal.backend.item import Item
from divine_arsenal.backend.item_stats import ItemStats


class TestBuildOptimizer(unittest.TestCase):
    """Test cases for the BuildOptimizer class."""

    def setUp(self):
        """Set up test environment."""
        self.db = MagicMock()
        self.optimizer = BuildOptimizer(self.db)

        # Create test items
        self.test_item = Item(
            name="Test Item",
            cost=2500,
            category="Physical",
            tags=["Power", "Penetration"],
            stats={"physical_power": 40, "physical_pen": 10},
            tier=3,
        )

        self.test_build = Build(items=[self.test_item], total_cost=2500)

    def test_build_creation(self):
        """Test basic build creation."""
        self.assertIsInstance(self.test_build, Build)
        self.assertEqual(len(self.test_build.items), 1)
        self.assertEqual(self.test_build.total_cost, 2500)

    def test_item_stats_operations(self):
        """Test ItemStats operations."""
        stats = ItemStats({"physical_power": 40, "physical_pen": 10})

        # Test attribute access
        self.assertEqual(stats.physical_power, 40)
        self.assertEqual(stats.physical_pen, 10)
        self.assertEqual(stats.nonexistent_stat, 0.0)

        # Test dictionary-like access
        self.assertEqual(stats["physical_power"], 40)
        self.assertEqual(stats["physical_pen"], 10)
        self.assertEqual(stats["nonexistent_stat"], 0.0)

        # Test get method
        self.assertEqual(stats.get("physical_power"), 40)
        self.assertEqual(stats.get("nonexistent_stat", 10.0), 10.0)

        # Test items method
        items = dict(stats.items())
        self.assertEqual(items["physical_power"], 40)
        self.assertEqual(items["physical_pen"], 10)

    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.db, self.db)


if __name__ == "__main__":
    unittest.main()
