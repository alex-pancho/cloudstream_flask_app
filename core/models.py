from dataclasses import dataclass
from typing import Dict, List
import re


@dataclass
class Plugin:
    name: str
    version: int | None
    url: str | None
    description: str


@dataclass
class Repository:
    name: str
    url: str
    plugins: List[Plugin]


@dataclass
class PluginConfig:
    base_url: str
    black_urls: str
    file_regex: re.Pattern
    subs_regex: re.Pattern
    main_pages: Dict[str, str]
    headers: Dict[str, str]