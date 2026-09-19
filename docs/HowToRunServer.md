# Server Instructions — ISO Policies RAG System

This guide explains how to start, stop, and manage the **ISO Policies RAG Web Application**.

---

## 1. Prerequisites

Before starting the server, ensure:
1. The virtual environment (`.venv`) is set up.
2. Your `GOOGLE_API_KEY` is configured in the `.env` file:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

---

## 2. How to Run the Server

### Standard Way (Recommended)

Open your terminal in the project root directory and run:

```bash
# Step 1: Activate the virtual environment
source .venv/bin/activate

# Step 2: Start the server
python server.py
```

Once started, open your web browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)** (or [http://127.0.0.1:8000](http://127.0.0.1:8000))

---

### One-Line Way (Without Activating Venv Manually)

You can run the server directly using the virtual environment's Python interpreter:

```bash
./.venv/bin/python server.py
```

---

### Development Mode (Auto-Reload on Code Changes)

If you are modifying Python files and want the server to reload automatically on save:

```bash
source .venv/bin/activate
uvicorn server:app --reload --port 8000
```

---

## 3. How to Stop the Server

### If Running in the Foreground (Normal Terminal Window)

Simply press:
```text
Ctrl + C
```

---

### If Running in the Background (or Port 8000 is Busy)

If the server was started in the background or terminal was closed without stopping it, free port 8000 with:

```bash
lsof -ti:8000 | xargs kill -9
```

Or stop it by process name:

```bash
pkill -f "server.py"
```

---

## 4. Verification & Status Checks

### Check if the Server is Running

Run the following command to check if any process is listening on port 8000:

```bash
lsof -i :8000
```

* **If active**: You will see a line like `Python ... (LISTEN)`.
* **If stopped**: The command returns no output.

---

## 5. Common Issues & Troubleshooting

### Issue: `zsh: command not found: python`
* **Why**: On macOS, the system Python command is `python3`, and `python` only becomes available when the virtual environment is activated.
* **Fix**: Run `source .venv/bin/activate` before running `python server.py`, or use `./.venv/bin/python server.py`.

### Issue: `[Errno 48] Address already in use`
* **Why**: Another process (or a previous server instance) is already using port 8000.
* **Fix**: Run `lsof -ti:8000 | xargs kill -9` to terminate the existing process, then start the server again.

### Issue: `GOOGLE_API_KEY is not set`
* **Why**: The `.env` file is missing or `GOOGLE_API_KEY` is commented out with a `#`.
* **Fix**: Open `.env` and verify your API key is uncommented:
  ```env
  GOOGLE_API_KEY=your_actual_key_here
  ```

---

## 6. Running Queries via CLI (Without Web Server)

You can also ask policy questions directly in the terminal without running the web server:

```bash
source .venv/bin/activate
python app.py "What are the rules regarding password complexity?"
```
