from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
llm = ChatOpenAI()
from langchain.schema import (
    AIMessage,     # 等价于OpenAI接口中的 assistant role
    HumanMessage,  # 等价于OpenAI接口中的 user role
    SystemMessage  # 等价于OpenAI接口中的 system role

)

messages = [
    SystemMessage(content="你是一个乐于助人的AI助手，回答时尽量简洁。"),
    HumanMessage(content="你好！你能介绍下自己吗？"),
    AIMessage(content='你好！我是AI助手，可以帮你解决问题。'),
    HumanMessage('Python里如何写"Hello World"')
]
print(llm.invoke(messages).content)

