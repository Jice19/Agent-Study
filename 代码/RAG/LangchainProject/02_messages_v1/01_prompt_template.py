from langchain_core.prompts import ChatPromptTemplate

from models import *

'''
    ChatPromptTemplate：提供角色设置: 
        system(系统角色), user(用户角色), assistant(大模型回复)
'''

prompt = ChatPromptTemplate([
    ("system", "把用户输入的中文翻译成{language}"),
    ("user", "{text}"),
    # ("assistant", "我是AI回复的内容"),
])
prompt = prompt.format(language="英文", text="我喜欢打篮球")
print("prompt:", prompt)
print('-' * 100)

# invoke调用
result = qwen.invoke(prompt)
print(result)