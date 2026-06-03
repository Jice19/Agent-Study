import random
from typing_extensions import TypedDict, Literal
from langgraph.graph import StateGraph, START
from langgraph.types import Command

import operator
from typing_extensions import Annotated


class State(TypedDict):
    foo: Annotated[str, operator.add]

def node_a(state: State):
    print("Called A")
    value = random.choice(["a", "b"])
    print(value)
    if value == "a":
        goto = "node_b"
    else:
        goto = "node_c"

    return Command(
        update={"foo": value},
        goto=goto,
        graph=Command.PARENT, # parent 返回到父图继续执行
    )

subgraph = StateGraph(State).add_node(node_a).add_edge(START, "node_a").compile()




def node_b(state: State):
    print("Called B")
    return {"foo": "b"}

def node_c(state: State):
    print("Called C")
    return {"foo": "c"}



builder = StateGraph(State)
builder.add_edge(START, "subgraph")
builder.add_node("subgraph", subgraph)
builder.add_node(node_b)
builder.add_node(node_c)
graph = builder.compile()

from IPython.display import display, Image
try:
    display(Image(graph.get_graph().draw_png(output_file_path='./img/示例7.png')))
except Exception as e:
    print(e)  # Failed to render the graph using the Mermaid.INK API. Status code: 400.
    pass

print(graph.invoke({"foo": "bc"}))