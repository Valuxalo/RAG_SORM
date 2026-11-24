from rag_sorm.memory.manager import (
    create_rag_graph,
    get_chat_history,
    run_chat,
)
from rag_sorm.observability.langfuse import get_langfuse


def main():

    thread_id = "test_dialog_001"

    with create_rag_graph() as graph:
        answer1 = run_chat(
            graph=graph,
            thread_id=thread_id,
            question="Что регулирует приказ №645?",
        )

        print("\nОтвет 1:")
        print(answer1)

        answer2 = run_chat(
            graph=graph,
            thread_id=thread_id,
            question="Какие требования он устанавливает?",
        )

        print("\nОтвет 2:")
        print(answer2)

        print("\nИстория диалога:")

        history = get_chat_history(
            graph=graph,
            thread_id=thread_id,
        )

        for message in history:
            print(f"\n{type(message).__name__}:")
            print(message.content)

    get_langfuse().flush()


if __name__ == "__main__":
    main()
