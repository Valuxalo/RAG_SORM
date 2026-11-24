from qdrant_client.models import Distance, VectorParams

from rag_sorm.config import settings
from rag_sorm.embeddings.model import get_embedding_dimension
from rag_sorm.vectorstore.client import get_qdrant_client


def create_collection():
    dim = get_embedding_dimension()
    client = get_qdrant_client()

    if client.collection_exists(settings.collection_name):
        print(f"Коллекция {settings.collection_name} уже существует.")
        return

    client.create_collection(
        collection_name=settings.collection_name,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    # индексирование для быстрого поиска


#     client.create_payload_index(
#         collection_name=settings.collection_name,
#         field_name="document_id",
#         field_schema=PayloadSchemaType.KEYWORD,
#     )
