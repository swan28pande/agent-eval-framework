"""A tiny two-agent LangGraph workflow used as the default evaluation target."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .tracing import traced_node


class State(TypedDict, total=False):
    input: str
    draft: str
    output: str


ANSWERS = {"capital of france": "Paris", "17 + 25": "42"}


def solver(state: State) -> State:
    q = state["input"].lower()
    answer = next((a for k, a in ANSWERS.items() if k in q), "I don't know")
    return {"draft": answer}


def reviewer(state: State) -> State:
    return {"output": f"Answer: {state['draft']}"}


def build_sample_workflow(tracer):
    g = StateGraph(State)
    g.add_node("solver", traced_node(tracer, "solver", solver))
    g.add_node("reviewer", traced_node(tracer, "reviewer", reviewer))
    g.add_edge(START, "solver")
    g.add_edge("solver", "reviewer")
    g.add_edge("reviewer", END)
    return g.compile()
