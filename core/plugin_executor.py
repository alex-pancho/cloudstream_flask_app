import logging
from urllib.parse import urljoin
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
    
    def get_first_movies(self, limit: int = 10):
        """
        Parse main page using lxml and plugin config.
        Uses:
        - main_pages if defined
        - otherwise base_url
        - file_regex to filter valid movie links
        """

        try:
            urls_to_scan = []

            # 1 if main_pages defined — we scan them, otherwise — base_url
            if self.config.main_pages:
                urls_to_scan = list(self.config.main_pages.keys())
            else:
                urls_to_scan = [self.config.base_url]

            movies = []

            for url in urls_to_scan:
                response = self.client.get(
                    url,
                    headers=self.config.headers or None,
                    timeout=self.timeout
                )
                response.raise_for_status()

                tree = html.fromstring(response.text)

                # 2 Get all <a href="">
                links = tree.xpath("//a[@href]/@href")

                for link in links:
                    absolute_url = urljoin(self.config.base_url, link)

                    # 3 Filter by file_regex
                    if self.config.file_regex:
                        if not self.config.file_regex.search(absolute_url):
                            continue

                    movies.append({
                        "title": absolute_url.split("/")[-1],
                        "url": absolute_url
                    })

                    if len(movies) >= limit:
                        return movies

            return movies

        except Exception as e:
            print(f"[PluginExecutor] Error in {self.config.name}: {e}")
            return []

class PluginFactory:

    def __init__(self):
        self.loader = KotlinPluginLoader()

    def create_executor(self, path: str) -> PluginExecutor:
        config = self.loader.load(path)
        return PluginExecutor(config)
