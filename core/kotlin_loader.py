import re
from pathlib import Path

import httpx
from core.models import PluginConfig


class KotlinPluginLoader:

    STRING_RE = r'"(.*?)"'

    BASE_URL_RE = re.compile(r'override var mainUrl = ' + STRING_RE)
    NAME_RE = re.compile(r'override var name = ' + STRING_RE)
    LANG_RE = re.compile(r'override var lang = ' + STRING_RE)
    DESC_RE = re.compile(r'override var description = ' + STRING_RE)

    BLACK_URL_RE = re.compile(r'val blackUrls = ' + STRING_RE)

    FILE_REGEX_RE = re.compile(r'val fileRegex = ' + STRING_RE + r'\.toRegex')
    SUBS_REGEX_RE = re.compile(r'val subsRegex = ' + STRING_RE + r'\.toRegex')

    MAIN_PAGE_RE = re.compile(r'\$mainUrl(.*?)"\s+to\s+"(.*?)"')

    HAS_MAIN_RE = re.compile(r'override var hasMainPage = (true|false)')
    SEQ_MAIN_RE = re.compile(r'override var sequentialMainPage = (true|false)')

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(timeout=10)

    def _safe(self, regex, content, default=None):
        match = regex.search(content)
        return match.group(1) if match else default

    def load(self, file_path: str) -> PluginConfig:
        content = self._read_source(file_path)

        base_url = self._safe(self.BASE_URL_RE, content)
        name = self._safe(self.NAME_RE, content)
        lang = self._safe(self.LANG_RE, content)
        description = self._safe(self.DESC_RE, content)

        black_urls = self._safe(self.BLACK_URL_RE, content, "")

        file_regex_raw = self._safe(self.FILE_REGEX_RE, content)
        subs_regex_raw = self._safe(self.SUBS_REGEX_RE, content)

        has_main = self._safe(self.HAS_MAIN_RE, content, "true") == "true"
        sequential = self._safe(self.SEQ_MAIN_RE, content, "false") == "true"

        main_pages = {}
        for path, page_name in self.MAIN_PAGE_RE.findall(content):
            main_pages[base_url + path] = page_name

        return PluginConfig(
            name=name,
            lang=lang,
            description=description,
            base_url=base_url,
            black_urls=black_urls,
            file_regex=re.compile(file_regex_raw) if file_regex_raw else None,
            subs_regex=re.compile(subs_regex_raw) if subs_regex_raw else None,
            main_pages=main_pages,
            has_main_page=has_main,
            sequential_main_page=sequential,
            headers={
                "Referer": base_url,
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0",
            },
        )

    def _read_source(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            response = self.client.get(path)
            response.raise_for_status()
            return response.text
        else:
            return Path(path).read_text(encoding="utf-8")
