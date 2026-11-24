from rag_sorm.ingestion.pipeline import ingest_documents


def main():

    result = ingest_documents()

    print("Индексация завершена!")
    print(f"Документов: {result['documents_count']}")
    print(f"Чанков: {result['chunks_count']}")


if __name__ == "__main__":
    main()
