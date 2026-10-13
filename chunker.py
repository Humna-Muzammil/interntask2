def chunk_segments(segments: list[dict], chunk_size: int = 1200, overlap: int = 180) -> list[dict]:
    """Split segments into overlapping character chunks and preserve their citations."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Require chunk_size > overlap >= 0.")
    chunks = []
    for segment in segments:
        text = segment["text"]
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append({
                    "text": piece,
                    "source": segment["source"],
                    "location": segment["location"],
                })
            if end == len(text):
                break
            start = end - overlap
    return chunks
