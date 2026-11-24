from pathlib import Path
from time import perf_counter

from rag_sorm.ingestion.chunker import build_chunks
from rag_sorm.ingestion.cleaner import clean_text, parse_points
from rag_sorm.ingestion.loaders import load_documents
from rag_sorm.vectorstore.client import get_qdrant_client
from rag_sorm.vectorstore.collection import create_collection
from rag_sorm.vectorstore.indexing import document_exists, index_chunks


def ingest_documents(
    directory: Path | None = None,
) -> dict:
    start_time = perf_counter()

    client = get_qdrant_client()
    create_collection()
    # 1. Загрузка документов
    documents = load_documents(directory)

    all_chunks = []

    # 2. Обработка каждого документа
    for document in documents:
        filename = document["filename"]
        text = document["text"]

        print(f"Обработка документа: {filename}")

        text = clean_text(text)
        points = parse_points(text)

        number, extension = filename.rsplit(".", maxsplit=1)

        doc_meta = {
            "title": f"Приказ № {number}",
            "document_id": f"prikaz_{number}",
            "source": filename,
        }

        # Проверяем, есть ли документ в Qdrant
        if document_exists(client, doc_meta["document_id"]):
            print(f"Документ {filename} уже проиндексирован. Пропускаем.")
            continue

        chunks = build_chunks(points, doc_meta, max_chars=2000)
        print(f"Документ {filename} загружен")
        all_chunks.extend(chunks)

    # 3. Индексация в Qdrant
    index_chunks(all_chunks)
    elapsed = perf_counter() - start_time
    print(f"Время создания коллекции: {elapsed:.4f} сек.")

    return {
        "documents_count": len(documents),
        "chunks_count": len(all_chunks),
    }
