import re
from pathlib import Path
from core.models import PluginConfig


class KotlinPluginLoader:

    BASE_URL_RE = re.compile(r'override var mainUrl = "(.*?)"')
    BLACK_URL_RE = re.compile(r'val blackUrls = "(.*?)"')
    FILE_REGEX_RE = re.compile(r'val fileRegex = "(.*?)"\.toRegex')
    SUBS_REGEX_RE = re.compile(r'val subsRegex = "(.*?)"\.toRegex')

    MAIN_PAGE_RE = re.compile(r'\$mainUrl(.*?)"\s+to\s+"(.*?)"')

    def load(self, file_path: str) -> PluginConfig:
        content = Path(file_path).read_text(encoding="utf-8")

        base_url = self.BASE_URL_RE.search(content).group(1)
        black_urls = self.BLACK_URL_RE.search(content).group(1)

        file_regex_raw = self.FILE_REGEX_RE.search(content).group(1)
        subs_regex_raw = self.SUBS_REGEX_RE.search(content).group(1)

        main_pages = {}
        for path, name in self.MAIN_PAGE_RE.findall(content):
            main_pages[base_url + path] = name

        return PluginConfig(
            base_url=base_url,
            black_urls=black_urls,
            file_regex=re.compile(file_regex_raw),
            subs_regex=re.compile(subs_regex_raw),
            main_pages=main_pages,
            headers={
                "Referer": base_url,
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0",
            },
        )
