import os
import asyncio
import aiohttp
import base64
from pathlib import Path
from fnmatch import fnmatch
from cachetools import TTLCache
from aiolimiter import AsyncLimiter


async def traverse_codebase_from_url(repo_url):
    owner, repo = repo_url.split("/")[-2:]
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"} if token else {}

    # Create a cache with a 1-hour TTL and a maximum of 1000 items
    cache = TTLCache(maxsize=1000, ttl=3600)

    # Create a rate limiter (5000 requests per hour is GitHub's limit)
    limiter = AsyncLimiter(5000, 3600)

    async def fetch_contents(session, path=""):
        cache_key = f"contents:{path}"
        if cache_key in cache:
            return cache[cache_key]

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        async with limiter:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
        cache[cache_key] = data
        return data

    async def fetch_gitignore(session):
        try:
            gitignore_content = await fetch_file_content(session, ".gitignore")
            return parse_gitignore(gitignore_content)
        except aiohttp.ClientResponseError:
            return []  # Return an empty list if .gitignore doesn't exist

    def parse_gitignore(content):
        patterns = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)

        return patterns

    def should_ignore(path, gitignore_patterns):
        path = Path(path)

        # List of common lock files to ignore
        lock_files = [
            "package-lock.json",
            "yarn.lock",
            "Gemfile.lock",
            "Cargo.lock",
            "composer.lock",
            "poetry.lock",
            "Pipfile.lock",
            "pnpm-lock.yaml",
        ]

        # Check if the file is a lock file
        if path.name in lock_files:
            return True

        # Check if the file matches any gitignore pattern
        for pattern in gitignore_patterns:
            if fnmatch(str(path), pattern) or fnmatch(str(path.name), pattern):
                return True

        return False

    async def fetch_file_content(session, path):
        cache_key = f"file:{path}"
        if cache_key in cache:
            return cache[cache_key]

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        async with limiter:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                content = await response.json()

        if isinstance(content, dict) and "content" in content:
            decoded_content = base64.b64decode(content["content"])
            try:
                result = decoded_content.decode("utf-8")
            except UnicodeDecodeError:
                result = (
                    f"[Binary content] - {path} - Size: {len(decoded_content)} bytes"
                )
        else:
            raise ValueError(f"Unexpected response format for file: {path}")

        cache[cache_key] = result
        return result

    async def process_item(session, item, gitignore_patterns):
        if should_ignore(item["path"], gitignore_patterns):
            return None
        if item["type"] == "file":
            try:
                return await fetch_file_content(session, item["path"])
            except aiohttp.ClientResponseError as e:
                return f"Error fetching file content: {e}"
        elif item["type"] == "dir":
            return await traverse_directory(session, item["path"], gitignore_patterns)
        else:
            return f"Unknown item type: {item['type']}"

    async def traverse_directory(session, path: str = "", gitignore_patterns=None):
        if gitignore_patterns is None:
            gitignore_patterns = await fetch_gitignore(session)
        contents = await fetch_contents(session, path)
        tasks = []
        for item in contents:
            if not should_ignore(item["path"], gitignore_patterns):
                tasks.append(process_item(session, item, gitignore_patterns))
        results = await asyncio.gather(*tasks)
        return {
            item["name"]: result
            for item, result in zip(contents, results)
            if result is not None
        }

    async with aiohttp.ClientSession() as session:
        return await traverse_directory(session)
