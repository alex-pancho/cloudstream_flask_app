from typing import List
from core.models import Repository, Plugin
from core.repo_fetcher import RepoFetcher


class RepoManager:

    def __init__(self, fetcher: RepoFetcher | None = None):
        self.fetcher = fetcher or RepoFetcher()
        self.repositories: List[Repository] = []

    # --- PUBLIC API ---

    def add_repository(self, url: str) -> dict:
        if "github.com" in url and "raw" not in url:
            url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
            url = url + "/refs/heads/master/repo.json"
        try:
            repository = self._build_repository(url)
            self.repositories.append(repository)
            return self._serialize_repository(repository)

        except Exception as e:
            return {"error": f"Failed to scan repo: {str(e)}"}

    def get_all_plugins(self) -> List[dict]:
        return [
            self._serialize_plugin(plugin)
            for repo in self.repositories
            for plugin in repo.plugins
        ]

    # --- INTERNAL LOGIC ---

    def _build_repository(self, url: str) -> Repository:
        manifest = self.fetcher.fetch_repo_manifest(url)

        repo_name = manifest.get("name", "Unknown Repo")
        plugin_list_urls = manifest.get("pluginLists", [])

        plugins = self._collect_plugins(repo_name, plugin_list_urls)

        return Repository(
            name=repo_name,
            url=url,
            plugins=plugins
        )

    def _collect_plugins(
        self,
        repo_name: str,
        plugin_list_urls: List[str]
    ) -> List[Plugin]:

        plugins: List[Plugin] = []

        for list_url in plugin_list_urls:
            plugin_dicts = self.fetcher.fetch_plugin_list(list_url)

            for data in plugin_dicts:
                plugins.append(
                    Plugin(
                        name=data.get("name", "Unknown"),
                        version=data.get("version"),
                        url=data.get("url"),
                        repo_name=data.get("description", "Unknown"),
                    )
                )

        return plugins

    # --- SERIALIZATION ---

    def _serialize_repository(self, repo: Repository) -> dict:
        return {
            "name": repo.name,
            "url": repo.url,
            "plugins": [
                self._serialize_plugin(p)
                for p in repo.plugins
            ]
        }

    def _serialize_plugin(self, plugin: Plugin) -> dict:
        return {
            "name": plugin.name,
            "version": plugin.version,
            "url": plugin.url,
            "repo_name": plugin.repo_name
        }