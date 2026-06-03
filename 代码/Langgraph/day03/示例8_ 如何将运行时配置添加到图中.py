import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict, Optional
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph, START
from langchain_openai import ChatOpenAI

openai_model = ChatOpenAI(model="gpt-4o-mini",api_key='sk-p6Ffzgxl7iTh3VUh32108d43FbEe426f8250A2E4596057A4',base_url="https://ai-yyds.com/v1/")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


from langchain_core.runnables.config import RunnableConfig
Anthropic_model = ChatOpenAI(model="claude-3-5-sonnet-latest",api_key='sk-p6Ffzgxl7iTh3VUh32108d43FbEe426f8250A2E4596057A4',base_url="https://ai-yyds.com/v1/")

models = {
    "anthropic": Anthropic_model,
    "openai": openai_model,
}


from langchain_core.messages import SystemMessage

# We can define a config schema to specify the configuration options for the graph
# A config schema is useful for indicating which fields are available in the configurable dict inside the config
class ConfigSchema(TypedDict):
    model: Optional[str]
    system_message: Optional[str]

def _call_model(state: AgentState, config: RunnableConfig):
    model_name = config["configurable"].get("model", "anthropic")
    model = models[model_name]
    messages = state["messages"]
    if "system_message" in config["configurable"]:
        messages = [SystemMessage(content=config["configurable"]["system_message"])] + messages
    response = model.invoke(messages)
    return {"messages": [response]}


# Define a new graph
builder = StateGraph(AgentState)
builder.add_node("model", _call_model)
builder.add_edge(START, "model")
builder.add_edge("model", END)

graph = builder.compile()
from IPython.display import display, Image

try:
    display(Image(graph.get_graph().draw_png(output_file_path='./img/示例8.png')))
except:
    pass


config = {"configurable": {"model": "anthropic"}}
print(graph.invoke({"messages": [HumanMessage(content="who are you?")]}, config=config))


config = {"configurable": {"system_message": "respond in Chinese","model": "openai"}}
print(graph.invoke({"messages": [HumanMessage(content="who are you?")]}, config=config))