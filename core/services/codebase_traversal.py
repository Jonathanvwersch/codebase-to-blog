import os
import gitmatch
import aiofiles
import asyncio
from typing import Dict

DEFAULT_IGNORE_PATTERNS = [
    ".git",
    "__pycache__",
    ".next",
    "pnpm-workspace.yaml",
    "*.pyc",
    "*.pyo",
    ".venv",
    "*.swp",
    "*.swo",
    "dist",
    "LICENSE",
    "*.DS_Store",
    "*.lock",
    "*.log",
    "*.tsbuildinfo",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "yarn-error.log",
    ".turbo",
    ".tsbuildinfo",
    "**/dist/**/*",
    "node_modules/**",
]


def parse_gitignore(repo_path: str, base_path: str = "") -> list:
    gitignore_path = os.path.join(repo_path, ".gitignore")
    if not os.path.exists(gitignore_path):
        return []
    with open(gitignore_path, "r") as f:
        patterns = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]
        return [os.path.join(base_path, pattern) for pattern in patterns]


def should_ignore(path: str, ignore_patterns: list) -> bool:
    matcher = gitmatch.compile(ignore_patterns)
    return bool(matcher.match(path))


async def traverse_codebase_from_path(repo_path: str) -> Dict[str, str]:
    codebase_dict = {}
    ignore_patterns = DEFAULT_IGNORE_PATTERNS.copy()
    ignore_patterns.extend(parse_gitignore(repo_path))

    async def process_file(file_path, relative_path):
        if should_ignore(relative_path, ignore_patterns):
            return

        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                codebase_dict[relative_path] = content
        except UnicodeDecodeError:
            print(f"Skipping binary file: {file_path}")
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")

    tasks = []
    for root, _, files in os.walk(repo_path):
        if ".gitignore" in files:
            relative_path = os.path.relpath(root, repo_path)
            ignore_patterns.extend(parse_gitignore(root, relative_path))

        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, repo_path)
            tasks.append(process_file(file_path, relative_path))

    await asyncio.gather(*tasks)
    return codebase_dict
