import httpx
from typing import List, Dict


class RepoFetcher:

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(timeout=10)

    def fetch_repo_manifest(self, url: str) -> Dict:
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def fetch_plugin_list(self, url: str) -> List[Dict]:
        response = self.client.get(url)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list):
            raise ValueError("plugins.json must return a list")

        return data