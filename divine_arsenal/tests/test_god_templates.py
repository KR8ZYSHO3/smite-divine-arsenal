"""Tests for the god templates module."""

import unittest
from unittest.mock import Mock, patch

from divine_arsenal.backend.build_optimizer import Build, Item, ItemStats
from divine_arsenal.backend.god_templates import GodTemplate, GodTemplateManager


class TestGodTemplateManager(unittest.TestCase):
    def setUp(self):
        self.manager = GodTemplateManager()
        self.mock_items = [
            Item(
                name="Jotunn's Wrath",
                cost=2500,
                category="Physical",
                tags=["Cooldown", "Penetration"],
                stats={"physical_power": 40, "physical_pen": 10, "cooldown": 20},
                tier=3,
            ),
            Item(
                name="Hydra's Lament",
                cost=2500,
                category="Physical",
                tags=["Cooldown", "Penetration"],
                stats={"physical_power": 40, "physical_pen": 10, "cooldown": 20},
                tier=3,
            ),
            Item(
                name="Magi's Cloak",
                cost=2000,
                category="Defense",
                tags=["Protection", "CCR"],
                stats={"magical_prot": 60, "ccr": 20},
                tier=3,
            ),
        ]

    def test_get_template(self):
        """Test getting a template for a specific god and role."""
        template = self.manager.get_template("Thor", "Assassin")
        if template is not None:
            self.assertEqual(template.god_name, "Thor")
            self.assertEqual(template.role, "Assassin")
        else:
            self.fail("Template for Thor as Assassin should not be None")

    def test_get_nonexistent_template(self):
        """Test getting a template for a nonexistent god/role combination."""
        template = self.manager.get_template("NonexistentGod", "NonexistentRole")
        self.assertIsNone(template)

    def test_get_core_items(self):
        """Test getting core items for a god."""
        core_items = self.manager.get_core_items("Thor", "Assassin")
        self.assertIn("Jotunn's Wrath", core_items)
        self.assertIn("Hydra's Lament", core_items)

    def test_get_counter_items(self):
        """Test getting counter items for specific enemy roles."""
        counter_items = self.manager.get_counter_items("Thor", "Assassin", "Mage")
        self.assertIn("Magi's Cloak", counter_items)

    def test_create_build_from_template(self):
        """Test creating a build from a template."""
        enemy_comp = ["Mage", "Hunter"]
        build = self.manager.create_build_from_template(
            "Thor", "Assassin", enemy_comp, self.mock_items
        )
        if build is not None:
            self.assertTrue(len(build.items) > 0)
            self.assertTrue(any(item.name == "Jotunn's Wrath" for item in build.items))
            self.assertTrue(any(item.name == "Hydra's Lament" for item in build.items))
            self.assertTrue(any(item.name == "Magi's Cloak" for item in build.items))
        else:
            self.fail("Build should not be None")

    def test_create_build_with_insufficient_items(self):
        """Test creating a build when not all template items are available."""
        limited_items = [self.mock_items[0]]  # Only Jotunn's Wrath
        enemy_comp = ["Mage"]
        build = self.manager.create_build_from_template(
            "Thor", "Assassin", enemy_comp, limited_items
        )
        if build is not None:
            self.assertEqual(len(build.items), 1)
            self.assertEqual(build.items[0].name, "Jotunn's Wrath")
        else:
            self.fail("Build should not be None")

    def test_create_build_for_nonexistent_god(self):
        """Test creating a build for a nonexistent god."""
        build = self.manager.create_build_from_template(
            "NonexistentGod", "Assassin", ["Mage"], self.mock_items
        )
        self.assertIsNone(build)

    def test_get_power_spike_items(self):
        """Test getting power spike items."""
        power_spike_items = self.manager.get_power_spike_items("Thor", "Assassin")
        self.assertIn("Jotunn's Wrath", power_spike_items)
        self.assertIn("Hydra's Lament", power_spike_items)

    def test_get_late_game_items(self):
        """Test getting late game items."""
        late_game_items = self.manager.get_late_game_items("Thor", "Assassin")
        self.assertIn("Titan's Bane", late_game_items)
        self.assertIn("Heartseeker", late_game_items)


if __name__ == "__main__":
    unittest.main()
