import os
import requests
from dotenv import load_dotenv

load_dotenv()


def traverse_codebase_from_url(repo_url):
    """
    Traverses a public GitHub repo and creates a nested dictionary representing the structure.
    Uses a Personal Access Token from .env file for authentication.

    Args:
    repo_url: The URL of the Github repository

    Returns:
    dict: A nested dictionary representing the repository structure
    """
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

    try:
        repo_structure = traverse_codebase_from_url(
            "https://github.com/Jonathanvwersch/ai-community-notes"
        )
        print(repo_structure)
    except requests.exceptions.HTTPError as e:
        print(f"An HTTP error occurred: {e}")
        if e.response.status_code == 403 and "rate limit exceeded" in str(e).lower():
            print(
                "You've hit the GitHub API rate limit. Check your GITHUB_TOKEN in the .env file."
            )
    except Exception as e:
        print(f"An error occurred: {e}")
