"""Scraper for Smite 2 Wiki (wiki.smite2.com)."""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class WikiSmite2Scraper:
    """Scraper for Smite 2 Wiki at wiki.smite2.com.

    This scraper extracts gods, items, and patch notes from the official Smite 2 Wiki.
    The wiki uses MediaWiki structure which provides predictable HTML patterns.
    """

    def __init__(self) -> None:
        """Initialize the scraper with base URL and headers."""
        self.base_url = "https://wiki.smite2.com"
        self.api_url = f"{self.base_url}/api.php"
        self.headers = {
            "User-Agent": "DivineArsenal/1.0 (https://github.com/your-repo; contact@example.com)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def get_all_gods(self) -> List[Dict[str, str]]:
        """Scrape all gods from the wiki.

        Returns:
            List of dictionaries containing god information
        """
        try:
            gods_data = []

            # Known Smite 2 gods based on the official wiki
            smite2_gods = [
                # Arthurian
                "Merlin",
                "Mordred",
                # Celtic
                "Cernunnos",
                "The Morrigan",
                # Chinese
                "Guan Yu",
                "Hua Mulan",
                "Jing Wei",
                "Nu Wa",
                "Sun Wukong",
                # Egyptian
                "Anhur",
                "Anubis",
                "Geb",
                "Khepri",
                "Neith",
                "Ra",
                "Sobek",
                # Greek
                "Achilles",
                "Aphrodite",
                "Apollo",
                "Ares",
                "Artemis",
                "Athena",
                "Cerberus",
                "Hades",
                "Hecate",
                "Medusa",
                "Nemesis",
                "Poseidon",
                "Scylla",
                "Thanatos",
                "Zeus",
                # Hindu
                "Agni",
                "Ganesha",
                "Kali",
                "Rama",
                # Japanese
                "Amaterasu",
                "Danzaburou",
                "Izanami",
                "Susano",
                # Korean
                "Princess Bari",
                # Maya
                "Awilix",
                "Cabrakan",
                "Chaac",
                "Hun Batz",
                "Kukulkan",
                # Norse
                "Fenrir",
                "Loki",
                "Odin",
                "Sol",
                "Thor",
                "Ullr",
                "Ymir",
                # Polynesian
                "Pele",
                # Roman
                "Bacchus",
                "Bellona",
                "Cupid",
                "Hercules",
                "Mercury",
                "Vulcan",
                # Tales of Arabia
                "Aladdin",
                # Voodoo
                "Baron Samedi",
                # Yoruba
                "Yemoja",
            ]

            # Get detailed info for each god
            for god_name in smite2_gods:
                god_data = self.get_god_details(god_name)
                if god_data:
                    gods_data.append(god_data)
                else:
                    # If direct name doesn't work, try with "(SMITE 2)" suffix
                    alt_name = f"{god_name} (SMITE 2)"
                    god_data = self.get_god_details(alt_name)
                    if god_data:
                        gods_data.append(god_data)

            logger.info(f"Successfully scraped {len(gods_data)} gods from wiki")
            return gods_data

        except Exception as e:
            logger.error(f"Error fetching gods list: {e}")
            return []

    def get_god_details(self, god_name: str) -> Optional[Dict[str, str]]:
        """Get detailed information for a specific god.

        Args:
            god_name: Name of the god

        Returns:
            Dictionary containing god details or None if not found
        """
        try:
            # Get page content using MediaWiki API
            params = {"action": "parse", "page": god_name, "format": "json", "prop": "text"}

            response = requests.get(self.api_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "parse" not in data:
                logger.warning(f"God page not found: {god_name}")
                return None

            html_content = data["parse"]["text"]["*"]
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract basic god information
            god_info = {
                "name": god_name,
                "pantheon": "",
                "role": "",
                "type": "",
                "damage_type": "",
                "health": "",
                "mana": "",
                "speed": "",
                "range": "",
                "attack_speed": "",
                "abilities": [],
                "lore": "",
                "image_url": "",
            }

            # Extract god image from infobox
            infobox = soup.find("table", class_="infobox") or soup.find(
                "table", {"class": re.compile(r".*infobox.*")}
            )
            if infobox and isinstance(infobox, Tag):
                # Look for god portrait image
                img_elem = infobox.find("img")
                if img_elem and isinstance(img_elem, Tag):
                    img_src = img_elem.get("src")
                    if img_src and isinstance(img_src, str):
                        # Convert relative URLs to absolute
                        if img_src.startswith("//"):
                            god_info["image_url"] = f"https:{img_src}"
                        elif img_src.startswith("/"):
                            god_info["image_url"] = f"https://wiki.smite2.com{img_src}"
                        else:
                            god_info["image_url"] = img_src

            # Look for infobox (common MediaWiki pattern)
            infobox = soup.find("table", class_="infobox") or soup.find(
                "table", {"class": re.compile(r".*infobox.*")}
            )

            if infobox and isinstance(infobox, Tag):
                rows = infobox.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        # Map common infobox fields
                        if "pantheon" in label:
                            god_info["pantheon"] = value
                        elif "role" in label or "class" in label:
                            god_info["role"] = value
                        elif "type" in label:
                            god_info["type"] = value
                        elif "damage" in label:
                            god_info["damage_type"] = value
                        elif "health" in label or "hp" in label:
                            god_info["health"] = value
                        elif "mana" in label or "mp" in label:
                            god_info["mana"] = value
                        elif "speed" in label:
                            god_info["speed"] = value
                        elif "range" in label:
                            god_info["range"] = value
                        elif "attack speed" in label:
                            god_info["attack_speed"] = value
                        # 🔥 NEW: Look for Intelligence and Strength scaling
                        elif "intelligence" in label or "int" in label:
                            god_info["intelligence"] = value
                        elif "strength" in label or "str" in label:
                            god_info["strength"] = value
                        elif "base" in label and ("intelligence" in label or "strength" in label):
                            # Handle combined base stats
                            if "intelligence" in label:
                                god_info["intelligence"] = value
                            elif "strength" in label:
                                god_info["strength"] = value

            # Extract abilities
            abilities_section = soup.find("h2", string=re.compile(r"abilities", re.I))
            if abilities_section and isinstance(abilities_section, Tag):
                abilities_content = []
                current = abilities_section.find_next_sibling()
                while current and current.name != "h2":
                    if hasattr(current, "name") and current.name in ["h3", "h4"]:
                        ability_name = current.get_text(strip=True)
                        ability_desc = ""
                        desc_elem = current.find_next_sibling(["p", "div"])
                        if desc_elem:
                            ability_desc = desc_elem.get_text(strip=True)

                        # 🔥 NEW: Look for Intelligence/Strength scaling in ability descriptions
                        scaling_info = self._extract_scaling_from_text(ability_desc)
                        if scaling_info:
                            ability_desc += f" [Scaling: {scaling_info}]"

                        abilities_content.append(
                            {"name": ability_name, "description": ability_desc}
                        )
                    current = current.find_next_sibling()
                god_info["abilities"] = abilities_content

            # 🔥 NEW: Look for Intelligence/Strength in the entire page content
            page_text = soup.get_text()
            scaling_data = self._extract_scaling_from_text(page_text)
            if scaling_data:
                god_info["scaling_info"] = scaling_data

            # Extract lore
            lore_section = soup.find("h2", string=re.compile(r"lore|background|story", re.I))
            if lore_section and isinstance(lore_section, Tag):
                lore_content = []
                current = lore_section.find_next_sibling()
                while current and hasattr(current, "name") and current.name != "h2":
                    if current.name == "p":
                        lore_content.append(current.get_text(strip=True))
                    current = current.find_next_sibling()
                god_info["lore"] = " ".join(lore_content)

            logger.info(f"Successfully scraped details for god: {god_name}")
            return god_info

        except requests.RequestException as e:
            logger.error(f"Error fetching god details for {god_name}: {e}")
            return None

    def get_all_item_titles(self) -> List[str]:
        """Fetch all item page titles from the Smite 2 Wiki's Items category using the MediaWiki API."""
        titles = []
        categories_to_try = [
            "Category:Items (Smite 2)",
            "Category:Items",
            "Category:Smite 2 Items",
        ]
        found_in_category = False
        for category in categories_to_try:
            print(f"[DEBUG] Trying category: {category}")
            cmcontinue = None
            while True:
                params = {
                    "action": "query",
                    "list": "categorymembers",
                    "cmtitle": category,
                    "cmlimit": "500",
                    "format": "json",
                }
                if cmcontinue:
                    params["cmcontinue"] = cmcontinue
                response = requests.get(self.api_url, params=params, headers=self.headers)
                print(f"[DEBUG] API URL: {response.url}")
                data = response.json()
                print(f"[DEBUG] API response: {json.dumps(data, indent=2)[:1000]}")
                members = data.get("query", {}).get("categorymembers", [])
                for m in members:
                    titles.append(m["title"])
                cmcontinue = data.get("continue", {}).get("cmcontinue")
                if not cmcontinue:
                    break
            print(f"[DEBUG] Category {category} returned {len(titles)} titles: {titles[:10]}...")
            if len(titles) > 20:
                print(f"[DEBUG] Found {len(titles)} titles in category: {category}")
                found_in_category = True
                break
        if not found_in_category:
            # Fallback: try different URLs for items pages
            print("[DEBUG] No items found in categories, trying different item page URLs...")
            item_urls_to_try = [
                "https://wiki.smite2.com/wiki/Items",
                "https://wiki.smite2.com/wiki/Item",
                "https://wiki.smite2.com/wiki/Items_(Smite_2)",
                "https://wiki.smite2.com/wiki/Category:Items_by_Type",
                "https://wiki.smite2.com/wiki/Category:Items_by_Tier",
            ]

            for items_page_url in item_urls_to_try:
                print(f"[DEBUG] Trying URL: {items_page_url}")
                response = requests.get(items_page_url, headers=self.headers)
                print(f"[DEBUG] Response status: {response.status_code}")
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    content = soup.find("div", {"class": "mw-parser-output"})
                    if content and isinstance(content, Tag):
                        print(f"[DEBUG] Content structure preview: {str(content)[:1000]}...")
                        links = content.find_all("a", href=True)
                        print(f"[DEBUG] Found {len(links)} total links")
                        item_titles = set()
                        for link in links:
                            href = link["href"]
                            title = link.get("title")
                            text = link.get_text(strip=True)
                            # Filter out non-item links (skip category, file, etc.)
                            if (
                                title
                                and not title.startswith("Category:")
                                and not title.startswith("File:")
                                and not title.startswith("Template:")
                            ):
                                item_titles.add(title)
                        print(f"[DEBUG] Parsed {len(item_titles)} item links from {items_page_url}")
                        if (
                            len(item_titles) > 10
                        ):  # Only use if we found a reasonable number of items
                            titles = sorted(item_titles)
                            break

            # Final fallback: use MediaWiki API to search for pages with "Item" in title
            if len(titles) <= 6:  # If we still don't have many items
                print("[DEBUG] Trying MediaWiki API search for specific item names...")
                item_names_to_search = [
                    "Axe",
                    "Gem",
                    "Shield",
                    "Ring",
                    "Bow",
                    "Sword",
                    "Staff",
                    "Book",
                    "Rod",
                    "Blade",
                ]

                for item_name in item_names_to_search:
                    print(f"[DEBUG] Searching for '{item_name}'...")
                    search_params = {
                        "action": "query",
                        "list": "search",
                        "srsearch": item_name,
                        "srlimit": "50",
                        "format": "json",
                    }
                    response = requests.get(
                        self.api_url, params=search_params, headers=self.headers
                    )
                    data = response.json()
                    search_results = data.get("query", {}).get("search", [])
                    print(
                        f"[DEBUG] Search for '{item_name}' returned {len(search_results)} results"
                    )

                    for result in search_results:
                        title = result.get("title", "")
                        snippet = result.get("snippet", "")
                        # Look for pages that seem to be actual items (not categories, templates, etc.)
                        if (
                            not title.startswith("Category:")
                            and not title.startswith("Template:")
                            and not title.startswith("User:")
                            and not title.startswith("Talk:")
                            and not title.startswith("File:")
                            and len(title.split()) <= 4  # Most item names are 1-4 words
                            and title not in titles
                        ):  # Avoid duplicates
                            titles.append(title)
                            print(f"[DEBUG] ✅ Found potential item: {title}")

                print(f"[DEBUG] Total titles list now has {len(titles)} items")
        return titles

    def get_all_items(self) -> List[Dict[str, str]]:
        """Scrape all items from the wiki dynamically."""
        try:
            items_data = []
            item_titles = self.get_all_item_titles()
            for item_name in item_titles:
                item_data = self.get_item_details(item_name)
                if item_data:
                    items_data.append(item_data)
                else:
                    # If direct name doesn't work, try with (SMITE 2) suffix
                    alt_name = f"{item_name} (SMITE 2)"
                    item_data = self.get_item_details(alt_name)
                    if item_data:
                        items_data.append(item_data)
            logger.info(f"Successfully scraped {len(items_data)} items from wiki dynamically")
            return items_data
        except Exception as e:
            logger.error(f"Error fetching items list: {e}")
            return []

    def get_item_details(self, item_name: str) -> Optional[Dict[str, str]]:
        """Get detailed information for a specific item.

        Args:
            item_name: Name of the item

        Returns:
            Dictionary containing item details or None if not found
        """
        try:
            # Get page content using MediaWiki API
            params = {"action": "parse", "page": item_name, "format": "json", "prop": "text"}

            response = requests.get(self.api_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "parse" not in data:
                logger.warning(f"Item page not found: {item_name}")
                return None

            html_content = data["parse"]["text"]["*"]
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract item information
            item_info = {
                "name": item_name,
                "type": "",
                "tier": "",
                "cost": "",
                "stats": {},
                "passive": "",
                "active": "",
                "description": "",
                "image_url": "",
                "recipe": [],
                "builds_into": [],
            }

            # Look for infobox
            infobox = soup.find("table", class_="infobox") or soup.find(
                "table", {"class": re.compile(r".*infobox.*")}
            )

            # Extract item image from infobox - look for higher quality images
            if infobox and isinstance(infobox, Tag):
                # Look for item icon image - prefer larger versions
                img_elem = infobox.find("img")
                if img_elem and isinstance(img_elem, Tag):
                    img_src = img_elem.get("src")
                    if img_src and isinstance(img_src, str):
                        # Convert relative URLs to absolute and try to get larger version
                        if img_src.startswith("//"):
                            item_info["image_url"] = f"https:{img_src}"
                        elif img_src.startswith("/"):
                            item_info["image_url"] = f"https://wiki.smite2.com{img_src}"
                        else:
                            item_info["image_url"] = img_src

                        # Try to get higher resolution version
                        if "/thumb/" in item_info["image_url"] and "px-" in item_info["image_url"]:
                            # Remove thumbnail sizing to get original
                            base_url = (
                                item_info["image_url"].split("/thumb/")[0]
                                + "/"
                                + item_info["image_url"].split("/")[-1].split("px-")[1]
                            )
                            item_info["image_url"] = base_url

            if infobox and isinstance(infobox, Tag):
                rows = infobox.find_all("tr")
                for row in rows:
                    cells = row.find_all(["th", "td"])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        # Enhanced stat extraction
                        if "type" in label or "category" in label:
                            item_info["type"] = value
                        elif "tier" in label:
                            item_info["tier"] = value
                        elif "cost" in label or "price" in label:
                            # Extract numeric cost
                            cost_match = re.search(r"(\d+)", value)
                            if cost_match:
                                item_info["cost"] = int(cost_match.group(1))
                        elif "physical power" in label or "strength" in label:
                            power_match = re.search(r"(\d+)", value)
                            if power_match:
                                item_info["stats"]["physical_power"] = int(power_match.group(1))
                        elif "magical power" in label or "intelligence" in label:
                            power_match = re.search(r"(\d+)", value)
                            if power_match:
                                item_info["stats"]["magical_power"] = int(power_match.group(1))
                        elif "health" in label and "max" not in label:
                            health_match = re.search(r"(\d+)", value)
                            if health_match:
                                item_info["stats"]["health"] = int(health_match.group(1))
                        elif "mana" in label:
                            mana_match = re.search(r"(\d+)", value)
                            if mana_match:
                                item_info["stats"]["mana"] = int(mana_match.group(1))
                        elif "physical protection" in label or "armor" in label:
                            prot_match = re.search(r"(\d+)", value)
                            if prot_match:
                                item_info["stats"]["physical_protection"] = int(prot_match.group(1))
                        elif "magical protection" in label:
                            prot_match = re.search(r"(\d+)", value)
                            if prot_match:
                                item_info["stats"]["magical_protection"] = int(prot_match.group(1))
                        elif "attack speed" in label:
                            speed_match = re.search(r"(\d+)", value)
                            if speed_match:
                                item_info["stats"]["attack_speed"] = int(speed_match.group(1))
                        elif "movement speed" in label:
                            speed_match = re.search(r"(\d+)", value)
                            if speed_match:
                                item_info["stats"]["movement_speed"] = int(speed_match.group(1))
                        elif "cooldown" in label:
                            cd_match = re.search(r"(\d+)", value)
                            if cd_match:
                                item_info["stats"]["cooldown_reduction"] = int(cd_match.group(1))
                        elif "penetration" in label:
                            pen_match = re.search(r"(\d+)", value)
                            if pen_match:
                                item_info["stats"]["penetration"] = int(pen_match.group(1))
                        elif "lifesteal" in label:
                            ls_match = re.search(r"(\d+)", value)
                            if ls_match:
                                item_info["stats"]["lifesteal"] = int(ls_match.group(1))
                        elif "critical" in label and "chance" in label:
                            crit_match = re.search(r"(\d+)", value)
                            if crit_match:
                                item_info["stats"]["crit_chance"] = int(crit_match.group(1))
                        elif "critical" in label and "damage" in label:
                            crit_match = re.search(r"(\d+)", value)
                            if crit_match:
                                item_info["stats"]["crit_damage"] = int(crit_match.group(1))

            # Extract passive/active effects with better parsing
            passive_section = soup.find("h3", string=re.compile(r"passive", re.I))
            if not passive_section:
                passive_section = soup.find(string=re.compile(r"passive", re.I))
            if passive_section:
                parent = (
                    passive_section.find_parent()
                    if hasattr(passive_section, "find_parent")
                    else passive_section.parent
                )
                if parent and isinstance(parent, Tag):
                    passive_elem = parent.find_next_sibling(["p", "div"])
                    if passive_elem:
                        item_info["passive"] = passive_elem.get_text(strip=True)

            active_section = soup.find("h3", string=re.compile(r"active", re.I))
            if not active_section:
                active_section = soup.find(string=re.compile(r"active", re.I))
            if active_section:
                parent = (
                    active_section.find_parent()
                    if hasattr(active_section, "find_parent")
                    else active_section.parent
                )
                if parent and isinstance(parent, Tag):
                    active_elem = parent.find_next_sibling(["p", "div"])
                    if active_elem:
                        item_info["active"] = active_elem.get_text(strip=True)

            # Extract description from first meaningful paragraph
            desc_paragraphs = soup.find_all("p")
            for p in desc_paragraphs:
                text = p.get_text(strip=True)
                if (
                    len(text) > 20
                    and not text.startswith("This page was")
                    and not text.startswith("Categories:")
                ):
                    item_info["description"] = text
                    break

            logger.info(f"Successfully scraped details for item: {item_name}")
            return item_info

        except requests.RequestException as e:
            logger.error(f"Error fetching item details for {item_name}: {e}")
            return None

    def get_patch_notes(self) -> List[Dict[str, str]]:
        """Scrape patch notes from the wiki.

        Returns:
            List of dictionaries containing patch information
        """
        try:
            # Get patch notes page
            params = {
                "action": "parse",
                "page": "Patch notes (SMITE 2)",
                "format": "json",
                "prop": "text",
            }

            response = requests.get(self.api_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "parse" not in data:
                logger.warning("Patch notes page not found")
                return []

            html_content = data["parse"]["text"]["*"]
            soup = BeautifulSoup(html_content, "html.parser")

            patches = []

            # Look for patch sections (headings that contain patch versions)
            patch_headings = soup.find_all(
                ["h2", "h3"], string=re.compile(r"(patch|update|beta|alpha)", re.I)
            )

            for heading in patch_headings:
                if isinstance(heading, Tag):
                    patch_title = heading.get_text(strip=True)

                    # Extract version number
                    version_match = re.search(r"(\d+\.?\d*\.?\d*)", patch_title)
                    version = version_match.group(1) if version_match else "Unknown"

                    # Get patch content
                    content_parts = []
                    current = heading.find_next_sibling()
                    while current and current.name not in ["h1", "h2", "h3"]:
                        if current.name in ["p", "ul", "ol", "div"]:
                            content_parts.append(current.get_text(strip=True))
                        current = current.find_next_sibling()

                    content = "\n".join(content_parts)

                    # Try to extract date
                    date_match = re.search(r"(\d{4}-\d{2}-\d{2}|\w+ \d+, \d{4})", content)
                    date = date_match.group(1) if date_match else "Unknown"

                    patches.append(
                        {
                            "version": version,
                            "title": patch_title,
                            "date": date,
                            "content": content,
                            "url": f"https://wiki.smite2.com/Patch_notes_(SMITE_2)",
                            "source": "wiki",
                        }
                    )

            # Also try alternative patch notes locations
            alt_pages = ["Updates", "Changelog", "Version history"]
            for page in alt_pages:
                try:
                    alt_patches = self._get_patch_details(page)
                    if alt_patches:
                        patches.extend(alt_patches)
                except Exception:
                    continue

            logger.info(f"Successfully scraped {len(patches)} patch notes")
            return patches[:20]  # Limit to 20 most recent

        except Exception as e:
            logger.error(f"Error fetching patch notes: {e}")
            return []

    def _get_patch_details(self, patch_title: str) -> Optional[Dict[str, str]]:
        """Get details for a specific patch note page.

        Args:
            patch_title: Title of the patch note page

        Returns:
            Dictionary containing patch details or None if not found
        """
        try:
            params = {"action": "parse", "page": patch_title, "format": "json", "prop": "text"}

            response = requests.get(self.api_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "parse" not in data:
                return None

            html_content = data["parse"]["text"]["*"]
            soup = BeautifulSoup(html_content, "html.parser")

            # Extract version from title
            version_match = re.search(r"(\d+\.\d+(?:\.\d+)?)", patch_title)
            version = version_match.group(1) if version_match else patch_title

            # Get patch content
            content_paragraphs = soup.find_all("p")
            content = "\n".join(
                [p.get_text(strip=True) for p in content_paragraphs if p.get_text(strip=True)]
            )

            return {
                "version": version,
                "title": patch_title,
                "date": datetime.now().strftime("%Y-%m-%d"),  # Wiki may not have explicit dates
                "content": content,
                "url": urljoin(self.base_url, f"/wiki/{patch_title.replace(' ', '_')}"),
            }

        except requests.RequestException as e:
            logger.error(f"Error fetching patch details for {patch_title}: {e}")
            return None

    def search_wiki(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """Search the wiki for pages matching a query.

        Args:
            query: Search term
            limit: Maximum number of results to return

        Returns:
            List of search results
        """
        try:
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "format": "json",
            }

            response = requests.get(self.api_url, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()

            if "query" not in data or "search" not in data["query"]:
                return []

            results = []
            for result in data["query"]["search"]:
                results.append(
                    {
                        "title": result["title"],
                        "snippet": result.get("snippet", ""),
                        "url": urljoin(self.base_url, f"/wiki/{result['title'].replace(' ', '_')}"),
                    }
                )

            logger.info(f"Found {len(results)} search results for query: {query}")
            return results

        except requests.RequestException as e:
            logger.error(f"Error searching wiki: {e}")
            return []

    def _extract_scaling_from_text(self, text: str) -> Optional[Dict[str, str]]:
        """Extract Intelligence and Strength scaling information from text."""
        scaling_data = {}

        # Look for Intelligence scaling patterns
        int_patterns = [
            r"intelligence[:\s]*(\d+\.?\d*)",
            r"int[:\s]*(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*intelligence",
            r"(\d+\.?\d*)\s*int",
        ]

        # Look for Strength scaling patterns
        str_patterns = [
            r"strength[:\s]*(\d+\.?\d*)",
            r"str[:\s]*(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*strength",
            r"(\d+\.?\d*)\s*str",
        ]

        # Check for Intelligence scaling
        for pattern in int_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                scaling_data["intelligence"] = match.group(1)
                break

        # Check for Strength scaling
        for pattern in str_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                scaling_data["strength"] = match.group(1)
                break

        # Also look for base stats patterns like "1.75 (+0.2)" which might be the new format
        base_stats_pattern = r"(\d+\.?\d*)\s*\(\+(\d+\.?\d*)\)"
        base_match = re.search(base_stats_pattern, text)
        if base_match:
            scaling_data["base_value"] = base_match.group(1)
            scaling_data["scaling_value"] = base_match.group(2)

        return scaling_data if scaling_data else None
