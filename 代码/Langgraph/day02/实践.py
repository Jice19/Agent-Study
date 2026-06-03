"""基本ChatBot+Tools+Memory"""

# 环境导入
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model_name="gpt-4o-mini")
# 搜索引擎工具 tavily
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=2)
tools = [tool]

# 绑定工具
llm_with_tools = llm.bind_tools(tools)

# 记忆 Memory
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

# 图结构
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list, add_messages]


# 初始化状态图
bulider_graph = StateGraph(State)


# 定义一个节点用于invoke我的prompt
def chatbot(state: State):
    # return {"messages": llm.invoke(state["messages"])}
    # return {"messages": llm_with_tools.invoke(state["messages"])}
    """修改部分 取值问题"""
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

import json
from langchain_core.messages import ToolMessage


class BasicToolNode:
    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


# 路由选择
def route_tools(state: State):
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


# 增加条件边
bulider_graph.add_conditional_edges('chatbot', route_tools, {"tools": "tools", END: END})

# 添加节点、添加边
tool_node = BasicToolNode(tools=[tool])
bulider_graph.add_node("tools", tool_node)
bulider_graph.add_edge("tools", 'chatbot')
bulider_graph.add_node("chatbot", chatbot)
bulider_graph.add_edge(START, "chatbot")
bulider_graph.add_edge("chatbot", END)

# 编译图
graph = bulider_graph.compile(checkpointer=memory)

# 可视化图
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png(output_file_path='./实践.png')))
except:
    pass


# 与模型交互
def stream_graph_updatas(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
        for value in event.values():
            print('AI:', value['messages'][-1].content)


# 运行图
while True:
    try:
        # 配置
        config = {'configurable': {'thread_id': '1'}}
        user_input = input("User: ")
        if user_input in ['quit', 'exit', 'q']:
            print('拜拜')
            break
        # 写一个函数用于讲user_input与LLM进行交互
        stream_graph_updatas(user_input)
    except Exception as e:
        print(e)
