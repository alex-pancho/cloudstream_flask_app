import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Plugin:
    repository_id: int
    name: str
    version: int | None
    description: str | None
    kt_url: str | None
    base_url: str | None
    created_at: Optional[str] = None
    _id: Optional[int] = None


@dataclass
class Repository:
    name: str
    url: str
    plugins: List[Plugin]
    _id: Optional[int] = None


@dataclass
class PluginConfig:
    # --- basic meta ---
    name: Optional[str] = None
    lang: Optional[str] = None
    description: Optional[str] = None
    # --- base ---
    base_url: str = ""
    black_urls: Optional[str] = None
    # --- regex ---
    file_regex: Optional[re.Pattern] = None
    subs_regex: Optional[re.Pattern] = None
    # --- main page ---
    main_pages: Dict[str, str] = field(default_factory=dict)
    has_main_page: bool = True
    sequential_main_page: bool = False
    # --- networking ---
    headers: Dict[str, str] = field(default_factory=dict)
