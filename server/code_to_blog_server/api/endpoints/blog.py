from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from code_to_blog_server.services.traverse_codebase import traverse_codebase_from_url
from code_to_blog_server.services.chunk_codebase import chunk_parsed_code
from code_to_blog_server.services.create_embeddings import create_embeddings
from code_to_blog_server.services.retrievals import RetrievalSystem
from code_to_blog_server.services.generate_blog import generate_blog_content

router = APIRouter()

class RepositoryRequest(BaseModel):
    repo_url: str
    background: str
    topic: str
    word_count: int
    writing_style: str

class BlogResponse(BaseModel):
    blog_content: str

@router.post("/generate_blog", response_model=BlogResponse)
async def generate_blog_post(request: RepositoryRequest):
    try:
        print("Starting blog generation")
        # Extract codebase information from the repository URL
        print(f"Processing repo URL: {request.repo_url}")
        codebase_dict = traverse_codebase_from_url(request.repo_url)
        print(f"Codebase dict: {codebase_dict}")
        
        # Split the code into manageable chunks
        chunks = chunk_parsed_code(codebase_dict)
        print(f"Chunks: {chunks}")

        # Create embeddings for the code chunks
        embeddings = create_embeddings(chunks)
        print(f"Embeddings: {embeddings}")

        # Initialize the retrieval system
        retrieval_system = RetrievalSystem(chunks, embeddings)
        print("Retrieval system initialized")

        # Retrieve relevant chunks based on the background (query) provided
        relevant_chunks = retrieval_system.retrieve(request.background)
        print(f"Relevant chunks: {relevant_chunks}")

        # Generate blog content using the provided parameters and relevant code chunks
        blog_content = generate_blog_content(
            request.topic,
            request.background,
            request.word_count,
            request.writing_style,
            relevant_chunks,
        )
        print(f"Blog content: {blog_content}")

        if not blog_content:
            raise HTTPException(status_code=500, detail="Failed to generate blog content")
        return {"blog_content": blog_content}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
