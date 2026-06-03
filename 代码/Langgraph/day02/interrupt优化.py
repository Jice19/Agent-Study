from typing import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.types import Command, interrupt

# 新增模型相关导入
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


# 定义状态类型
class State(TypedDict):
    some_text: str


# 初始化大模型
model = ChatOpenAI(model="gpt-4o-mini")

# 初始化检查点存储
checkpointer = MemorySaver()


# 改造后的人类介入节点
def human_node(state: State):
    # 接收用户输入并构造新指令
    value = interrupt(
        {
            "text_to_revise": state["some_text"],
            "instructions": "请输入修改要求："
        }
    )
    return {"some_text": f"根据用户要求生成格式美观的乘法表：{value}"}


# 优化后的自动处理节点
def process_text(state: State):
    # 强化格式要求的提示词
    message = model.invoke([
        HumanMessage(content=f'''当前请求：{state["some_text"]}''')
    ])
    return {"some_text": message.content}


# 构建循环工作流
graph_builder = StateGraph(State)
graph_builder.add_node("human_review", human_node)
graph_builder.add_node("auto_process", process_text)

# 设置循环流程
graph_builder.set_entry_point("auto_process")
graph_builder.add_edge("auto_process", "human_review")
graph_builder.add_edge("human_review", "auto_process")  # 新增循环连接

# 编译图表
graph = graph_builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]
)

# 使用示例
if __name__ == "__main__":
    thread_id = "thread_123"
    thread_config = {"configurable": {"thread_id": thread_id}}

    # 初始执行
    initial_state = {"some_text": "使用python语法生成五五乘法表"}
    result = graph.invoke(initial_state, config=thread_config)
    print("首次处理结果:\n", result["some_text"])

    # 人类输入环节
    human_input = input("\n请输入修改要求：")

    # 恢复执行时直接传递新状态
    resume_result = graph.invoke(
        {"some_text": human_input},  # 关键修改点
        config=thread_config
    )

    print("\n最终处理结果:\n", resume_result["some_text"])