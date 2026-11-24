from collections.abc import Iterator
from contextlib import contextmanager

from langchain_core.messages import HumanMessage
from langgraph.graph import CompiledStateGraph
from sorm_rag.memory.checkpointer import create_checkpointer
from sorm_rag.rag.pipeline import build_rag_graph


@contextmanager
def create_rag_graph() -> Iterator[CompiledStateGraph]:

    with create_checkpointer() as checkpointer:
        graph = build_rag_graph(checkpointer)

        yield graph


def run_chat(
    graph: CompiledStateGraph,
    thread_id: str,
    question: str,
) -> str:

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    result = graph.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config,
    )

    return result["messages"][-1].content


def get_chat_history(
    graph: CompiledStateGraph,
    thread_id: str,
) -> list:

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    state = graph.get_state(config)

    return state.values.get("messages", [])
