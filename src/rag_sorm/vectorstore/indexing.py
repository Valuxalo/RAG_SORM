import uuid

from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

from rag_sorm.config import settings
from rag_sorm.embeddings.model import get_embedding_model
from rag_sorm.vectorstore.client import get_qdrant_client
from rag_sorm.vectorstore.collection import create_collection


def index_chunks(chunks, batch_size=32):
    model = get_embedding_model()
    client = get_qdrant_client()
    create_collection()
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c["text"] for c in batch]

        vectors = model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,  # для косинусной близости
        )

        points = []
        for chunk, vec in zip(batch, vectors, strict=False):
            # детерминированный id: повторный запуск не создаст дубли
            key = f"{chunk['meta']['document_id']}:{chunk['meta']['section']}:{chunk['meta']['points']}:{chunk['meta']['part']}"
            point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, key))

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vec.tolist(),
                    payload={**chunk["meta"], "text": chunk["text"]},
                )
            )

        client.upload_points(
            collection_name=settings.collection_name,
            points=points,
            batch_size=100,
        )


def document_exists(client, document_id: str) -> bool:

    records, _ = client.scroll(
        collection_name=settings.collection_name,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id),
                )
            ]
        ),
        limit=1,
        with_payload=False,
        with_vectors=False,
    )

    return len(records) > 0
