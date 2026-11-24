def serialize_chunks(chunks: list[dict]) -> list[dict]:
    result = []

    for chunk in chunks:
        result.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "text": chunk.get("text"),
                "title": chunk.get("title"),
                "document_id": chunk.get("document_id"),
                "section": chunk.get("section"),
                "points": chunk.get("points"),
                "score": chunk.get("score"),
                "rerank_score": chunk.get("rerank_score"),
            }
        )

    return result
