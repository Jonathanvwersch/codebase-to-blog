import os
import warnings
from dotenv import load_dotenv
from codebase_parser import traverse_codebase_from_url
from chunk_parsed_codebase import chunk_parsed_code
from create_embeddings import create_embeddings
from retrievals import RetrievalSystem
from generate_blog import generate_blog_content

warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()


def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY is not set in the environment variables.")
        print("Please make sure you have a .env file with the OPENAI_API_KEY.")
        return

    repo_url = "https://github.com/Jonathanvwersch/frontend-monorepo-boilerplate"

    try:
        print("Traversing the codebase...")
        codebase_dict = traverse_codebase_from_url(repo_url)

        print("Chunking the codebase...")
        chunks = chunk_parsed_code(codebase_dict)

        print("Creating embeddings...")
        embeddings = create_embeddings(chunks)

        print("Setting up retrieval system...")
        retrieval_system = RetrievalSystem(chunks, embeddings)

        query = "What are the limitations of tsup that parts of this codebase seek to resolve"
        print(f"Generating a blog post for this query: {query}")
        relevant_chunks = retrieval_system.retrieve(query)
        blog_content = generate_blog_content(query, relevant_chunks)

        if blog_content:
            print("\nGenerated Blog Content:")
            print(blog_content)
        else:
            print("Failed to generate blog content.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
