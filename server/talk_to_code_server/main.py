from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from talk_to_code_server.api import router

load_dotenv()

app = FastAPI(
    title="Code-to-Blog API",
    description="API for generating blog posts from code repositories",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:3002",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


def main():
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("talk_to_code_server.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    main()
