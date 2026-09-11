import os
import time
import warnings
from pathlib import Path
from typing import Dict, Any, List

# Suppress minor version and SSL warning messages
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()


def get_api_key() -> str:
    """Retrieve and validate the Google API Key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is not set. Please set it in your .env file.")
    return api_key


def get_vectorstore(
    source_path: str,
    persist_directory: str = "./chroma_db",
    collection_name: str = "iso_policies_all",
    force_reload: bool = False,
    batch_size: int = 50,
) -> Chroma:
    """
    Initializes or loads a persistent Chroma vector store.
    Accepts either a single PDF file path or a directory containing multiple PDF files.
    If persist_directory exists and contains data (and force_reload is False),
    it directly loads the stored vector database to save API calls.
    """
    api_key = get_api_key()
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key,
    )

    persist_path = Path(persist_directory)

    # Check if existing database collection exists
    if not force_reload and persist_path.exists() and any(persist_path.iterdir()):
        print(f"Loading existing vector store from: {persist_directory}")
        return Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(persist_path),
        )

    target_path = Path(source_path)
    if not target_path.exists():
        raise FileNotFoundError(f"Path does not exist: {source_path}")

    # Gather PDF files
    if target_path.is_dir():
        pdf_files = sorted(list(target_path.glob("*.pdf")))
        print(f"Found {len(pdf_files)} PDF policies to index in '{target_path.name}/'")
    else:
        pdf_files = [target_path]
        print(f"Indexing single policy file: {target_path.name}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""],
    )

    all_chunks = []
    total_pages = 0

    for pdf in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf))
            docs = loader.load()
            total_pages += len(docs)
            for d in docs:
                # Ensure clean filename metadata
                d.metadata["source"] = pdf.name
                d.metadata["policy_name"] = pdf.stem
            chunks = text_splitter.split_documents(docs)
            all_chunks.extend(chunks)
        except Exception as err:
            print(f"⚠️ Error reading {pdf.name}: {err}")

    print(f"Extracted {len(all_chunks)} chunks across {total_pages} total pages.")

    # Initialize Chroma store
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_path),
    )

    # Batch insert with automatic backoff to respect API rate limits
    total_chunks = len(all_chunks)
    print(f"Embedding and persisting {total_chunks} chunks in batches of {batch_size}...")
    
    for i in range(0, total_chunks, batch_size):
        batch = all_chunks[i : i + batch_size]
        max_retries = 6
        for attempt in range(max_retries):
            try:
                vectorstore.add_documents(batch)
                print(f"  Indexed chunks {i + 1} to {min(i + batch_size, total_chunks)} / {total_chunks}")
                # Brief sleep between batches to avoid hitting rate limits
                time.sleep(2)
                break
            except Exception as e:
                err_str = str(e)
                if any(phrase in err_str for phrase in ["429", "Quota exceeded", "ResourceExhausted"]):
                    wait_seconds = 20 + (attempt * 10)
                    print(f"  ⏳ Free-tier rate limit reached. Waiting {wait_seconds}s before retrying batch {i + 1}...")
                    time.sleep(wait_seconds)
                else:
                    raise e
        else:
            raise RuntimeError(f"Failed to index batch starting at chunk {i + 1} after {max_retries} attempts.")

    print(f"✅ All {total_chunks} policy chunks successfully indexed and saved to: {persist_directory}")
    return vectorstore


def format_docs_with_sources(docs) -> str:
    """Format retrieved document chunks with citation information."""
    formatted_chunks = []
    for doc in docs:
        page_num = doc.metadata.get("page", 0) + 1  # 1-indexed page number
        source_name = doc.metadata.get("source") or Path(doc.metadata.get("file_path", "document")).name
        header = f"[Policy Document: {source_name} | Page: {page_num}]"
        formatted_chunks.append(f"{header}\n{doc.page_content.strip()}")
    return "\n\n".join(formatted_chunks)


def build_rag_system(
    vectorstore: Chroma,
    model_name: str = "gemini-3.6-flash",
    k: int = 4,
):
    """Builds a LangChain LCEL RAG chain over the vector store."""
    api_key = get_api_key()
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        google_api_key=api_key,
    )

    prompt_template = """You are a compliance and security expert assistant analyzing an official ISO Information Security Policy.
Answer the user's question accurately and strictly based on the provided policy context below.

Rules:
1. Base your answer ONLY on the provided context. If the policy does not state or cover the answer, state: "This information is not covered in the provided policy document." Do not speculate or invent policies.
2. Always cite the specific page numbers (e.g. "[Page 3]") where the policy requirements are found.
3. Present your answer clearly using concise bullet points where appropriate.

Context:
{context}

Question:
{question}

Answer:"""

    prompt = PromptTemplate.from_template(prompt_template)

    # Standard LCEL chain
    chain = (
        {
            "context": retriever | format_docs_with_sources,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    def query(question: str) -> Dict[str, Any]:
        """Query the RAG pipeline and return both the answer and the source documents."""
        source_docs = retriever.invoke(question)
        answer = chain.invoke(question)
        return {
            "question": question,
            "answer": answer,
            "source_documents": source_docs,
        }

    return query, chain, retriever
