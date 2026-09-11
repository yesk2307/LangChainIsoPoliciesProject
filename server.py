import os
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.rag import get_vectorstore, build_rag_system

BASE_DIR = Path(__file__).parent
POLICIES_DIR = BASE_DIR / "Policies"
CHROMA_DIR = BASE_DIR / "chroma_db"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="ISO Policies RAG API",
    description="Interactive knowledge assistant for ISO compliance policy documents",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG engine reference
rag_query_fn = None


@app.on_event("startup")
def startup_event():
    """Load the persistent vector store and compile the RAG engine on startup."""
    global rag_query_fn
    print("Initializing ISO Policies Vector Store...")
    vectorstore = get_vectorstore(
        source_path=str(POLICIES_DIR),
        persist_directory=str(CHROMA_DIR),
        collection_name="iso_policies_all",
    )
    query_fn, _, _ = build_rag_system(
        vectorstore=vectorstore,
        model_name="gemini-3.6-flash",
        k=5,
    )
    rag_query_fn = query_fn
    print("ISO Policies RAG engine ready!")


class QueryRequest(BaseModel):
    question: str


class SourceItem(BaseModel):
    policy: str
    page: int
    snippet: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceItem]


@app.post("/api/query", response_model=QueryResponse)
def query_policy(req: QueryRequest):
    """Execute a RAG query over the ISO compliance policies."""
    global rag_query_fn
    if not rag_query_fn:
        raise HTTPException(status_code=503, detail="RAG system is still initializing")

    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = rag_query_fn(question)
        sources = []
        for doc in result.get("source_documents", []):
            sources.append(
                SourceItem(
                    policy=doc.metadata.get("source", "Document"),
                    page=doc.metadata.get("page", 0) + 1,
                    snippet=doc.page_content.strip()[:350],
                )
            )

        return QueryResponse(
            question=question,
            answer=result["answer"],
            sources=sources,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/policies")
def list_policies() -> List[Dict[str, Any]]:
    """Return the catalog of all available ISO policy documents."""
    policies = []
    if POLICIES_DIR.exists():
        for f in sorted(POLICIES_DIR.glob("*.pdf")):
            policies.append({
                "filename": f.name,
                "title": f.stem,
                "size_kb": round(f.stat().st_size / 1024, 1),
            })
    return policies


# Serve static frontend files
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_home():
    """Serve the web application frontend."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "ISO Policies RAG API is running. Place index.html in static/"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
