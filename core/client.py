import httpx
import time

from lxml import html
from core.models import PluginConfig


class UakinoClient:

    def __init__(self, config: PluginConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=15)

    async def get(self, url: str):
        r = await self.client.get(url)
        r.raise_for_status()
        return r.text

    async def post(self, url: str, data: dict):
        r = await self.client.post(url, data=data)
        r.raise_for_status()
        return r.text

    async def get_main(self, path: str, page: int):
        return await self.get(f"{path}{page}")

    async def search(self, query: str):
        return await self.post(
            self.config.base_url,
            {
                "do": "search",
                "subaction": "search",
                "story": query.replace(" ", "+"),
            }
        )

    async def get_playlist(self, news_id: str):
        url = (
            f"{self.config.base_url}/engine/ajax/playlists.php"
            f"?news_id={news_id}&xfield=playlist&time={int(time.time()*1000)}"
        )

        r = await self.client.get(url, headers=self.config.ajax_headers)
        r.raise_for_status()

        return r.json().get("response", "")

    async def get_player(self, url: str):
        r = await self.client.get(
            url,
            headers={"Referer": self.config.base_url}
        )
        r.raise_for_status()
        return r.text


class UakinoParser:

    def __init__(self, config: PluginConfig):
        self.config = config

    # -----------------------
    # MAIN
    # -----------------------
    def parse_main(self, html_text: str):
        tree = html.fromstring(html_text)

        elements = tree.xpath(
            "//div[contains(@class,'owl-item') or contains(@class,'movie-item')]"
        )

        result = []

        for el in elements:
            title = el.xpath(
                ".//a[contains(@class,'movie-title')]/text() | "
                ".//div[contains(@class,'full-movie-title')]/text()"
            )
            href = el.xpath(
                ".//a[contains(@class,'movie-title')]/@href | "
                ".//a[contains(@class,'full-movie')]/@href"
            )
            poster = el.xpath(".//img/@src")

            if not title or not href:
                continue

            link = href[0]

            if self.config.black_urls and \
               self.config.black_urls.search(link):
                continue

            result.append({
                "title": title[0].strip(),
                "url": link,
                "poster": poster[0] if poster else None
            })

        return result

    # -----------------------
    # PLAYER
    # -----------------------
    def parse_player(self, html_text: str):
        tree = html.fromstring(html_text)

        scripts = tree.xpath("//script/text()")

        links = []
        subs = []

        for script in scripts:
            if "Playerjs" not in script:
                continue

            file_match = self.config.file_regex.search(script)
            if file_match:
                links.append({
                    "source": "Player",
                    "url": file_match.group(1)
                })

            subs_match = self.config.subs_regex.search(script)
            if subs_match:
                subs.append({
                    "raw": subs_match.group(1)
                })
        return links, subs
