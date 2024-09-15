import os
import asyncio
import argparse
from typing import List

from services import chunk_parsed_code
from services import traverse_codebase_from_path
from services import FAISSRetrievalSystem
from models import CodeLocation

INDEX_PATH = "faiss_index.idx"


async def index_repository(repo_path: str):
    try:
        print(f"Processing repository: {repo_path}")
        codebase_dict = await traverse_codebase_from_path(repo_path)
        print("Chunking")
        chunks = chunk_parsed_code(codebase_dict)
        print("Initializing FAISS retrieval system...")
        retrieval_system = FAISSRetrievalSystem(chunks)
        print("Retrieval system initialized")
        retrieval_system.save_index(INDEX_PATH)
        print("Repository indexed successfully")
    except Exception as e:
        print(f"Unexpected error in index_repository: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args}")


def query_codebase(query: str) -> List[CodeLocation]:
    try:
        if not os.path.exists(INDEX_PATH):
            print("No repository has been indexed yet")
            return []
        retrieval_system = FAISSRetrievalSystem(index_path=INDEX_PATH)
        results = retrieval_system.retrieve(query)
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(description="Local Code Search Tool")
    parser.add_argument("action", choices=["index", "query"], help="Action to perform")
    parser.add_argument("--path", help="Path to the repository for indexing")
    parser.add_argument("--query", help="Query to search in the codebase")

    args = parser.parse_args()

    if args.action == "index":
        if not args.path:
            print("Please provide a path to the repository for indexing")
            return
        asyncio.run(index_repository(args.path))
    elif args.action == "query":
        if not args.query:
            print("Please provide a query to search in the codebase")
            return
        results = query_codebase(args.query)
        for result in results:
            print(f"File: {result.file_path}")
            print(f"Lines: {result.start_line} - {result.end_line}")
            print(f"Score: {result.score}")
            print("---")


if __name__ == "__main__":
    main()
