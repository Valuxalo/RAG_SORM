from functools import lru_cache

from sentence_transformers import SentenceTransformer

from rag_sorm.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Загружает embedding-модель."""

    model = SentenceTransformer(settings.embedding_model)
    model.max_seq_length = settings.embedding_max_seq_length

    return model


def get_embedding_dimension() -> int:
    """Возвращает размерность эмбеддингов."""

    return get_embedding_model().get_sentence_embedding_dimension()
