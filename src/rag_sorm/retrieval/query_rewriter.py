def build_search_query(
    question: str,
    history: list[dict],
) -> str:

    if not history:
        return question

    history_text = "\n".join(message["content"] for message in history[-4:])

    return f"{history_text}\n{question}"
