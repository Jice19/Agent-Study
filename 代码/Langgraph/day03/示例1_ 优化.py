"""加载环境变量"""
from dotenv import load_dotenv

load_dotenv()
from operator import add

# 自定义
# def add(left, right):
#     return left + right

"""定义状态"""
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from typing_extensions import TypedDict, Annotated

# class State(TypedDict):
#     messages: Annotated[list[AnyMessage], add]
#     extra_field: int


from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    extra_field: int


from langgraph.graph import MessagesState


class State(MessagesState):
    extra_field: int


"""
内置规约器使用
from langgraph.graph.message import add_messages
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    extra_field: int
    
状态管理
from langgraph.graph import MessagesState
class State(MessagesState):
    extra_field: int
"""


def node(state: State):
    new_message = AIMessage("Hello!")
    """注意点"""
    return {"messages": [new_message], "extra_field": 10}


from langgraph.graph import START, StateGraph

graph = StateGraph(State).add_node(node).add_edge(START, "node").compile()

result = graph.invoke({"messages": [HumanMessage("Hi")]})
print(result)

for message in result["messages"]:
    message.pretty_print()
