from functools import lru_cache

from qdrant_client import QdrantClient

from rag_sorm.config import settings


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    """Создаёт и возвращает клиент Qdrant."""

    return QdrantClient(
        #        url=QDRANT_URL,
        #        api_key=QDRANT_API_KEY,
        path=str(settings.qdrant_path)
    )
