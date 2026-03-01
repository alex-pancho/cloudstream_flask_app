from typing import List
from core.models import Repository, Plugin
from core.repo_fetcher import RepoFetcher
from core.database import db


class RepoManager:

    def __init__(self, fetcher: RepoFetcher | None = None):
        self.fetcher = fetcher or RepoFetcher()
        self.repositories: List[Repository] = []
        self._load_from_db()

    # ------------------------
    # PUBLIC API
    # ------------------------

    def add_repository(self, url: str) -> dict:
        url = self._normalize_github_url(url)

        try:
            repository = self._build_repository(url)

            # Зберігаємо в БД
            db.repositories.insert(
                name=repository.name,
                url=repository.url
            )
            db.commit()

            self.repositories.append(repository)

            return self._serialize_repository(repository)

        except Exception as e:
            return {"error": f"Failed to scan repo: {str(e)}"}

    def delete_repository(self, repo_id: int) -> dict:
        row = db.repositories(repo_id)
        if not row:
            return {"error": "Repository not found"}

        db(db.repositories.id == repo_id).delete()
        db.commit()

        # Видаляємо з пам'яті
        self.repositories = [
            r for r in self.repositories if r.url != row.url
        ]

        return {"status": "deleted"}

    def get_all_plugins(self) -> List[dict]:
        return [
            self._serialize_plugin(plugin)
            for repo in self.repositories
            for plugin in repo.plugins
        ]

    def list_repositories(self) -> List[dict]:
        return [
            {
                "id": row.id,
                "name": row.name,
                "url": row.url
            }
            for row in db(db.repositories).select()
        ]

    # ------------------------
    # INIT LOAD
    # ------------------------

    def _load_from_db(self):
        rows = db(db.repositories).select()

        for row in rows:
            try:
                repository = self._build_repository(row.url)
                self.repositories.append(repository)
            except:
                continue  # not validate server

    # ------------------------
    # INTERNAL LOGIC
    # ------------------------

    def _normalize_github_url(self, url: str) -> str:
        if "github.com" in url and "raw" not in url:
            url = url.replace("github.com", "raw.githubusercontent.com") \
                     .replace("/blob/", "/")
            url = url + "/refs/heads/master/repo.json"
        return url

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
                        description=data.get("description", "Unknown"),
                    )
                )

        return plugins

    # ------------------------
    # SERIALIZATION
    # ------------------------

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
            "description": plugin.description
        }
