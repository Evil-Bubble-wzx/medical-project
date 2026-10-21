from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class RetrievalState(TypedDict, total=False):
    question: str
    patient_context: str
    query: str
    result: dict


def retrieval_graph(engine, mode="keyword", limit=10):
    if mode not in ("keyword", "vector", "hybrid"):
        raise ValueError("unknown_retrieval_strategy")

    def prepare(state):
        query = " ".join([state["question"], state.get("patient_context", "")]).strip()
        if not query or len(query) > 500:
            raise ValueError("invalid_retrieval_query")
        return {"query": query}

    def retrieve(state):
        return {"result": engine.retrieve(state["query"], mode, limit)}

    builder = StateGraph(RetrievalState)
    builder.add_node("prepare_query", prepare)
    builder.add_node("retrieve_evidence", retrieve)
    builder.add_edge(START, "prepare_query")
    builder.add_edge("prepare_query", "retrieve_evidence")
    builder.add_edge("retrieve_evidence", END)
    return builder.compile()
