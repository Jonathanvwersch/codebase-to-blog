import os
import requests


def traverse_codebase_from_url(repo_url):
    owner, repo = repo_url.split("/")[-2:]
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    def fetch_contents(path=""):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def process_item(item):
        if item["type"] == "file":
            file_url = item["download_url"]
            content_response = requests.get(file_url, headers=headers)
            if content_response.status_code == 200:
                return content_response.text
            else:
                return f"Error fetching file content: {content_response.status_code}"
        elif item["type"] == "dir":
            return traverse_directory(item["path"])
        else:
            return f"Unknown item type: {item['type']}"

    def traverse_directory(path: str = ""):
        contents = fetch_contents(path)
        return {item["name"]: process_item(item) for item in contents}

    return traverse_directory()
