import sys
from pathlib import Path
from src.rag import get_vectorstore, build_rag_system

POLICIES_DIR = Path(__file__).parent / "Policies"
CHROMA_DIR = Path(__file__).parent / "chroma_db"


def main():
    print("=" * 65)
    print("  ISO Policies Knowledge Base RAG (LangChain + Gemini)")
    print("=" * 65)

    if not POLICIES_DIR.exists():
        print(f"Error: Policies directory not found at: {POLICIES_DIR}")
        sys.exit(1)

    # Check for --reindex flag
    force_reindex = "--reindex" in sys.argv
    cli_args = [arg for arg in sys.argv[1:] if arg != "--reindex"]

    # 1. Initialize or load the persistent vector database across all policies
    vectorstore = get_vectorstore(
        source_path=str(POLICIES_DIR),
        persist_directory=str(CHROMA_DIR),
        collection_name="iso_policies_all",
        force_reload=force_reindex,
        batch_size=50,
    )

    # 2. Build RAG system (retrieve top 5 relevant chunks across all policies)
    query_fn, _, _ = build_rag_system(
        vectorstore=vectorstore,
        model_name="gemini-3.6-flash",
        k=5,
    )

    # If question passed via CLI: python app.py "What is..."
    if cli_args:
        question = " ".join(cli_args)
        print(f"\n❓ Question: {question}\n")
        result = query_fn(question)
        print("💡 Answer:\n" + result["answer"])
        return

    # Sample cross-policy queries demonstrating retrieval across different policy files
    test_questions = [
        "What are the key rules and responsibilities for employees regarding security incident reporting?",
        "What is the company policy regarding the use of Generative AI tools?",
        "What are the requirements for password complexity and multi-factor authentication?",
    ]

    print("\n--- Running Demonstration Policy Queries ---")
    for question in test_questions:
        print(f"\n❓ Question: {question}\n")
        result = query_fn(question)
        print("💡 Answer:\n" + result["answer"])
        print("\n" + "-" * 65)


if __name__ == "__main__":
    main()
