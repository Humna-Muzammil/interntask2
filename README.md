# Advanced AI Productivity Assistant

Features:
- PDF, TXT, and DOCX text extraction
- Chunking with source/page/section metadata
- OpenAI embeddings persisted in ChromaDB
- Retrieval-augmented document Q&A with citations
- Explicit fallback when uploaded documents do not verify an answer
- SQLite conversation history, reopening, and recent-message context
- Model-selected tools: document retrieval, arithmetic calculator, workflow planner
- Workflow planning without claiming external actions were executed

## Setup

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
5. Run:

   ```bash
   streamlit run app.py
   ```

The first run creates `chat_history.db` and `chroma_db/` in the working directory.

## Notes / limitations

- The example uses character-based chunking for clarity; production systems should consider token-based chunking and reranking.
- PDF page numbers are retained. DOCX uses heading/section labels because DOCX does not have reliable fixed page numbers.
- Scanned PDFs need OCR, which is not included.
- File replacement is keyed by filename; use unique filenames if unrelated documents share a name.
- Local SQLite and Chroma files are not encrypted. Do not use this demo for confidential data without appropriate security controls.
- Workflow automation currently creates plans, not external side effects. Integrate and permission-check specific APIs before automating email, calendar, or other actions.
- Protect the `.env` file and never commit API keys.
