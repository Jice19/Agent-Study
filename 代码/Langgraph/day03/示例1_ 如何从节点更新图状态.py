"""加载环境变量"""
from dotenv import load_dotenv
load_dotenv()

"""定义状态"""
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict

class State(TypedDict):
    messages: list[AnyMessage]
    extra_field: int


"""定义图结构"""
from langchain_core.messages import AIMessage

def node(state: State):
    """
    该节点简单地将一条消息添加到我们的消息列表中，并填充一个额外字段。
    注意点: 节点应直接返回状态更新，而不是修改状态。
    """
    messages = state["messages"]
    new_message = AIMessage("Hello!")
    return {"messages": messages + [new_message], "extra_field": 10}


from langgraph.graph import StateGraph
graph_builder = StateGraph(State)

graph_builder.add_node(node)
graph_builder.set_entry_point("node")
graph = graph_builder.compile()


"""可视化图"""
from IPython.display import Image, display
display(Image(graph.get_graph().draw_mermaid_png(output_file_path='./img/示例1.png')))


"""运行图"""
from langchain_core.messages import HumanMessage
result = graph.invoke({"messages": [HumanMessage("Hi")]})
print(result)


"""美化打印消息对象的内容"""
for message in result["messages"]:
    message.pretty_print()

