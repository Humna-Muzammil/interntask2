import hashlib
import os
import chromadb
from openai import OpenAI
from rag.document_loader import extract_file
from rag.chunker import chunk_segments

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = "productivity_documents"

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

def embed_texts(texts: list[str]) -> list[list[float]]:
    client = OpenAI()
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    vectors = []
    # Keep batches modest to avoid oversized requests.
    for start in range(0, len(texts), 64):
        response = client.embeddings.create(model=model, input=texts[start:start+64])
        vectors.extend(item.embedding for item in response.data)
    return vectors

def ingest_file(path: str) -> int:
    segments = extract_file(path)
    chunks = chunk_segments(segments)
    if not chunks:
        return 0
    vectors = embed_texts([chunk["text"] for chunk in chunks])
    collection = get_collection()
    # Deterministic IDs make re-uploading a file replace its previous chunks.
    file_key = hashlib.sha256(os.path.basename(path).encode()).hexdigest()[:16]
    old = collection.get(where={"file_key": file_key})
    if old["ids"]:
        collection.delete(ids=old["ids"])
    ids, metadatas, documents = [], [], []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        ids.append(f"{file_key}-{i}")
        metadatas.append({
            "source": chunk["source"],
            "location": chunk["location"],
            "file_key": file_key,
        })
        documents.append(chunk["text"])
    collection.add(ids=ids, embeddings=vectors, metadatas=metadatas, documents=documents)
    return len(chunks)

def retrieve(query: str, top_k: int = 5) -> list[dict]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    vector = embed_texts([query])[0]
    result = collection.query(
        query_embeddings=[vector],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"]
    )
    hits = []
    for doc, metadata, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        hits.append({"text": doc, **metadata, "distance": distance})
    return hits
