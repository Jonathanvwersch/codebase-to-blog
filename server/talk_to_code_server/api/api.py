# talk_to_code_server/api.py
import os
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from talk_to_code_server.services.traverse_codebase import traverse_codebase_from_url
from talk_to_code_server.services.chunk_codebase import chunk_parsed_code
from talk_to_code_server.services.retrievals import FAISSRetrievalSystem
from talk_to_code_server.services.query_ai import query_ai
from typing import List

router = APIRouter()


class IndexRepositoryRequest(BaseModel):
    repo_url: str


class IndexRepositoryResponse(BaseModel):
    message: str


class QueryRequest(BaseModel):
    query: str


class CodeLocation(BaseModel):
    file_path: str
    start_line: int
    end_line: int
    score: float


INDEX_PATH = "faiss_index.idx"


@router.post("/index", response_model=IndexRepositoryResponse)
async def index_repository(request: IndexRepositoryRequest):
    try:
        print(f"Processing repo URL: {request.repo_url}")
        codebase_dict = await traverse_codebase_from_url(request.repo_url)
        print("Chunking")
        chunks = await asyncio.to_thread(chunk_parsed_code, codebase_dict)
        print(f"Number of chunks: {len(chunks)}")
        print(f"Sample chunk: {chunks[0] if chunks else 'No chunks'}")
        print("Initializing FAISS retrieval system...")
        retrieval_system = FAISSRetrievalSystem(chunks)
        print("Retrieval system initialized")
        retrieval_system.save_index(INDEX_PATH)
        return {"message": "Repository indexed successfully"}
    except Exception as e:
        print(f"Unexpected error in index_repository: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=List[CodeLocation])
async def query_codebase(request: QueryRequest):
    try:
        if not os.path.exists(INDEX_PATH):
            raise HTTPException(
                status_code=400, detail="No repository has been indexed yet"
            )
        retrieval_system = FAISSRetrievalSystem(index_path=INDEX_PATH)
        results = await asyncio.to_thread(retrieval_system.retrieve, request.query)
        print("----------")
        print(results)
        return [CodeLocation(**result) for result in results]
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
