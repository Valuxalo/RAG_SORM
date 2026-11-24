from pathlib import Path

import pymupdf
from docx import Document
from striprtf.striprtf import rtf_to_text

from rag_sorm.config import settings


def _table_to_markdown(table) -> str:
    """Таблица в markdown; запасной вариант, если to_markdown недоступен."""
    try:
        return table.to_markdown().strip()
    except Exception:
        rows = [[(c or "").replace("\n", " ").strip() for c in row] for row in table.extract() if row]
        if not rows:
            return ""
        header, *body = rows
        lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join("---" for _ in header) + " |",
        ]
        lines += ["| " + " | ".join(r) + " |" for r in body]
        return "\n".join(lines)


def _page_text(page, top, bottom) -> str:
    """Текст страницы в вертикальной полосе [top, bottom]."""
    if bottom - top < 1:
        return ""
    rect = pymupdf.Rect(0, top, page.rect.width, bottom)
    return page.get_text("text", clip=rect).strip()


def load_pdf(path, header_margin=0, footer_margin=0):
    """
    Извлекает текст и таблицы в правильном порядке.
    Таблицы вставляются в markdown на своё место, без дублей в тексте.
    header_margin / footer_margin: сколько пунктов обрезать сверху/снизу
    (колонтитулы, номера страниц).
    """
    doc = pymupdf.open(str(Path(path)))
    pages = []

    try:
        for page in doc:
            page_top = header_margin
            page_bottom = page.rect.height - footer_margin

            tables = sorted(
                page.find_tables().tables,
                key=lambda t: t.bbox[1],
            )

            parts = []
            y = page_top

            for table in tables:
                _, t_top, _, t_bottom = table.bbox

                # текст над таблицей
                if t_top > y:
                    text = _page_text(page, y, t_top)
                    if text:
                        parts.append(text)

                md = _table_to_markdown(table)
                if md:
                    parts.append(md)

                y = max(y, t_bottom)

            # текст под последней таблицей (или весь текст, если таблиц нет)
            text = _page_text(page, y, page_bottom)
            if text:
                parts.append(text)

            pages.append("\n\n".join(parts))
    finally:
        doc.close()

    return "\n\n".join(pages)


def load_docx(path):
    doc = Document(str(path))

    paragraphs = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]

    return "\n".join(paragraphs)


def load_rtf(path):
    with open(path, encoding="utf-8", errors="replace") as file:
        rtf_content = file.read()

    return rtf_to_text(rtf_content)


def load_document(path):
    path = Path(path)

    loaders = {
        ".pdf": load_pdf,
        ".docx": load_docx,
        ".rtf": load_rtf,
    }

    loader = loaders.get(path.suffix.lower())

    if loader is None:
        raise ValueError(f"Неподдерживаемый формат файла: {path.suffix}")

    return loader(path)


def load_documents(directory: Path | None = None) -> list[dict]:
    documents = []
    directory = directory or settings.documents_dir

    for file_path in directory.iterdir():
        if not file_path.is_file():
            continue

        try:
            text = load_document(file_path)

            if text:
                documents.append({"filename": file_path.name, "text": text})

        except Exception as error:
            print(f"Ошибка загрузки {file_path.name}: {error}")

    return documents
