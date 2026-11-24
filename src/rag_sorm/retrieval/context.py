def build_context(chunks, max_chars=12000):
    parts, total = [], 0
    for i, c in enumerate(chunks, 1):
        m = c["meta"]
        pts = ", ".join(m.get("points", []))
        header = f"[{i}] {m['title']}"
        if m.get("section"):
            header += f", {m['section']}"
        header += f", п. {pts}"
        block = f"{header}\n{c['text']}"
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    return "\n\n---\n\n".join(parts)
