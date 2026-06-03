import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph, START
from langchain_openai import ChatOpenAI
openai_model = ChatOpenAI(model="gpt-4o-mini",api_key='sk-p6Ffzgxl7iTh3VUh32108d43FbEe426f8250A2E4596057A4',base_url="https://ai-yyds.com/v1/")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


# def _call_model(state):
#     print(state["messages"])
#     response = openai_model.invoke(state["messages"])
#     print(response)
#     return {"messages": [response]}
#
# # Define a new graph
# builder = StateGraph(AgentState)
# builder.add_node("model", _call_model)
# builder.add_edge(START, "model")
# builder.add_edge("model", END)
# graph = builder.compile()
# print(graph.invoke({"messages": [HumanMessage(content="hi")]}))


from langchain_core.runnables.config import RunnableConfig
Anthropic_model = ChatOpenAI(model="claude-3-5-sonnet-latest",api_key='sk-Ixp4CiSN1Fl7vivL109b94B777Be413699936f6f6a038a04',base_url="https://ai-yyds.com/v1/")

models = {
    "anthropic": Anthropic_model,
    "openai": openai_model,
}

def _call_model(state: AgentState, config: RunnableConfig):
    # Access the config through the configurable key
    print('###',config["configurable"])
    model_name = config["configurable"].get("model", "anthropic")
    print('model_name：',model_name)
    model = models[model_name]
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# Define a new graph
builder = StateGraph(AgentState)
builder.add_node("model", _call_model)
builder.add_edge(START, "model")
builder.add_edge("model", END)

graph = builder.compile()

config = {"configurable": {"model": "openai"}}
print(graph.invoke({"messages": [HumanMessage(content="who are you?")]}, config=config))