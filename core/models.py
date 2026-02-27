from dataclasses import dataclass
from typing import List


@dataclass
class Plugin:
    name: str
    version: int | None
    url: str | None
    repo_name: str


@dataclass
class Repository:
    name: str
    url: str
    plugins: List[Plugin]
