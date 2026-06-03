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


# 初始化大模型（需要设置OPENAI_API_KEY环境变量）
model = ChatOpenAI(model="gpt-4o-mini")


# 初始化检查点存储
checkpointer = MemorySaver()

# 定义人类介入节点
def human_node(state: State):
    value = interrupt(
        {
            "text_to_revise": state["some_text"],
            "instructions": "请修改以下文本："
        }
    )
    return {"some_text": value}

# 修改后的自动处理节点（调用大模型）
def process_text(state: State):
    # 构造模型请求
    message = model.invoke([
        HumanMessage(content=f"请处理以下请求：{state['some_text']}。保持回答简洁。")
    ])
    # 返回模型生成的文本
    return {"some_text": message.content}


# 构建工作流
graph_builder = StateGraph(State)

# 添加节点
graph_builder.add_node("human_review", human_node)
graph_builder.add_node("auto_process", process_text)

# 设置流程
graph_builder.set_entry_point("auto_process")
graph_builder.add_edge("auto_process", "human_review")

# 编译图表
graph = graph_builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"]
)

# 使用示例（保持不变）
if __name__ == "__main__":
    thread_id = "thread_123"
    thread_config = {"configurable": {"thread_id": thread_id}}

    initial_state = {"some_text": "输出一个五五乘法表"}
    result = graph.invoke(initial_state, config=thread_config)
    print("自动处理结果:", result["some_text"])

    human_input = input("请输入人类输入：")
    resume_result = graph.invoke(
        Command(resume=human_input),
        config=thread_config
    )

    print("最终结果:", resume_result["some_text"])


