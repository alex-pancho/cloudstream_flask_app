import logging
from typing import List, Optional

import httpx
from lxml import html
from core.models import PluginConfig
from core.kotlin_loader import KotlinPluginLoader

logger = logging.getLogger(__name__)


class PluginExecutor:

    def __init__(self, config: PluginConfig, timeout: int = 10):
        self.config = config
        self.timeout = timeout
        
        self.client = httpx.Client(
            timeout=httpx.Timeout(timeout),
            headers=config.headers or {},
            follow_redirects=True,
        )

    # -------------------------
    # Capabilities
    # -------------------------

    @property
    def has_main_page(self) -> bool:
        return bool(self.config.has_main_page and self.config.main_pages)

    @property
    def has_file_regex(self) -> bool:
        return self.config.file_regex is not None

    @property
    def has_subs_regex(self) -> bool:
        return self.config.subs_regex is not None

    # -------------------------
    # Networking
    # -------------------------

    def fetch(self, url: str) -> Optional[str]:
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(
                "[%s] Fetch failed: %s | %s",
                self.config.name,
                url,
                e
            )
            return None

    # -------------------------
    # Main Page
    # -------------------------

    def get_main_page_urls(self) -> List[str]:
        if not self.has_main_page:
            return []

        return list(self.config.main_pages.keys())

    def fetch_main_page(self) -> List[dict]:
        """
        Return first 10 items from first main page.
        """
        if not self.has_main_page:
            return []

        first_url = self.get_main_page_urls()[0]
        html = self.fetch(first_url)
        if not html:
            return []

        return self._extract_titles(html)[:10]

    # -------------------------
    # Parsing
    # -------------------------

    def _extract_titles(self, html: str) -> List[dict]:
        """
        Very generic extraction based on file_regex.
        Production-safe (does not crash).
        """
        if not self.has_file_regex:
            return []

        matches = self.config.file_regex.findall(html)

        results = []
        for match in matches:
            if isinstance(match, tuple):
                url = match[0]
            else:
                url = match

            if self.config.black_urls and self.config.black_urls in url:
                continue

            results.append({
                "plugin": self.config.name,
                "url": url
            })

        return results
    
    def get_first_movies(self, plugin):
        """
        Here we can implement different strategies based on plugin capabilities:
        1. Get main page URLs from config
        2. Parse main page and extract movie links using file_regex
        3. Get first 10 movies and return them
        """

        try:
            base_url = plugin.url
            response = httpx.get(base_url, timeout=10)
            tree = html.fromstring(response.text)

            links = tree.xpath("//a[@href]")
            movies = []

            for link in links[:10]:
                title = link.text_content().strip()
                href = link.get("href")

                if title and href:
                    movies.append({
                        "title": title,
                        "url": href
                    })

            return movies

        except Exception as e:
            return []


class PluginFactory:

    def __init__(self):
        self.loader = KotlinPluginLoader()

    def create_executor(self, path: str) -> PluginExecutor:
        config = self.loader.load(path)
        return PluginExecutor(config)
