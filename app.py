from flask import Flask, jsonify, request
from flask import render_template
from core.repo_manager import RepoManager
from core.plugin_executor import PluginExecutor, PluginFactory
from core.stream_cache_service import StreamCacheService



factory = PluginFactory()
cache_service = StreamCacheService()
repo_manager = RepoManager()

app = Flask(__name__)


@app.route('/api/repo/add', methods=['POST'])
def add_repo():
    data = request.json
    repo_url = data.get('url')
    if not repo_url:
        return jsonify({"error": "URL is required"}), 400
    
    result = repo_manager.add_repository(repo_url)
    return jsonify(result)


@app.route("/api/repo/list", methods=["GET"])
def list_repos():
    return jsonify(repo_manager.list_repositories())


@app.route("/api/repo/delete/<int:repo_id>", methods=["DELETE"])
def delete_repo(repo_id):
    return jsonify(repo_manager.delete_repository(repo_id))


@app.route('/api/plugins', methods=['GET'])
def list_plugins():
    return jsonify(repo_manager.get_all_plugins())


@app.route('/plugins')
def plugins():
    return render_template('repo.html')


@app.route("/api/scan_plugins", methods=["GET"])
def scan_plugins():
    plugins = repo_manager.get_all_plugins()

    for plugin in plugins:
        executor: PluginExecutor = factory.create_executor(plugin["name"])
        movies = executor.get_first_movies(plugin)
        cache_service.save_movies(plugin["name"], movies)

    return jsonify(cache_service.get_all())

if __name__ == '__main__':
    app.run(
        debug=True,
        port=80
    )
