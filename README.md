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

### 🌐 Web Interface (Recommended)
Launch the interactive web application:

```bash
python server.py
```

Then open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

The interface includes:
- An intuitive dark-mode interface with instant question chips.
- Markdown rendering for policy quotes and requirements.
- Verified document and page-level citation badges for every answer.
- An interactive catalog modal to browse all 25 indexed policy documents.

> For detailed start/stop commands, background execution, and troubleshooting, see [HowToRunServer.md](HowToRunServer.md).

---

### 💻 Command-Line Interface (CLI)
You can also ask questions directly in your terminal:

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
