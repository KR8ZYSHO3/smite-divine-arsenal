#!/usr/bin/env python3
"""AI-powered patch notes enhancement system."""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PatchNotesEnhancer:
    """Enhances patch notes with clearer descriptions and analysis."""

    def __init__(self):
        self.enhancement_patterns = {
            # Damage changes
            r"damage.*increased.*(\d+).*to.*(\d+)": "Damage buffed from {0} to {1} - expect stronger performance",
            r"damage.*decreased.*(\d+).*to.*(\d+)": "Damage nerfed from {0} to {1} - will hit softer now",
            r"damage.*reduced.*(\d+).*to.*(\d+)": "Damage reduced from {0} to {1} - less threatening in fights",
            # Cooldown changes
            r"cooldown.*increased.*(\d+).*to.*(\d+)": "Cooldown increased from {0}s to {1}s - less frequent ability use",
            r"cooldown.*decreased.*(\d+).*to.*(\d+)": "Cooldown reduced from {0}s to {1}s - more spammable ability",
            r"cooldown.*reduced.*(\d+).*to.*(\d+)": "Cooldown lowered from {0}s to {1}s - higher uptime",
            # Cost changes
            r"mana.*cost.*increased.*(\d+).*to.*(\d+)": "Mana cost raised from {0} to {1} - harder to spam",
            r"mana.*cost.*decreased.*(\d+).*to.*(\d+)": "Mana cost lowered from {0} to {1} - easier to use repeatedly",
            # Health/Protection changes
            r"health.*increased.*(\d+).*to.*(\d+)": "Health buffed from {0} to {1} - more survivability",
            r"health.*decreased.*(\d+).*to.*(\d+)": "Health nerfed from {0} to {1} - easier to kill",
            r"protections.*increased.*(\d+).*to.*(\d+)": "Protections boosted from {0} to {1} - tankier",
            r"protections.*decreased.*(\d+).*to.*(\d+)": "Protections reduced from {0} to {1} - squishier",
            # Range/Speed changes
            r"range.*increased.*(\d+).*to.*(\d+)": "Range extended from {0} to {1} - safer positioning",
            r"range.*decreased.*(\d+).*to.*(\d+)": "Range shortened from {0} to {1} - must get closer",
            r"movement.*speed.*increased.*(\d+).*to.*(\d+)": "Movement speed boosted from {0} to {1} - more mobile",
            r"movement.*speed.*decreased.*(\d+).*to.*(\d+)": "Movement speed reduced from {0} to {1} - slower",
            # Duration changes
            r"duration.*increased.*(\d+).*to.*(\d+)": "Duration extended from {0}s to {1}s - longer effect",
            r"duration.*decreased.*(\d+).*to.*(\d+)": "Duration shortened from {0}s to {1}s - briefer effect",
        }

        self.god_impact_keywords = {
            "buff": ["increased", "improved", "enhanced", "boosted", "stronger"],
            "nerf": ["decreased", "reduced", "lowered", "weakened", "nerfed"],
            "rework": ["reworked", "redesigned", "changed", "modified", "updated"],
            "bug_fix": ["fixed", "corrected", "resolved", "addressed"],
        }

        self.item_impact_keywords = {
            "meta_shift": ["cost increased", "cost decreased", "stats changed"],
            "viability": ["damage increased", "damage decreased", "protection"],
            "accessibility": ["cost", "tier", "recipe"],
        }

    def enhance_patch_notes(self, patch_data: Dict[str, str]) -> Dict[str, Any]:
        """Enhance patch notes with clearer descriptions and analysis.

        Args:
            patch_data: Dictionary containing patch information

        Returns:
            Enhanced patch data with additional analysis
        """
        try:
            original_content = patch_data.get("content", "")
            enhanced_data: Dict[str, Any] = patch_data.copy()

            # Generate enhanced summary
            enhanced_data["enhanced_summary"] = self._generate_summary(original_content)

            # Analyze god changes
            enhanced_data["god_changes"] = self._analyze_god_changes(original_content)

            # Analyze item changes
            enhanced_data["item_changes"] = self._analyze_item_changes(original_content)

            # Generate impact assessment
            enhanced_data["meta_impact"] = self._assess_meta_impact(original_content)

            # Clean up and enhance content
            enhanced_data["enhanced_content"] = self._enhance_content(original_content)

            return enhanced_data

        except Exception as e:
            logger.error(f"Error enhancing patch notes: {e}")
            return patch_data

    def _generate_summary(self, content: str) -> str:
        """Generate a concise summary of patch changes."""
        try:
            # Extract key changes
            god_mentions = re.findall(
                r"([A-Z][a-z]+).*?(?:increased|decreased|changed|fixed)", content, re.IGNORECASE
            )
            item_mentions = re.findall(
                r"([A-Z][a-z\s]+).*?(?:cost|damage|protection)", content, re.IGNORECASE
            )

            # Count change types
            buffs = len(re.findall(r"increased|improved|enhanced|boosted", content, re.IGNORECASE))
            nerfs = len(re.findall(r"decreased|reduced|lowered|nerfed", content, re.IGNORECASE))
            fixes = len(re.findall(r"fixed|corrected|resolved", content, re.IGNORECASE))

            summary_parts = []

            if god_mentions:
                unique_gods = list(set(god_mentions[:5]))  # Top 5 unique gods
                summary_parts.append(f"🦸 Gods affected: {', '.join(unique_gods)}")

            if item_mentions:
                unique_items = list(set(item_mentions[:3]))  # Top 3 unique items
                summary_parts.append(f"⚔️ Items changed: {', '.join(unique_items)}")

            if buffs > 0:
                summary_parts.append(f"📈 {buffs} buffs")
            if nerfs > 0:
                summary_parts.append(f"📉 {nerfs} nerfs")
            if fixes > 0:
                summary_parts.append(f"🔧 {fixes} bug fixes")

            return (
                " | ".join(summary_parts) if summary_parts else "General updates and improvements"
            )

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Patch contains various balance changes and updates"

    def _analyze_god_changes(self, content: str) -> List[Dict[str, str]]:
        """Analyze specific god changes in the patch."""
        try:
            god_changes = []

            # Look for god-specific sections
            god_sections = re.findall(
                r"([A-Z][a-z]+)\s*\n(.*?)(?=\n[A-Z][a-z]+|\n\n|\Z)", content, re.DOTALL
            )

            for god_name, changes in god_sections:
                if len(changes.strip()) > 10:  # Meaningful change content
                    change_type = self._categorize_change(changes)
                    impact = self._assess_god_impact(changes)
                    enhanced_desc = self._enhance_god_description(changes)

                    god_changes.append(
                        {
                            "god": god_name,
                            "type": change_type,
                            "impact": impact,
                            "description": enhanced_desc,
                            "original": changes.strip(),
                        }
                    )

            return god_changes[:10]  # Limit to top 10

        except Exception as e:
            logger.error(f"Error analyzing god changes: {e}")
            return []

    def _analyze_item_changes(self, content: str) -> List[Dict[str, str]]:
        """Analyze specific item changes in the patch."""
        try:
            item_changes = []

            # Look for item-specific mentions
            item_patterns = [
                r"([A-Z][a-z\s\']+).*?cost.*?(\d+).*?to.*?(\d+)",
                r"([A-Z][a-z\s\']+).*?damage.*?(\d+).*?to.*?(\d+)",
                r"([A-Z][a-z\s\']+).*?protection.*?(\d+).*?to.*?(\d+)",
            ]

            for pattern in item_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) >= 3:
                        item_name = match[0].strip()
                        old_val = match[1]
                        new_val = match[2]

                        change_type = "buff" if int(new_val) > int(old_val) else "nerf"
                        impact = self._assess_item_impact(item_name, change_type)

                        item_changes.append(
                            {
                                "item": item_name,
                                "type": change_type,
                                "impact": impact,
                                "change": f"{old_val} → {new_val}",
                                "description": f"{item_name} stats {'improved' if change_type == 'buff' else 'reduced'}",
                            }
                        )

            return item_changes[:10]  # Limit to top 10

        except Exception as e:
            logger.error(f"Error analyzing item changes: {e}")
            return []

    def _categorize_change(self, change_text: str) -> str:
        """Categorize the type of change."""
        change_text_lower = change_text.lower()

        if any(word in change_text_lower for word in self.god_impact_keywords["buff"]):
            return "buff"
        elif any(word in change_text_lower for word in self.god_impact_keywords["nerf"]):
            return "nerf"
        elif any(word in change_text_lower for word in self.god_impact_keywords["rework"]):
            return "rework"
        elif any(word in change_text_lower for word in self.god_impact_keywords["bug_fix"]):
            return "bug_fix"
        else:
            return "adjustment"

    def _assess_god_impact(self, change_text: str) -> str:
        """Assess the impact level of god changes."""
        change_text_lower = change_text.lower()

        # High impact indicators
        if any(word in change_text_lower for word in ["damage", "ultimate", "passive", "rework"]):
            return "high"
        # Medium impact indicators
        elif any(word in change_text_lower for word in ["cooldown", "mana", "range", "duration"]):
            return "medium"
        # Low impact indicators
        else:
            return "low"

    def _assess_item_impact(self, item_name: str, change_type: str) -> str:
        """Assess the impact level of item changes."""
        # High impact items (core items)
        high_impact_items = ["rod of tahuti", "deathbringer", "book of thoth", "transcendence"]

        if any(item in item_name.lower() for item in high_impact_items):
            return "high"
        elif change_type in ["buff", "nerf"]:
            return "medium"
        else:
            return "low"

    def _enhance_god_description(self, change_text: str) -> str:
        """Enhance god change descriptions with clearer language."""
        enhanced = change_text

        # Apply enhancement patterns
        for pattern, replacement in self.enhancement_patterns.items():
            matches = re.finditer(pattern, enhanced, re.IGNORECASE)
            for match in matches:
                try:
                    enhanced_text = replacement.format(*match.groups())
                    enhanced = enhanced.replace(match.group(), enhanced_text)
                except Exception:
                    continue

        return enhanced

    def _assess_meta_impact(self, content: str) -> Dict[str, str]:
        """Assess overall meta impact of the patch."""
        try:
            content_lower = content.lower()

            # Count different types of changes
            total_changes = len(
                re.findall(r"increased|decreased|changed|fixed|improved", content_lower)
            )
            god_changes = len(re.findall(r"[a-z]+\s*\n.*?(?:increased|decreased)", content_lower))
            item_changes = len(re.findall(r"cost|damage.*(?:increased|decreased)", content_lower))

            # Determine impact level
            if total_changes > 20:
                impact_level = "Major"
            elif total_changes > 10:
                impact_level = "Moderate"
            elif total_changes > 5:
                impact_level = "Minor"
            else:
                impact_level = "Minimal"

            # Predict meta shifts
            meta_prediction = "Standard balance updates"
            if god_changes > 5:
                meta_prediction = "Expect god tier list changes"
            if item_changes > 3:
                meta_prediction += " and build path adjustments"

            return {
                "level": impact_level,
                "prediction": meta_prediction,
                "total_changes": str(total_changes),
                "focus": "Gods" if god_changes > item_changes else "Items",
            }

        except Exception as e:
            logger.error(f"Error assessing meta impact: {e}")
            return {"level": "Unknown", "prediction": "Impact analysis unavailable"}

    def _enhance_content(self, content: str) -> str:
        """Clean up and enhance the original content."""
        try:
            # Remove excessive whitespace
            enhanced = re.sub(r"\n\s*\n", "\n\n", content)

            # Add section headers for better readability
            enhanced = re.sub(r"\n([A-Z][a-z]+)\n", r"\n## \1\n", enhanced)

            # Highlight important numbers
            enhanced = re.sub(r"(\d+(?:\.\d+)?)", r"**\1**", enhanced)

            # Clean up common formatting issues
            enhanced = enhanced.replace("  ", " ")
            enhanced = enhanced.strip()

            return enhanced

        except Exception as e:
            logger.error(f"Error enhancing content: {e}")
            return content
