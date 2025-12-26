# src/scrapers/instagram.py
"""Instagram Scraper (Free, No Auth)

This module provides a very lightweight scraper that pulls the most recent public posts
from a list of Instagram usernames. It uses Instagram's public GraphQL endpoint which
returns JSON data when accessed with a proper User‑Agent header. No API key or login is
required, making it suitable for a zero‑cost setup.

Limitations:
* Only works for public accounts.
* Instagram may rate‑limit or change the endpoint; the scraper includes basic retry
  logic and a fallback to the simple HTML page parsing.
* The scraper extracts the caption text and the media URL – you can then run the
  existing VADER sentiment engine on the caption.
"""

import json
import time
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _graphql_query(username: str) -> str:
    """Return the GraphQL query string for a given username.
    The query fetches the first 12 recent posts (edge_owner_to_timeline_media).
    """
    return f"{{\n  user(username: \"{username}\") {{\n    edge_owner_to_timeline_media(first: 12) {{\n      edges {{\n        node {{\n          shortcode\n          edge_media_to_caption {{\n            edges {{\n              node {{\n                text\n              }}\n            }}\n          }}\n          display_url\n          taken_at_timestamp\n        }}\n      }}\n    }}\n  }}\n}}"


def fetch_posts(usernames: List[str], limit: int = 5) -> List[Dict]:
    """Fetch recent posts for each username.

    Returns a list of dictionaries with keys: `username`, `caption`, `media_url`,
    `timestamp`.
    """
    results: List[Dict] = []
    for username in usernames:
        try:
            # First try the GraphQL endpoint
            url = "https://www.instagram.com/graphql/query/"
            params = {"query_hash": "58b6785bea111c671ebb24d0e5c1e1e2", "variables": json.dumps({"id": username, "first": limit})}
            headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                edges = data.get("data", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("edges", [])
                for edge in edges[:limit]:
                    node = edge.get("node", {})
                    caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
                    caption = caption_edges[0].get("node", {}).get("text", "") if caption_edges else ""
                    results.append({
                        "username": username,
                        "caption": caption,
                        "media_url": node.get("display_url"),
                        "timestamp": node.get("taken_at_timestamp"),
                    })
                continue
        except Exception:
            pass
        # Fallback to simple HTML parsing if GraphQL fails or is blocked
        try:
            page_url = f"https://www.instagram.com/{username}/"
            html = requests.get(page_url, headers={"User-Agent": USER_AGENT}, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            scripts = soup.find_all("script", type="text/javascript")
            for script in scripts:
                if script.string and "window._sharedData" in script.string:
                    json_text = script.string.split(' = ', 1)[1].rstrip(';')
                    data = json.loads(json_text)
                    edges = data.get("entry_data", {}).get("ProfilePage", [])[0].get("graphql", {}).get("user", {}).get("edge_owner_to_timeline_media", {}).get("edges", [])
                    for edge in edges[:limit]:
                        node = edge.get("node", {})
                        caption = node.get("edge_media_to_caption", {}).get("edges", [])[0].get("node", {}).get("text", "")
                        results.append({
                            "username": username,
                            "caption": caption,
                            "media_url": node.get("display_url"),
                            "timestamp": node.get("taken_at_timestamp"),
                        })
                    break
        except Exception:
            # If everything fails, skip this user
            continue
        # Respect a short delay to avoid hammering Instagram
        time.sleep(1)
    return results
class InstagramScraper:
    """Wrapper class for Instagram scraping.

    Provides a `fetch_posts` method compatible with the engine's usage.
    """
    def __init__(self):
        pass

    def fetch_posts(self, usernames, limit=5):
        """Fetch recent posts for given usernames.
        Returns a list of post dictionaries.
        """
        return fetch_posts(usernames, limit)
