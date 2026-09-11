# LangChain ISO Policies RAG Project

A Retrieval-Augmented Generation (RAG) system built with **LangChain**, **Google Gemini**, and **ChromaDB** to search and query across 25 ISO Information Security policy documents.

## Features

- **Multi-Document Indexing**: Automatically processes, chunks, and embeds all PDFs located in `Policies/`.
- **Persistent Vector Store**: Uses ChromaDB (`./chroma_db/`) to cache embeddings locally, eliminating repeated API requests and reducing latency.
- **Accurate Citations**: Answers cite the specific policy filename and page number for compliance and audit verification.
- **Zero-Hallucination Guardrail**: Strict prompting instructs the model not to speculate if a requirement is not covered in the policies.

---

## Setup

### 1. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Make sure your `GOOGLE_API_KEY` is set in `.env`:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## Usage

### Run Demonstration Queries
Runs sample queries across multiple policies:

```bash
python app.py
```

### Ask Custom Questions
Pass any question as a command-line argument:

```bash
python app.py "What are the rules regarding password and credential security?"
python app.py "What is the policy regarding the use of Generative AI tools?"
python app.py "Which policy describes how to report security incidents?"
```

### Force Re-indexing
To clear the cache and re-index the documents from scratch:

```bash
python app.py --reindex
```
