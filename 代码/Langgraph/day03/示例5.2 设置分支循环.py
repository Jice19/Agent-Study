import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
count = 0

class State(TypedDict):
    aggregate: Annotated[list, operator.add]


def a(state: State):
    print(f'Node A sees {state["aggregate"]}')
    return {"aggregate": ["A"]}


def b(state: State):
    print(f'Node B sees {state["aggregate"]}')
    return {"aggregate": ["B"]}


def c(state: State):
    print(f'Node C sees {state["aggregate"]}')
    return {"aggregate": ["C"]}


def d(state: State):
    print(f'Node D sees {state["aggregate"]}')
    return {"aggregate": ["D"]}

builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(c)
builder.add_node(d)

def route(state: State) -> Literal["b", END]:
    print(len(state["aggregate"]))
    if len(state["aggregate"]) < 100:
        return "b"
    else:
        return END


builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "c")
builder.add_edge("b", "d")
builder.add_edge(["c", "d"], "a")
graph = builder.compile()

from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_png(output_file_path='./img/示例5.2.1.png')))
except:
    pass

from langgraph.errors import GraphRecursionError

try:
    # result = graph.invoke({"aggregate": []})
    result = graph.invoke({"aggregate": []}, {"recursion_limit": 25})
    print(result)
except GraphRecursionError:
    print("Recursion Error")
