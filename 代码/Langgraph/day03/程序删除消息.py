from typing import Literal
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode

memory = MemorySaver()


@tool
def search(query: str):
    """Call to surf the web."""
    # This is a placeholder for the actual implementation
    # Don't let the LLM know this though 😊
    return "It's sunny in San Francisco, but you better look out if you're a Gemini 😈."


tools = [search]
tool_node = ToolNode(tools)
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model_name="gpt-4o-mini")
bound_model = model.bind_tools(tools)


def should_continue(state: MessagesState):
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return END
    return "action"


def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    ["action", END],
)

workflow.add_edge("action", "agent")

app = workflow.compile(checkpointer=memory)


from langchain_core.messages import RemoveMessage
from langgraph.graph import END


'自定义'
def delete_messages(state):
    messages = state["messages"]
    print('############@',messages)
    if len(messages) > 3:
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:-3]]}


# We need to modify the logic to call delete_messages rather than end right away
def should_continue(state: MessagesState) -> Literal["action", "delete_messages"]:
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "delete_messages"
    return "action"


# Define a new graph
workflow = StateGraph(MessagesState)
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# This is our new node we're defining
workflow.add_node(delete_messages)


workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
)
workflow.add_edge("action", "agent")

# This is the new edge we're adding: after we delete messages, we finish
workflow.add_edge("delete_messages", END)
app = workflow.compile(checkpointer=memory)
from IPython.display import Image, display
try:
    display(Image(app.get_graph().draw_png(output_file_path='./img/程序删除消息.png')))
except:
    pass


from langchain_core.messages import HumanMessage


config = {"configurable": {"thread_id": "3"}}
input_message = HumanMessage(content="hi! I'm bob")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    print(event)
    print([(message.type, message.content) for message in event["messages"]])


input_message = HumanMessage(content="what's my name?")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    print([(message.type, message.content) for message in event["messages"]])



