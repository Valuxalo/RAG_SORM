import requests
from prompts import SYSTEM_PROMPT

from rag_sorm.config import YANDEX_API_KEY, YANDEX_FOLDER_ID, YANDEX_URL
from rag_sorm.retrieval.context import build_context


def ask_yandexgpt(
    question: str,
    chunks: list[dict],
    history: list[dict] | None = None,
    model_name: str = "yandexgpt",
    temperature: float = 0.1,
    max_tokens: int = 1500,
) -> str:

    context = build_context(chunks)

    messages = [
        {
            "role": "system",
            "text": SYSTEM_PROMPT,
        }
    ]

    # Добавляем историю диалога
    if history:
        for message in history:
            messages.append(
                {
                    "role": message["role"],
                    "text": message["content"],
                }
            )

    # Текущий вопрос и найденные фрагменты
    user_prompt = f"Фрагменты документов:\n\n{context}\n\nВопрос: {question}"

    messages.append(
        {
            "role": "user",
            "text": user_prompt,
        }
    )

    body = {
        "modelUri": (f"gpt://{YANDEX_FOLDER_ID}/{model_name}/latest"),
        "completionOptions": {
            "stream": False,
            "temperature": temperature,
            "maxTokens": str(max_tokens),
        },
        "messages": messages,
    }

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "x-folder-id": YANDEX_FOLDER_ID,
    }

    response = requests.post(
        YANDEX_URL,
        json=body,
        headers=headers,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()["result"]["alternatives"][0]["message"]["text"]
