from openai import OpenAI
from models import *

'''
    1.传统方式跟大模型交互
'''
# 创建大模型连接
'''
client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
completion = client.chat.completions.create(
    model="qwen3-max",
    02_messages_v1=[
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': '你是谁？'}],
)
print(completion.choices[0].message.content)
'''



'''
    2.langchain访问大模型LLM
'''

response = qwen.invoke("你是谁？")  # invoke: 调用
print(response.content)

