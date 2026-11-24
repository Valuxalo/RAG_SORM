def split_long_point(point, max_chars):
    lines = point["text"].split("\n")
    first, rest = lines[0], lines[1:]

    # вводная фраза: только если она короткая
    intro = first if len(first) <= 300 else ""
    if not intro:
        rest = lines  # первая строка тоже участвует в нарезке

    parts, cur, size = [], [], len(intro)
    for ln in rest:
        if cur and size + len(ln) + 1 > max_chars:
            parts.append("\n".join(([intro] if intro else []) + cur))
            cur, size = [], len(intro)
        cur.append(ln)
        size += len(ln) + 1
    if cur:
        parts.append("\n".join(([intro] if intro else []) + cur))
    return parts or [point["text"]]


def _prefix(doc_meta, section, label):
    prefix = doc_meta["title"]
    if section:
        prefix += f" > {section}"
    return f"{prefix} > {label}"


def build_chunks(points, doc_meta, max_chars=1500):
    chunks = []
    buf = []  # накопленные пункты
    buf_len = 0

    def flush():
        nonlocal buf, buf_len
        if not buf:
            return
        nums = [p["point"] for p in buf]
        label = f"п. {nums[0]}" if len(nums) == 1 else f"п. {nums[0]}-{nums[-1]}"
        prefix = _prefix(doc_meta, buf[0]["section"], label)
        chunks.append(
            {
                "text": f"{prefix}\n\n" + "\n\n".join(p["text"] for p in buf),
                "meta": {
                    **doc_meta,
                    "section": buf[0]["section"],
                    "points": nums,
                    "part": 1,
                    "parts_total": 1,
                },
            }
        )
        buf, buf_len = [], 0

    for p in points:
        label = f"п. {p['point']}"
        prefix_len = len(_prefix(doc_meta, p["section"], label)) + 2
        limit = max(max_chars - prefix_len, 300)

        # смена раздела закрывает буфер
        if buf and buf[0]["section"] != p["section"]:
            flush()

        # длинный пункт: отдельные чанки, буфер закрываем
        if len(p["text"]) > limit:
            flush()
            parts = split_long_point(p, limit)
            for i, part in enumerate(parts, 1):
                suffix = f" (часть {i}/{len(parts)})" if len(parts) > 1 else ""
                chunks.append(
                    {
                        "text": f"{_prefix(doc_meta, p['section'], label)}{suffix}\n\n{part}",
                        "meta": {
                            **doc_meta,
                            "section": p["section"],
                            "points": [p["point"]],
                            "part": i,
                            "parts_total": len(parts),
                        },
                    }
                )
            continue

        # обычный пункт: в буфер, если помещается
        add = len(p["text"]) + (2 if buf else 0)
        if buf and buf_len + add > max_chars - prefix_len:
            flush()
            add = len(p["text"])
        buf.append(p)
        buf_len += add

    flush()
    return chunks
