from flask import Flask, jsonify, request
from flask import render_template
from core.repo_manager import RepoManager

app = Flask(__name__)
repo_manager = RepoManager()

@app.route('/api/repo/add', methods=['POST'])
def add_repo():
    data = request.json
    repo_url = data.get('url')
    if not repo_url:
        return jsonify({"error": "URL is required"}), 400
    
    result = repo_manager.add_repository(repo_url)
    return jsonify(result)

@app.route('/api/plugins', methods=['GET'])
def list_plugins():
    return jsonify(repo_manager.get_all_plugins())


@app.route('/plugins')
def plugins():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
