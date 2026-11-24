from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph

from rag_sorm.config import settings
from rag_sorm.generation.yandex import ask_yandexgpt
from rag_sorm.observability.langfuse import get_langfuse
from rag_sorm.observability.tracing import serialize_chunks
from rag_sorm.retrieval.query_rewriter import build_search_query
from rag_sorm.retrieval.reranker import Reranker
from rag_sorm.retrieval.search import search_chunks


def build_rag_graph(checkpointer):

    langfuse = get_langfuse()

    # Загружаем reranker один раз при создании графа
    reranker = Reranker()

    def rag_node(
        state: MessagesState,
        config: RunnableConfig,
    ):

        messages = state["messages"]

        # Текущий вопрос
        question = messages[-1].content

        # Получаем историю без последнего вопроса
        history = []

        for message in messages[:-1]:
            if isinstance(message, HumanMessage):
                role = "user"

            elif isinstance(message, AIMessage):
                role = "assistant"

            else:
                continue

            history.append(
                {
                    "role": role,
                    "content": str(message.content),
                }
            )

        # Ограничиваем историю для использования в контексте
        history = history[-settings.memory_window :]

        thread_id = config["configurable"]["thread_id"]

        # Создаём трассировку одного пользовательского запроса
        with langfuse.start_as_current_observation(
            as_type="span",
            name="sorm-rag-pipeline",
            input={
                "question": question,
                "history": history,
            },
        ) as trace:
            with langfuse.propagate_attributes(
                session_id=thread_id,
                trace_name="SORM RAG",
                metadata={
                    "pipeline": "hybrid-rag",
                },
            ):
                # ==================================
                # 1. MEMORY
                # ==================================

                with langfuse.start_as_current_observation(
                    as_type="span",
                    name="memory",
                    input={
                        "thread_id": thread_id,
                    },
                ) as memory_span:
                    memory_span.update(
                        output={
                            "messages_count": len(history),
                            "history": history,
                        }
                    )

                # ==================================
                # 2. QUERY PREPARATION
                # ==================================

                search_query = build_search_query(
                    question=question,
                    history=history,
                )

                with langfuse.start_as_current_observation(
                    as_type="span",
                    name="query-preparation",
                    input={
                        "question": question,
                        "history": history,
                    },
                ) as query_span:
                    query_span.update(
                        output={
                            "search_query": search_query,
                        }
                    )

                # ==================================
                # 3. RETRIEVAL
                # ==================================

                with langfuse.start_as_current_observation(
                    as_type="retriever",
                    name="qdrant-retrieval",
                    input={
                        "query": search_query,
                        "top_k": settings.retrieval_top_k,
                    },
                ) as retrieval_span:
                    chunks = search_chunks(
                        question=search_query,
                        top_k=settings.retrieval_top_k,
                    )

                    retrieval_span.update(
                        output={
                            "chunks_count": len(chunks),
                            "chunks": serialize_chunks(chunks),
                        }
                    )

                # ==================================
                # 4. RERANKING
                # ==================================

                with langfuse.start_as_current_observation(
                    as_type="span",
                    name="reranking",
                    input={
                        "query": search_query,
                        "chunks_count": len(chunks),
                    },
                ) as rerank_span:
                    ranked_chunks = reranker.rerank(
                        query=search_query,
                        chunks=chunks,
                        top_k=settings.final_top_k,
                    )

                    rerank_span.update(
                        output={
                            "chunks_count": len(ranked_chunks),
                            "chunks": serialize_chunks(ranked_chunks),
                        }
                    )

                # ==================================
                # 5. GENERATION
                # ==================================

                with langfuse.start_as_current_observation(
                    as_type="generation",
                    name="yandexgpt-generation",
                    model="yandexgpt",
                    model_parameters={
                        "temperature": 0.1,
                        "max_tokens": 1500,
                    },
                    input={
                        "question": question,
                        "history": history,
                        "chunks": serialize_chunks(ranked_chunks),
                    },
                ) as generation:
                    response = ask_yandexgpt(
                        question=question,
                        chunks=ranked_chunks,
                        history=history,
                    )

                    generation.update(
                        output={
                            "answer": response,
                        }
                    )

                # ==================================
                # 6. PIPELINE RESULT
                # ==================================

                trace.update(
                    output={
                        "answer": response,
                        "retrieved_chunks": len(chunks),
                        "reranked_chunks": len(ranked_chunks),
                    }
                )

        return {"messages": [AIMessage(content=response)]}

    builder = StateGraph(MessagesState)

    builder.add_node("rag", rag_node)

    builder.add_edge(START, "rag")
    builder.add_edge("rag", END)

    return builder.compile(checkpointer=checkpointer)
