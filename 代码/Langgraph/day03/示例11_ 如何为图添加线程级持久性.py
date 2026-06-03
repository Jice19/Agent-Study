from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
model = ChatOpenAI(model="gpt-4o-mini")

from langgraph.graph import StateGraph, MessagesState, START

def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")

from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

graph = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "1"}}


input_message = {"role": "user", "content": "hi! I'm Cat"}
for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()


input_message = {"role": "user", "content": "what's my name?"}
for chunk in graph.stream({"messages": [input_message]},{"configurable": {"thread_id": "1"}},stream_mode="values",):
    chunk["messages"][-1].pretty_print()