from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call,ModelRequest,ModelResponse
from langgraph.checkpoint.memory import InMemorySaver

from models import *

# Model 模型
#  静态模型

# agent_v1 = create_agent("gpt-5")
# 或
# model = ChatOpenAI(model="gpt-5")
# agent_v1 = create_agent(qwen)
# response = agent_v1.invoke({"messages": [{"role": "user", "content": "元旦节是几号?"}]})
# print(response)



#  动态模型 Dynamic model
#   动态模型是在运行时根据当前状态和上下文选择的。这使得复杂的路由逻辑和成本优化成为可能。
#   要使用动态模型，使用@wrap_model_call装饰器创建中间件，在请求中修改模型：
basic_model = qwen
advanced_model = ds

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """根据会话复杂度选择模型."""
    message_count = len(request.state["messages"])
    # print(request.state)
    print("message_count:", message_count)
    # 根据会话长度，修改模型
    if message_count > 5:
        # 使用高级模式进行更长的对话
        model = advanced_model
        print('message_count > 5 advanced_model')
    else:
        model = basic_model
        print('message_count <= 5 basic_model')


    return handler(request.override(model=model))

# 设置记忆：支持多轮会话
checkpointer = InMemorySaver()
config = {"configurable": {"thread_id": "1"}}  # 会话的唯一标识符。

# 创建agent
agent = create_agent(
    model=basic_model,  # 默认模型
    tools=[],
    middleware=[dynamic_model_selection],
    checkpointer=checkpointer,
)

# 执行agent
for _ in range(5):
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "元旦节是几号"}]},
        config=config)
    print(response)

