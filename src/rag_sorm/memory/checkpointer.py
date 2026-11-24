from collections.abc import Iterator
from contextlib import contextmanager

from langgraph.checkpoint.postgres import PostgresSaver

from rag_sorm.config import POSTGRES_URI


@contextmanager
def create_checkpointer() -> Iterator[PostgresSaver]:

    with PostgresSaver.from_conn_string(POSTGRES_URI) as checkpointer:
        checkpointer.setup()

        yield checkpointer
