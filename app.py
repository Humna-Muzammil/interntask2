import os
import tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from database import (
    init_db, create_conversation, list_conversations,
    get_messages, add_message, rename_conversation
)
from rag.vector_store import ingest_file
from assistant import answer

st.set_page_config(page_title="AI Productivity Assistant", page_icon="🤖", layout="wide")
init_db()

st.title("🤖 AI Productivity Assistant")
st.caption("RAG document Q&A · Persistent chat memory · Tool selection · Workflow planning")

if not os.getenv("OPENAI_API_KEY"):
    st.warning("Set OPENAI_API_KEY in your .env file, then restart the app.")

with st.sidebar:
    st.header("Conversations")
    if st.button("＋ New conversation", use_container_width=True):
        st.session_state.conversation_id = create_conversation()
        st.rerun()

    conversations = list_conversations()
    if conversations:
        labels = {row["id"]: f'{row["title"]} (#{row["id"]})' for row in conversations}
        ids = [row["id"] for row in conversations]
        current = st.session_state.get("conversation_id")
        index = ids.index(current) if current in ids else 0
        selected_id = st.selectbox(
            "Open previous conversation",
            ids,
            index=index,
            format_func=lambda cid: labels[cid]
        )
        st.session_state.conversation_id = selected_id
    else:
        st.session_state.conversation_id = create_conversation()
        st.rerun()

    st.divider()
    st.header("Upload documents")
    uploads = st.file_uploader(
        "PDF, TXT, or DOCX",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True
    )
    if st.button("Index uploaded files", use_container_width=True, disabled=not uploads):
        progress = st.empty()
        total_chunks = 0
        for uploaded in uploads:
            suffix = Path(uploaded.name).suffix.lower()
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded.getvalue())
                    tmp_path = tmp.name
                try:
                    count = ingest_file(tmp_path)
                    total_chunks += count
                    progress.success(f"Indexed {uploaded.name}: {count} chunks")
                finally:
                    Path(tmp_path).unlink(missing_ok=True)
            except Exception as exc:
                progress.error(f"Could not index {uploaded.name}: {exc}")
        st.info(f"Finished indexing. Total chunks processed: {total_chunks}")

conversation_id = st.session_state.conversation_id
stored = get_messages(conversation_id)

# Display persistent messages.
for row in stored:
    with st.chat_message(row["role"]):
        st.markdown(row["content"])

prompt = st.chat_input("Ask about your documents, calculate something, or plan a workflow…")
if prompt:
    add_message(conversation_id, "user", prompt)
    if len(stored) == 0:
        rename_conversation(conversation_id, prompt[:60] or "New conversation")
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build history from stored messages before the just-added user message.
    history = [{"role": row["role"], "content": row["content"]} for row in stored]
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                response = answer(prompt, history)
            except Exception as exc:
                response = (
                    f"An error occurred: {type(exc).__name__}: {exc}\n\n"
                    "Check your API key, network connection, and model settings."
                )
            st.markdown(response)
    add_message(conversation_id, "assistant", response)
    st.rerun()
