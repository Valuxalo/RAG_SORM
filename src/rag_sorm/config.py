import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
YANDEX_URL = os.getenv("YANDEX_URL")
POSTGRES_URI = os.getenv("POSTGRES_URI")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_BASE_URL = os.getenv("LANGFUSE_BASE_URL")
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Путь к папке с исходными документами
    documents_dir: Path = PROJECT_ROOT / "data" / "raw"
    qdrant_path: Path = PROJECT_ROOT / "data" / "qdrant"
    # Qdrant
    #     qdrant_url: str
    #     qdrant_api_key: str
    collection_name: str = "sorm_orders"

    # Embeddings
    embedding_model: str = "BAAI/bge-m3"
    embedding_max_seq_length: int = 1024

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    # Reranker
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_top_k: int = 5

    memory_window: int = 10


settings = Settings()
