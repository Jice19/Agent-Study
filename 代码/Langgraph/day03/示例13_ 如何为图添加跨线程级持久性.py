# 加载环境变量（通常用于存储API密钥等敏感信息）
from dotenv import load_dotenv
load_dotenv()

# 导入内存存储模块和OpenAI嵌入模型
from langgraph.store.memory import InMemoryStore
from langchain_openai import OpenAIEmbeddings

# 初始化内存存储系统，配置嵌入模型和维度
in_memory_store = InMemoryStore(
    index={
        "embed": OpenAIEmbeddings(model="text-embedding-3-small"),  # 使用OpenAI的小型嵌入模型
        "dims": 1536,  # 对应text-embedding-3-small模型的输出维度
    }
)

# 导入必要模块
import uuid
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.base import BaseStore

# 初始化OpenAI聊天模型（使用最新的gpt-4o-mini模型）
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o-mini")


# 定义核心处理函数
def call_model(state: MessagesState, config: RunnableConfig, *, store: BaseStore):
    """对话处理核心逻辑，包含记忆存储和检索功能"""
    # 从配置中获取用户ID，创建专属的命名空间
    user_id = config["configurable"]["user_id"]
    namespace = ("memories", user_id)

    # 在存储中搜索与当前对话相关的记忆
    memories = store.search(namespace, query=str(state["messages"][-1].content))

    # 将记忆数据转换为字符串格式
    info = "\n".join([d.value["data"] for d in memories])

    # 构建系统提示，包含用户记忆信息
    system_msg = f"You are a helpful assistant talking to the user. User info: {info}"

    # 检查是否需要存储新记忆
    last_message = state["messages"][-1]
    print('last_message：',last_message)
    if "remember" in last_message.content.lower():
        # 生成并存储新记忆（示例记忆内容）
        memory = "User name is Cat"
        store.put(namespace, str(uuid.uuid4()), {"data": memory})  # 使用UUID作为唯一键

    # 调用AI模型生成回复（结合系统提示和对话历史）
    response = model.invoke(
        [{"role": "system", "content": system_msg}] + state["messages"]
    )
    return {"messages": response}


# 构建状态图工作流
builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)  # 添加处理节点
builder.add_edge(START, "call_model")  # 设置起始节点


# 编译完整的工作流图，配置内存检查点和存储
graph = builder.compile(
    checkpointer=MemorySaver(),  # 用于保存对话状态的检查点
    store=in_memory_store  # 使用之前配置的内存存储
)

from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_png(output_file_path='./img/示例13.png')))
except:
    pass




# 测试场景1：存储记忆
config = {"configurable": {"thread_id": "1", "user_id": "1"}}  # 用户1的对话配置
input_message = {"role": "user", "content": "Hi! Remember: my name is Cat"}
print("第一次对话（存储记忆）:")
for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()  # 格式化输出模型回复

# 查看存储的记忆
print("\n存储的记忆内容:")
for memory in in_memory_store.search(("memories", "1")):
    print(memory.value)

# 测试场景2：读取记忆
config = {"configurable": {"thread_id": "3", "user_id": "1"}}  # 用户2的对话配置
input_message = {"role": "user", "content": "what is my name?"}
print("\n第二次对话（读取记忆）:")

# 跨线程读取到记忆
for chunk in graph.stream({"messages": [input_message]}, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

