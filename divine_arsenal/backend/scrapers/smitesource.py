"""Scraper for SmiteSource.com pro builds and guides."""

from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag


class SmiteSourceScraper:
    """Scraper for SmiteSource.com pro builds and guides.

    TODO: Update selectors after inspecting actual HTML structure at smitesource.com
    Current selectors are placeholders and will need to be updated:
    - .god-build: Container for each god's build
    - .build-items: List of items in the build
    - .build-notes: Additional build notes/tips
    - .pro-player: Name of the pro player who created the build
    """

    def __init__(self) -> None:
        """Initialize the scraper with base URL and headers."""
        self.base_url = "https://smitesource.com"
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def get_god_build(self, god_name: str) -> Optional[Dict[str, str]]:
        """Scrape pro build for a specific god.

        Args:
            god_name: Name of the god to get build for

        Returns:
            Dictionary containing build information or None if not found
        """
        try:
            # Format god name for URL (lowercase, replace spaces with hyphens)
            formatted_name = god_name.lower().replace(" ", "-")
            url = f"{self.base_url}/god/{formatted_name}"

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # TODO: Update selectors based on actual HTML structure
            # Current: .god-build
            # Expected: Look for build container elements
            build_container = soup.find(class_="god-build")
            if not build_container:
                return None

            # Extract build items
            items = []
            # TODO: Update selector for items
            if isinstance(build_container, Tag):
                item_elements = build_container.find_all("div", class_="build-items")
                for item in item_elements:
                    items.append(item.text.strip())
            else:
                return None

            # Extract build notes
            notes = ""
            # TODO: Update selector for notes
            notes_elem = build_container.find(class_="build-notes")
            if notes_elem:
                notes = notes_elem.text.strip()

            # Extract pro player info
            pro_player = ""
            # TODO: Update selector for pro player
            player_elem = build_container.find(class_="pro-player")
            if player_elem:
                pro_player = player_elem.text.strip()

            build_data = {
                "god": god_name,
                "items": items,
                "notes": notes,
                "pro_player": pro_player,
                "last_updated": datetime.now().isoformat(),
            }

            return build_data

        except requests.RequestException as e:
            return None

    def get_meta_builds(self) -> List[Dict[str, str]]:
        """Scrape all current meta builds.

        Returns:
            List of dictionaries containing build information
        """
        try:
            url = f"{self.base_url}/meta"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            builds = []

            # TODO: Update selector based on actual HTML structure
            # Current: .meta-build
            # Expected: Look for meta builds container
            build_elements = soup.find_all(class_="meta-build")

            for build in build_elements:
                # TODO: Update selectors for build details
                god_name = build.find(class_="god-name").text.strip()
                build_data = self.get_god_build(god_name)
                if build_data:
                    builds.append(build_data)

            return builds

        except requests.RequestException as e:
            return []

    def get_god_build_and_icon(self, god_name: str):
        # Format god name for URL (lowercase, hyphens)
        formatted_name = god_name.lower().replace(" ", "-")
        url = f"{self.base_url}/god/{formatted_name}"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the god icon (usually in an <img> tag near the top)
        icon_url = None
        icon_img = soup.find("img", {"alt": god_name})
        if isinstance(icon_img, Tag):
            icon_url = icon_img.get("src")

        # Find the build items from the 'Recent Builds' section
        build_items = []
        # Look for the 'Final Build' text and extract following item names
        final_build_header = soup.find(string=lambda t: isinstance(t, str) and "Final Build" in t)
        if final_build_header:
            current = final_build_header.parent
            found = 0
            while current and found < 8:
                current = current.find_next_sibling()
                if not current:
                    break
                if hasattr(current, "name") and current.name in ["span", "div"]:
                    text = current.get_text(strip=True)
                    if text and text not in ["Final Build", "Starter Build"]:
                        build_items.append(text)
                        found += 1
                elif (
                    isinstance(current, Tag)
                    and current.string
                    and current.string.strip()
                    and current.string.strip() not in ["Final Build", "Starter Build"]
                ):
                    build_items.append(current.string.strip())
                    found += 1
        # Fallback: Try to parse 'Most Popular Items' if no build found
        if not build_items:
            popular_section = soup.find(string=lambda t: isinstance(t, str) and "Most Popular" in t)
            if popular_section:
                parent = popular_section.parent
                if parent:
                    for sibling in parent.find_all_next(["h3", "h4", "div", "span"], limit=8):
                        text = sibling.get_text(strip=True)
                        if text and text not in build_items and text not in ["Starter", "Relic"]:
                            build_items.append(text)
        return {"god": god_name, "icon_url": icon_url, "build": build_items}


if __name__ == "__main__":
    scraper = SmiteSourceScraper()
    data = scraper.get_god_build_and_icon("Merlin")
    print(data)
